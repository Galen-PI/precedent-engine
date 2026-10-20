#!/usr/bin/env python3
"""
band_coverage_test.py -- READ-ONLY (local matrices; the database is read for 8-K filings and recorded event days).
THE ONE CLAIM THE PRODUCT MAKES THAT HAS NOT BEEN MEASURED: the day card draws a band, 1.645 x the stock's slow spread x market-wide stress x a multiplier, and calls it a
reference line. If it is honest, about 90% of actual misses should fall inside it. This measures the REALIZED coverage on every stock-day since 2006, by group, era and stress.

Usage:   python3 -u scripts/card/band_coverage_test.py
Needs:   data_cache/audit_matrices.npz (gap_audit.py builds it); models/event_band_model.json and models/earnings_band_model.json (the same files the card reads).

WHAT IS MEASURED. For each scored stock-day the card's 'band units' = miss / (slow spread x sqrt(q) x multiplier), where q = the mean squared standardized miss of ALL OTHER stocks
that day and the multiplier is exactly what the card would use: the joint event-day model for a recorded event, 2.72 / 2.47 for an earnings window (8-K item 2.02, day 0 / +1),
2.87 for both, 1.36 for a Regulation FD filing (7.01) with no event or earnings, else 1.0. The band holds the miss when |band units| <= 1.645.
HONESTY ABOUT WHAT THIS CHECKS. (1) The band uses the SAME DAY's market-wide stress, which is known only after the day: it is an explanation band, not a forecast range. As a
sensitivity the ordinary and earnings groups are also scored with the PREVIOUS day's stress. (2) The multipliers were fit on these same years, so the coverage of the event and
earnings groups is an in-sample check of calibration (the slow spread itself is walk-forward by construction); era-by-era results show whether the multipliers drift.
PRE-SET RULE (written before the first run). A group is CALIBRATED if its realized coverage is within 87-93% in EACH of 2006-2012, 2013-2019, 2020-2026 (a group needs >= 1,000
scored days in an era to be judged there). UNDER-COVERS if any judged era is below 87%; OVER-COVERS if any judged era is above 93% and none is below 87%. Also reported: the share
of misses beyond the 99% edge (2.576 band units; 1% for a normal) and the mean squared band unit (1.0 if the scale is right).
PREDICTIONS (before the run): ordinary days are calibrated (89-92% in every era); earnings day 0 under-covers (86-89%) and day +1 over-covers or is calibrated (90-94%), because each
flagged day mixes filers whose reaction falls on it with filers whose reaction falls on the other day; recorded-event days under-cover (85-89%); and the band under-covers when
market-wide stress is high (above 1.5) even after scaling by it.
"""
import os, sys, math, time, bisect, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
TEST_START = 2006
EDGE90, EDGE99 = 1.645, 2.576
LOW, HIGH = 0.87, 0.93
MIN_DAYS_ERA = 1000
ERAS = [("2006-2012", 2006, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]


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
        sys.exit("models/earnings_band_model.json not found: the earnings multipliers are needed.")
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
    nrows = 0
    for r in paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        nrows += 1
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
    print("matrices: %d stocks x %d days | 8-K rows read: %d | event stock-days %d | earnings day 0 %d, day +1 %d | event+earnings %d | 7.01 only %d | %.0fs" % (
        N, n, nrows, int((EV & ok).sum()), int((EA0 & ~EV & ok).sum()), int((EA1 & ~EV & ok).sum()), int((both & ok).sum()), int((only701 & ok).sum()), time.time() - t0), flush=True)

    with np.errstate(invalid="ignore", divide="ignore"):
        bu = np.abs(E.astype(np.float64)) / (SD.astype(np.float64) * np.sqrt(qo) * MULT)
        q_prev = np.concatenate([[np.nan], q_all[:-1]])
        bu_prev = np.abs(E.astype(np.float64)) / (SD.astype(np.float64) * np.sqrt(q_prev)[None, :] * MULT)
    test = ok & (years >= TEST_START)[None, :]
    ordinary = test & ~EV & ~EA & ~only701
    groups = [("ordinary (no event, earnings or 7.01)", ordinary),
              ("recorded event, no earnings", test & EV & ~EA),
              ("earnings window, day 0 (no event)", test & EA0 & ~EV),
              ("earnings window, day +1 (no event)", test & EA1 & ~EV),
              ("earnings window + recorded event", test & both),
              ("Regulation FD (7.01) only", test & only701)]

    def cov(mask, arr=None):
        a = bu if arr is None else arr
        m = mask & np.isfinite(a)
        c = int(m.sum())
        if c == 0:
            return float("nan"), 0, float("nan"), float("nan")
        v = a[m]
        return float((v <= EDGE90).mean()), c, float((v > EDGE99).mean()), float((v ** 2).mean())

    print("\nREALIZED COVERAGE OF THE CARD'S BAND (target 90%; 'beyond 99%' target 1%; mean squared band unit target 1.0)")
    print("  %-38s %10s %9s | %-9s %-9s %-9s | %9s %9s | %s" % ("group", "days", "coverage", ERAS[0][0], ERAS[1][0], ERAS[2][0], "beyond99", "mean b^2", "verdict"))
    results = {}
    for name, mask in groups:
        c_all, n_all, b99, ms = cov(mask)
        eras = []
        for e in ERAS:
            em = mask & ((years >= e[1]) & (years <= e[2]))[None, :]
            ce, ne, _, _ = cov(em)
            eras.append((ce, ne))
        judged = [(ce, ne) for ce, ne in eras if ne >= MIN_DAYS_ERA]
        if len(judged) < 2:
            verdict = "too few days to judge"
        elif any(ce < LOW for ce, ne in judged):
            verdict = "UNDER-COVERS"
        elif any(ce > HIGH for ce, ne in judged):
            verdict = "OVER-COVERS"
        else:
            verdict = "CALIBRATED"
        results[name] = (c_all, verdict)
        cells = ["%6.1f%%" % (100 * ce) if ne >= MIN_DAYS_ERA else "  n/a  " for ce, ne in eras]
        print("  %-38s %10d %8.1f%% | %-9s %-9s %-9s | %8.2f%% %9.2f | %s" % (name, n_all, 100 * c_all, cells[0], cells[1], cells[2], 100 * b99, ms, verdict))

    print("\nBY MARKET-WIDE STRESS (the day's root-mean-square standardized miss), ordinary days")
    print("  %-22s %10s %9s %9s" % ("stress", "days", "coverage", "mean b^2"))
    for lo, hi, lab in ((0, 0.8, "calm (< 0.8)"), (0.8, 1.2, "normal (0.8-1.2)"), (1.2, 1.5, "elevated (1.2-1.5)"), (1.5, 2.5, "high (1.5-2.5)"), (2.5, 99, "extreme (> 2.5)")):
        m = ordinary & ((stress_day >= lo) & (stress_day < hi))[None, :]
        c, nn, b99, ms = cov(m)
        print("  %-22s %10d %8.1f%% %9.2f" % (lab, nn, 100 * c if nn else float("nan"), ms))

    print("\nSENSITIVITY: the same band scored with the PREVIOUS day's market-wide stress (what could be known in advance)")
    for name, mask in (groups[0], groups[2], groups[3]):
        c, nn, b99, ms = cov(mask, bu_prev)
        c0, _, _, _ = cov(mask)
        print("  %-38s same-day stress %5.1f%% | previous-day stress %5.1f%%  (%d days)" % (name, 100 * c0, 100 * c, nn))

    print("\nREADING: coverage above 93% means the band is wider than it needs to be; below 87% it misses too often. The band is an explanation line built with the same day's stress,")
    print("         not a forecast range; the previous-day rows show how much of the coverage depends on knowing the day's stress.")
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
