"""
spot_check_stale_url_effect.py

Spot-check for the stale primary_document_url problem (see the
HIGH PRIORITY GitHub issue): how often does a verdict actually change
once the classifier can see the complete filing (cover page + exhibits)?

Each sampled filing is classified TWICE with today's prompt:
  ctl = the stale URL's text exactly as originally used (CONTROL --
        measures plain re-classification noise: temperature, prompt
        version drift, updated recent-events context)
  fix = the corrected complete-submission .txt URL
The real effect of the URL bug is the fix arm's flip rate over the
control arm's, tested with paired (McNemar-style) counts.

READ-ONLY: writes nothing to the database. Results go to a CSV so old
verdicts stay intact and every flipped row can be read individually.

Usage:
    python spot_check_stale_url_effect.py [--per-cohort 150] [--seed N] [--yes]
"""

import argparse
import csv
import math
import os
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime

from classify_8k_filings_batch_v2 import (
    supabase, fetch_all_filing_texts_concurrently, get_recent_event_titles,
    build_batch_request, chunk_list, submit_batch, poll_batches_until_all_done,
    fetch_batch_results, MAX_BATCH_SIZE, REAL_OBSERVED_COST_PER_FILING,
)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ingestion"))
from import_8k_filings import COMPANIES

FAILED_MARKERS = ("BATCH REQUEST FAILED", "MALFORMED API RESPONSE")

COHORTS = {
    "human_reviewed": [
        lambda q: q.not_.like("primary_document_url", "%.txt"),
        lambda q: q.not_.is_("human_verdict", "null"),
    ],
    "ai_only": [
        lambda q: q.not_.like("primary_document_url", "%.txt"),
        lambda q: q.is_("human_verdict", "null"),
        lambda q: q.eq("flagged_for_review", False),
    ],
}


def paginated_keys(filters):
    rows, offset = [], 0
    while True:
        q = supabase.table("filing_ai_classifications") \
            .select("ticker,filing_date,accession_number")
        for f in filters:
            q = f(q)
        page = q.order("ticker").order("filing_date").order("accession_number") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    return rows


def fetch_full_rows(keys):
    out = {}
    accs = list({k[2] for k in keys})
    for i in range(0, len(accs), 100):
        page = supabase.table("filing_ai_classifications").select(
            "ticker,filing_date,accession_number,item_codes,primary_document_url,"
            "ai_verdict,ai_confidence,ai_reasoning,human_verdict,prompt_version"
        ).in_("accession_number", accs[i:i + 100]).execute().data
        for r in page:
            out[(r["ticker"], r["filing_date"], r["accession_number"])] = r
    return out


def correct_url(cik, accession):
    return (f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
            f"{accession.replace('-', '')}/{accession}.txt")


def valid(res):
    if not res:
        return False
    reasoning = res.get("reasoning") or ""
    return not any(reasoning.startswith(m) for m in FAILED_MARKERS)


def normalize_human(hv):
    if hv is None:
        return None
    if hv == "real_event":
        return "real_event"
    if "noise" in hv or "reject" in hv:
        return "likely_noise"
    return hv


def pct_ci(k, n):
    p = k / n
    half = 1.96 * math.sqrt(p * (1 - p) / n)
    return f"{100 * p:.1f}% (95% CI {100 * max(0, p - half):.1f}-{100 * min(1, p + half):.1f}%)"


def summarize(label, recs):
    n = len(recs)
    print(f"\n=== {label} (n={n}) ===")
    if n == 0:
        return
    flip_ctl = sum(r["ctl_flip"] for r in recs)
    flip_fix = sum(r["fix_flip"] for r in recs)
    b = sum(1 for r in recs if r["fix_flip"] and not r["ctl_flip"])
    c = sum(1 for r in recs if r["ctl_flip"] and not r["fix_flip"])
    print(f"  CONTROL flip rate vs old AI verdict (noise floor): {pct_ci(flip_ctl, n)}")
    print(f"  FIX     flip rate vs old AI verdict:               {pct_ci(flip_fix, n)}")
    print(f"  Paired: fix-only flips b={b}, control-only flips c={c}", end="")
    if b + c > 0:
        print(f", McNemar z = {(b - c) / math.sqrt(b + c):+.2f} (|z|>=2 is conventionally notable)")
    else:
        print(" (no discordant pairs)")
    for arm in ("ctl", "fix"):
        ct = Counter((r["old_ai"], r[f"{arm}_verdict"]) for r in recs)
        print(f"  old -> {arm} verdict crosstab: " +
              ", ".join(f"{o}->{nw}: {v}" for (o, nw), v in sorted(ct.items())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-cohort", type=int, default=150)
    ap.add_argument("--seed", type=int, default=20260928)
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--item-code", default=None)
    ap.add_argument("--old-verdict", default=None)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    print("Sampling stale-URL rows with an existing verdict...")
    extra = []
    if args.item_code:
        extra.append(lambda q: q.like("item_codes", f"%{args.item_code}%"))
    if args.old_verdict:
        extra.append(lambda q: q.eq("ai_verdict", args.old_verdict))
    sampled = []
    for cohort, filters in COHORTS.items():
        uniq = sorted({(k["ticker"], k["filing_date"], k["accession_number"])
                       for k in paginated_keys(filters + extra)})
        print(f"  {cohort}: {len(uniq)} rows in pool")
        for k in rng.sample(uniq, min(args.per_cohort, len(uniq))):
            sampled.append((cohort, k))

    full = fetch_full_rows([k for _, k in sampled])
    cik_by_ticker = {c["ticker"]: c["cik"] for c in COMPANIES}

    control_cands, fixed_cands, meta, skipped_no_cik = [], [], {}, 0
    for cohort, key in sampled:
        row = full.get(key)
        cik = cik_by_ticker.get(key[0])
        if row is None or cik is None or row["ai_verdict"] is None:
            skipped_no_cik += 1
            continue
        base = {"ticker": key[0], "filing_date": key[1],
                "accession_number": key[2], "item_codes": row["item_codes"]}
        fixed_url = correct_url(cik, key[2])
        control_cands.append({**base, "primary_document_url": row["primary_document_url"]})
        fixed_cands.append({**base, "primary_document_url": fixed_url})
        meta[f"{key[0]}__{key[1]}__{key[2]}"] = {"cohort": cohort, "row": row, "fixed_url": fixed_url}
    print(f"Sample ready: {len(control_cands)} filings ({skipped_no_cik} skipped: no CIK / no old AI verdict).")

    n_req = 2 * len(control_cands)
    print(f"\nEstimate: {n_req} requests, ~${n_req * REAL_OBSERVED_COST_PER_FILING:,.2f}.")
    if not args.yes and input("Proceed? [y/N]: ").strip().lower() != "y":
        print("Aborted, nothing sent.")
        return

    print("\nFetching CONTROL text (stale URLs)...")
    ctl_fetched, _ = fetch_all_filing_texts_concurrently(control_cands)
    print("\nFetching FIX text (corrected .txt URLs)...")
    fix_fetched, _ = fetch_all_filing_texts_concurrently(fixed_cands)
    paired = sorted(set(ctl_fetched) & set(fix_fetched))
    print(f"\n{len(paired)} filings fetched successfully in BOTH arms "
          f"(fetch failures on either arm are excluded, not counted as flips).")

    recent, reqs = {}, []
    for base_id in paired:
        c, ctl_text = ctl_fetched[base_id]
        _, fix_text = fix_fetched[base_id]
        if c["ticker"] not in recent:
            recent[c["ticker"]] = get_recent_event_titles(c["ticker"])
        for suffix, text in (("ctl", ctl_text), ("fix", fix_text)):
            reqs.append(build_batch_request(f"{base_id}__{suffix}", c["ticker"],
                                            c["filing_date"], c["item_codes"], text,
                                            recent[c["ticker"]]))

    batch_ids = [submit_batch(chunk) for chunk in chunk_list(reqs, MAX_BATCH_SIZE)]
    final_batches = poll_batches_until_all_done(batch_ids)
    results = {}
    for bid, batch in final_batches.items():
        url = batch.get("results_url")
        if not url:
            print(f"  WARNING: batch {bid} has no results_url")
            continue
        res, _usage = fetch_batch_results(url)
        results.update(res)

    recs, invalid = [], 0
    for base_id in paired:
        ctl, fix = results.get(f"{base_id}__ctl"), results.get(f"{base_id}__fix")
        if not (valid(ctl) and valid(fix)):
            invalid += 1
            continue
        m = meta[base_id]
        row = m["row"]
        old = row["ai_verdict"]
        recs.append({
            "cohort": m["cohort"], "ticker": row["ticker"], "filing_date": row["filing_date"],
            "accession_number": row["accession_number"], "filing_year": str(row["filing_date"])[:4],
            "item_codes": row["item_codes"], "old_ai": old, "old_ai_confidence": row["ai_confidence"],
            "old_human": row["human_verdict"], "old_prompt_version": row["prompt_version"],
            "ctl_verdict": ctl["verdict"], "ctl_confidence": ctl["confidence"],
            "fix_verdict": fix["verdict"], "fix_confidence": fix["confidence"],
            "ctl_flip": int(ctl["verdict"] != old), "fix_flip": int(fix["verdict"] != old),
            "old_reasoning": row["ai_reasoning"], "ctl_reasoning": ctl["reasoning"],
            "fix_reasoning": fix["reasoning"], "stale_url": row["primary_document_url"],
            "fixed_url": m["fixed_url"],
        })
    print(f"\n{len(recs)} filings with valid results in both arms ({invalid} dropped: failed/malformed).")

    summarize("ALL", recs)
    for cohort in COHORTS:
        summarize(cohort, [r for r in recs if r["cohort"] == cohort])

    human = [r for r in recs if r["cohort"] == "human_reviewed"]
    if human:
        print("\nRaw old human_verdict values in sample:",
              dict(Counter(r["old_human"] for r in human)))
        hn = [(normalize_human(r["old_human"]), r) for r in human]
        print(f"  New AI verdict agrees with old human verdict -- control: "
              f"{sum(r['ctl_verdict'] == h for h, r in hn)}/{len(hn)}, "
              f"fix: {sum(r['fix_verdict'] == h for h, r in hn)}/{len(hn)}")

    by_decade = defaultdict(lambda: [0, 0])
    for r in recs:
        d = r["filing_year"][:3] + "0s"
        by_decade[d][0] += 1
        by_decade[d][1] += r["fix_flip"]
    print("\nFix-arm flip rate by filing decade:")
    for d in sorted(by_decade):
        n, k = by_decade[d]
        print(f"  {d}: {k}/{n} ({100 * k / n:.0f}%)")

    if recs:
        out = f"spot_check_results_{datetime.now():%Y%m%d_%H%M}.csv"
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(recs[0].keys()))
            w.writeheader()
            w.writerows(recs)
        print(f"\nFull row-level results (old + control + fix reasoning) written to {out}")
        print("Next step: read the rows where fix_flip=1 and ctl_flip=0 individually.")


if __name__ == "__main__":
    main()
