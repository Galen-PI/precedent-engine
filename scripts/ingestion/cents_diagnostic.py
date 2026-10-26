#!/usr/bin/env python3
"""
cents_diagnostic.py -- EXPLORATORY and READ-ONLY: it reads data_cache/round_tests_cache.jsonl (written by round_number_tests.py) and touches neither the database nor the vendor. It is NOT a registered test and cannot produce a pass; it only DESCRIBES why the clustering calibration failed and what drives the extreme whole-dollar ratios.
PRINTS: (A) the cents distribution of closes of $10 and above per era as a 10 x 10 grid (rows = tens digit, columns = units digit): each cell is the share of that cents value divided by the mean share of the 80 plain (non-multiple-of-5) values; (B) the same by units digit and by tens digit; (C) the spread across TICKERS of the whole-dollar ratio (closes of $10 to $100, tickers with at least 400 baseline closes); (D) the tickers behind the largest whole-dollar excess in chosen price buckets.
Usage:   python3 scripts/ingestion/cents_diagnostic.py
"""
import os, sys, json
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data_cache", "round_tests_cache.jsonl")
BASE = [c for c in range(100) if c % 5]


def load(path=None):
    recs = []
    for line in open(path or CACHE):
        try:
            recs.append(json.loads(line))
        except ValueError:
            pass
    return recs


def pctile(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, int(round(q * (len(xs) - 1)))))]


def main(path=None, out=print):
    recs = load(path)
    out("tickers in the cache: %d" % len(recs))
    for e, label in (("A", "ERA A (2001-06 to 2013)"), ("B", "ERA B (2014 to 2026)")):
        tot = [sum(r["cents"][e][c] for r in recs) for c in range(100)]
        m = sum(tot[c] for c in BASE) / 80.0
        out("\n(A) %s: closes of $10 and above %d. Cents grid: share / mean plain share (rows = tens digit, columns = units digit)" % (label, sum(tot)))
        out("        " + "".join("   u=%d" % u for u in range(10)))
        for t in range(10):
            out("   t=%d  " % t + "".join("%6.2f" % (tot[t * 10 + u] / m) for u in range(10)))
        out("(B) by units digit (mean over tens digits): " + "  ".join("%d:%.2f" % (u, sum(tot[t * 10 + u] for t in range(10)) / 10.0 / m) for u in range(10)))
        out("    by tens digit  (mean over units digits): " + "  ".join("%d:%.2f" % (t, sum(tot[t * 10 + u] for u in range(10)) / 10.0 / m) for t in range(10)))
    out("\n(C) SPREAD ACROSS TICKERS of the whole-dollar ratio, closes of $10 to $100 (tickers with at least 400 baseline closes)")
    for e in ("A", "B"):
        rs = []
        for r in recs:
            c0 = base = 0
            for b in ("$10-20", "$20-50", "$50-100"):
                cell = r["bk"].get(e + "|" + b)
                if cell:
                    c0 += cell[0]; base += cell[4]
            if base >= 400:
                rs.append((c0 * 80.0 / base, r["ticker"]))
        if rs:
            xs = [x for x, _ in rs]
            out("   era %s: %d tickers | percentiles 10/25/50/75/90: %s | tickers above 1.5: %d | above 3: %d | top 5: %s" % (e, len(rs), "  ".join("%.2f" % pctile(xs, q) for q in (0.1, 0.25, 0.5, 0.75, 0.9)), sum(1 for x in xs if x > 1.5), sum(1 for x in xs if x > 3), ", ".join("%s %.1f" % (t, x) for x, t in sorted(rs, reverse=True)[:5])))
    out("\n(D) TICKERS BEHIND THE LARGEST WHOLE-DOLLAR EXCESS (excess = whole-dollar closes minus the plain-cent mean, per price bucket)")
    for e, b in (("A", "$250-up"), ("A", "$100-250"), ("B", "$250-up")):
        rows = []
        for r in recs:
            cell = r["bk"].get(e + "|" + b)
            if cell and cell[4] > 0:
                rows.append((cell[0] - cell[4] / 80.0, r["ticker"], cell[0], cell[4]))
        rows.sort(reverse=True)
        tot_ex = sum(x[0] for x in rows if x[0] > 0)
        out("   era %s %s: %d tickers; top 6 by excess: %s" % (e, b, len(rows), "; ".join("%s c0 %d of %d baseline (%.0f%% of the bucket's excess)" % (t, c0, bs, 100.0 * ex / tot_ex if tot_ex else 0) for ex, t, c0, bs in rows[:6])))
    return recs


if __name__ == "__main__":
    main()
