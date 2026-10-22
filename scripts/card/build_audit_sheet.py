#!/usr/bin/env python3
"""
build_audit_sheet.py -- READ-ONLY (the database is read; SEC exhibits through add_exhibit_excerpts, cached). Writes results/random_audit_sheet.csv.
WHAT IT IS. The classifier already flags a random sample of its own NOISE calls for review (flag_reason = random_audit_sample, human_verdict still NULL). Those rows are an UNBIASED sample of what the classifier calls noise, so reading a seeded random subset of them measures its MISS RATE directly, with an interval, which no reaction-ranked
queue can do. Each sheet row shows the classifier's verdict and reasoning and the first 1,200 characters of the filing's press-release exhibit, in the same columns the review importer reads (tier AUDIT; decision 'event' = the classifier MISSED a real event; 'not an event' = the noise call was right).
READING RULE (fixed before reading): judge each filing by your materiality rubric on its CONTENT (the stock's move is not shown on purpose). Do not skip rows, do not change the sample, and read in the order given; 'need more' is allowed but is reported as its own count.
PREDICTION (before any reading): miss rate (event decisions / all decided) 2-5% (central about 3%): 4-10 events in 200, mostly guidance or press-release-stub deals; an earlier 100-row audit found 0 clear and 2 lean-real (interval 0.2-7%). With n=200 and a true 3% rate the 95% interval is about +-2.4 points.
PRECISION MODE (--airreal, default n=100, seed +1, tier PREC, results/ai_real_precision_sheet.csv): the same reading rule applied to the classifier's REAL_EVENT calls at confidence 0.80-0.92 that no human has decided; decision 'event' = the classifier was RIGHT, 'not an event' = it was wrong.
PREDICTION for precision mode (before any reading): precision 60-80% (central 70%; the 0.92+ band read about 82% before exclusions), +-9 points at n=100.
Usage:   python3 -u scripts/card/build_audit_sheet.py [n, default 200] [--airreal]       (needs SEC_USER_AGENT with a real contact for exhibits not yet cached)
After reading:  python3 -u scripts/card/import_review_decisions.py --reviewer "Galen" results/random_audit_sheet.csv --write
Then:           SELECT decision, COUNT(*) FROM review_queue_decisions WHERE tier = $$AUDIT$$ GROUP BY 1;
"""
import os, sys, csv, random
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import unrecorded_candidates as uc
import add_exhibit_excerpts as ae

RESULTS = os.path.join(os.path.abspath(os.path.join(HERE, "..", "..")), "results")
SEED = 20261022
COL = "reviewer_decision (event / not an event / need more)"


def main():
    airreal = "--airreal" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n = int(args[0]) if args else (100 if airreal else 200)
    sb = ew.get_sb()
    cols = "accession_number,ticker,filing_date,item_codes,primary_document_url,ai_verdict,ai_confidence,ai_reasoning"
    if airreal:      # PRECISION CHECK: the classifier's REAL_EVENT calls at confidence 0.80-0.92 with no human decision; 'event' = the classifier was RIGHT
        rows = list(uc.paged(lambda: sb.table("filing_ai_classifications").select(cols).eq("flag_reason", "novel_real_event_no_template_match").eq("ai_verdict", "real_event")
                             .is_("human_verdict", "null").gte("ai_confidence", 0.80).lt("ai_confidence", 0.92).order("accession_number")))
    else:
        rows = list(uc.paged(lambda: sb.table("filing_ai_classifications").select(cols).eq("flag_reason", "random_audit_sample").eq("ai_verdict", "likely_noise").is_("human_verdict", "null").order("accession_number")))
    smp = random.Random(SEED + (1 if airreal else 0)).sample(rows, min(n, len(rows)))
    ua_ok = "@" in ae.UA and not any(w in ae.UA for w in ("example.com", "YOUR_REAL", "your"))
    out, nex = [], 0
    for r in smp:
        url = r.get("primary_document_url") or ""
        p = ae.parse_url(url)
        cached = p is not None and os.path.exists(os.path.join(ae.CACHE, p[1] + ".json"))
        if p is not None and not cached and not ua_ok:
            sys.exit("Set SEC_USER_AGENT to a real contact first, e.g.  export SEC_USER_AGENT=\"stock-research1 you@yourdomain.com\"")
        res = ae.excerpt_for(url) if p is not None else {"type": "", "excerpt": "", "status": "no accession in URL"}
        ex = ("[%s] %s" % (res["type"], res["excerpt"][:1200])) if res.get("excerpt") else "(%s)" % res.get("status", "no exhibit")
        nex += int(bool(res.get("excerpt")))
        d = str(r["filing_date"])[:10]
        out.append({"tier": "PREC" if airreal else "AUDIT", "date": d, "ticker": r["ticker"], "evidence": ("precision check of a real_event call (0.80-0.92): items %s filed %s %s" if airreal else "random audit of a noise call: items %s filed %s %s") % (r["item_codes"], d, url),
                    "classifier_verdict": r["ai_verdict"], "classifier_confidence": r["ai_confidence"], "classifier_reasoning": (r["ai_reasoning"] or "")[:300], "exhibit_excerpt": ex, COL: "", "notes": ""})
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, "ai_real_precision_sheet.csv" if airreal else "random_audit_sheet.csv")
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    yrs = Counter(o["date"][:4] for o in out)
    print(("pool of unreviewed real_event calls at 0.80-0.92: %d" if airreal else "pool of unreviewed random-audit noise calls: %d") % len(rows) + " | sample %d (seed %d) | with an exhibit excerpt %d | wrote %s" % (len(out), SEED + (1 if airreal else 0), nex, path))
    print("by year: " + ", ".join("%s %d" % kv for kv in sorted(yrs.items())))


if __name__ == "__main__":
    main()
