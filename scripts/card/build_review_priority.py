#!/usr/bin/env python3
"""
build_review_priority.py -- ranks results/human_review_queue_with_excerpts.csv for a human reviewer and writes results/human_review_priority.csv (nothing is written to the database).
  P1  the classifier said noise or uncertain, but the press-release exhibit matches an event type (keyword_hint non-empty): the likeliest misclassifications.
  P2  the classifier said noise or uncertain and there IS an exhibit, but no keyword matched: read the excerpt.
  P3  the classifier said real_event (it agrees with the market reaction): usually a genuine event still waiting to be created or linked.
  P4  no exhibit excerpt (nothing in the filing text, or the fetch failed): judge from the filing page and the move.
Within a priority rows are ordered by volume ratio x band units. keyword_hint is a crude keyword match, NOT a verdict.
Usage:   python3 -u scripts/card/build_review_priority.py
"""
import os, csv
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.abspath(os.path.join(HERE, "..", "..")), "results")


def main():
    rows = list(csv.DictReader(open(os.path.join(RESULTS, "human_review_queue_with_excerpts.csv"))))
    def pr(r):
        v = r["classifier_verdict"].lower()
        has_ex = bool(r["exhibit_excerpt"]) and not r["exhibit_excerpt"].startswith("(")
        if "real_event" in v and "likely_noise" not in v and "uncertain" not in v:
            return "P3 classifier says event (agrees)"
        if not has_ex:
            return "P4 no exhibit excerpt"
        return "P1 noise/uncertain but the exhibit matches an event type" if r["keyword_hint"] else "P2 noise/uncertain, exhibit present, no keyword: read it"
    def score(r):
        try:
            return -float(r["volume_ratio"] or 0) * float(r["band_units"] or 0)
        except ValueError:
            return 0.0
    out = sorted(((pr(r), score(r), r) for r in rows), key=lambda x: (x[0], x[1]))
    counts = Counter(p for p, _, _ in out)
    path = os.path.join(RESULTS, "human_review_priority.csv")
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["priority"] + list(rows[0].keys()))
        w.writeheader()
        for p, _, r in out:
            w.writerow(dict(r, priority=p))
    print("rows %d -> %s" % (len(rows), path))
    for k in sorted(counts):
        print("  %-62s %4d" % (k, counts[k]))
    hints = Counter(h.strip() for p, _, r in out if p.startswith("P1") for h in r["keyword_hint"].split(";") if h.strip())
    print("P1 by keyword hint: " + ", ".join("%s %d" % kv for kv in hints.most_common()))
    print("first P1 rows:")
    for p, _, r in [x for x in out if x[0].startswith("P1")][:8]:
        print("  %s %-6s %6s%% | %s | %s | %s" % (r["date"], r["ticker"], r["return_pct"], r["classifier_verdict"][:12], r["keyword_hint"][:28], r["exhibit_excerpt"][:90]))


if __name__ == "__main__":
    main()
