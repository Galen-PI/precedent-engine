#!/usr/bin/env python3
"""
split_artifact_audit.py -- READ-ONLY (data_cache/volume only; run it after build_volume_cache.py). Writes nothing.
THE QUESTION. The volume cache showed close / adjusted_close = 1.000 for 30 years of XOM, so adjusted_close is not dividend-adjusted (returns are PRICE returns). Are stock splits adjusted in the
prices and in the volume? An unadjusted 2-for-1 split is a -50% "return" (right at the pipeline's 50% filter) and doubles the volume level; either would sit among the big ordinary-day misses.
THREE CHECKS, descriptive (no verdict):
  A  Does close ever differ from adjusted_close? (share of securities with any relative difference above 1e-4)
  B  PRICE JUMPS from 2005: a daily price ratio <= 0.65 or >= 1.6 is listed, and marked SPLIT-LIKE if it sits within 1.5% of 1/k or k for k = 2,3,4,5,6,8,10,20 (a crash is unlikely to land on an exact
     split ratio). For each SPLIT-LIKE jump the volume level (median of the next 20 days / median of the previous 20) is shown: a step near k the other way means price AND volume are unadjusted.
  C  VOLUME STEPS WITHOUT A PRICE JUMP from 2005: the median volume of the next 20 days is >= 1.7x or <= 1/1.7 of the previous 20 and stays that way 40 days later, with an absolute price move under 10% on
     the day. These are volume artefacts at splits whose PRICES were adjusted (or other level shifts).
Usage:   python3 -u scripts/card/split_artifact_audit.py
PREDICTIONS (before the run): close equals adjusted_close for at least 95% of securities; price jumps at split ratios are rare (under 30 in the universe) because the provider adjusts splits;
volume steps without a price jump are a larger group (30-150 events) because volume is often not adjusted; most of C's steps are near integer ratios 2 or 3 (up) when a split happened.
"""
import os, sys, glob, pickle, math
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
VOL_DIR = os.path.join(ROOT, "data_cache", "volume")
FROM_DATE = "2005-01-01"
SPLIT_K = (2, 3, 4, 5, 6, 8, 10, 20)
STEP = 1.7


def near_split(ratio):
    for k in SPLIT_K:
        for target in (1.0 / k, float(k)):
            if abs(ratio / target - 1.0) <= 0.015:
                return "1:%d" % k if target > 1 else "%d:1" % k
    return ""


def med_ratio(v, i, w=20):
    a, b = v[max(0, i - w): i], v[i: i + w]
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if len(a) < 10 or len(b) < 10:
        return float("nan")
    return float(np.median(b) / np.median(a))


def main():
    files = sorted(glob.glob(os.path.join(VOL_DIR, "*.pkl")))
    if not files:
        sys.exit("No files in %s: run build_volume_cache.py first." % VOL_DIR)
    n_sec, n_diff, diff_examples = 0, 0, []
    jumps, steps = [], []
    for f in files:
        with open(f, "rb") as fh:
            d = pickle.load(fh)
        n_sec += 1
        dates = d["dates"]
        cl = np.array([np.nan if v is None else v for v in d["close"]], dtype=np.float64)
        ad = np.array([np.nan if v is None else v for v in d["adj"]], dtype=np.float64)
        vo = np.array([np.nan if (v is None or v <= 0) else v for v in d["vol"]], dtype=np.float64)
        with np.errstate(invalid="ignore", divide="ignore"):
            rel = np.abs(cl / ad - 1.0)
        if np.isfinite(rel).any() and np.nanmax(rel) > 1e-4:
            n_diff += 1
            diff_examples.append((d["ticker"], float(np.nanmax(rel))))
        first = next((i for i, x in enumerate(dates) if x >= FROM_DATE), len(dates))
        with np.errstate(invalid="ignore", divide="ignore"):
            pr = ad[1:] / ad[:-1]
        pj = {}
        for i in np.where((pr <= 0.65) | (pr >= 1.6))[0] + 1:
            if i >= first:
                pj[i] = float(pr[i - 1])
                jumps.append((d["ticker"], dates[i], float(pr[i - 1]), near_split(float(pr[i - 1])), med_ratio(vo, i)))
        # volume steps: persistent level shift in the median, without a big price move that day
        if len(vo) > 100:
            W = sliding_window_view(vo, 20)
            cnt = np.isfinite(W).sum(axis=1)
            med = np.where(cnt >= 10, np.nanmedian(W, axis=1), np.nan)          # med[i] = median of vo[i:i+20]
            last_step = -100
            for i in range(max(first, 20), len(vo) - 60):
                a, b, c = med[i - 20], med[i], med[i + 20]
                if not (np.isfinite(a) and np.isfinite(b) and np.isfinite(c)):
                    continue
                r1, r2 = b / a, c / a
                if (r1 >= STEP and r2 >= STEP) or (r1 <= 1 / STEP and r2 <= 1 / STEP):
                    move = abs(ad[i] / ad[i - 1] - 1.0) if np.isfinite(ad[i]) and np.isfinite(ad[i - 1]) else float("nan")
                    if move < 0.10 and i - last_step > 40:
                        steps.append((d["ticker"], dates[i], float(r1), float(move)))
                        last_step = i

    print("securities read: %d" % n_sec)
    print("\nA. close vs adjusted_close: %d of %d securities (%.1f%%) have any relative difference above 1e-4" % (n_diff, n_sec, 100.0 * n_diff / n_sec))
    for t, v in sorted(diff_examples, key=lambda x: -x[1])[:5]:
        print("     %-6s largest relative difference %.4f" % (t, v))
    sl = [j for j in jumps if j[3]]
    print("\nB. PRICE JUMPS from %s (ratio <= 0.65 or >= 1.6): %d | SPLIT-LIKE (within 1.5%% of an exact split ratio): %d" % (FROM_DATE, len(jumps), len(sl)))
    for t, dt, r, lab, vr in sorted(jumps, key=lambda x: (x[3] == "", x[1]))[:14]:
        print("     %-6s %s price ratio %.4f %-5s | volume step across the date %s" % (t, dt, r, lab or "(not an exact ratio)", "n/a" if not math.isfinite(vr) else "%.2fx" % vr))
    print("\nC. VOLUME LEVEL STEPS WITHOUT A PRICE JUMP from %s (median volume of the next 20 days vs the previous 20 beyond %.1fx, persisting): %d" % (FROM_DATE, STEP, len(steps)))
    up = [s for s in steps if s[2] >= STEP]
    print("     up %d | down %d | near an integer ratio (within 12%% of 2, 3, 4 or 5 up, or 1/2..1/5 down): %d" % (
        len(up), len(steps) - len(up), sum(1 for s in steps if any(abs((s[2] if s[2] >= 1 else 1 / s[2]) / k - 1) <= 0.12 for k in (2, 3, 4, 5)))))
    for t, dt, r, mv in sorted(steps, key=lambda x: -abs(math.log(x[2])))[:14]:
        print("     %-6s %s volume step %.2fx | price move that day %.1f%%" % (t, dt, r, 100 * mv))
    print("\nREADING: B tells whether split days can sit among the big misses; C tells whether volume ratios are polluted around splits (then a baseline that looks at both sides of the day is safer).")
    print("NOTE: the dates in C are approximate (within about 10 trading days of the step), and an event whose price AND volume are both unadjusted can appear in both B and C.")


if __name__ == "__main__":
    main()
