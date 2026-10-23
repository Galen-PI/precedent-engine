#!/usr/bin/env python3
"""
fomc_day_sector_test.py -- READ-ONLY (database: fomc_meetings, macro_long and sector_day_z). Writes nothing.
Registered rule, grouping, window, predictions and limits: results/PREREG_fomc_sector_test_2026-10-23.md (committed before the first real run).
QUESTION. Around scheduled FOMC announcements, do the rate-sensitive sectors (Financials, Real Estate, Utilities) move more than the other eight, on the same meeting dates? Reuses fomc_day_test.py's announcements and exclusion set, and fed_change_day_test's sector series (log_ratio) and baseline (ld).
Usage:   python3 -u scripts/card/fomc_day_sector_test.py
"""
import os, sys, bisect, math, time, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fed_change_day_test as fct
import fomc_day_test as fd

RATE = ("Financials", "Real Estate", "Utilities")
ERAS = fd.ERAS
SHIFTS = fd.SHIFTS


def ld_w(lr, i, X):
    a, b = fct.ld(lr, i, 0, X), fct.ld(lr, i, 1, X)
    return None if a is None or b is None else (a + b) / 2.0


def paired(vals):
    a = np.array([v for v in vals if v is not None and np.isfinite(v)], dtype=float)
    n = len(a)
    if n < 3:
        return None
    m, se = float(a.mean()), float(a.std(ddof=1) / math.sqrt(n))
    return {"n": n, "ratio": math.exp(m), "lo": math.exp(m - 1.96 * se), "hi": math.exp(m + 1.96 * se), "t": (m / se) if se > 0 else float("nan")}


def pfmt(r):
    return "n/a" if r is None else "n %3d  ratio %.3f [%.3f, %.3f]  t %+.2f" % (r["n"], r["ratio"], r["lo"], r["hi"], r["t"])


def verdict_of(res, plc):
    A, B = res["2004-2014"], res["2015-2026"]
    if A is None or B is None:
        return "CANNOT TEST (too few meetings)"
    clean = all(plc[lab] is not None and abs(plc[lab]["t"]) < 2.5 for lab, _, _ in ERAS)
    if A["ratio"] >= 1.05 and B["ratio"] >= 1.05 and A["t"] >= 2.5 and B["t"] >= 2.5 and clean:
        return "PASS: the rate-sensitive sectors move more than the rest around scheduled FOMC announcements"
    if A["ratio"] > 1.03 and B["ratio"] > 1.03 and A["t"] >= 2.0 and B["t"] >= 2.0:
        return "LEAD (ratio above 1.03 with t >= 2.0 in both eras, below the pass line)"
    if A["ratio"] <= 0.95 and B["ratio"] <= 0.95 and A["t"] <= -2.5 and B["t"] <= -2.5:
        return "REVERSE: the rate-sensitive sectors move LESS than the rest"
    return "NULL: no documented difference between the rate-sensitive sectors and the rest"


def main(sb=None):
    t0 = time.time()
    sb = sb or fct.ew.get_sb()
    days, MZ, NN = fct.load_sector_day(sb)
    D = len(days)
    allann = [a for a in fd.load_announcements(sb) if a["date"] >= datetime.date(2004, 1, 1)]
    for a in allann:
        a["i"] = bisect.bisect_left(days, a["date"].isoformat())
    allann = [a for a in allann if a["i"] < D]
    X = set()
    for a in allann:
        X.update((a["i"], a["i"] + 1))
    sched = sorted({a["i"] for a in allann if not a["unsched"]})
    LR = {s: fct.log_ratio(MZ, NN, k) for k, s in enumerate(fct.SECTORS)}
    yr = lambda i: int(days[i][:4])
    print("sector-days %d | scheduled meetings from 2004 %d | exclusion days %d | %.0fs" % (D, len(sched), len(X), time.time() - t0), flush=True)
    rest = [s for s in fct.SECTORS if s not in RATE]

    def delta(i):
        r = [ld_w(LR[s], i, X) for s in RATE]
        o = [ld_w(LR[s], i, X) for s in rest]
        if any(v is None for v in r) or any(v is None for v in o):
            return None
        return float(np.mean(r) - np.mean(o))

    def shifted(i, sh):
        j = i + sh
        if not (0 <= j < D) or ({j - 1, j, j + 1, j + 2} & X):
            return None
        return delta(j)
    res, plc = {}, {}
    print("\nPRIMARY: paired difference RATE (Financials, Real Estate, Utilities) minus REST (other eight), day 0 and day +1 averaged, scheduled meetings")
    for lab, lo, hi in ERAS:
        idxs = [i for i in sched if lo <= yr(i) <= hi]
        res[lab] = paired([delta(i) for i in idxs])
        plc[lab] = paired([shifted(i, sh) for i in idxs for sh in SHIFTS])
        print("  %-10s %s" % (lab, pfmt(res[lab])))
    print("PLACEBO of the same difference (meetings shifted +21 and -21 trading days; skipped near an announcement)")
    for lab, _, _ in ERAS:
        print("  %-10s %s" % (lab, pfmt(plc[lab])))
    v = verdict_of(res, plc)
    print("\nDESCRIPTIVE (exploratory; each sector against its own baseline): amplification = exp(mean log-difference)")
    print("  %-24s %s" % ("sector", "   |   ".join("%s day 0 / day +1 / both (n)" % lab for lab, _, _ in ERAS)))
    for s in fct.SECTORS:
        cells = []
        for lab, lo, hi in ERAS:
            idxs = [i for i in sched if lo <= yr(i) <= hi]
            parts = []
            for f in (lambda i: fct.ld(LR[s], i, 0, X), lambda i: fct.ld(LR[s], i, 1, X), lambda i: ld_w(LR[s], i, X)):
                vals = [x for x in (f(i) for i in idxs) if x is not None]
                parts.append("%.3f" % math.exp(float(np.mean(vals))) if len(vals) >= 3 else "n/a")
            cells.append("%s / %s / %s (%d)" % (parts[0], parts[1], parts[2], len(idxs)))
        print("  %-24s %s%s" % (s + (" *" if s in RATE else ""), "   |   ".join(cells), ""))
    print("  (* = RATE group)")
    print("\nVERDICT (registered rule): %s" % v)
    print("REGISTERED PREDICTIONS: RATIO A 1.06 (0.98-1.15), B 1.05 (0.97-1.14); P(PASS) 30%%, P(LEAD) 15%%, P(NULL) 50%%, P(REVERSE) 5%%; Financials the largest single sector in at least one era (60%%)")
    print("total %.0fs" % (time.time() - t0))
    return res, plc, v


if __name__ == "__main__":
    main()
