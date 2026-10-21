#!/usr/bin/env python3
"""
sector_cluster_check.py -- READ-ONLY (local matrices, results/unrecorded_candidates.csv, results/unrecorded_group_flags.csv if present; the database is read once for tickers and sectors). Writes results/unrecorded_sector_cluster_flags.csv.
WHY THIS EXISTS. theme_day_check.py counted OTHER stocks ANYWHERE with a big same-direction miss on the day of each big miss and found no excess (2.2% vs 2.5% placebo, excess -0.3 points [-1.0, +0.4]). But on real data an arbitrary day already has
about 5 such stocks (roughly 1% of stock-days are big, across 495 stocks), while my synthetic validation had a baseline near 2, so the check's power for NARROW themes (5-8 stocks, like the 2026-02-12 logistics selloff) was overstated: it can only see
broad event days. The right granularity for a narrow theme is the stock's own sector, where the arbitrary-day baseline is about 0.5-1.
METHOD. Signed band units as in theme_day_check.py. For each big miss (the candidates CSV's rows from 2006 on, with the sign of its miss) CLUSTER = the number of other stocks IN THE SAME SECTOR whose signed band unit that day, times the miss's
sign, is at least 2.5. PLACEBO: three random days of the same year for the same stock and sign (the stock itself excluded), the same count within its sector on those days. A SECTOR THEME = a CLUSTER above the 95th percentile of the pooled placebo
counts OF THAT SECTOR (thresholds differ with sector size; at least 1). Reported: the share (real vs placebo) overall, by category, era, size of the miss and sector; the overlap with the group-move flags and with the all-stock theme flags among the
big volume-spike misses; twelve random sector-theme examples with the stocks that moved together.
NORMALISATION FIX (POST HOC, written after the first real run of theme_day_check.py and a diagnosis on a synthetic CONTROL world with no themes, where real days read BELOW placebo days, 1.9% vs 4.0%): the cause is mechanical. A band unit is divided
by the square root of the other stocks' mean squared miss that day, and that mean includes the focal stock's own big miss, so a big miss by one stock shrinks every other stock's band unit by about 2%; with fat tails that cuts the chance of
passing a threshold by about 10% (synthetic: 3.01 other stocks at or above 2.5 on days with a big miss vs 3.44 on arbitrary days, the same in every market-scale bin, so matching placebo days on market scale does NOT fix it). The counts of OTHER stocks
are now computed with the focal stock left out of the normalisation, identically on real and placebo days. The first real run (unfixed: real 2.2% vs placebo 2.5%, excess -0.3 points [-1.0, +0.4]; real mean cluster 4.8 vs 5.0) is superseded;
its null was biased downward by about 4%.
SECTOR-MEAN CORRECTION (same post-hoc fix): the matrices subtract a leave-one-out sector mean, so every sector-MATE of the focal stock has an expected return that includes the focal stock's return divided by (sector size - 1); a +5% jump by
one stock lowers its mates' misses by about 0.1% (z by about -0.06), which cut the same-sector control from 4.0% to 2.6%. The focal stock's raw return over (n - 1) is added back to each mate's miss (sector-factor loading taken as 1, an approximation).
PRE-SET RULE: SECTOR THEMES ARE MATERIAL if, among the big volume-spike misses ('volume spike only' plus 'volume spike + article spike'), the sector-theme share exceeds the placebo share by at least 10 points and the 95% interval of that excess
(resampling calendar MONTHS, 500 resamples) is above 0. READING GUIDE (fixed before any real run of THIS design, from the synthetic validation below): an excess of 2 points or more with the interval above 0 counts as evidence of narrow themes, and the excess approximates the themed share of the big misses
(a theme day inflates its own scale, so it is a floor); the 10-point rule stays as the headline test of whether themes are MATERIAL.
VALIDATION (synthetic worlds with heavy-tailed noise, so an arbitrary day already has about 3.4 other big misses as in real data; narrow themes = 6 random stocks inside one sector sharing a 3-6% shock): CONTROL with no themes: excess -0.5 points [-1.1, +0.2] (all-stock
version -0.0 [-0.6, +0.5]); with themes on 4% of days only 3.0% of the candidate rows were themed stock-days (most 3-6% shocks do not clear 3 band units), 89% of those were flagged, and the excess read +2.2 points [+1.3, +3.1] (all-stock version +0.6 [-0.1, +1.4]: it cannot see
narrow themes). Before the two post-hoc fixes the control read -2.2 [-2.8, -1.6] (a mechanical negative dependence), which would have hidden themes.
PREDICTIONS (before the run): the placebo threshold is 1-3 stocks per sector; the real sector-theme share among big volume-spike misses is 7-14% against about 4% placebo (excess 3-10 points: MATERIAL probability about 15%, the 2-point reading guide met
with probability about 70%); the share is higher in Industrials, Information Technology and Financials than in Utilities; CHRW 2026-02-12 is a sector theme (probability about 80%), LMT 2024-10-01 is one (about 60%); the share rises across eras.
Usage:   python3 -u scripts/card/sector_cluster_check.py [seed]       Needs: data_cache/audit_matrices.npz, results/unrecorded_candidates.csv and the database (securities.ticker, securities.sector).
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
    Y = d["Y"].astype(np.float64)                                     # the stock's own raw return
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

    sector = {}
    sb = ew.get_sb()
    for r in uc.paged(lambda: sb.table("securities").select("ticker,sector").order("id")):
        if r.get("ticker") and r.get("sector"):
            sector[r["ticker"]] = r["sector"]
    names = sorted(set(sector.values()))
    sid = {s: i for i, s in enumerate(names)}
    sec_of = np.array([sid.get(sector.get(t), -1) for t in tickers])
    print("sectors: %d | stocks with a sector: %d of %d | %.0fs" % (len(names), int((sec_of >= 0).sum()), N, time.time() - t0), flush=True)

    def others_bu(k, t, sg):
        """Signed band units of every stock on day t, normalised WITHOUT the focal stock k in the day's mean squared miss (and without the stock itself),
        the same way for a real big-miss day and a placebo day. (With the focal stock left in, its own big miss shrinks every other stock's band unit by about 2%,
        which with fat tails cuts the chance of passing a threshold by about 10%: a mechanical negative dependence that made real days look LESS clustered than arbitrary days.)"""
        out = np.full(N, np.nan)
        if cnt[t] <= 20:
            return out
        zt = z[:, t]
        v = np.isfinite(zt)
        zk2 = zt[k] ** 2 if v[k] else 0.0
        ck = cnt[t] - (1 if v[k] else 0)
        zadj = zt.copy()
        if sec_of[k] >= 0 and v[k] and np.isfinite(Y[k, t]):
            mates = (sec_of == sec_of[k]) & v
            mates[k] = False
            nsec = int(mates.sum()) + 1
            if nsec > 1:
                with np.errstate(invalid="ignore", divide="ignore"):
                    zadj[mates] = zt[mates] + Y[k, t] / ((nsec - 1) * SD[mates, t])      # add back the focal stock's share of each sector-mate's expected return (loading taken as 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            qo_j = (S[t] - np.where(v, zt ** 2, 0.0) - zk2) / (ck - 1)
            out = sg * zadj / np.sqrt(qo_j)
        out[k] = np.nan
        return out

    def count_others(k, t, sg):
        b = others_bu(k, t, sg)
        return int((np.nan_to_num(b, nan=-9.0)[sec_of == sec_of[k]] >= OTHER_BU).sum())

    kk = {t: k for k, t in enumerate(tickers)}
    rows = []
    with open(cand_path) as fh:
        for r in csv.DictReader(fh):
            k, t = kk.get(r["ticker"]), bisect.bisect_left(dl, r["date"])
            if k is None or t >= n or dl[t] != r["date"] or years[t] < TEST_START or sec_of[k] < 0:
                continue
            miss = float(r["miss_pct"])
            if miss == 0.0:
                continue
            rows.append((k, t, 1 if miss > 0 else -1, r["category"], float(r["band_units"])))
    rng = np.random.RandomState(seed)
    year_days = {int(y): np.where(years == y)[0] for y in np.unique(years)}
    real_c, plc_c = [], []
    for k, t, sg, cat, bu_ in rows:
        real_c.append(count_others(k, t, sg))
        yd = year_days[int(years[t])]
        ok = yd[(yd != t) & np.isfinite(buS[k, yd])]
        picks = rng.choice(ok, size=N_PLACEBO, replace=len(ok) < N_PLACEBO)
        plc_c.append([count_others(k, tp, sg) for tp in picks])
    real_c, plc_c = np.array(real_c), np.array(plc_c)
    srow = np.array([sec_of[r[0]] for r in rows])
    thr = np.zeros(len(names))
    for i in range(len(names)):
        m = srow == i
        thr[i] = max(1.0, float(np.percentile(plc_c[m], PCTL))) if m.any() else 1.0
    th_row = thr[srow]
    theme = real_c > th_row
    plc_theme = plc_c > th_row[:, None]
    cats = np.array([r[3] for r in rows])
    bun = np.array([r[4] for r in rows])
    tt = np.array([r[1] for r in rows])
    yy, mm = years[tt], months[tt]
    print("big misses scored: %d | placebo thresholds per sector (stocks above which a cluster counts): %s | %.0fs" % (len(rows), ", ".join("%s %.0f" % (names[i][:14], thr[i]) for i in range(len(names))), time.time() - t0), flush=True)
    print("\nCLUSTER (other stocks in the SAME SECTOR with a big miss the same way that day, >= %.1f band units): placebo mean %.2f | real mean %.2f" % (OTHER_BU, float(plc_c.mean()), float(real_c.mean())))
    print("SECTOR THEME: real %s | placebo %s" % (pct(float(theme.mean())), pct(float(plc_theme.mean()))))

    def cell(mask):
        if mask.sum() < 30:
            return "n/a"
        return "%s vs %s (n %d)" % (pct(float(theme[mask].mean())), pct(float(plc_theme[mask].mean())), int(mask.sum()))
    print("\nSECTOR-THEME SHARE (real vs placebo) BY CATEGORY")
    for c in sorted(set(cats)):
        print("  %-36s %s" % (c, cell(cats == c)))
    print("BY ERA")
    for lab, lo, hi in ERAS:
        print("  %-10s %s" % (lab, cell((yy >= lo) & (yy <= hi))))
    print("BY SIZE OF THE MISS (band units)")
    for lo, hi in ((3, 4), (4, 5), (5, 7), (7, 1e9)):
        print("  %-10s %s" % ("%d to %s" % (lo, "more" if hi > 1e8 else str(hi)), cell((bun >= lo) & (bun < hi))))
    print("BY SECTOR")
    for i in range(len(names)):
        print("  %-26s %s" % (names[i], cell(srow == i)))

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
    print("\nRULE (volume-spike misses, n %d): sector-theme share real %s, placebo %s, excess %+.1f points [%+.1f, %+.1f]" % (int(vs.sum()), pct(float(theme[vs].mean())), pct(float(plc_theme[vs].mean())), 100 * pt, 100 * lo, 100 * hi))
    print("VERDICT (pre-set: excess at least 10 points and the interval above 0): SECTOR THEMES ARE %s" % ("MATERIAL" if (pt >= 0.10 and lo > 0) else "NOT material"))
    print("READING GUIDE (fixed beforehand: 2 points or more with the interval above 0 is evidence of narrow themes; the excess approximates the themed share): %s" % ("MET" if (pt >= 0.02 and lo > 0) else "not met"))

    # overlaps, examples, flags ------------------------------------------------------------------------------------------------------------------------------------
    grp, thm = {}, {}
    for fn, store, col in (("unrecorded_group_flags.csv", grp, "group_move"), ("unrecorded_theme_flags.csv", thm, "theme_day")):
        p = os.path.join(RESULTS, fn)
        if os.path.exists(p):
            for r in csv.DictReader(open(p)):
                store[(r["date"], r["ticker"])] = int(r[col])
    if grp:
        g = np.array([grp.get((dl[r[1]], tickers[r[0]]), -1) for r in rows])
        have = vs & (g >= 0)
        nv = max(int(have.sum()), 1)
        a, b, c_, d_ = have & theme & (g == 1), have & theme & (g == 0), have & ~theme & (g == 1), have & ~theme & (g == 0)
        print("\nOVERLAP WITH PEER GROUP MOVES among the big volume-spike misses (n %d): both %s | sector theme only %s | peer group move only %s | neither %s | UNION %s" % (
            nv, pct(a.sum() / nv), pct(b.sum() / nv), pct(c_.sum() / nv), pct(d_.sum() / nv), pct((a.sum() + b.sum() + c_.sum()) / nv)))
    ex = [i for i in range(len(rows)) if theme[i]]
    r3 = random.Random(seed)
    print("\nTWELVE RANDOM SECTOR-THEME MISSES (ticker, sector, date, size, cluster, the same-sector stocks that moved the same way):")
    for i in r3.sample(ex, min(12, len(ex))):
        k, t, sg = rows[i][0], rows[i][1], rows[i][2]
        vals = others_bu(k, t, sg)
        part = [j for j in np.argsort(-np.nan_to_num(vals, nan=-9.0)) if j != k and sec_of[j] == sec_of[k] and np.isfinite(vals[j]) and vals[j] >= OTHER_BU]
        print("  %-6s %-22s %s  %.1f bu  cluster %2d | %s" % (tickers[k], names[sec_of[k]][:22], dl[t], rows[i][4], real_c[i], " ".join(tickers[j] for j in part[:8])))
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "unrecorded_sector_cluster_flags.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "ticker", "category", "band_units", "sector", "cluster_n", "sector_theme", "participants"])
        for i, (k, t, sg, cat, bu_) in enumerate(rows):
            part = ""
            if theme[i]:
                vals = others_bu(k, t, sg)
                part = " ".join(tickers[j] for j in np.argsort(-np.nan_to_num(vals, nan=-9.0)) if j != k and sec_of[j] == sec_of[k] and np.isfinite(vals[j]) and vals[j] >= OTHER_BU)
            w.writerow([dl[t], tickers[k], cat, "%.2f" % bu_, names[sec_of[k]], int(real_c[i]), int(theme[i]), part])
    print("\nwrote results/unrecorded_sector_cluster_flags.csv | total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
