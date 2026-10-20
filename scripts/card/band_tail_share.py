#!/usr/bin/env python3
"""
band_tail_share.py -- READ-ONLY (local matrices; the database is read for 8-K filings and recorded event days). Writes models/tail_share_reference.json.
THE DAY MAP counts the stocks whose miss is beyond 2 band units and says "about 4.6% expected if misses were normal". That is a Gaussian figure, and the measured tails are not Gaussian
(band_coverage_test.py: 1.34% of ordinary-day misses beyond 2.576 units against a nominal 1%; 2.3-2.7% in earnings windows). This measures the REAL baseline: the share of stocks beyond 2.0
band units on a typical day, as a DISTRIBUTION over days (a single number would hide that the share moves from day to day), using exactly the band units the map uses (same-day market
stress, the card's multipliers for events, earnings windows and Regulation FD).

Usage:   python3 -u scripts/card/band_tail_share.py
Needs:   data_cache/audit_matrices.npz (gap_audit.py builds it); models/event_band_model.json and models/earnings_band_model.json.
DESCRIPTIVE: no pass/fail rule; this sets a reference, it does not test a hypothesis. Days need >= 150 scored stocks (as in eo_market_test.py). Test years from 2006.
PREDICTIONS (before the run): the pooled share beyond 2.0 units is 3.0-4.2% (below the Gaussian 4.55%, because the band edges were calibrated and the typical stock sits inside); the median day is
within 0.5 points of the pooled share; the 5th-95th percentile range of the daily share is roughly 1.5-6.5%; the share is higher in earnings windows than on ordinary days; and the shares beyond
1.645 / 2.576 / 3.0 are about 6.7% / 1.3-1.6% / 0.5-0.9% for ordinary days.
"""
import os, sys, time, bisect, json, warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
OUT_FILE = os.path.join(ROOT, "models", "tail_share_reference.json")
TEST_START = 2006
MIN_STOCKS = 150
EDGES = (1.645, 2.0, 2.576, 3.0)
MAP_EDGE = 2.0
ERAS = [("2006-2012", 2006, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]
STRESS_BINS = (("calm (<0.8)", 0.0, 0.8), ("normal (0.8-1.2)", 0.8, 1.2), ("elevated (1.2-1.5)", 1.2, 1.5), ("high (>=1.5)", 1.5, 99.0))


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


def pct_line(x):
    return "%5.2f%%" % (100.0 * x)


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

    groups = [("all stock-days", test), ("ordinary (no event, earnings or 7.01)", test & ~EV & ~EA & ~only701), ("recorded event, no earnings", test & EV & ~EA),
              ("earnings window (day 0 or +1, with or without an event)", test & EA), ("Regulation FD (7.01) only", test & only701)]
    print("\nPOOLED SHARE OF STOCK-DAYS BEYOND EACH EDGE (band units; the map uses %.1f)" % MAP_EDGE)
    print("  %-56s %10s | %s" % ("group", "days", "  ".join("%7s" % ("> %g" % e) for e in EDGES)))
    pooled = {}
    for name, mask in groups:
        v = bu[mask]
        sh = [float((v > e).mean()) for e in EDGES]
        pooled[name] = sh
        print("  %-56s %10d | %s" % (name, v.size, "  ".join(pct_line(x) for x in sh)))
    print("  (Gaussian reference: %s)" % "  ".join("> %g: %s" % (e, pct_line(float(2 * (1 - 0.5 * (1 + __import__("math").erf(e / 2 ** 0.5)))))) for e in EDGES))

    # the day-to-day distribution of the share beyond the map's edge (days with at least MIN_STOCKS scored stocks)
    n_t = test.sum(axis=0)
    over_t = ((bu > MAP_EDGE) & test).sum(axis=0)
    days = np.where(n_t >= MIN_STOCKS)[0]
    sh = over_t[days] / n_t[days]
    q = {k: float(np.quantile(sh, p)) for k, p in (("p05", 0.05), ("p25", 0.25), ("median", 0.5), ("p75", 0.75), ("p95", 0.95))}
    q["mean"] = float(sh.mean())
    print("\nDAILY SHARE OF STOCKS BEYOND %.1f BAND UNITS (%d days with >= %d scored stocks, 2006 on)" % (MAP_EDGE, days.size, MIN_STOCKS))
    print("  all days:  mean %s | 5%% %s | 25%% %s | median %s | 75%% %s | 95%% %s" % (pct_line(q["mean"]), pct_line(q["p05"]), pct_line(q["p25"]), pct_line(q["median"]), pct_line(q["p75"]), pct_line(q["p95"])))
    for lab, lo, hi in ERAS:
        m = (years[days] >= lo) & (years[days] <= hi)
        if m.sum() > 20:
            print("  %-10s mean %s | 5%% %s | median %s | 95%% %s  (%d days)" % (lab, pct_line(sh[m].mean()), pct_line(np.quantile(sh[m], 0.05)), pct_line(np.quantile(sh[m], 0.5)), pct_line(np.quantile(sh[m], 0.95)), int(m.sum())))
    print("  by the day's market-wide stress:")
    for lab, lo, hi in STRESS_BINS:
        m = (stress_day[days] >= lo) & (stress_day[days] < hi)
        if m.sum() > 20:
            print("    %-20s mean %s | 5%% %s | median %s | 95%% %s  (%d days)" % (lab, pct_line(sh[m].mean()), pct_line(np.quantile(sh[m], 0.05)), pct_line(np.quantile(sh[m], 0.5)), pct_line(np.quantile(sh[m], 0.95)), int(m.sum())))
    # how much of a one-day share is just sampling noise for a day of about 490 stocks?
    binom = float(np.sqrt(q["median"] * (1 - q["median"]) / np.median(n_t[days])))
    sd_obs = float(sh.std())
    print("  for scale: pure sampling noise for a day of about %d stocks would give a standard deviation of %.2f points; the observed standard deviation across days is %.2f points (%.2fx: above 1.0 means misses cluster on some days; below 1.0 is possible because the same-day stress scaling fixes each day's average squared miss)" % (
        int(np.median(n_t[days])), 100 * binom, 100 * sd_obs, sd_obs / binom))

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w") as fh:
        json.dump({"what": "Share of stocks beyond %.1f band units on a day (the day map's 'big miss' threshold), measured over all days since %d with >= %d scored stocks; band units as the day map computes them." % (MAP_EDGE, TEST_START, MIN_STOCKS),
                   "edge": MAP_EDGE, "n_days": int(days.size), "pooled_share_all": pooled["all stock-days"][EDGES.index(MAP_EDGE)],
                   "pooled_share_by_group": {k: v[EDGES.index(MAP_EDGE)] for k, v in pooled.items()}, "daily_share": q,
                   "caveats": ["Descriptive reference, not a test.", "Same-day market stress is used in the band units, so the share is conditional on knowing the day's stress.", "Fitted on the same years it describes."]}, fh, indent=1)
    print("\nsaved %s | total %.0fs" % (OUT_FILE, time.time() - t0))


if __name__ == "__main__":
    main()
