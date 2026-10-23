#!/usr/bin/env python3
"""
fomc_day_sector_absolute.py -- READ-ONLY, DESCRIPTIVE (exploratory, no verdict; no registration needed because it re-reads a registered result). Writes nothing.
WHY. In fomc_day_sector_test.py the eleven sector amplifications average about 0.99 while the market-wide statistic reads 1.11-1.14 on day 0 and about 1.20 on day +1. A sector series that is RELATIVE to the rest of the market cancels the market-wide effect by construction, so that table shows who moves more than the market, not who moves more than normal. This script uses each sector's ABSOLUTE series, log of its own mean z (MZ[k]), against its own baseline (fed_change_day_test.ld, the same exclusion set), so each sector's own Fed-day amplification is visible.
IT PRINTS (1) each sector's absolute amplification at day 0, day +1 and both, per era, for the scheduled meetings; (2) a RECONCILIATION: the equal-weighted mean of the sector amplifications beside the market-wide amplification (they differ slightly: a mean of logs is not the log of a mean); (3) the registered RATE-minus-REST contrast re-run on the absolute series (robustness check of the registered NULL; no verdict).
Usage:   python3 -u scripts/card/fomc_day_sector_absolute.py
"""
import os, sys, bisect, math, time, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fed_change_day_test as fct
import fomc_day_test as fd
import fomc_day_sector_test as fs


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
    yr = lambda i: int(days[i][:4])
    AB = {}
    for k, s in enumerate(fct.SECTORS):
        v = np.full(MZ.shape[1], np.nan)
        ok = (NN[k] > 0) & np.isfinite(MZ[k]) & (MZ[k] > 0)
        v[ok] = np.log(MZ[k][ok])
        AB[s] = v
    ok = np.isfinite(MZ) & np.isfinite(NN) & (NN > 0)
    num, den = np.where(ok, NN * MZ, 0.0).sum(axis=0), np.where(ok, NN, 0.0).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        lm = np.log(num / den)
    lm[~(den > 0)] = np.nan
    print("sector-days %d | scheduled meetings from 2004 %d | %.0fs" % (D, len(sched), time.time() - t0), flush=True)
    amp = lambda ser, idxs, w: (lambda vals: math.exp(float(np.mean(vals))) if len(vals) >= 3 else float("nan"))([x for x in (fct.ld(ser, i, w, X) for i in idxs) if x is not None])
    print("\nABSOLUTE sector amplification (each sector's own mean z against its own baseline): day 0 / day +1 per era; * = RATE group")
    cols = {}
    for lab, lo, hi in fd.ERAS:
        idxs = [i for i in sched if lo <= yr(i) <= hi]
        cols[lab] = (idxs, {s: (amp(AB[s], idxs, 0), amp(AB[s], idxs, 1)) for s in fct.SECTORS})
    print("  %-24s %s" % ("sector", "   |   ".join("%s day 0 / day +1" % lab for lab, _, _ in fd.ERAS)))
    for s in fct.SECTORS:
        print("  %-24s %s" % (s + (" *" if s in fs.RATE else ""), "   |   ".join("%.3f / %.3f" % cols[lab][1][s] for lab, _, _ in fd.ERAS)))
    print("\nRECONCILIATION with the market-wide statistic (the equal-weighted mean of the 11 sector amplifications vs the market-wide one)")
    for lab, _, _ in fd.ERAS:
        idxs, d = cols[lab]
        print("  %-10s day 0: sector mean %.3f vs market-wide %.3f | day +1: sector mean %.3f vs market-wide %.3f" % (lab, np.mean([d[s][0] for s in fct.SECTORS]), amp(lm, idxs, 0), np.mean([d[s][1] for s in fct.SECTORS]), amp(lm, idxs, 1)))
    rest = [s for s in fct.SECTORS if s not in fs.RATE]

    def delta(i):
        r = [fs.ld_w(AB[s], i, X) for s in fs.RATE]
        o = [fs.ld_w(AB[s], i, X) for s in rest]
        return None if any(v is None for v in r + o) else float(np.mean(r) - np.mean(o))
    print("\nROBUSTNESS: the registered RATE minus REST contrast on the ABSOLUTE series (day 0 and day +1 averaged; no verdict)")
    out = {}
    for lab, lo, hi in fd.ERAS:
        out[lab] = fs.paired([delta(i) for i in [i for i in sched if lo <= yr(i) <= hi]])
        print("  %-10s %s" % (lab, fs.pfmt(out[lab])))
    print("total %.0fs" % (time.time() - t0))
    return cols, out


if __name__ == "__main__":
    main()
