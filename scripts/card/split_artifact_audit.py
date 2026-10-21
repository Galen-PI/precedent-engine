#!/usr/bin/env python3
"""
split_artifact_audit.py -- READ-ONLY (data_cache/volume only; run it after build_volume_cache.py). Writes nothing.
THE QUESTION. The volume cache showed close / adjusted_close = 1.000 for 30 years of XOM, so adjusted_close is not dividend-adjusted (returns are PRICE returns). Are stock splits adjusted in the
prices and in the volume? An unadjusted 2-for-1 split is a -50% "return" (right at the pipeline's 50% filter) and doubles the volume level; either would sit among the big ordinary-day misses.
FOUR CHECKS, descriptive (no verdict):
  A  Does close ever differ from adjusted_close? (share of securities with any relative difference above 1e-4)
  B  PRICE JUMPS from 2005: a daily price ratio <= 0.65 or >= 1.6 is listed, and marked SPLIT-LIKE if it sits within 1.5% of 1/k or k for k = 2,3,4,5,6,8,10,20 (a crash is unlikely to land on an exact
     split ratio). For each SPLIT-LIKE jump the volume level (median of the next 20 days / median of the previous 20) is shown: a step near k the other way means price AND volume are unadjusted.
  C  VOLUME STEPS WITHOUT A PRICE JUMP from 2005: the median volume of the next 20 days is >= 1.7x or <= 1/1.7 of the previous 20 and stays that way 40 days later, with an absolute price move under 10% on
     the day. These are volume artefacts at splits whose PRICES were adjusted (or other level shifts).
  D  KNOWN SPLITS (added after the first run): AAPL 4:1 and TSLA 5:1 on 2020-08-31, TSLA 3:1 on 2022-08-25, NVDA 4:1 on 2021-07-20 and 10:1 on 2024-06-10, AMZN 20:1 on 2022-06-06, GOOGL 20:1 on
     2022-07-18, WMT 3:1 on 2024-02-26: the price ratio across the date and the volume level step (median of the next 20 days / the previous 20). Both near 1.00 = prices and volume adjusted; a price
     ratio near 1/k = prices unadjusted; a volume step near k = volume unadjusted. B and C also print size breakdowns (B: how many down-jumps of 35-50% survive the pipeline's 50% return filter; C: steps by size).
Usage:   python3 -u scripts/card/split_artifact_audit.py
FIRST-RUN PREDICTIONS (scored): close equals adjusted_close for at least 95% of securities; price jumps at split ratios are rare (under 30 in the universe) because the provider adjusts splits;
volume steps without a price jump are a larger group (30-150 events) because volume is often not adjusted; most of C's steps are near integer ratios 2 or 3 (up) when a split happened.
PREDICTIONS FOR D (before it runs): all eight price ratios within 5% of 1.00 (splits are adjusted in prices); at least six of the eight volume steps within 25% of 1.00 (about 65% confidence that volume is
adjusted too); the extreme volume steps (4x or more) number 20-80 across the universe.
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
    KNOWN = [("AAPL", "2020-08-31", 4), ("TSLA", "2020-08-31", 5), ("TSLA", "2022-08-25", 3), ("NVDA", "2021-07-20", 4), ("NVDA", "2024-06-10", 10),
             ("AMZN", "2022-06-06", 20), ("GOOGL", "2022-07-18", 20), ("WMT", "2024-02-26", 3)]
    known_tickers, held = {k[0] for k in KNOWN}, {}
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
        if d["ticker"] in known_tickers:
            held[d["ticker"]] = (dates, ad, vo)
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
    down_kept = sum(1 for j in jumps if 0.5 < j[2] <= 0.65)
    print("     size: down-jumps of more than 50%% (ratio <= 0.50, dropped by the pipeline's 50%% filter): %d | down 35-50%% (KEPT as returns): %d | up 60%% or more (dropped): %d" % (
        sum(1 for j in jumps if j[2] <= 0.5), down_kept, sum(1 for j in jumps if j[2] >= 1.6)))
    print("\nC. VOLUME LEVEL STEPS WITHOUT A PRICE JUMP from %s (median volume of the next 20 days vs the previous 20 beyond %.1fx, persisting): %d" % (FROM_DATE, STEP, len(steps)))
    up = [s for s in steps if s[2] >= STEP]
    print("     up %d | down %d | near an integer ratio (within 12%% of 2, 3, 4 or 5 up, or 1/2..1/5 down): %d" % (
        len(up), len(steps) - len(up), sum(1 for s in steps if any(abs((s[2] if s[2] >= 1 else 1 / s[2]) / k - 1) <= 0.12 for k in (2, 3, 4, 5)))))
    for t, dt, r, mv in sorted(steps, key=lambda x: -abs(math.log(x[2])))[:14]:
        print("     %-6s %s volume step %.2fx | price move that day %.1f%%" % (t, dt, r, 100 * mv))
    mags = [max(x[2], 1.0 / x[2]) for x in steps]
    print("     by size (either direction): 1.7-2.5x %d | 2.5-4x %d | 4-10x %d | 10x or more %d  (4x or more looks like a unit, source or ticker change)" % (
        sum(1 for m in mags if m < 2.5), sum(1 for m in mags if 2.5 <= m < 4), sum(1 for m in mags if 4 <= m < 10), sum(1 for m in mags if m >= 10)))
    print("\nD. KNOWN SPLITS (price ratio across the date; volume level step = median of the next 20 days / the previous 20):")
    print("     %-6s %-11s %5s | %-12s %-14s | %s" % ("ticker", "date", "split", "price ratio", "volume step", "reading (adjusted = both near 1.00)"))
    for tk, dt, k in KNOWN:
        if tk not in held:
            print("     %-6s %-11s %4d:1 | not in the cache" % (tk, dt, k))
            continue
        dates_, ad_, vo_ = held[tk]
        i = next((j for j, x in enumerate(dates_) if x >= dt), None)
        if i is None or i < 25 or i + 25 > len(dates_):
            print("     %-6s %-11s %4d:1 | date outside the history" % (tk, dt, k))
            continue
        p_ = ad_[i] / ad_[i - 1]
        v_ = med_ratio(vo_, i)
        read = []
        read.append("prices ADJUSTED" if abs(p_ - 1) < 0.10 else ("prices UNADJUSTED (about 1/%d)" % k if abs(p_ * k - 1) < 0.15 else "price moved %.0f%%" % (100 * (p_ - 1))))
        read.append("volume ADJUSTED" if math.isfinite(v_) and abs(v_ - 1) < 0.35 else ("volume UNADJUSTED (about %dx)" % k if math.isfinite(v_) and abs(v_ / k - 1) < 0.30 else "volume step %.2fx (unclear)" % v_))
        print("     %-6s %-11s %4d:1 | %-12.3f %-14.2f | %s" % (tk, dt, k, p_, v_, "; ".join(read)))
    print("\nREADING: B tells whether split days can sit among the big misses; C tells whether volume ratios are polluted around splits (then a baseline that looks at both sides of the day is safer).")
    print("NOTE: the dates in C are approximate (within about 10 trading days of the step), and an event whose price AND volume are both unadjusted can appear in both B and C.")


if __name__ == "__main__":
    main()
