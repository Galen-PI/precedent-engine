#!/usr/bin/env python3
"""
build_bucket_sheet.py -- READ-ONLY (database read; SEC exhibits through add_exhibit_excerpts, cached). Writes results/bucket_<k>_sheet.csv.
WHAT IT IS. The classifier's UNDECIDED real_event calls (human_verdict NULL, flagged for review) sorted into the nine text buckets of the cluster query (financing tied to a deal, deal or filing administration, governance documents, legal procedure, equity or benefit housekeeping,
charitable, CONTROL top leadership, CONTROL deal with a dollar figure, other), using the same first-match order as the SQL. It prints each bucket's count next to the SQL counts of 2026-10-22 (a built-in check that the Python logic matches), then samples N rows (seeded) from the bucket asked for,
with the classifier's reasoning and the exhibit text, in the columns the review importer reads (tier BUCK<k>; decision 'event' = the classifier's real_event call was RIGHT, 'not an event' = WRONG).
DECISION RULES (fixed before any reading): for the clean-candidate buckets 7 and 8 (n=30 each): if at least 28 of 30 are right, the bucket's remainder may be confirmed (after excluding rows the reading shows are sub-C-suite or administrative), followed by a 20-row post-check of the confirmed remainder (accept if at least 19 of 20 are right);
otherwise nothing is confirmed. Every other bucket stays UNDECIDED (no cost: undecided rows are outside the events table) unless a read of at least 20 rows shows at least 80% wrong, in which case a reject rule may be written.
Usage:   python3 -u scripts/card/build_bucket_sheet.py <bucket 1-9> [n, default 30]
"""
import os, sys, csv, random
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import unrecorded_candidates as uc
import add_exhibit_excerpts as ae

RESULTS = os.path.join(os.path.abspath(os.path.join(HERE, "..", "..")), "results")
SEED = 20261024
COL = "reviewer_decision (event / not an event / need more)"
SQL_COUNTS = {1: 351, 2: 1030, 3: 236, 4: 332, 5: 145, 6: 17, 7: 1183, 8: 695, 9: 3795}
NAMES = {1: "financing tied to a deal", 2: "deal or filing administration", 3: "governance documents", 4: "legal procedure", 5: "equity or benefit housekeeping", 6: "charitable or social", 7: "CONTROL top leadership", 8: "CONTROL deal with a dollar figure", 9: "other"}


def has(t, pats):
    return any(p in t for p in pats)


def bucket(title, desc, reasoning):
    t = ((title or " ") + " " + (desc or " ") + " " + (reasoning or " ")).lower()
    if has(t, ["bridge", "term loan", "credit facility", "credit agreement", "underwriting agreement", "senior notes", "warrant", "capped call"]) and has(t, ["acquisition", "merger", "pending"]):
        return 1
    if has(t, ["hart-scott", "waiting period", "proxy statement", "prospectus supplement", "special meeting", "stockholder approval", "regulatory approval", "form u-1", "extend"]):
        return 2
    if has(t, ["bylaw", "by-law", "certificate of incorporation", "proxy access", "rights agreement", "poison pill"]):
        return 3
    if has(t, ["ruling", "dismiss", "jurisdiction", "appeal", "deferred prosecution", "motion", "remand"]):
        return 4
    if has(t, ["benefit trust", "esop", "treasury shares", "hedge", "convertible"]):
        return 5
    if has(t, ["foundation", "charitable", "donation", "philanthrop"]):
        return 6
    if has(t, ["chief executive", "chief financial", " ceo ", " cfo ", "president", "chairman"]):
        return 7
    if has(t, ["definitive agreement", "completes", "completion of the", "completed the", "sale of", "acquired"]) and "$" in t:
        return 8
    return 9


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if k not in NAMES:
        sys.exit("Usage: build_bucket_sheet.py <bucket 1-9> [n]")
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    sb = ew.get_sb()
    cols = "accession_number,ticker,filing_date,item_codes,primary_document_url,ai_verdict,ai_confidence,ai_reasoning,ai_suggested_title,ai_suggested_description"
    rows = list(uc.paged(lambda: sb.table("filing_ai_classifications").select(cols).eq("ai_verdict", "real_event").eq("flagged_for_review", True).is_("human_verdict", "null").order("accession_number")))
    cnt = Counter()
    by = {i: [] for i in NAMES}
    for r in rows:
        b = bucket(r.get("ai_suggested_title"), r.get("ai_suggested_description"), r.get("ai_reasoning"))
        cnt[b] += 1
        by[b].append(r)
    print("undecided real_event rows %d | bucket counts (this script vs the SQL of 2026-10-22):" % len(rows))
    ok = True
    for i in sorted(NAMES):
        match = cnt[i] == SQL_COUNTS[i]
        ok &= match
        print("  %d %-36s %5d vs %5d  %s" % (i, NAMES[i], cnt[i], SQL_COUNTS[i], "MATCH" if match else "MISMATCH (the data moved since, or the logic differs)"))
    smp = random.Random(SEED + k).sample(by[k], min(n, len(by[k])))
    ua_ok = "@" in ae.UA and not any(w in ae.UA for w in ("example.com", "YOUR_REAL", "your"))
    out, nex = [], 0
    for r in smp:
        url = r.get("primary_document_url") or ""
        p = ae.parse_url(url)
        cached = p is not None and os.path.exists(os.path.join(ae.CACHE, p[1] + ".json"))
        if p is not None and not cached and not ua_ok:
            sys.exit("Set SEC_USER_AGENT to a real contact first.")
        res = ae.excerpt_for(url) if p is not None else {"type": "", "excerpt": "", "status": "no accession in URL"}
        ex = ("[%s] %s" % (res["type"], res["excerpt"][:1200])) if res.get("excerpt") else "(%s)" % res.get("status", "no exhibit")
        nex += int(bool(res.get("excerpt")))
        d = str(r["filing_date"])[:10]
        why = ((r.get("ai_suggested_title") or "") + " | " + (r["ai_reasoning"] or ""))[:300]
        out.append({"tier": "BUCK%d" % k, "date": d, "ticker": r["ticker"], "evidence": "bucket %d (%s) real_event call: items %s filed %s %s" % (k, NAMES[k], r["item_codes"], d, url),
                    "classifier_verdict": r["ai_verdict"], "classifier_confidence": r["ai_confidence"], "classifier_reasoning": why, "exhibit_excerpt": ex, COL: "", "notes": ""})
    path = os.path.join(RESULTS, "bucket_%d_sheet.csv" % k)
    os.makedirs(RESULTS, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print("bucket %d (%s): pool %d | sample %d (seed %d) | with an exhibit excerpt %d | wrote %s%s" % (k, NAMES[k], len(by[k]), len(out), SEED + k, nex, path, "" if ok else " | NOTE: counts differ from the SQL"))


if __name__ == "__main__":
    main()
