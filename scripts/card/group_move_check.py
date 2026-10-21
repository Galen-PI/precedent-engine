#!/usr/bin/env python3
"""
group_move_check.py -- READ-ONLY (local matrices and results/unrecorded_candidates.csv; no database). Writes results/unrecorded_group_flags.csv and results/unrecorded_reading_sample_groups_SEED.csv.
THE QUESTION. About 12,700 big ordinary misses (>= 3.0 band units, no own recorded event or earnings window, not an aftershock) carry no recorded explanation, and nothing we hold (our own other 8-Ks, calendar flow days, pre-event
windows) accounts for more than a few percent of them. The card's sector factor averages 11 sectors, so news that moves a SUB-INDUSTRY (semiconductor equipment, regional banks, a drug class, a commodity) appears as a big
miss in several related stocks on the same day. If that is common, a big miss is not a stock-specific unrecorded event at all, and the reading effort belongs elsewhere.
METHOD. PEERS: for each stock, every 63 trading days (from day 250), the 10 stocks with the highest correlation of daily standardized misses (miss / own spread, clipped at +-4) over the PREVIOUS 250 days, at least 150 days in
common: no look-ahead, no industry codes. For each big miss (the CSV's rows from 2006 on, with the sign of its miss) the peers' SIGNED band units that day are multiplied by the miss's sign; a peer MOVED WITH it if that is at least
1.5 band units. SUPPORT = how many of the 10 peers moved with it (at least 6 peers must have a value). A GROUP MOVE = support of at least 4. PLACEBO: the same measure with 10 random stocks (not the stock itself, not its peers) that have a
value that day, three draws per miss: random stocks share the market day but not a sub-industry. The EXCESS of real peers over placebo is the group-news share beyond chance (it still includes anything a shared sub-industry
factor would capture, which is the point: it is not stock-specific).
Reported: the support distribution (real vs placebo); the GROUP MOVE share by category (volume spike + article spike, volume spike only, article spike only, quiet, aftershocks), by era and by the size of the miss; the mean peer move;
twelve random GROUP MOVE examples with the peers that moved; and the READING FRAME: how many big volume-spike misses are group moves and how many are NOT (support of 0 or 1).
PRE-SET RULE: GROUP NEWS IS MATERIAL if, among the big volume-spike misses ('volume spike only' plus 'volume spike + article spike'), the real-peer GROUP MOVE share exceeds the placebo share by at least 10 points and the 95%
interval of that excess (resampling calendar MONTHS, 500 resamples, because misses cluster in time) is above 0. The category rows, eras and sizes are descriptive.
PREDICTIONS (before the run): placebo GROUP MOVE share 0.2-1.5%; real-peer share among big volume-spike misses 14-30% (excess 12-28 points, so GROUP NEWS IS MATERIAL, probability about 65%); the quiet misses lower (6-14%); the share rises
with the size of the miss (3-4 band units below 6-7 and above); no strong trend across eras (within 6 points); mean signed peer move about +0.4 to +0.9 band units for real peers and about 0.0-0.15 for placebo.
Usage:   python3 -u scripts/card/group_move_check.py [seed]       Needs: data_cache/audit_matrices.npz and results/unrecorded_candidates.csv (unrecorded_candidates.py writes it).
"""
import os, sys, csv, time, random, bisect, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
RESULTS = os.path.join(ROOT, "results")
TEST_START = 2006
WINDOW, STEP, N_PEERS, MIN_COMMON = 250, 63, 10, 150
MOVE_BU, GROUP_MIN, MIN_PEERS_VALID = 1.5, 4, 6
N_PLACEBO_DRAWS = 3
N_BOOT = 500
SEED = 20261021
SAMPLE_FROM = "2024-01-01"
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
        buS = z / np.sqrt(qo)                                      # signed band units
    buS[~((cnt[None, :] > 20) & np.isfinite(buS))] = np.nan
    zc = np.clip(z, -4.0, 4.0)

    # peers every STEP days from day WINDOW ----------------------------------------------------------------------------------------------------------------------
    starts = list(range(WINDOW, n, STEP))
    peers = np.full((len(starts), N, N_PEERS), -1, dtype=np.int32)
    for qi, q0 in enumerate(starts):
        W = zc[:, q0 - WINDOW:q0]
        Vm = np.isfinite(W)
        nv = Vm.sum(axis=1)
        mu = np.where(nv > 0, np.nansum(W, axis=1) / np.maximum(nv, 1), 0.0)
        sd = np.sqrt(np.where(nv > 1, np.nansum((W - mu[:, None]) ** 2, axis=1) / np.maximum(nv - 1, 1), np.nan))
        Zw = np.where(Vm, (W - mu[:, None]) / sd[:, None], 0.0)
        Zw[~np.isfinite(Zw)] = 0.0
        common = Vm.astype(np.float64) @ Vm.astype(np.float64).T
        C = (Zw @ Zw.T) / np.maximum(common, 1.0)
        C[common < MIN_COMMON] = -9.0
        np.fill_diagonal(C, -9.0)
        okrow = nv >= 200
        top = np.argsort(-C, axis=1)[:, :N_PEERS]
        for k in range(N):
            if okrow[k] and C[k, top[k]].min() > -9.0:
                peers[qi, k] = top[k]
    print("peer sets built for %d quarters x %d stocks | %.0fs" % (len(starts), N, time.time() - t0), flush=True)

    kk = {t: k for k, t in enumerate(tickers)}
    rows = []
    with open(cand_path) as fh:
        for r in csv.DictReader(fh):
            k, t = kk.get(r["ticker"]), bisect.bisect_left(dl, r["date"])
            if k is None or t >= n or dl[t] != r["date"] or t < WINDOW or years[t] < TEST_START:
                continue
            miss = float(r["miss_pct"])
            if miss == 0.0:
                continue
            rows.append((k, t, 1.0 if miss > 0 else -1.0, r["category"], float(r["band_units"]), r["ticker"]))
    rng = np.random.RandomState(seed)
    out = []                           # k, t, category, bu, support, mean_peer, placebo_support list, placebo_mean list, moved peers
    for k, t, sgn, cat, bunit, tk in rows:
        qi = (t - WINDOW) // STEP
        pj = peers[qi, k]
        if pj[0] < 0:
            continue
        v = sgn * buS[pj, t]
        fin = np.isfinite(v)
        if fin.sum() < MIN_PEERS_VALID:
            continue
        support = int((v[fin] >= MOVE_BU).sum())
        moved = [tickers[j] for j, x in zip(pj, v) if np.isfinite(x) and x >= MOVE_BU]
        pool = np.flatnonzero(np.isfinite(buS[:, t]))
        pool = pool[(pool != k) & ~np.isin(pool, pj)]
        ps, pm = [], []
        for _ in range(N_PLACEBO_DRAWS):
            pick = rng.choice(pool, size=N_PEERS, replace=False)
            pv = sgn * buS[pick, t]
            ps.append(int((pv >= MOVE_BU).sum()))
            pm.append(float(np.nanmean(pv)))
        out.append((k, t, cat, bunit, support, float(np.nanmean(v)), ps, pm, moved))
    print("big misses scored: %d of %d rows | %.0fs" % (len(out), len(rows), time.time() - t0), flush=True)

    sup = np.array([o[4] for o in out])
    cats = np.array([o[2] for o in out])
    bun = np.array([o[3] for o in out])
    tt = np.array([o[1] for o in out])
    yy = years[tt]
    mm = months[tt]
    real_g = sup >= GROUP_MIN
    plc_s = np.array([o[6] for o in out])                    # n x draws
    plc_g = (plc_s >= GROUP_MIN)
    mean_real = np.array([o[5] for o in out])
    mean_plc = np.array([np.mean(o[7]) for o in out])

    print("\nSUPPORT DISTRIBUTION (how many of the 10 peers moved at least %.1f band units the same way as the big miss)" % MOVE_BU)
    print("  support    " + " ".join("%6d" % j for j in range(N_PEERS + 1)))
    print("  real peers " + " ".join("%5.1f%%" % (100 * np.mean(sup == j)) for j in range(N_PEERS + 1)))
    print("  placebo    " + " ".join("%5.1f%%" % (100 * np.mean(plc_s == j)) for j in range(N_PEERS + 1)))
    print("  GROUP MOVE (support >= %d): real peers %s | placebo %s | mean signed peer move: real %+.2f, placebo %+.2f band units" % (GROUP_MIN, pct(float(real_g.mean())), pct(float(plc_g.mean())), float(np.nanmean(mean_real)), float(np.nanmean(mean_plc))))

    def cell(mask):
        if mask.sum() < 30:
            return "n/a"
        return "%s vs %s (n %d)" % (pct(float(real_g[mask].mean())), pct(float(plc_g[mask].mean())), int(mask.sum()))
    print("\nGROUP MOVE SHARE (real peers vs placebo) BY CATEGORY")
    for c in sorted(set(cats)):
        print("  %-36s %s" % (c, cell(cats == c)))
    print("BY ERA")
    for lab, lo, hi in ERAS:
        print("  %-10s %s" % (lab, cell((yy >= lo) & (yy <= hi))))
    print("BY SIZE OF THE MISS (band units)")
    for lo, hi in ((3, 4), (4, 5), (5, 7), (7, 1e9)):
        print("  %-10s %s" % ("%d to %s" % (lo, "more" if hi > 1e8 else str(hi)), cell((bun >= lo) & (bun < hi))))

    # pre-set rule: volume-spike misses, month-block bootstrap of the excess -----------------------------------------------------------------------------------------
    vs = np.isin(cats, VOLUME_CATS)
    def per_month(mask):
        return np.bincount(mm[mask], minlength=M).astype(float)
    tot, hit_r, hit_p = per_month(vs), per_month(vs & real_g), np.array([np.bincount(mm[vs], weights=plc_g[vs][:, j].astype(float), minlength=M) for j in range(N_PLACEBO_DRAWS)]).mean(axis=0)
    def excess(w):
        return ((w @ hit_r) - (w @ hit_p)) / max(w @ tot, 1.0)
    pt = excess(np.ones(M))
    live = np.where(tot > 0)[0]
    brng = np.random.RandomState(seed + 1)
    boot = [excess(np.bincount(brng.choice(live, size=len(live)), minlength=M).astype(float)) for _ in range(N_BOOT)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print("\nRULE (volume-spike misses, n %d): real-peer GROUP MOVE %s, placebo %s, excess %+.1f points [%+.1f, %+.1f]" % (int(vs.sum()), pct(float(real_g[vs].mean())), pct(float(plc_g[vs].mean())), 100 * pt, 100 * lo, 100 * hi))
    print("VERDICT (pre-set: excess at least 10 points and the interval above 0): GROUP NEWS IS %s" % ("MATERIAL" if (pt >= 0.10 and lo > 0) else "NOT material"))

    # examples and the reading frame ---------------------------------------------------------------------------------------------------------------------------
    ex = [i for i in range(len(out)) if real_g[i]]
    r3 = random.Random(seed)
    print("\nTWELVE RANDOM GROUP MOVES (ticker, date, size, support, the peers that moved):")
    for i in r3.sample(ex, min(12, len(ex))):
        o = out[i]
        print("  %-6s %s  %.1f band units  support %d  %s" % (tickers[o[0]], dl[o[1]], o[3], o[4], " ".join(o[8])))
    idio = vs & (sup <= 1)
    print("\nREADING FRAME: big volume-spike misses %d | group moves (support >= %d) %d (%s) | STOCK-SPECIFIC (support 0 or 1) %d (%s) | in between %d" % (
        int(vs.sum()), GROUP_MIN, int((vs & real_g).sum()), pct(float((vs & real_g).sum() / max(vs.sum(), 1))), int(idio.sum()), pct(float(idio.sum() / max(vs.sum(), 1))), int((vs & ~real_g & ~idio).sum())))

    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "unrecorded_group_flags.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "ticker", "category", "band_units", "support", "mean_peer_move", "placebo_support_draw1", "group_move", "peers_moved"])
        for o in out:
            w.writerow([dl[o[1]], tickers[o[0]], o[2], "%.2f" % o[3], o[4], "%.2f" % o[5], o[6][0], int(o[4] >= GROUP_MIN), " ".join(o[8])])
    first = bisect.bisect_left(dl, SAMPLE_FROM)
    pools = {"volume spike, STOCK-SPECIFIC (support 0-1)": [i for i in range(len(out)) if idio[i] and out[i][1] >= first],
             "volume spike, GROUP MOVE (support >= %d)" % GROUP_MIN: [i for i in range(len(out)) if vs[i] and real_g[i] and out[i][1] >= first],
             "quiet, STOCK-SPECIFIC (support 0-1)": [i for i in range(len(out)) if cats[i] == "quiet (neither)" and sup[i] <= 1 and out[i][1] >= first]}
    rs = random.Random(seed)
    path_s = os.path.join(RESULTS, "unrecorded_reading_sample_groups_%d.csv" % seed)
    with open(path_s, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stratum", "date", "ticker", "band_units", "support", "peers_moved", "found (yes/no)", "category", "what_happened_and_source"])
        for lab, pool in pools.items():
            pick = sorted(rs.sample(pool, min(12, len(pool))), key=lambda i: (out[i][1], out[i][0]))
            print("  new reading sample, %-48s available %5d | sampled %d" % (lab, len(pool), len(pick)))
            for i in pick:
                o = out[i]
                w.writerow([lab, dl[o[1]], tickers[o[0]], "%.2f" % o[3], o[4], " ".join(o[8]), "", "", ""])
    print("wrote results/unrecorded_group_flags.csv and %s | total %.0fs" % (os.path.basename(path_s), time.time() - t0))


if __name__ == "__main__":
    main()
