#!/usr/bin/env python3
"""
earnings_timing_diagnostics.py -- READ-ONLY (matrices, the OHLC cache, the database for 8-K filings). Writes nothing. A companion of earnings_timing_check.py, which read 85.0% leave-one-out habit agreement
against its 90% threshold (METHOD NOT VALID), with stable reporters at 91-100% and TSLA at 51%, JPM at 85%. These diagnostics do NOT change that verdict; they ask why. Three explanations predict different patterns:
  1. NOISE AT WEAK GAPS: an event is classifiable once either day has a gap of 2 own-sd, but a weak reaction is easily beaten by a noise gap on the other day. Agreement should CLIMB with gap strength.
  2. MISDATED FILINGS: if a company files its 8-K a day or more after the release, the reaction gap sits on days before i (the filing day) and neither i nor i+1 holds it. The day of the LARGEST gap among days i-2..i+3
     should then be spread away from i and i+1 for those stocks, and the same measure on random placebo days (about 33% on i or i+1 by chance) is the reference.
  3. UNSTABLE HABITS: agreement stays low even at large gaps, across many stocks.
Reported: (A) leave-one-out agreement by gap-strength tier of the event itself (the larger of its two gaps in own sd: 2-3, 3-5, 5 or more), gap method and close-to-close method on the same events; (B) agreement by year;
(C) ALIGNMENT: the share of earnings events whose largest gap among days i-2..i+3 falls on i or on i+1 (vs placebo days of the same stocks and years), its distribution over the six offsets, and per stock the aligned
share, with the twelve least aligned stocks (at least 20 events) and their most common offset, and the fourteen recalled tickers.
PRE-SET READING (written before the first run): NOISE AT WEAK GAPS holds if agreement in the 5-or-more tier is at least 95% and the 2-3 tier is at most 80%. A DATING PROBLEM holds if fewer than 60% of all earnings events
have their largest gap on i or i+1 AND at least 15 stocks (with at least 20 events) have an aligned share below 50%. UNSTABLE HABITS holds if agreement is below 92% in every tier. The three are not exclusive.
PREDICTIONS (before the run): agreement 70-80% in the 2-3 tier, 85-92% in the 3-5 tier, 93-99% in the 5-or-more tier; agreement 80% or more in every year, the earliest years lowest; all events aligned 60-75% against about 33%
for placebo days; TSLA aligned below 50%; at least 10 stocks below 50% aligned; NOISE AT WEAK GAPS holds (probability about 65%) and a DATING PROBLEM holds for a minority of stocks only (fewer than 15, so the dating-problem
reading as defined does NOT hold overall).
Usage:   python3 -u scripts/card/earnings_timing_diagnostics.py       Needs: data_cache/audit_matrices.npz, data_cache/ohlc, the database.
"""
import os, sys, time, bisect, warnings
from collections import defaultdict, Counter
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc
import earnings_timing_check as etc

CACHE_FILE = uc.CACHE_FILE
TEST_START = etc.TEST_START
GAP_WIN, GAP_MIN, MAX_GAP, CLASSIFY_Z, MIN_OTHERS = etc.GAP_WIN, etc.GAP_MIN, etc.MAX_GAP, etc.CLASSIFY_Z, etc.MIN_OTHERS
BASE_NEAR = etc.BASE_NEAR
RECALL = etc.RECALL
OFF = list(range(-2, 4))
TIERS = [(2.0, 3.0), (3.0, 5.0), (5.0, 1e9)]
SEED = 20261021


def pct(x):
    return "%5.1f%%" % (100.0 * x) if np.isfinite(x) else "  n/a "


def main():
    t0 = time.time()
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, tickers, E, SD = d["dates"], d["ids"].tolist(), [str(x) for x in d["tickers"]], d["E"], d["SD"]
    N, n = E.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    with np.errstate(invalid="ignore", divide="ignore"):
        Zsq = (E.astype(np.float64) / SD.astype(np.float64)) ** 2
    valid = np.isfinite(Zsq)
    S = np.where(valid, Zsq, 0.0).sum(axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        bu = np.sqrt(Zsq / qo)
    bu[~((cnt[None, :] > 20) & np.isfinite(bu))] = np.nan

    O, C, have = etc.load_ohlc(ids, dl)
    G = np.full((N, n), np.nan)
    G[:, 1:] = O[:, 1:] / C[:, :-1] - 1.0
    G[np.abs(G) > MAX_GAP] = np.nan
    V = np.isfinite(G)
    X = np.where(V, G, 0.0)
    z = np.zeros((N, 1))
    c1, c2, cc = (np.concatenate([z, np.cumsum(a_, axis=1)], axis=1) for a_ in (X, X * X, V))
    S1, S2, Cn = c1[:, GAP_WIN:n] - c1[:, :n - GAP_WIN], c2[:, GAP_WIN:n] - c2[:, :n - GAP_WIN], cc[:, GAP_WIN:n] - cc[:, :n - GAP_WIN]
    with np.errstate(invalid="ignore", divide="ignore"):
        var = (S2 - S1 * S1 / Cn) / (Cn - 1)
    GSD = np.full((N, n), np.nan)
    GSD[:, GAP_WIN:] = np.where(Cn >= GAP_MIN, np.sqrt(np.maximum(var, 0.0)), np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        ZG = np.abs(G) / GSD

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    raw = defaultdict(list)
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is None or "2.02" not in dc.parse_items(r.get("item_codes")):
            continue
        i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
        if i < n:
            raw[k].append(i)
    ev = []
    near = np.zeros((N, n), dtype=bool)
    for k, lst in raw.items():
        keep = []
        for i in sorted(lst):
            if not keep or i - keep[-1] >= 20:
                keep.append(i)
        for i in keep:
            near[k, max(i + BASE_NEAR[0], 0): i + BASE_NEAR[1] + 1] = True
            if i >= GAP_WIN + 1 and i + 3 < n and years[i] >= TEST_START:
                ev.append((k, i))
    ek, ei = np.array([e[0] for e in ev]), np.array([e[1] for e in ev])
    ey = years[ei]
    Zoff = np.array([[ZG[k, i + o] for o in OFF] for k, i in ev])
    a, b = Zoff[:, 2], Zoff[:, 3]
    have_gap = np.isfinite(a) & np.isfinite(b)
    zmax = np.maximum(np.nan_to_num(a), np.nan_to_num(b))
    cls = have_gap & (zmax >= CLASSIFY_Z)
    tim_gap = (np.nan_to_num(b) > np.nan_to_num(a)).astype(int)
    tim_bu = (np.nan_to_num(np.abs(bu[ek, ei + 1])) > np.nan_to_num(np.abs(bu[ek, ei]))).astype(int)
    print("earnings events from %d: %d | classifiable %d | %.0fs" % (TEST_START, len(ev), int(cls.sum()), time.time() - t0), flush=True)

    by_k = defaultdict(list)
    for e in range(len(ev)):
        if cls[e]:
            by_k[ek[e]].append(e)
    ag = np.full(len(ev), -1)
    ab = np.full(len(ev), -1)
    for k, lst in by_k.items():
        if len(lst) - 1 < MIN_OTHERS:
            continue
        tg = np.array([tim_gap[e] for e in lst])
        tb = np.array([tim_bu[e] for e in lst])
        for j, e in enumerate(lst):
            pg, pb = np.delete(tg, j).mean(), np.delete(tb, j).mean()
            ag[e] = int(tg[j] == (1 if pg >= 0.5 else 0))
            ab[e] = int(tb[j] == (1 if pb >= 0.5 else 0))
    have_h = ag >= 0

    print("\n(A) LEAVE-ONE-OUT AGREEMENT BY THE EVENT'S OWN GAP STRENGTH (the larger of its two gaps, in own overnight-gap sd)")
    print("  %-14s %7s | %12s %20s" % ("gap strength", "events", "gap method", "close-to-close method"))
    tier_res = []
    for lo, hi in TIERS:
        m = have_h & (zmax >= lo) & (zmax < hi)
        if m.any():
            tier_res.append((lo, hi, float(ag[m].mean()), int(m.sum())))
            print("  %-14s %7d | %12s %20s" % ("%.0f to %s" % (lo, "more" if hi > 1e8 else "%.0f" % hi), int(m.sum()), pct(float(ag[m].mean())), pct(float(ab[m].mean()))))
    print("  %-14s %7d | %12s %20s" % ("all", int(have_h.sum()), pct(float(ag[have_h].mean())), pct(float(ab[have_h].mean()))))

    print("\n(B) AGREEMENT BY YEAR (gap method)")
    line = []
    for y in range(TEST_START, int(years.max()) + 1):
        m = have_h & (ey == y)
        if m.sum() >= 100:
            line.append("%d %.0f%% (%d)" % (y, 100 * ag[m].mean(), m.sum()))
    print("  " + " | ".join(line))

    print("\n(C) ALIGNMENT: the day of the LARGEST overnight gap among days i-2..i+3 (i = the filing day)")
    prof = np.isfinite(Zoff).sum(axis=1) >= 5
    arg = np.argmax(np.nan_to_num(Zoff, nan=-1.0), axis=1)
    aligned = (arg == 2) | (arg == 3)
    rng = np.random.RandomState(SEED)
    fin = np.isfinite(ZG)
    # six consecutive finite values at days t-2..t+3
    W = np.zeros((N, n), dtype=np.int32)
    for o in OFF:
        sh = np.zeros((N, n), dtype=bool)
        if o >= 0:
            sh[:, : n - o] = fin[:, o:]
        else:
            sh[:, -o:] = fin[:, : n + o]
        W += sh
    cand_ok = (W == 6) & ~near
    cand_ok[:, : GAP_WIN + 1] = False
    cand_ok &= (years >= TEST_START)[None, :]
    plc_arg = []
    for e in np.where(prof)[0]:
        k, y = ek[e], ey[e]
        ys, ye = int(np.searchsorted(years, y, side="left")), int(np.searchsorted(years, y, side="right"))
        c = np.flatnonzero(cand_ok[k, ys:ye])
        if len(c):
            t = ys + int(c[rng.randint(len(c))])
            plc_arg.append(int(np.argmax(np.nan_to_num(np.array([ZG[k, t + o] for o in OFF]), nan=-1.0))))
    plc_arg = np.array(plc_arg)
    print("  events with a profile: %d | largest gap on i or on i+1: %s | placebo days of the same stocks and years (n %d): %s" % (int(prof.sum()), pct(float(aligned[prof].mean())), len(plc_arg), pct(float(np.mean((plc_arg == 2) | (plc_arg == 3))))))
    dist = [float(np.mean(arg[prof] == j)) for j in range(6)]
    pdist = [float(np.mean(plc_arg == j)) for j in range(6)]
    print("  offsets      " + " ".join("%7s" % ("%+d" % o) for o in OFF))
    print("  earnings     " + " ".join("%6.1f%%" % (100 * x) for x in dist))
    print("  placebo      " + " ".join("%6.1f%%" % (100 * x) for x in pdist))

    per = defaultdict(list)
    for e in np.where(prof)[0]:
        per[ek[e]].append(e)
    rows = []
    for k, lst in per.items():
        if len(lst) >= 20:
            al = float(np.mean(aligned[lst]))
            mode = Counter(OFF[arg[e]] for e in lst).most_common(1)[0]
            rows.append((al, tickers[k], len(lst), mode[0], mode[1] / len(lst)))
    rows.sort()
    n_low = sum(1 for r in rows if r[0] < 0.5)
    print("\n  stocks with at least 20 events: %d | aligned share below 50%%: %d | below 40%%: %d" % (len(rows), n_low, sum(1 for r in rows if r[0] < 0.4)))
    print("  the twelve least aligned (ticker, events, aligned share, most common offset of the largest gap and its share):")
    for al, t, m, mo, ms in rows[:12]:
        print("    %-6s %3d events | aligned %s | most common offset %+d (%s)" % (t, m, pct(al), mo, pct(ms)))
    print("  the fourteen recalled tickers (share of events with the largest gap at each offset %s):" % " ".join("%+d" % o for o in OFF))
    kk = {t: k for k, t in enumerate(tickers)}
    for t in RECALL:
        k = kk.get(t)
        lst = per.get(k, []) if k is not None else []
        if len(lst) >= 8:
            print("    %-6s %3d events | %s" % (t, len(lst), " ".join("%4.0f%%" % (100 * np.mean([arg[e] == j for e in lst])) for j in range(6))))

    print("\nREADING (pre-set rules)")
    t5 = [r for r in tier_res if r[0] == 5.0]
    t23 = [r for r in tier_res if r[0] == 2.0]
    noise = bool(t5 and t23 and t5[0][2] >= 0.95 and t23[0][2] <= 0.80)
    dating = bool(float(aligned[prof].mean()) < 0.60 and n_low >= 15)
    unstable = bool(tier_res and all(r[2] < 0.92 for r in tier_res))
    print("  NOISE AT WEAK GAPS: %s (5-or-more tier %s, 2-3 tier %s; thresholds 95%% and 80%%)" % ("HOLDS" if noise else "does not hold", pct(t5[0][2]) if t5 else "n/a", pct(t23[0][2]) if t23 else "n/a"))
    print("  DATING PROBLEM:     %s (aligned %s vs 60%%; %d stocks below 50%% vs 15)" % ("HOLDS" if dating else "does not hold", pct(float(aligned[prof].mean())), n_low))
    print("  UNSTABLE HABITS:    %s (every tier below 92%%)" % ("HOLDS" if unstable else "does not hold"))
    print("\ntotal %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
