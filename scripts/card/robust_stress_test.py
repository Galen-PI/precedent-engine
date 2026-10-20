#!/usr/bin/env python3
"""
robust_stress_test.py -- READ-ONLY (local matrices; the database is read for 8-K filings and recorded event days). Writes nothing except its printout.
THE QUESTION. The card scales each stock's miss by sqrt(q), q = the MEAN squared standardized miss of all OTHER stocks that day. A few extreme stocks inflate that mean, so on a stressed day
everyone else looks smaller: the share of stocks beyond 2.0 band units is 4.4% on calm days and 2.3% on high-stress days (band_tail_share.py), and coverage with one edge drifts with stress.
The product works around it with a separate edge per stress bin (band_calibrate.py). Would a scale built on the MEDIAN squared miss remove the dependence, so ONE edge works on every day?

THREE VERSIONS, scored on ORDINARY days only (no recorded event, no earnings window, no Regulation FD filing), walk-forward, test years from 2009:
  A  the current scale, ONE edge for all days (shows the problem)
  B  the current scale, an edge PER STRESS BIN (what the card does today)
  C  the median scale  sqrt(median(z^2) / 0.45494)  [0.45494 = the median of a squared standard normal], ONE edge for all days
Edges are the 90th percentile of |band units| over the years BEFORE the test year. Stress bins are defined by the CURRENT stress, sqrt(mean z^2) of the day, so every version is judged on
the same days: calm < 0.8, normal 0.8-1.2, elevated 1.2-1.5, high >= 1.5. The median is taken over all stocks of the day including the stock itself (one stock cannot move a median of ~450).
Event, earnings and Regulation FD days are NOT part of this test: if C earns its place their multipliers and edges would need refitting under the new scale (a separate step).

Usage:   python3 -u scripts/card/robust_stress_test.py
Needs:   data_cache/audit_matrices.npz (gap_audit.py builds it).

PRE-SET RULE (written before the first run). C EARNS ITS PLACE if, in EACH of 2009-2012, 2013-2019, 2020-2026:
  (1) its coverage is within 88-92% in every stress bin that has >= 1,000 ordinary stock-days in that era, AND
  (2) its mean 90% interval score (width + 20 x the overshoot, in own-volatility units: 2w + 20*max(|y|-w, 0) with w = edge x scale) is no more than 1% above B's.
Both conditions in all three eras, or it does not earn its place (the printout says which fails).
PREDICTIONS (before the run): A's coverage differs across stress bins by 4-7 points; C's by 2.5 points or less; C passes the coverage condition in the two later eras; the high-stress bin in
2009-2012 (the crisis years, few days) is the likeliest to miss; chance of a full pass about 45%. Descriptive extra (NO verdict, and I am unsure which way it goes): the share of ordinary
stock-days beyond 2.0 band units by stress bin. Under the current scale it falls with stress (calm 4.4% -> high 2.3% as a daily median). Under the median scale it may flatten, or it may even
RISE with stress, because the few extreme stocks that inflate the mean are counted as exceedances instead of hiding themselves and everyone else (a synthetic check showed that rise).
"""
import os, sys, time, bisect, warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
TEST_START = 2006
FIRST_TEST_YEAR = 2009
MED_CONST = 0.45494
LOW, HIGH = 0.88, 0.92
MIN_CELLS = 1000
SHARP_TOL = 1.01
ERAS = [("2009-2012", 2009, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]
BINS = (("calm (<0.8)", 0.0, 0.8), ("normal (0.8-1.2)", 0.8, 1.2), ("elevated (1.2-1.5)", 1.2, 1.5), ("high (>=1.5)", 1.5, 99.0))


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
    stress_day = np.sqrt(q_all)
    s_cur = np.sqrt(qo)
    s_rob = np.sqrt(med_t / MED_CONST)[None, :] * np.ones((N, 1))

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids.tolist())}
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids.tolist()))
    EV = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                EV[k, t] = True
    FL = np.zeros((N, n), dtype=bool)          # any earnings (2.02) or Regulation FD (7.01) filing flagged on day 0 or +1
    for r in paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is None:
            continue
        its = dc.parse_items(r.get("item_codes"))
        if "2.02" in its or "7.01" in its:
            i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
            if i < n:
                FL[k, i] = True
                if i + 1 < n:
                    FL[k, i + 1] = True
    with np.errstate(invalid="ignore", divide="ignore"):
        absy = np.abs(Ef) / SDf
        bu_cur = absy / s_cur
        bu_rob = absy / s_rob
    ordinary = (valid & (cnt[None, :] > 20) & np.isfinite(qo) & (qo > 0) & np.isfinite(bu_cur) & np.isfinite(bu_rob) & (med_t > 0)[None, :]
                & ~EV & ~FL & (years >= TEST_START)[None, :])
    print("matrices: %d stocks x %d days | ordinary stock-days: %d | %.0fs" % (N, n, int(ordinary.sum()), time.time() - t0), flush=True)

    bin_of = np.full(n, -1)
    for b, (_, lo, hi) in enumerate(BINS):
        bin_of[(stress_day >= lo) & (stress_day < hi)] = b
    BIN = bin_of[None, :] * np.ones((N, 1), dtype=int)

    versions = ("A  current scale, one edge", "B  current scale, edge per stress bin (today)", "C  median scale, one edge")
    hit = {(v, e[0], b): [0, 0] for v in range(3) for e in ERAS for b in range(len(BINS))}
    score = {(v, e[0]): [0.0, 0] for v in range(3) for e in ERAS}
    for Y in sorted(set(years.tolist())):
        if Y < FIRST_TEST_YEAR:
            continue
        prior = ordinary & ((years >= TEST_START) & (years < Y))[None, :]
        cur = ordinary & (years == Y)[None, :]
        if int(prior.sum()) < 50000 or not cur.any():
            continue
        edge_A = float(np.quantile(bu_cur[prior], 0.90))
        edge_C = float(np.quantile(bu_rob[prior], 0.90))
        edge_B = {}
        for b in range(len(BINS)):
            pb = prior & (BIN == b)
            edge_B[b] = float(np.quantile(bu_cur[pb], 0.90)) if int(pb.sum()) >= 2000 else edge_A
        era = next(e[0] for e in ERAS if e[1] <= Y <= e[2])
        for b in range(len(BINS)):
            cb = cur & (BIN == b)
            if not cb.any():
                continue
            yb, sc, sr = absy[cb], s_cur[cb], s_rob[cb]
            for v, (w, bu_v) in enumerate(((edge_A * sc, bu_cur[cb] / edge_A), (edge_B[b] * sc, bu_cur[cb] / edge_B[b]), (edge_C * sr, bu_rob[cb] / edge_C))):
                inside = bu_v <= 1.0
                h = hit[(v, era, b)]
                h[0] += int(inside.sum())
                h[1] += int(inside.size)
                sc_ = score[(v, era)]
                sc_[0] += float((2 * w + 20 * np.maximum(yb - w, 0.0)).sum())
                sc_[1] += int(inside.size)

    print("\nOUT-OF-SAMPLE COVERAGE BY STRESS BIN (target 90%; the rule judges C in 88-92%)")
    verdict_cov = {}
    for v in range(3):
        print("\n  %s" % versions[v])
        print("    %-20s %s" % ("", "".join("%-16s" % e[0] for e in ERAS)))
        for b, (lab, lo, hi) in enumerate(BINS):
            cells = []
            for e in ERAS:
                h = hit[(v, e[0], b)]
                cells.append(("%6.2f%% (%7d)" % (100.0 * h[0] / h[1], h[1])) if h[1] >= MIN_CELLS else "      n/a       ")
            print("    %-20s %s" % (lab, "".join("%-16s" % c for c in cells)))
        spreads = []
        for e in ERAS:
            cov = [hit[(v, e[0], b)][0] / hit[(v, e[0], b)][1] for b in range(len(BINS)) if hit[(v, e[0], b)][1] >= MIN_CELLS]
            spreads.append(100 * (max(cov) - min(cov)) if cov else float("nan"))
        print("    spread across bins (max - min, points): %s" % "  ".join("%s %.1f" % (e[0], s_) for e, s_ in zip(ERAS, spreads)))
        if v == 2:
            for e in ERAS:
                bad = [(BINS[b][0], hit[(2, e[0], b)][0] / hit[(2, e[0], b)][1]) for b in range(len(BINS))
                       if hit[(2, e[0], b)][1] >= MIN_CELLS and not (LOW <= hit[(2, e[0], b)][0] / hit[(2, e[0], b)][1] <= HIGH)]
                verdict_cov[e[0]] = bad

    print("\nMEAN 90%% INTERVAL SCORE (own-volatility units; lower is better; the rule: C <= %.2f x B in every era)" % SHARP_TOL)
    ratios = {}
    for e in ERAS:
        m = [score[(v, e[0])][0] / max(score[(v, e[0])][1], 1) for v in range(3)]
        ratios[e[0]] = m[2] / m[1]
        print("  %-10s A %.4f | B %.4f | C %.4f | C/B = %.4f %s" % (e[0], m[0], m[1], m[2], m[2] / m[1], "ok" if m[2] / m[1] <= SHARP_TOL else "TOO WIDE/LOSSY"))

    print("\nDESCRIPTIVE (no verdict): share of ordinary stock-days beyond 2.0 band units, by stress bin, all test years pooled. Under the median scale the extreme stocks that inflate the mean are")
    print("counted as exceedances, so this share may rise with stress instead of flattening; coverage at the 90% edge above is what the rule judges.")
    ordT = ordinary & (years >= FIRST_TEST_YEAR)[None, :]
    print("  %-20s %12s %12s" % ("", "current scale", "median scale"))
    for b, (lab, lo, hi) in enumerate(BINS):
        m = ordT & (BIN == b)
        if int(m.sum()) >= MIN_CELLS:
            print("  %-20s %11.2f%% %11.2f%%" % (lab, 100 * float((bu_cur[m] > 2.0).mean()), 100 * float((bu_rob[m] > 2.0).mean())))

    print()
    fails = []
    for e in ERAS:
        if verdict_cov[e[0]]:
            fails.append("%s coverage outside 88-92%%: %s" % (e[0], "; ".join("%s %.1f%%" % (lab, 100 * c) for lab, c in verdict_cov[e[0]])))
        if ratios[e[0]] > SHARP_TOL:
            fails.append("%s interval score C/B = %.3f (> %.2f)" % (e[0], ratios[e[0]], SHARP_TOL))
    if not fails:
        print("VERDICT under the pre-set rule: C (the median scale, one edge) EARNS ITS PLACE.")
    else:
        print("VERDICT under the pre-set rule: C does NOT earn its place.")
        for f in fails:
            print("  - " + f)
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
