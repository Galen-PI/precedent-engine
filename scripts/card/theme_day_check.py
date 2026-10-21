#!/usr/bin/env python3
"""
theme_day_check.py -- READ-ONLY (local matrices, results/unrecorded_candidates.csv, optionally results/unrecorded_group_flags.csv; the database is read once for tickers and sectors). Writes results/unrecorded_theme_flags.csv.
THE QUESTION. group_move_check.py found that only 4.6% of the big volume-spike misses had 4 or more of their 10 statistical peers moving the same way, and the reading then turned up two hits that were thematic or geopolitical (an AI-disruption
selloff across logistics services on 2026-02-12; Iran's missile attack on Israel lifting defense contractors on 2024-10-01), one of which the peer check had classed as stock-specific because the news hit stocks OUTSIDE its statistical peer list.
This check needs no peer list: on the day of each big miss, how many OTHER stocks anywhere have a big miss in the same direction?
METHOD. Signed band units as in group_move_check.py (the miss in own-spread units divided by the square root of the other stocks' mean squared standardized miss that day). For each big miss (the candidates CSV's rows from 2006, with the sign
of its miss) CLUSTER = the number of other stocks whose signed band unit that day, multiplied by the miss's sign, is at least 2.5. PLACEBO: three random days of the same year for the same stock and sign (the stock itself excluded), giving the
distribution of CLUSTER on an arbitrary day. A THEME DAY = a CLUSTER above the 95th percentile of the pooled placebo counts, so about 5% of arbitrary days qualify by construction. Reported: the theme-day share (real vs placebo) overall, by
category, era and size of the miss; for theme-day misses whether the cluster is concentrated in the stock's own sector (at least half of the participants in its sector: SECTOR THEME) or spread across sectors (CROSS-SECTOR); the overlap with the
group-move flags (support of 4 or more peers) among the big volume-spike misses; twelve random theme-day examples with the participating tickers and sectors; and the file of flags for the next reading sample.
PRE-SET RULE: THEME DAYS ARE MATERIAL if, among the big volume-spike misses ('volume spike only' plus 'volume spike + article spike'), the theme-day share exceeds the placebo share by at least 10 points and the 95% interval of that
excess (resampling calendar MONTHS, 500 resamples) is above 0. Everything else is descriptive.
SENSITIVITY (synthetic worlds, written before the real run): with no theme shocks the excess was -0.8 points [-1.7, +0.1] (no false positive); with 12 random stocks from any sector sharing a 3-6% shock on 1% of days (about 12% of the
big misses were themed) it read +6.5 points [+4.3, +10.1], which the 10-point rule calls NOT material. A theme day inflates its own scale (the other stocks' mean squared miss rises), which pulls the participants' band units down, so the real
excess is a FLOOR. Reading guide, fixed before the run: an excess of 5 points or more with the interval above 0 counts as evidence of themes even when the rule says NOT material; the rule itself is unchanged.
PREDICTIONS (before the run): the placebo median CLUSTER is 2-4 and its 95th percentile 7-11; the real theme-day share among big volume-spike misses is 12-25% (excess 7-20 points: MATERIAL with probability about 45%); quiet misses 10-20%; the
share rises across eras by at least 5 points (2006-2012 below 2020-2026); 25-45% of theme-day misses are SECTOR THEMES and the rest CROSS-SECTOR; theme days and group moves overlap only partly, and their union covers 14-28% of the big
volume-spike misses; CHRW 2026-02-12 is a theme day (probability about 85%) and LMT 2024-10-01 is one (about 50%).
Usage:   python3 -u scripts/card/theme_day_check.py [seed]       Needs: data_cache/audit_matrices.npz and results/unrecorded_candidates.csv.
"""
import os, sys, csv, time, random, bisect, warnings
from collections import Counter
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import unrecorded_candidates as uc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
RESULTS = os.path.join(ROOT, "results")
TEST_START = 2006
OTHER_BU = 2.5
N_PLACEBO = 3
PCTL = 95
SECTOR_SHARE = 0.5
N_BOOT = 500
SEED = 20261021
ERAS = [("2006-2012", 2006, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]
VOLUME_CATS = ("volume spike only", "volume spike + article spike")


def pct(x):
    return "%5.1f%%" % (100.0 * x) if np.isfinite(x) else "  n/a "


def main():
    t0 = time.time()
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(time.strftime("%Y%m%d"))
    cand_path = os.path.join(RESULTS, "unrecorded_candidates.csv")
    for f in (CACHE_FILE, cand_path):
        if not os.path.exists(f):
            sys.exit("Missing %s" % f)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, tickers, E, SD = d["dates"], [str(x) for x in d["tickers"]], d["E"].astype(np.float64), d["SD"].astype(np.float64)
    N, n = E.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    months = np.array([(int(x[:4]) - TEST_START) * 12 + int(x[5:7]) - 1 for x in dl])
    M = int(months.max()) + 1
    with np.errstate(invalid="ignore", divide="ignore"):
        z = E / SD
    valid = np.isfinite(z)
    S = np.where(valid, z ** 2, 0.0).sum(axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, z ** 2, 0.0)) / (cnt[None, :] - 1)
        buS = z / np.sqrt(qo)
    buS[~((cnt[None, :] > 20) & np.isfinite(buS))] = np.nan
    pos = np.nan_to_num(buS, nan=0.0) >= OTHER_BU
    neg = np.nan_to_num(buS, nan=0.0) <= -OTHER_BU
    cpos, cneg = pos.sum(axis=0), neg.sum(axis=0)

    sector = {}
    try:
        sb = ew.get_sb()
        for r in uc.paged(lambda: sb.table("securities").select("ticker,sector").order("id")):
            if r.get("ticker"):
                sector[r["ticker"]] = r.get("sector") or "(none)"
    except Exception as e:
        print("sectors not available (%s): sector composition is skipped" % str(e)[:80])
    tick_sector = [sector.get(t) for t in tickers]

    kk = {t: k for k, t in enumerate(tickers)}
    rows = []
    with open(cand_path) as fh:
        for r in csv.DictReader(fh):
            k, t = kk.get(r["ticker"]), bisect.bisect_left(dl, r["date"])
            if k is None or t >= n or dl[t] != r["date"] or years[t] < TEST_START:
                continue
            miss = float(r["miss_pct"])
            if miss == 0.0:
                continue
            rows.append((k, t, 1 if miss > 0 else -1, r["category"], float(r["band_units"])))
    rng = np.random.RandomState(seed)
    year_days = {int(y): np.where(years == y)[0] for y in np.unique(years)}
    real_c, plc_c = [], []
    for k, t, sg, cat, bu_ in rows:
        cs = cpos if sg > 0 else cneg
        real_c.append(int(cs[t]) - 1)
        yd = year_days[int(years[t])]
        ok = yd[(yd != t) & np.isfinite(buS[k, yd])]
        picks = rng.choice(ok, size=N_PLACEBO, replace=len(ok) < N_PLACEBO)
        plc_c.append([int(cs[tp]) - int(sg * buS[k, tp] >= OTHER_BU) for tp in picks])
    real_c, plc_c = np.array(real_c), np.array(plc_c)
    thr = float(np.percentile(plc_c, PCTL))
    theme = real_c > thr
    plc_theme = plc_c > thr
    cats = np.array([r[3] for r in rows])
    bun = np.array([r[4] for r in rows])
    tt = np.array([r[1] for r in rows])
    yy, mm = years[tt], months[tt]
    print("big misses scored: %d | %.0fs" % (len(rows), time.time() - t0), flush=True)
    print("\nCLUSTER (other stocks with a big miss the same way that day, >= %.1f band units): placebo median %.0f, mean %.1f, 95th percentile %.0f | real median %.0f, mean %.1f" % (
        OTHER_BU, float(np.median(plc_c)), float(plc_c.mean()), thr, float(np.median(real_c)), float(real_c.mean())))
    print("THEME DAY = a cluster above %.0f: real %s | placebo %s" % (thr, pct(float(theme.mean())), pct(float(plc_theme.mean()))))

    def cell(mask):
        if mask.sum() < 30:
            return "n/a"
        return "%s vs %s (n %d)" % (pct(float(theme[mask].mean())), pct(float(plc_theme[mask].mean())), int(mask.sum()))
    print("\nTHEME-DAY SHARE (real vs placebo) BY CATEGORY")
    for c in sorted(set(cats)):
        print("  %-36s %s" % (c, cell(cats == c)))
    print("BY ERA")
    for lab, lo, hi in ERAS:
        print("  %-10s %s" % (lab, cell((yy >= lo) & (yy <= hi))))
    print("BY SIZE OF THE MISS (band units)")
    for lo, hi in ((3, 4), (4, 5), (5, 7), (7, 1e9)):
        print("  %-10s %s" % ("%d to %s" % (lo, "more" if hi > 1e8 else str(hi)), cell((bun >= lo) & (bun < hi))))

    vs = np.isin(cats, VOLUME_CATS)
    def per_month(mask):
        return np.bincount(mm[mask], minlength=M).astype(float)
    tot, hit_r = per_month(vs), per_month(vs & theme)
    hit_p = np.array([np.bincount(mm[vs], weights=plc_theme[vs][:, j].astype(float), minlength=M) for j in range(N_PLACEBO)]).mean(axis=0)
    def excess(w):
        return ((w @ hit_r) - (w @ hit_p)) / max(w @ tot, 1.0)
    pt = excess(np.ones(M))
    live = np.where(tot > 0)[0]
    brng = np.random.RandomState(seed + 1)
    boot = [excess(np.bincount(brng.choice(live, size=len(live)), minlength=M).astype(float)) for _ in range(N_BOOT)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print("\nRULE (volume-spike misses, n %d): theme-day share real %s, placebo %s, excess %+.1f points [%+.1f, %+.1f]" % (int(vs.sum()), pct(float(theme[vs].mean())), pct(float(plc_theme[vs].mean())), 100 * pt, 100 * lo, 100 * hi))
    print("VERDICT (pre-set: excess at least 10 points and the interval above 0): THEME DAYS ARE %s" % ("MATERIAL" if (pt >= 0.10 and lo > 0) else "NOT material"))

    # participants, sector composition, examples ----------------------------------------------------------------------------------------------------------------
    info = {}
    for i in np.where(theme)[0]:
        k, t, sg = rows[i][0], rows[i][1], rows[i][2]
        vals = sg * buS[:, t]
        part = [j for j in np.argsort(-np.nan_to_num(vals, nan=-9.0)) if j != k and np.isfinite(vals[j]) and vals[j] >= OTHER_BU]
        secs = Counter(tick_sector[j] for j in part if tick_sector[j])
        own = tick_sector[k]
        share = (secs.get(own, 0) / max(len(part), 1)) if (own and sector) else float("nan")
        info[i] = (part, secs, share)
    if sector and info:
        shares = np.array([v[2] for v in info.values()])
        print("\nTHEME-DAY MISSES (%d): SECTOR THEME (at least %.0f%% of the participants in the stock's own sector) %s | CROSS-SECTOR %s" % (
            len(info), 100 * SECTOR_SHARE, pct(float(np.nanmean(shares >= SECTOR_SHARE))), pct(float(np.nanmean(shares < SECTOR_SHARE)))))
    grp = {}
    gpath = os.path.join(RESULTS, "unrecorded_group_flags.csv")
    if os.path.exists(gpath):
        for r in csv.DictReader(open(gpath)):
            grp[(r["date"], r["ticker"])] = int(r["group_move"])
        g = np.array([grp.get((dl[r[1]], tickers[r[0]]), -1) for r in rows])
        have = vs & (g >= 0)
        both, only_t, only_g, neither = (have & theme & (g == 1)), (have & theme & (g == 0)), (have & ~theme & (g == 1)), (have & ~theme & (g == 0))
        nv = max(int(have.sum()), 1)
        print("\nOVERLAP WITH GROUP MOVES among the big volume-spike misses that have a group flag (n %d): both %s | theme day only %s | group move only %s | neither %s | UNION %s" % (
            nv, pct(both.sum() / nv), pct(only_t.sum() / nv), pct(only_g.sum() / nv), pct(neither.sum() / nv), pct((both.sum() + only_t.sum() + only_g.sum()) / nv)))
    ex = sorted(info)
    r3 = random.Random(seed)
    print("\nTWELVE RANDOM THEME-DAY MISSES (ticker, date, size, cluster, the top sectors among participants, a few participants):")
    for i in r3.sample(ex, min(12, len(ex))):
        k, t = rows[i][0], rows[i][1]
        part, secs, share = info[i]
        print("  %-6s %s  %.1f bu  cluster %3d  %s | %s" % (tickers[k], dl[t], rows[i][4], real_c[i], ", ".join("%s %d" % (s, c) for s, c in secs.most_common(3)), " ".join(tickers[j] for j in part[:6])))

    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "unrecorded_theme_flags.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "ticker", "category", "band_units", "cluster_n", "theme_day", "own_sector_share", "top_participants"])
        for i, (k, t, sg, cat, bu_) in enumerate(rows):
            sh = info[i][2] if i in info else ""
            w.writerow([dl[t], tickers[k], cat, "%.2f" % bu_, int(real_c[i]), int(theme[i]), ("%.2f" % sh) if sh != "" and np.isfinite(sh) else "", " ".join(tickers[j] for j in info[i][0][:8]) if i in info else ""])
    print("\nwrote results/unrecorded_theme_flags.csv | total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
