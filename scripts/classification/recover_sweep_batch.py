"""
recover_sweep_batch.py

Recovers a completed sweep_stale_url_noise.py batch that never got written --
the local process died (Codespace stopped, or the batch was stuck on a billing
hold) before it could fetch results and write them. Nothing is re-sent to
Anthropic; this only pulls already-completed results and writes them.

Reconstructs everything process_chunk() would have had in memory, without that
memory: the batch's own custom_id encodes ticker__filing_date__accession_number
directly, old_ai_verdict/old_human_verdict are re-fetched from
filing_ai_classifications by that same natural key, and fixed_url is recomputed
via the same correct_url() the original run used (deterministic from CIK +
accession number, not stored anywhere -- doesn't need to be looked up).

Usage:
    python recover_sweep_batch.py msgbatch_011zGpb8oTCgPtKRr83kD5mN
"""
import sys
import os
from collections import Counter

from classify_8k_filings_batch_v2 import supabase, fetch_batch_results
from sweep_stale_url_noise import TABLE, correct_url, valid, write_rows
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ingestion"))
from import_8k_filings import COMPANIES

import requests

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]


def get_batch(batch_id):
    r = requests.get(
        f"https://api.anthropic.com/v1/messages/batches/{batch_id}",
        headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def lookup_old_verdicts(keys):
    """keys: list of (ticker, filing_date, accession_number). Returns dict keyed
    the same way -> {ai_verdict, human_verdict}.

    REAL FIX (2026-09-30): original version had NO pagination on this query --
    a batch of 50 tickers can easily exceed Supabase's silent 1000-row cap given
    155,141 total 8-K filings across ~499 companies, causing most rows to be
    silently dropped. Confirmed directly: first run recovered only 97/2500 (96%
    missing) before this fix. Same bug class already documented for
    tag_reaction_character.py and classify_8k_filings.py -- should have checked
    for it before writing this script, not after seeing the failure."""
    out = {}
    tickers = sorted({k[0] for k in keys})
    for i in range(0, len(tickers), 50):
        batch_tickers = tickers[i:i + 50]
        offset = 0
        while True:
            rows = (supabase.table("filing_ai_classifications")
                    .select("ticker,filing_date,accession_number,ai_verdict,human_verdict")
                    .in_("ticker", batch_tickers)
                    .range(offset, offset + 999).execute().data)
            if not rows:
                break
            for r in rows:
                out[(r["ticker"], str(r["filing_date"])[:10], r["accession_number"])] = r
            if len(rows) < 1000:
                break
            offset += 1000
    return out


def main():
    if len(sys.argv) < 2:
        print("Usage: python recover_sweep_batch.py <batch_id>")
        sys.exit(1)
    batch_id = sys.argv[1]

    print(f"Checking batch {batch_id}...")
    batch = get_batch(batch_id)
    status = batch.get("processing_status")
    counts = batch.get("request_counts")
    print(f"  status: {status}, counts: {counts}")
    if status != "ended":
        print("Batch has not ended yet -- nothing to recover.")
        return

    url = batch.get("results_url")
    if not url:
        print("No results_url on this batch -- cannot recover.")
        return

    print("Fetching results...")
    results, _usage = fetch_batch_results(url)
    print(f"  {len(results)} results fetched.")

    # Parse every custom_id back into (ticker, filing_date, accession_number)
    parsed = {}
    for cid in results:
        parts = cid.split("__")
        if len(parts) != 3:
            print(f"  WARNING: unparseable custom_id {cid!r}, skipping")
            continue
        parsed[cid] = tuple(parts)  # (ticker, filing_date, accession_number)

    print("Looking up old verdicts from filing_ai_classifications...")
    old_verdicts = lookup_old_verdicts(list(parsed.values()))
    cik_by_ticker = {c["ticker"]: c["cik"] for c in COMPANIES}

    out = []
    invalid = 0
    missing_old = 0
    for cid, key in parsed.items():
        ticker, filing_date, accession_number = key
        res = results[cid]
        if not valid(res):
            invalid += 1
            continue
        old = old_verdicts.get(key)
        if old is None:
            missing_old += 1
            print(f"  WARNING: no filing_ai_classifications row found for {key}, skipping")
            continue
        cik = cik_by_ticker.get(ticker)
        if cik is None:
            print(f"  WARNING: no CIK for {ticker}, skipping {key}")
            continue
        out.append({
            "ticker": ticker, "filing_date": filing_date, "accession_number": accession_number,
            "old_ai_verdict": old["ai_verdict"], "old_human_verdict": old["human_verdict"],
            "new_verdict": res["verdict"], "new_confidence": res["confidence"],
            "new_reasoning": res["reasoning"], "new_title": res.get("suggested_title"),
            "new_description": res.get("suggested_description"),
            "new_event_type": res.get("suggested_event_type"),
            "fixed_url": correct_url(cik, accession_number),
        })

    write_rows(out)
    dist = Counter(o["new_verdict"] for o in out)
    print(f"\nWrote {len(out)} rows to {TABLE}: {dict(dist)}")
    print(f"{invalid} invalid results not written, {missing_old} skipped (no matching filing_ai_classifications row).")


if __name__ == "__main__":
    main()
