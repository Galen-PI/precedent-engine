#!/usr/bin/env python3
"""
median_scale_adoption_check.py -- READ-ONLY (local matrices; the database is read for 8-K filings and recorded event days). Writes models/band_median_calibration.json (edges + verdict).
robust_stress_test.py showed that scaling the band by the MEDIAN squared miss (sqrt(median(z^2)/0.45494)) instead of the mean, with ONE edge, holds coverage at about 90% across market-stress
levels on ORDINARY days (89.63-91.08% in all 12 era-by-bin cells) and is about 1.5% tighter than today's per-stress-bin edges. This is the ADOPTION CHECK for every group the card uses.

WHAT IS COMPARED, walk-forward (each test year scored with edges fitted on the years before it, from 2006; test years from 2009), on the six groups of band_calibrate.py:
  ordinary | recorded event, no earnings | earnings window day 0 (no event) | earnings window day +1 (no event) | earnings window + recorded event | Regulation FD (7.01) only
  B  = TODAY'S CARD: the mean-based scale sqrt(mean of the other stocks' squared misses); one edge per group (ordinary: one edge per stress bin).
  C  = the MEDIAN scale; ONE edge per group (ordinary: one edge for all days). The EXISTING multipliers are used unchanged. A multiplier and its edge are collinear (band = edge x multiplier x scale),
       so refitting the edge absorbs any constant mismatch; what is really tested is whether the median day-scale tracks each group's dispersion at least as well as the mean-based one.
  Cp = C with the PREVIOUS day's median scale (descriptive only: what could be known in advance).
Edges are the 90th percentile of |band units| over the prior years. Stress bins (ordinary days): calm < 0.8, normal 0.8-1.2, elevated 1.2-1.5, high >= 1.5, defined by the current mean-based stress.

Usage:   python3 -u scripts/card/median_scale_adoption_check.py
Needs:   data_cache/audit_matrices.npz (gap_audit.py builds it); models/event_band_model.json and models/earnings_band_model.json.

PRE-SET RULE (written before the first run). C is ADOPTABLE if, for EVERY group and EVERY era (2009-2012, 2013-2019, 2020-2026) in which the group has >= 1,000 scored stock-days:
  (1) C's coverage is within 90% +- max(2 points, 3 standard errors), where the standard error is sqrt(0.09 / n) for the n stock-days of that group and era (the size-aware tolerance is chosen because the
      smallest groups have only about 1,500 days per era; I know from band_calibrate.py that earnings + event sat near 88.5% there, so a fixed 88-92% window would be a coin flip for noise reasons), AND
  (2) C's mean 90% interval score (2w + 20 x the overshoot, own-volatility units, w = edge x multiplier x scale) is no more than 1% above B's for a group-era with >= 10,000 days, 3% for fewer, AND
  (3) for the ORDINARY group, C's coverage is within the same tolerance in every stress bin with >= 1,000 days in that era.
All conditions everywhere, or the median scale is NOT adopted (the printout lists every failing cell). Cp is descriptive and carries no verdict.
PREDICTIONS (before the run): ordinary passes (it did in robust_stress_test.py); the three large non-ordinary groups (recorded event, earnings day 0, earnings day +1: about 25,000-36,000 days each) pass both
conditions, with C/B interval score between 0.97 and 1.00; the two small groups (earnings + event, Regulation FD) pass coverage but are the most likely to miss the interval-score tolerance by noise;
overall chance of an ADOPTABLE verdict about 55%; Cp coverage within 1 point of C's for ordinary days.

If ADOPTABLE nothing in the product changes by itself: models/band_median_calibration.json holds the edges, and switching day_card / day_map / the coverage and tail references is a separate step.
"""
import os, sys, time, bisect, json, math, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
OUT_FILE = os.path.join(ROOT, "models", "band_median_calibration.json")
TEST_START = 2006
FIRST_TEST_YEAR = 2009
MED_CONST = 0.45494
MIN_DAYS = 1000
MIN_PRIOR = 500
ERAS = [("2009-2012", 2009, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]
BINS = (("calm (<0.8)", 0.0, 0.8), ("normal (0.8-1.2)", 0.8, 1.2), ("elevated (1.2-1.5)", 1.2, 1.5), ("high (>=1.5)", 1.5, 99.0))


def tol_cov(n):
    return max(0.02, 3.0 * math.sqrt(0.09 / max(n, 1)))


def tol_is(n):
    return 0.01 if n >= 10000 else 0.03


def paged(make_query):
    rows, off = [], 0
    while True:
        page = make_query().range(off, off + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return rows


def main():
    t0 = time.time()
    if not os.path.exists(CACHE_FILE):
        sys.exit("Run gap_audit.py first: it builds %s." % CACHE_FILE)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E, SD = d["dates"], d["ids"], d["E"], d["SD"]
    N, n = E.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    SDf, Ef = SD.astype(np.float64), E.astype(np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        Zsq = (Ef / SDf) ** 2
    valid = ~np.isnan(Zsq)
    S = np.nansum(Zsq, axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        q_all = S / np.maximum(cnt, 1)
    med_t = np.nanmedian(np.where(cnt[None, :] > 20, Zsq, np.nan), axis=0)
    s_day = np.sqrt(med_t / MED_CONST)
    s_prev_day = np.concatenate([[np.nan], s_day[:-1]])
    stress_day = np.sqrt(q_all)
    s_cur = np.sqrt(qo)
    ones = np.ones((N, 1))
    s_rob, s_prev = s_day[None, :] * ones, s_prev_day[None, :] * ones

    band_model = dc.load_json("event_band_model.json")
    earn_model = dc.load_json("earnings_band_model.json")
    if earn_model is None:
        sys.exit("models/earnings_band_model.json not found.")
    mm = earn_model["multipliers_vs_ordinary_day"]
    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids.tolist())}
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids.tolist()))
    EV = np.zeros((N, n), dtype=bool)
    MULT = np.ones((N, n))
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is None:
            continue
        for t, (pt, off, size, timing) in days.items():
            EV[k, t] = True
            m, _ = dc.band_multiplier(band_model, pt, size, timing, off)
            MULT[k, t] = m if m else 1.0
    EA0 = np.zeros((N, n), dtype=bool)
    EA1 = np.zeros((N, n), dtype=bool)
    F701 = np.zeros((N, n), dtype=bool)
    for r in paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is None:
            continue
        its = dc.parse_items(r.get("item_codes"))
        i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
        if i >= n:
            continue
        if "2.02" in its:
            EA0[k, i] = True
            if i + 1 < n:
                EA1[k, i + 1] = True
        elif "7.01" in its:
            F701[k, i] = True
            if i + 1 < n:
                F701[k, i + 1] = True
    EA1 &= ~EA0
    EA = EA0 | EA1
    both = EA & EV
    MULT[EA0 & ~EV] = mm["earnings_day0"]
    MULT[EA1 & ~EV] = mm["earnings_day1"]
    MULT[both] = mm["event_and_earnings"]
    only701 = F701 & ~EA & ~EV
    MULT[only701] = mm["item_7_01"]
    with np.errstate(invalid="ignore", divide="ignore"):
        absy = np.abs(Ef) / SDf
        bu_B = absy / (s_cur * MULT)
        bu_C = absy / (s_rob * MULT)
        bu_Cp = absy / (s_prev * MULT)
    ok = (valid & (cnt[None, :] > 20) & np.isfinite(qo) & (qo > 0) & (med_t > 0)[None, :] & np.isfinite(bu_B) & np.isfinite(bu_C) & (years >= TEST_START)[None, :])
    print("matrices: %d stocks x %d days | %.0fs" % (N, n, time.time() - t0), flush=True)

    bin_of = np.full(n, -1)
    for b, (_, lo, hi) in enumerate(BINS):
        bin_of[(stress_day >= lo) & (stress_day < hi)] = b
    BIN = bin_of[None, :] * np.ones((N, 1), dtype=int)

    groups = [("ordinary", ok & ~EV & ~EA & ~only701), ("recorded event, no earnings", ok & EV & ~EA),
              ("earnings window, day 0 (no event)", ok & EA0 & ~EV), ("earnings window, day +1 (no event)", ok & EA1 & ~EV),
              ("earnings window + recorded event", ok & both), ("Regulation FD (7.01) only", ok & only701)]
    Ys = [Y for Y in sorted(set(years.tolist())) if Y >= FIRST_TEST_YEAR]
    tally = defaultdict(lambda: np.zeros(8))      # [n, hit_B, hit_C, n_p, hit_Cp, IS_B, IS_C, 0]
    bin_tally = defaultdict(lambda: np.zeros(3))  # [n, hit_B, hit_C]   (ordinary only)
    for gname, gmask in groups:
        for Y in Ys:
            prior = gmask & ((years >= TEST_START) & (years < Y))[None, :]
            if int(prior.sum()) < MIN_PRIOR:
                continue
            cur = gmask & (years == Y)[None, :]
            if not cur.any():
                continue
            era = next(e[0] for e in ERAS if e[1] <= Y <= e[2])
            eC = float(np.quantile(bu_C[prior], 0.90))
            pc = prior & np.isfinite(bu_Cp)
            eCp = float(np.quantile(bu_Cp[pc], 0.90)) if int(pc.sum()) >= MIN_PRIOR else None
            eB_all = float(np.quantile(bu_B[prior], 0.90))
            if gname == "ordinary":
                eB_bins = np.array([float(np.quantile(bu_B[prior & (BIN == b)], 0.90)) if int((prior & (BIN == b)).sum()) >= 2000 else eB_all for b in range(len(BINS))])
                bc = BIN[cur]
                eBc = np.where(bc >= 0, eB_bins[np.maximum(bc, 0)], eB_all)
            else:
                eBc = eB_all
            y, sc, sr, mu = absy[cur], s_cur[cur], s_rob[cur], MULT[cur]
            wB, wC = eBc * sc * mu, eC * sr * mu
            inB, inC = bu_B[cur] <= eBc, bu_C[cur] <= eC
            tt = tally[(gname, era)]
            tt[0] += y.size
            tt[1] += float(inB.sum())
            tt[2] += float(inC.sum())
            cp = bu_Cp[cur]
            fin = np.isfinite(cp)
            if eCp is not None and fin.any():
                tt[3] += float(fin.sum())
                tt[4] += float((cp[fin] <= eCp).sum())
            tt[5] += float((2 * wB + 20 * np.maximum(y - wB, 0.0)).sum())
            tt[6] += float((2 * wC + 20 * np.maximum(y - wC, 0.0)).sum())
            if gname == "ordinary":
                for b in range(len(BINS)):
                    mb = bc == b
                    if mb.any():
                        bt = bin_tally[(era, b)]
                        bt[0] += float(mb.sum())
                        bt[1] += float(inB[mb].sum())
                        bt[2] += float(inC[mb].sum())

    print("\nOUT-OF-SAMPLE, BY GROUP AND ERA (target coverage 90%; tolerance = max(2 points, 3 standard errors) for C)")
    print("  %-38s %-10s %9s %6s | %8s %8s %8s | %8s  %s" % ("group", "era", "days", "tol", "B cov", "C cov", "Cp cov", "C/B IS", "verdict"))
    fails = []
    for gname, _ in groups:
        for e in ERAS:
            tt = tally.get((gname, e[0]))
            if tt is None or tt[0] < MIN_DAYS:
                print("  %-38s %-10s %9s" % (gname, e[0], "n/a" if tt is None else "%d (<%d: not judged)" % (tt[0], MIN_DAYS)))
                continue
            nn = tt[0]
            covB, covC = tt[1] / nn, tt[2] / nn
            covCp = (tt[4] / tt[3]) if tt[3] > 0 else float("nan")
            ratio = tt[6] / tt[5]
            tc, ti = tol_cov(nn), tol_is(nn)
            bad = []
            if abs(covC - 0.90) > tc:
                bad.append("coverage %.2f%% outside 90%% +- %.2f" % (100 * covC, 100 * tc))
            if ratio > 1.0 + ti:
                bad.append("interval score C/B %.4f > %.2f" % (ratio, 1.0 + ti))
            if bad:
                fails.append("%s, %s: %s" % (gname, e[0], "; ".join(bad)))
            print("  %-38s %-10s %9d %5.1f%% | %7.2f%% %7.2f%% %7.2f%% | %8.4f  %s" % (gname, e[0], nn, 100 * tc, 100 * covB, 100 * covC, 100 * covCp, ratio, "ok" if not bad else "FAILS"))

    print("\nORDINARY DAYS BY STRESS BIN (condition 3; B = today's per-bin edges, C = one edge under the median scale)")
    print("  %-20s %-10s %9s %6s | %8s %8s  %s" % ("stress bin", "era", "days", "tol", "B cov", "C cov", "verdict"))
    for b, (lab, lo, hi) in enumerate(BINS):
        for e in ERAS:
            bt = bin_tally.get((e[0], b))
            if bt is None or bt[0] < MIN_DAYS:
                continue
            tc = tol_cov(bt[0])
            covC = bt[2] / bt[0]
            bad = abs(covC - 0.90) > tc
            if bad:
                fails.append("ordinary, stress bin %s, %s: coverage %.2f%% outside 90%% +- %.2f" % (lab, e[0], 100 * covC, 100 * tc))
            print("  %-20s %-10s %9d %5.1f%% | %7.2f%% %7.2f%%  %s" % (lab, e[0], bt[0], 100 * tc, 100 * bt[1] / bt[0], 100 * covC, "ok" if not bad else "FAILS"))

    # edges fitted on ALL years for the card (only meaningful if the verdict is ADOPTABLE)
    edges = {}
    for gname, gmask in groups:
        if int(gmask.sum()) >= MIN_PRIOR:
            edges[gname] = float(np.quantile(bu_C[gmask], 0.90))
    print("\nEDGES UNDER THE MEDIAN SCALE, fitted on all years (one number per group; band = edge x SD x median-scale x multiplier):")
    for k, v in edges.items():
        print("  %-38s %.3f" % (k, v))
    adopt = not fails
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w") as fh:
        json.dump({"what": "Edges for the median-scale band (90%% coverage), one per group; band = edge x SD x sqrt(median(z^2)/%.5f) x multiplier (existing multipliers unchanged)." % MED_CONST,
                   "scale": {"type": "median_squared_miss", "const": MED_CONST}, "edge_90": edges, "verdict_adoptable": adopt, "failing_cells": fails,
                   "caveats": ["Fitted on all years; the walk-forward table is the honest check.", "An explanation band: it uses the same day's cross-section.", "Not used by the card until a separate switch."]}, fh, indent=1)
    print()
    if adopt:
        print("VERDICT under the pre-set rule: the median scale is ADOPTABLE for every group.")
    else:
        print("VERDICT under the pre-set rule: the median scale is NOT adopted. Failing cells:")
        for f in fails:
            print("  - " + f)
    print("saved %s | total %.0fs" % (OUT_FILE, time.time() - t0))


if __name__ == "__main__":
    main()
