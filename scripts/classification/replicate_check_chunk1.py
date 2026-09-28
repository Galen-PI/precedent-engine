"""
replicate_check_chunk1.py

Read-only unless --write. Two batches classified the same first ~2,500 sweep
filings with the same corrected-URL text: TZ7E (results written to
stale_url_sweep_results) and HUhZ (duplicate run, results never written).
Compares them to measure how many chunk-1 flips replicate. --write backfills
description/title/type (old code didn't store them) from TZ7E into the sweep
table, real_event rows only. Never touches filing_ai_classifications.
"""
import csv, os, sys
from datetime import datetime
import requests
from classify_8k_filings_batch_v2 import supabase, fetch_batch_results

PRIMARY = "msgbatch_01TZ7E5AxxuXWwJWSpYMtNn4"
REPLICATE = "msgbatch_01HUhZvM81DpVbF9X2ZkdcFr"
HEAD = {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"}
BAD = ("BATCH REQUEST FAILED", "MALFORMED API RESPONSE")


def load(batch_id):
    b = requests.get(f"https://api.anthropic.com/v1/messages/batches/{batch_id}",
                     headers=HEAD, timeout=30).json()
    if b.get("processing_status") != "ended" or not b.get("results_url"):
        sys.exit(f"{batch_id} not ready: {b.get('processing_status')}")
    res, _usage = fetch_batch_results(b["results_url"])
    return res


def ok(r):
    return bool(r) and not (r.get("reasoning") or "").startswith(BAD)


a, b = load(PRIMARY), load(REPLICATE)
both = [c for c in a if c in b and ok(a[c]) and ok(b[c])]
agree = sum(a[c]["verdict"] == b[c]["verdict"] for c in both)
a_real = [c for c in both if a[c]["verdict"] == "real_event"]
b_real = [c for c in both if b[c]["verdict"] == "real_event"]
both_real = [c for c in a_real if b[c]["verdict"] == "real_event"]

print(f"Filings valid in both runs: {len(both)}")
print(f"Verdict agreement: {agree}/{len(both)} ({100 * agree / len(both):.1f}%)")
print(f"real_event flags: primary={len(a_real)}, replicate={len(b_real)}, both={len(both_real)}")
print(f"Primary flips that did NOT replicate: {len(a_real) - len(both_real)}")

rows = [{"custom_id": c, "primary": a[c]["verdict"], "primary_conf": a[c]["confidence"],
         "replicate": b[c]["verdict"], "replicate_conf": b[c]["confidence"],
         "title": a[c].get("suggested_title")} for c in a_real]
out = f"output/replicate_check_{datetime.now():%Y%m%d_%H%M}.csv"
if rows:
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Primary-flip detail written to {out}")

if "--write" in sys.argv:
    n = 0
    for c in a_real:
        t, d, acc = c.split("__")
        supabase.table("stale_url_sweep_results").update({
            "new_description": a[c].get("suggested_description"),
            "new_title": a[c].get("suggested_title"),
            "new_event_type": a[c].get("suggested_event_type"),
        }).eq("ticker", t).eq("filing_date", d).eq("accession_number", acc) \
          .eq("new_verdict", "real_event").execute()
        n += 1
    print(f"Backfilled description/title/type on {n} sweep rows.")
else:
    print("Read-only run. Re-run with --write to backfill descriptions.")
