#!/usr/bin/env python3
"""
build_matrices_exjump.py -- builds data_cache/audit_matrices_exjump.npz: the same chapter-1 misses E and spreads SD as gap_audit.py's matrices, with ONE change.
THE CHANGE. gap_audit.py estimates each stock's chapter-1 fit and spread from a rolling window of its previous 250 valid days. Every day goes into that window, INCLUDING the stock's own
earnings windows (8-K item 2.02, day 0 and +1), recorded-event days (day 0 and +1) and Regulation FD filings (item 7.01, day 0 and +1). Those days have far larger moves (earnings about 7x the
variance of an ordinary day), so they inflate the stock's spread: by my arithmetic about 14% in variance (earnings windows are about 1.9% of stock-days, recorded events about 1%, Regulation FD
filings about 0.8%). NOTE: the earlier "mean squared band unit 0.84 on ordinary days" is NOT a clean measure of this: that band unit is scaled by the day's cross-section, which the flagged stocks
inflate too. exjump_spread_test.py measures the spread directly.
THE FIX. A flagged day is STILL SCORED (its E and SD are computed from the window as it stands) but is NOT ADDED to the window, so the window holds the previous 250 UNFLAGGED days. Nothing else changes: same cache, same market and sector regressors,
same minimum history, same walk-forward (a day's estimate uses only earlier days).

Usage:   python3 -u scripts/card/build_matrices_exjump.py        (a few minutes: the same loops as gap_audit.py --rebuild, plus one read of the events and 8-K filings)
Needs:   data_cache/returns (the price cache), gap_audit.py and decomp_validation.py in this folder. Writes ONLY data_cache/audit_matrices_exjump.npz. The existing matrices are untouched.
Then:    python3 -u scripts/card/exjump_spread_test.py   (the pre-set test of whether this earns its place)
"""
import os, sys, math, time, bisect
from collections import defaultdict, deque
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import decomp_validation as dv
import gap_audit as ga
import event_width_test as ew
import day_card as dc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "data_cache", "audit_matrices_exjump.npz")


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


def residuals_exjump(ret, rm, s, dates, skip):
    """Identical to gap_audit.residuals_for_stock except that a day with skip[t] True is scored but not added to the estimation window."""
    n = len(dates)
    E = np.full(n, np.nan, dtype=np.float32)
    SD = np.full(n, np.nan, dtype=np.float32)
    Y = np.full(n, np.nan, dtype=np.float32)
    K = 3
    A = [[0.0] * K for _ in range(K)]
    b = [0.0] * K
    syy = 0.0
    win = deque()
    for t in range(1, n):
        y, xm, xs = ret[t], rm[t], s[t]
        if None in (y, xm, xs):
            continue
        row = (1.0, xm, xs)
        m = len(win)
        if m >= dv.MIN_EST and dates[t] >= ga.STATS_START:
            c = dv.solve(A, b, [0, 1, 2])
            if c:
                E[t] = y - (c[1] * xm + c[2] * xs)
                sse1 = syy - (c[0] * b[0] + c[1] * b[1] + c[2] * b[2])
                SD[t] = math.sqrt(max(sse1, 1e-18) / (m - 3))
                Y[t] = y
        if skip[t]:
            continue            # scored above, but the window keeps only unflagged days
        win.append((y,) + row)
        for i in range(K):
            ri = row[i]
            b[i] += y * ri
            Ai = A[i]
            for j in range(K):
                Ai[j] += ri * row[j]
        syy += y * y
        if len(win) > dv.EST:
            o = win.popleft()
            yo, ro = o[0], o[1:]
            for i in range(K):
                b[i] -= yo * ro[i]
                Ai = A[i]
                for j in range(K):
                    Ai[j] -= ro[i] * ro[j]
            syy -= yo * yo
    return E, SD, Y


def main():
    t0 = time.time()
    secs, _m = dv.load_cache()
    spy = [x for x in secs if x["ticker"] == "SPY"]
    if not spy:
        sys.exit("SPY is not in the cache.")
    master = list(spy[0]["dates"])
    pos = {d: i for i, d in enumerate(master)}
    n = len(master)
    rm, _ = dv.aligned_returns(spy[0], pos, n)
    stocks = [x for x in secs if x["ticker"] != "SPY" and x.get("sector")]
    rets = {}
    ssum, scnt = defaultdict(lambda: [0.0] * n), defaultdict(lambda: [0] * n)
    for x in stocks:
        r, _ = dv.aligned_returns(x, pos, n)
        rets[x["id"]] = r
        su, sc = ssum[x["sector"]], scnt[x["sector"]]
        for t in range(n):
            if r[t] is not None:
                su[t] += r[t]
                sc[t] += 1
    N = len(stocks)
    ids = [x["id"] for x in stocks]
    idset = set(ids)

    # the days to keep OUT of each stock's estimation window: own recorded events (day 0, +1), earnings (item 2.02) and Regulation FD (item 7.01) filings (day 0, +1)
    sb = ew.get_sb()
    dl = [str(x) for x in master]
    flag = {sid: np.zeros(n, dtype=bool) for sid in ids}
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, idset)
    for sid, days in einfo.items():
        if sid in flag:
            for t in days:
                flag[sid][t] = True
    nfil = 0
    for r in paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        sid = r["security_id"]
        if sid not in flag:
            continue
        its = dc.parse_items(r.get("item_codes"))
        if "2.02" in its or "7.01" in its:
            i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
            if i < n:
                flag[sid][i] = True
                if i + 1 < n:
                    flag[sid][i + 1] = True
                nfil += 1
    tot_flag = sum(int(f.sum()) for f in flag.values())
    tot_ret = sum(sum(1 for v in rets[sid] if v is not None) for sid in ids)
    print("flagged days kept out of the estimation window: %d of %d stock-days with a return (%.2f%%); 8-K filings used: %d | %.0fs" % (
        tot_flag, tot_ret, 100.0 * tot_flag / max(tot_ret, 1), nfil, time.time() - t0), flush=True)

    E = np.full((N, n), np.nan, dtype=np.float32)
    SD = np.full((N, n), np.nan, dtype=np.float32)
    Y = np.full((N, n), np.nan, dtype=np.float32)
    for k, x in enumerate(stocks):
        r = rets[x["id"]]
        su, sc = ssum[x["sector"]], scnt[x["sector"]]
        sarr = [None] * n
        for t in range(1, n):
            if r[t] is not None and rm[t] is not None and sc[t] - 1 >= dv.MIN_PEERS:
                sarr[t] = (su[t] - r[t]) / (sc[t] - 1) - rm[t]
        E[k], SD[k], Y[k] = residuals_exjump(r, rm, sarr, master, flag[x["id"]])
        if (k + 1) % 100 == 0 or k + 1 == N:
            print("  residuals: %d/%d stocks, %.0fs" % (k + 1, N, time.time() - t0), flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    np.savez_compressed(OUT, dates=np.array(master), ids=np.array(ids), tickers=np.array([x["ticker"] for x in stocks]), E=E, SD=SD, Y=Y)
    print("saved %s | total %.0fs" % (OUT, time.time() - t0))


if __name__ == "__main__":
    main()
