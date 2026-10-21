#!/usr/bin/env python3
"""
quiet_profile.py -- READ-ONLY (results/unrecorded_candidates.csv, data_cache/audit_matrices.npz, data_cache/volume). Writes nothing.
THE QUESTION. unrecorded_candidates.py found that 47% of the non-aftershock big ordinary misses (>= 3 band units, no own event / earnings / Regulation FD window) carry NO volume spike (volume under 2x
the median of the previous 20 days). Are those QUIET misses noise-like, bad prints, or real but mild news? This profiles each category WITHOUT reading anything, using what the data already hold:
  NEXT-DAY REVERSAL: the next day's miss has the OPPOSITE sign and at least half the size of this one (a bad print that corrects looks like this); CONTINUATION: the same sign and at least half the size.
     Rough reference for iid Gaussian noise after a big miss: each is about 6-7% (the next day must be at least 1.5 sigma on the right side); volatility clustering lifts both a little.
  VOLUME RATIO SHAPE (today's volume / the median of the previous 20 days): quartiles. A quiet group centred near 1.0 looks like noise; centred at 1.3-1.8 looks like real but mild news.
  PRICE LEVEL (split-adjusted close on the day): share under $10 (thin, low-priced stocks carry more microstructure noise).
  MARKET STRESS of the day (sqrt of the mean squared standardized miss across stocks; 1.2 or more = elevated) and ERA (2020-2026 share).
  SIGN: share of negative misses; SIZE: median |miss| in percent and in band units.
Usage:   python3 -u scripts/card/quiet_profile.py
DESCRIPTIVE: no verdict. PREDICTIONS (before the run): the quiet group's next-day reversal share is higher than the volume-spike group's but still far below 50% (most quiet misses are not bad prints); the
quiet group's volume ratio has a median of 1.1-1.4; its share under $10 is higher than the spike group's; its median band units are smaller (3.3 vs 3.6); the aftershock group shows the highest
continuation share (volatility clustering); negative and positive misses are about equally common in every group (45-60% negative).
"""
import os, sys, csv, glob, pickle, math, bisect
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CSV_FILE = os.path.join(ROOT, "results", "unrecorded_candidates.csv")
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
VOL_DIR = os.path.join(ROOT, "data_cache", "volume")
CATS = ["volume spike + article spike", "volume spike only", "article spike only", "quiet (neither)", "aftershock: previous day big", "aftershock: within 5 days after an event/earnings/7.01"]


def pct(x):
    return "%5.1f%%" % (100.0 * x)


def main():
    for f in (CSV_FILE, CACHE_FILE):
        if not os.path.exists(f):
            sys.exit("Missing %s (run unrecorded_candidates.py first)." % f)
    rows = list(csv.DictReader(open(CSV_FILE)))
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, tickers, E, SD = d["dates"], d["tickers"], d["E"].astype(np.float64), d["SD"].astype(np.float64)
    dl = [str(x) for x in dates]
    tpos = {t: i for i, t in enumerate(dl)}
    kpos = {str(t): k for k, t in enumerate(tickers.tolist())}
    with np.errstate(invalid="ignore", divide="ignore"):
        z2 = (E / SD) ** 2
    valid = np.isfinite(z2)
    stress = np.sqrt(np.where(valid, z2, 0.0).sum(axis=0) / np.maximum(valid.sum(axis=0), 1))

    need = defaultdict(set)
    for r in rows:
        need[r["ticker"]].add(r["date"])
    price = {}
    for f in glob.glob(os.path.join(VOL_DIR, "*.pkl")):
        with open(f, "rb") as fh:
            c = pickle.load(fh)
        if c["ticker"] in need and c["dates"]:
            pos = {x: i for i, x in enumerate(c["dates"])}
            for dt in need[c["ticker"]]:
                i = pos.get(dt)
                if i is not None and c["adj"][i] is not None:
                    price[(c["ticker"], dt)] = c["adj"][i]

    stats = defaultdict(lambda: defaultdict(list))
    for r in rows:
        k, t = kpos.get(r["ticker"]), tpos.get(r["date"])
        if k is None or t is None or t + 1 >= len(dl):
            continue
        cat = r["category"] or "(none)"
        s = stats[cat]
        miss = float(r["miss_pct"])
        s["neg"].append(miss < 0)
        s["absmiss"].append(abs(miss))
        s["bu"].append(float(r["band_units"]))
        if r["volume_ratio"] != "":
            s["vr"].append(float(r["volume_ratio"]))
        s["stress"].append(stress[t] >= 1.2)
        s["era"].append(int(r["date"][:4]) >= 2020)
        p = price.get((r["ticker"], r["date"]))
        if p is not None:
            s["lowp"].append(p < 10.0)
        e0, e1 = E[k, t], E[k, t + 1]
        if np.isfinite(e0) and np.isfinite(e1) and e0 != 0:
            rel = abs(e1) / abs(e0)
            s["rev"].append(bool(np.sign(e1) != np.sign(e0) and rel >= 0.5))
            s["cont"].append(bool(np.sign(e1) == np.sign(e0) and rel >= 0.5))

    print("PROFILE OF THE %d BIG ORDINARY MISSES BY CATEGORY (no row was read; every figure comes from the data)" % len(rows))
    print("  %-52s %6s | %7s %8s %6s | %-19s | %7s %7s | %8s %8s %7s %7s" % ("category", "n", "negative", "|miss|%", "band", "volume ratio p25/50/75", "stress", "2020+", "under$10", "reversal", "contin.", "(n rev)"))
    for cat in CATS + ["no volume data"]:
        s = stats.get(cat)
        if not s or not s["bu"]:
            continue
        vr = s["vr"]
        vrt = "%.2f / %.2f / %.2f" % tuple(np.quantile(vr, [0.25, 0.5, 0.75])) if len(vr) >= 20 else "n/a"
        print("  %-52s %6d | %7s %7.2f%% %6.2f | %-19s | %7s %7s | %8s %8s %7s %7d" % (
            cat, len(s["bu"]), pct(np.mean(s["neg"])), float(np.median(s["absmiss"])), float(np.median(s["bu"])), vrt, pct(np.mean(s["stress"])), pct(np.mean(s["era"])),
            pct(np.mean(s["lowp"])) if s["lowp"] else "n/a", pct(np.mean(s["rev"])) if s["rev"] else "n/a", pct(np.mean(s["cont"])) if s["cont"] else "n/a", len(s["rev"])))
    q, v = stats.get("quiet (neither)"), stats.get("volume spike only")
    if q and v and q["rev"] and v["rev"]:
        print("\n  quiet vs volume-spike-only: reversal %s vs %s | continuation %s vs %s | under $10 %s vs %s | median volume ratio %.2f vs %.2f" % (
            pct(np.mean(q["rev"])), pct(np.mean(v["rev"])), pct(np.mean(q["cont"])), pct(np.mean(v["cont"])),
            pct(np.mean(q["lowp"])) if q["lowp"] else "n/a", pct(np.mean(v["lowp"])) if v["lowp"] else "n/a", float(np.median(q["vr"])), float(np.median(v["vr"]))))
    print("\n  reference: for iid Gaussian noise each of reversal and continuation would be about 6-7%; a bad print that corrects the next day would show a reversal share far above that.")


if __name__ == "__main__":
    main()
