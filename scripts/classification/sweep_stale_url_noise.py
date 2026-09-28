"""
sweep_stale_url_noise.py

Fix-arm-only sweep for the stale primary_document_url problem: re-classify
old likely_noise verdicts (default stratum: Item 2.02 earnings releases)
using the corrected complete-submission .txt URL, and write results to
stale_url_sweep_results for human review. NEVER touches
filing_ai_classifications -- old AI and human verdicts stay intact.

Spot checks (2026-09-28) found ~1% of old-noise stale-URL verdicts hide
deal news that only appears in the press-release exhibit (e.g. GoDaddy/
Neustar, Merck/Organon, eBay/StubHub, Oracle's first dividend).

Resumable: rows already in the results table are skipped on rerun.
Fetch failures are recorded as new_verdict='fetch_failed' so persistent
404s aren't retried forever. Malformed/failed API results are NOT
written, so a rerun retries them.

Usage:
    python sweep_stale_url_noise.py [--item-code 2.02] [--limit N] [--yes]
"""

import argparse
import os
import sys
from collections import Counter

from classify_8k_filings_batch_v2 import (
    supabase, fetch_all_filing_texts_concurrently, get_recent_event_titles,
    build_batch_request, chunk_list, submit_batch, poll_batches_until_all_done,
    fetch_batch_results, MAX_BATCH_SIZE, CHUNK_SIZE, REAL_OBSERVED_COST_PER_FILING,
)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ingestion"))
from import_8k_filings import COMPANIES

TABLE = "stale_url_sweep_results"
FAILED_MARKERS = ("BATCH REQUEST FAILED", "MALFORMED API RESPONSE")


def fetch_pool(item_code):
    rows, offset = [], 0
    while True:
        page = (supabase.table("filing_ai_classifications")
                .select("ticker,filing_date,accession_number,item_codes,"
                        "primary_document_url,ai_verdict,human_verdict,flagged_for_review")
                .not_.like("primary_document_url", "%.txt")
                .eq("ai_verdict", "likely_noise")
                .like("item_codes", f"%{item_code}%")
                .order("ticker").order("filing_date").order("accession_number")
                .range(offset, offset + 999).execute().data)
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    keep = []
    for r in rows:
        hv = r["human_verdict"]
        if hv is None and r["flagged_for_review"] is False:
            keep.append(r)          # auto-cleared, never human-reviewed
        elif hv is not None and hv != "real_event":
            keep.append(r)          # human agreed it was noise
    return keep


def fetch_done_keys():
    done, offset = set(), 0
    while True:
        try:
            page = (supabase.table(TABLE).select("ticker,filing_date,accession_number")
                    .order("ticker").order("filing_date").order("accession_number")
                    .range(offset, offset + 999).execute().data)
        except Exception as e:
            print(f"Could not read {TABLE} -- did you create the table? ({e})")
            sys.exit(1)
        if not page:
            break
        done.update((r["ticker"], str(r["filing_date"])[:10], r["accession_number"]) for r in page)
        if len(page) < 1000:
            break
        offset += 1000
    return done


def correct_url(cik, accession):
    return (f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
            f"{accession.replace('-', '')}/{accession}.txt")


def valid(res):
    if not res:
        return False
    reasoning = res.get("reasoning") or ""
    return not any(reasoning.startswith(m) for m in FAILED_MARKERS)


def write_rows(rows):
    for i in range(0, len(rows), 500):
        supabase.table(TABLE).upsert(
            rows[i:i + 500], on_conflict="ticker,filing_date,accession_number").execute()


def process_chunk(chunk, recent_cache):
    cands = [{"ticker": r["ticker"], "filing_date": r["filing_date"],
              "accession_number": r["accession_number"], "item_codes": r["item_codes"],
              "primary_document_url": r["fixed_url"]} for r in chunk]
    old_by_id = {f"{r['ticker']}__{r['filing_date']}__{r['accession_number']}": r for r in chunk}

    fetched, _errors = fetch_all_filing_texts_concurrently(cands)
    out = []
    for cid, r in old_by_id.items():
        if cid not in fetched:
            out.append({"ticker": r["ticker"], "filing_date": r["filing_date"],
                        "accession_number": r["accession_number"],
                        "old_ai_verdict": r["ai_verdict"], "old_human_verdict": r["human_verdict"],
                        "new_verdict": "fetch_failed", "fixed_url": r["fixed_url"]})

    reqs = []
    for cid, (c, text) in fetched.items():
        if c["ticker"] not in recent_cache:
            recent_cache[c["ticker"]] = get_recent_event_titles(c["ticker"])
        reqs.append(build_batch_request(cid, c["ticker"], c["filing_date"],
                                        c["item_codes"], text, recent_cache[c["ticker"]]))

    results = {}
    if reqs:
        batch_ids = [submit_batch(ch) for ch in chunk_list(reqs, MAX_BATCH_SIZE)]
        for bid, batch in poll_batches_until_all_done(batch_ids).items():
            url = batch.get("results_url")
            if not url:
                print(f"  WARNING: batch {bid} has no results_url")
                continue
            res, _usage = fetch_batch_results(url)
            results.update(res)

    invalid = 0
    for cid, res in results.items():
        if not valid(res):
            invalid += 1
            continue
        r = old_by_id[cid]
        out.append({"ticker": r["ticker"], "filing_date": r["filing_date"],
                    "accession_number": r["accession_number"],
                    "old_ai_verdict": r["ai_verdict"], "old_human_verdict": r["human_verdict"],
                    "new_verdict": res["verdict"], "new_confidence": res["confidence"],
                    "new_reasoning": res["reasoning"], "new_title": res.get("suggested_title"),
                    "new_event_type": res.get("suggested_event_type"),
                    "fixed_url": r["fixed_url"]})
    write_rows(out)
    dist = Counter(o["new_verdict"] for o in out)
    print(f"  Chunk written: {len(out)} rows {dict(dist)}; {invalid} invalid results not written (rerun retries them).")
    return len(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--item-code", default="2.02")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    print(f"Building pool: stale-URL old-noise rows containing item {args.item_code}...")
    pool = fetch_pool(args.item_code)
    print(f"  {len(pool)} rows in scope.")
    done = fetch_done_keys()
    cik_by_ticker = {c["ticker"]: c["cik"] for c in COMPANIES}

    todo, no_cik = [], 0
    for r in pool:
        if (r["ticker"], str(r["filing_date"])[:10], r["accession_number"]) in done:
            continue
        cik = cik_by_ticker.get(r["ticker"])
        if cik is None:
            no_cik += 1
            continue
        todo.append({**r, "fixed_url": correct_url(cik, r["accession_number"])})
    print(f"  {len(done)} already swept, {no_cik} skipped (no CIK), {len(todo)} to do.")
    if args.limit:
        todo = todo[:args.limit]
    if not todo:
        print("Nothing to do.")
        return

    print(f"\nEstimate: {len(todo)} requests, ~${len(todo) * REAL_OBSERVED_COST_PER_FILING:,.2f}.")
    if not args.yes and input("Proceed? [y/N]: ").strip().lower() != "y":
        print("Aborted, nothing sent.")
        return

    recent_cache, total = {}, 0
    n_chunks = (len(todo) + CHUNK_SIZE - 1) // CHUNK_SIZE
    for i in range(0, len(todo), CHUNK_SIZE):
        print(f"\n{'=' * 60}\nCHUNK {i // CHUNK_SIZE + 1}/{n_chunks}\n{'=' * 60}")
        total += process_chunk(todo[i:i + CHUNK_SIZE], recent_cache)

    print(f"\nDone: {total} rows written to {TABLE}.")
    print("Review flips with: SELECT ... FROM stale_url_sweep_results WHERE new_verdict = 'real_event'")


if __name__ == "__main__":
    main()
