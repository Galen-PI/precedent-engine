"""
backfill_sweep_descriptions.py

For stale_url_sweep_results rows marked review_status='confirmed', fill in missing
title / description / event type from Anthropic batch results (the original sweep
code did not store descriptions). Batches are tried in the order given; the first
batch with a valid real_event result carrying a title AND description wins, and
that result also sets the verdict fields. Read-only unless --write.
Never touches filing_ai_classifications.

Usage: python backfill_sweep_descriptions.py msgbatch_A msgbatch_B [--write]
"""
import os, sys
import requests
from classify_8k_filings_batch_v2 import supabase, fetch_batch_results

HEAD = {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"}
BAD = ("BATCH REQUEST FAILED", "MALFORMED API RESPONSE")


def load(bid):
    b = requests.get(f"https://api.anthropic.com/v1/messages/batches/{bid}",
                     headers=HEAD, timeout=30).json()
    if b.get("processing_status") != "ended" or not b.get("results_url"):
        sys.exit(f"{bid} not ready: {b.get('processing_status')}")
    res, _usage = fetch_batch_results(b["results_url"])
    return res


def usable(x):
    return (bool(x) and not (x.get("reasoning") or "").startswith(BAD)
            and x["verdict"] == "real_event"
            and x.get("suggested_title") and x.get("suggested_description"))


batch_ids = [a for a in sys.argv[1:] if a.startswith("msgbatch_")]
if not batch_ids:
    sys.exit("Give at least one msgbatch_ id.")
write = "--write" in sys.argv
results = [load(b) for b in batch_ids]

rows = supabase.table("stale_url_sweep_results").select(
    "ticker,filing_date,accession_number,new_verdict,new_title,new_description,new_event_type"
).eq("review_status", "confirmed").execute().data
print(f"{len(rows)} confirmed rows in the sweep table.")

filled, unresolved, already = [], [], 0
for r in rows:
    if r["new_verdict"] == "real_event" and r["new_title"] and r["new_description"] and r["new_event_type"]:
        already += 1
        continue
    cid = f"{r['ticker']}__{str(r['filing_date'])[:10]}__{r['accession_number']}"
    chosen = next((res[cid] for res in results if usable(res.get(cid))), None)
    if chosen is None:
        unresolved.append((r["ticker"], str(r["filing_date"])[:10]))
        continue
    filled.append(cid)
    if write:
        supabase.table("stale_url_sweep_results").update({
            "new_verdict": "real_event", "new_confidence": chosen["confidence"],
            "new_reasoning": chosen["reasoning"], "new_title": chosen["suggested_title"],
            "new_description": chosen["suggested_description"],
            "new_event_type": chosen.get("suggested_event_type"),
        }).eq("ticker", r["ticker"]).eq("filing_date", r["filing_date"]) \
          .eq("accession_number", r["accession_number"]).execute()

print(f"Already complete: {already}. {'Filled' if write else 'Would fill'}: {len(filled)}. "
      f"Unresolved (no usable title+description in any batch): {len(unresolved)}")
for t, d in unresolved:
    print(f"  unresolved: {t} {d}")
if not write:
    print("Read-only run. Re-run with --write to apply.")
