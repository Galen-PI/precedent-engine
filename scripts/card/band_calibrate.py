#!/usr/bin/env python3
"""
band_calibrate.py -- READ-ONLY (local matrices; the database is read for 8-K filings and recorded event days). Writes models/band_calibration.json.
band_coverage_test.py found the card's band (edge 1.645) too WIDE in every group: ordinary days cover 93.3%, recorded events 93.8%, earnings day 0 91.8%, day +1 92.7%,
event + earnings 92.9%, Regulation FD 94.3%, against a target of 90%. The slow spread comes from the previous 250 days, which include each stock's own earnings and event
jumps, so it is inflated (the mean squared band unit on ordinary days is 0.84, not 1.0), and the market-stress scaling over-corrects when stress is elevated.
THIS SETS EACH GROUP'S EDGE TO THE EMPIRICAL 90th PERCENTILE of |band units| (instead of 1.645) and CHECKS IT OUT OF SAMPLE: for each test year the edge is the 90th percentile
over the years BEFORE it (from 2006), and the realized coverage of that year is counted. Ordinary days get a separate edge for each market-stress bin (calm < 0.8, normal
0.8-1.2, elevated 1.2-1.5, high >= 1.5), because the stress scaling is uneven; the other groups have one edge each.

Usage:   python3 -u scripts/card/band_calibrate.py
Needs:   data_cache/audit_matrices.npz (gap_audit.py builds it); models/event_band_model.json and models/earnings_band_model.json.

PRE-SET RULE (written before the first run). After the walk-forward calibration a group is CALIBRATED if its realized coverage is within 88-92% in EACH judged era (a group needs
>= 1,000 scored days in an era; test years start in 2009, so the first era is 2009-2012). Otherwise it is flagged with the direction of the error.
PREDICTIONS (before the run): ordinary days, recorded events and the two earnings groups land within 89.5-90.5% in every era; the two smallest groups (earnings + event, about
3,600 days; Regulation FD) stay within 88-92% but are noisier; ordinary-day edges fall as stress rises from calm to elevated (the stress scaling over-corrects) and the all-years
ordinary edge is about 1.47-1.52 band units (a scale of about 0.90-0.92 against 1.645).
THE CALIBRATION IS NOT A NEW CLAIM ABOUT THE WORLD: it makes the band's label honest. The band is still an explanation line scored with the same day's stress.
"""
import os, sys, math, time, bisect, json, warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
OUT_FILE = os.path.join(ROOT, "models", "band_calibration.json")
TEST_START = 2006
FIRST_TEST_YEAR = 2009
MIN_PRIOR_CELLS = 500
MIN_DAYS_ERA = 1000
LOW, HIGH = 0.88, 0.92
NOMINAL_EDGE = 1.645
STRESS_BINS = (("calm", 0.0, 0.8), ("normal", 0.8, 1.2), ("elevated", 1.2, 1.5), ("high", 1.5, 99.0))
ERAS = [("2009-2012", 2009, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]


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
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = E / SD
    Zsq = Z.astype(np.float64) ** 2
    valid = ~np.isnan(Zsq)
    S = np.nansum(Zsq, axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        q_all = S / np.maximum(cnt, 1)
    ok = valid & np.isfinite(qo) & (qo > 0) & (cnt[None, :] > 20)
    stress_day = np.sqrt(q_all)

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
        bu = np.abs(E.astype(np.float64)) / (SD.astype(np.float64) * np.sqrt(qo) * MULT)
    test = ok & (years >= TEST_START)[None, :] & np.isfinite(bu)
    print("matrices: %d stocks x %d days | %.0fs" % (N, n, time.time() - t0), flush=True)

    # group keys: ordinary splits by stress bin; the rest are single groups
    base_groups = [("ordinary", test & ~EV & ~EA & ~only701), ("recorded event, no earnings", test & EV & ~EA),
                   ("earnings window, day 0 (no event)", test & EA0 & ~EV), ("earnings window, day +1 (no event)", test & EA1 & ~EV),
                   ("earnings window + recorded event", test & both), ("Regulation FD (7.01) only", test & only701)]
    keyed = []
    for name, mask in base_groups:
        if name == "ordinary":
            for bn, lo, hi in STRESS_BINS:
                keyed.append(("ordinary", bn, mask & ((stress_day >= lo) & (stress_day < hi))[None, :]))
        else:
            keyed.append((name, "", mask))

    yrs = [y for y in sorted(set(years.tolist())) if y >= FIRST_TEST_YEAR]
    cov_hit = {}            # (group name, era) -> [covered, total]
    cov_year = {}
    for gname, bn, mask in keyed:
        for Y in yrs:
            prior = mask & ((years >= TEST_START) & (years < Y))[None, :]
            if int(prior.sum()) < MIN_PRIOR_CELLS:
                continue
            edge = float(np.quantile(bu[prior], 0.90))
            cur = mask & (years == Y)[None, :]
            c = int(cur.sum())
            if c == 0:
                continue
            hit = int((bu[cur] <= edge).sum())
            for e in ERAS:
                if e[1] <= Y <= e[2]:
                    a = cov_hit.setdefault((gname, e[0]), [0, 0])
                    a[0] += hit
                    a[1] += c
            a = cov_year.setdefault(gname, {}).setdefault(Y, [0, 0])
            a[0] += hit
            a[1] += c

    print("\nOUT-OF-SAMPLE COVERAGE AFTER CALIBRATION (each year scored with the 90th percentile of the years before it; target 90%)")
    print("  %-38s %10s %9s | %-10s %-10s %-10s | %s" % ("group", "days", "coverage", ERAS[0][0], ERAS[1][0], ERAS[2][0], "verdict"))
    names = [g[0] for g in base_groups]
    verdicts = {}
    for gname in names:
        tot = [sum(cov_hit.get((gname, e[0]), [0, 0])[0] for e in ERAS), sum(cov_hit.get((gname, e[0]), [0, 0])[1] for e in ERAS)]
        cells, judged = [], []
        for e in ERAS:
            h, c = cov_hit.get((gname, e[0]), [0, 0])
            if c >= MIN_DAYS_ERA:
                cells.append("%7.2f%%" % (100.0 * h / c))
                judged.append(h / c)
            else:
                cells.append("   n/a  ")
        if len(judged) < 2:
            v = "too few days to judge"
        elif all(LOW <= x <= HIGH for x in judged):
            v = "CALIBRATED"
        else:
            v = "UNDER-COVERS" if any(x < LOW for x in judged) else "OVER-COVERS"
        verdicts[gname] = v
        print("  %-38s %10d %8.2f%% | %-10s %-10s %-10s | %s" % (gname, tot[1], 100.0 * tot[0] / max(tot[1], 1), cells[0], cells[1], cells[2], v))
    print("\n  ordinary days by market-stress bin (all test years pooled):")
    for bn, lo, hi in STRESS_BINS:
        m = [k for k in keyed if k[0] == "ordinary" and k[1] == bn][0][2]
        h = c = 0
        for Y in yrs:
            prior = m & ((years >= TEST_START) & (years < Y))[None, :]
            cur = m & (years == Y)[None, :]
            if int(prior.sum()) >= MIN_PRIOR_CELLS and int(cur.sum()) > 0:
                edge = float(np.quantile(bu[prior], 0.90))
                h += int((bu[cur] <= edge).sum())
                c += int(cur.sum())
        print("    %-10s %10d days  %6.2f%%" % (bn, c, 100.0 * h / max(c, 1)))

    # the all-years edges for the card
    edges = {}
    ordinary_edges = {}
    for gname, bn, mask in keyed:
        if int(mask.sum()) < MIN_PRIOR_CELLS:
            continue
        e90 = float(np.quantile(bu[mask], 0.90))
        if gname == "ordinary":
            ordinary_edges[bn] = e90
        else:
            edges[gname] = e90
    edges["ordinary_all"] = float(np.quantile(bu[base_groups[0][1]], 0.90))
    print("\nEDGES FITTED ON ALL YEARS (band units; the old fixed edge is %.3f):" % NOMINAL_EDGE)
    print("  ordinary, all stress levels: %.3f (scale %.3f)" % (edges["ordinary_all"], edges["ordinary_all"] / NOMINAL_EDGE))
    for bn, lo, hi in STRESS_BINS:
        if bn in ordinary_edges:
            print("    ordinary, %-9s stress: %.3f (scale %.3f)" % (bn, ordinary_edges[bn], ordinary_edges[bn] / NOMINAL_EDGE))
    for k, v in edges.items():
        if k != "ordinary_all":
            print("  %-38s %.3f (scale %.3f)" % (k, v, v / NOMINAL_EDGE))
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w") as fh:
        json.dump({"what": "Empirical 90th percentile of |miss / (slow spread x sqrt(q) x multiplier)| per group, in band units. Use as the band edge instead of 1.645. Walk-forward verified in band_calibrate.py.",
                   "nominal_edge_replaced": NOMINAL_EDGE, "edge_90": edges, "ordinary_by_stress_bin": ordinary_edges,
                   "stress_bins": [{"name": b, "from": lo, "to": hi} for b, lo, hi in STRESS_BINS], "fit_years": "all years %d on in the matrices" % TEST_START,
                   "verdicts": verdicts,
                   "caveats": ["An explanation band: it is scored with the same day's market-wide stress.", "Fitted on all years: the walk-forward coverage above is the honest check.",
                               "The slow spread includes each stock's own earnings and event jumps; a spread computed without them would be the cleaner fix."]}, fh, indent=1)
    print("\nsaved %s" % OUT_FILE)
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
