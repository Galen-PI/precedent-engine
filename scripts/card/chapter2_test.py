#!/usr/bin/env python3
"""
chapter2_test.py -- READ-ONLY (local cache). Walk-forward test of 'chapter 2' candidates: what can the macro flags add to chapter 1
(market + sector) on the days they are active?

Usage:
    python3 -u scripts/card/chapter2_test.py --limit 40 --stride 5     (trial)
    python3 -u scripts/card/chapter2_test.py                           (full run)

SETUP. Chapter 1 = each stock's market + sector fit over the last 250 valid days (exactly as in decomp_validation.py), giving a miss e1 for
every stock-day. Flags (same lines as the ledger): oil |move| >= 3%, yield |change| >= 0.10 pp, credit widening >= 0.03 pp. A FLAG DAY is
a stock-day with at least one flag on. Each candidate is fit ONLY on data from years BEFORE the test year (walk-forward, expanding) and
scored on the test year; test years 2005 on. Nothing is fit on the day it is scored on.

NOTE ON WHAT CAN WORK. Chapter 1 uses the sector's same-day move, so any macro response shared by the whole sector is already inside it.
A1 and A2 (betas pooled across a sector or all stocks) are therefore CONTROLS and are expected to add about nothing. The candidate that can
help is A3: each stock's own exposure relative to its peers, learned over all its prior flag days and shrunk toward zero.

CENTER (signed) candidates: the predicted miss is beta . x, with x = (oil move, yield change, credit change), each set to zero unless
its own flag is on. Ridge shrinkage adds 100 'pseudo-observations' of each factor's own second moment; a fit needs >= 150 prior flag-day
rows, otherwise the candidate abstains (adds nothing).
  A1 = betas pooled per sector;  A2 = pooled over all stocks;  A3 = per stock.
  Score: 1 - (sum of squared misses after the candidate) / (sum of squared chapter-1 misses), on flag days.
WIDTH candidates (is the spread right on flag days?). s_slow = chapter 1's residual sd over its fit window; s_fast = sd of the stock's last 20
misses (needs >= 10). A scale c is calibrated on prior years from z-squared: no flags (bin 0), one flag (bin 1), two or more (bin 2).
  W0 = s_slow x c0 (baseline);  W1 = s_slow x c(bin);  W2 = s_fast x c0';  W3 = s_fast x c'(bin).
  Score: Gaussian log score per stock-day on flag days (nats; higher is better).
  W1 - W0 = do flags widen the slow spread?   W3 - W2 = do flags add anything beyond RECENT volatility (the clustering check)?

PRE-SET RULES (judgment calls, written before the first run):
  A center candidate earns its place if its SSE reduction is >= 0.5% in each of the three eras AND positive in >= 70% of test years.
  A width candidate earns its place if its log-score gain is >= 0.005 nats per stock-day in each era AND positive in >= 70% of test years.
  Effective sample size: all stocks share the same flag days, so the number of distinct flag days per era (printed) is the number that counts.
READING W3 - W2: a gain means the flags carry information about today's spread beyond the stock's last 20 misses. It cannot tell whether a flag
  CAUSES the widening or only marks the start of a volatile period before recent returns reveal it; either way a flag-aware band is useful.
Predictions made before the run: A1 and A2 about zero; A3 small and uncertain; W1 - W0 positive; W3 - W2 smaller than W1 - W0.
"""
import os, sys, math, time
from collections import deque, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decomp_validation as dv

STATS_START = "1995-01-01"
TEST_START = 2005
PSEUDO = 100
MIN_PRIOR = 150
MIN_BIN = 300
ERAS = [("2005-2012", 2005, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]


def new_stat():
    return [0.0] * 11


def add_stat(st, e, x):
    st[0] += 1
    st[1] += e * e
    st[2] += e * x[0]
    st[3] += e * x[1]
    st[4] += e * x[2]
    st[5] += x[0] * x[0]
    st[6] += x[0] * x[1]
    st[7] += x[0] * x[2]
    st[8] += x[1] * x[1]
    st[9] += x[1] * x[2]
    st[10] += x[2] * x[2]


def plus(a, b):
    return [p + q for p, q in zip(a, b)]


def ridge_beta(st):
    n = st[0]
    if n < MIN_PRIOR:
        return None
    A = [[st[5] * (1 + PSEUDO / n) + 1e-12, st[6], st[7]],
         [st[6], st[8] * (1 + PSEUDO / n) + 1e-12, st[9]],
         [st[7], st[9], st[10] * (1 + PSEUDO / n) + 1e-12]]
    return dv.solve(A, [st[2], st[3], st[4]], [0, 1, 2])


def sse_with(st, b):
    if b is None:
        return st[1]
    q = b[0] * b[0] * st[5] + b[1] * b[1] * st[8] + b[2] * b[2] * st[10] + 2 * (b[0] * b[1] * st[6] + b[0] * b[2] * st[7] + b[1] * b[2] * st[9])
    return st[1] - 2 * (b[0] * st[2] + b[1] * st[3] + b[2] * st[4]) + q


def run_stock(sid, ret, rm, s, oil, yld, crd, dates, stock_stats, W, stride):
    n = len(dates)
    K = 3
    A = [[0.0] * K for _ in range(K)]
    b = [0.0] * K
    syy = 0.0
    win = deque()
    recent = deque(maxlen=20)
    cnt = 0
    for t in range(1, n):
        y, xm, xs, xo, xy, xc = ret[t], rm[t], s[t], oil[t], yld[t], crd[t]
        if None in (y, xm, xs, xo, xy, xc):
            continue
        row = (1.0, xm, xs)
        m = len(win)
        if m >= dv.MIN_EST and dates[t] >= STATS_START and t % stride == 0:
            c = dv.solve(A, b, [0, 1, 2])
            if c:
                e1 = y - (c[1] * xm + c[2] * xs)
                sse1 = syy - (c[0] * b[0] + c[1] * b[1] + c[2] * b[2])
                sd1 = math.sqrt(max(sse1, 1e-18) / (m - 3))
                o_on, y_on, c_on = abs(xo) >= 0.03, abs(xy) >= 0.10 - 1e-9, xc >= 0.03 - 1e-9
                nfl = o_on + y_on + c_on
                year = int(dates[t][:4])
                if len(recent) >= 10:
                    sd20 = math.sqrt(max(sum(recent) / len(recent), 1e-18))
                    wb = 0 if nfl == 0 else (1 if nfl == 1 else 2)
                    w = W[(year, wb)]
                    w[0] += 1
                    w[1] += math.log(sd1)
                    w[2] += (e1 / sd1) ** 2
                    w[3] += math.log(sd20)
                    w[4] += (e1 / sd20) ** 2
                if nfl >= 1:
                    st = stock_stats[year] if year in stock_stats else stock_stats.setdefault(year, new_stat())
                    add_stat(st, e1, (xo if o_on else 0.0, xy if y_on else 0.0, xc if c_on else 0.0))
                recent.append(e1 * e1)
                cnt += 1
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
    return cnt


def era_of_year(y):
    for name, lo, hi in ERAS:
        if lo <= y <= hi:
            return name
    return None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    stride = int(sys.argv[sys.argv.index("--stride") + 1]) if "--stride" in sys.argv else 1
    t0 = time.time()
    secs, macro = dv.load_cache()
    spy = [x for x in secs if x["ticker"] == "SPY"]
    if not spy:
        sys.exit("SPY is not in the cache.")
    master = list(spy[0]["dates"])
    pos = {d: i for i, d in enumerate(master)}
    n = len(master)
    stocks = [x for x in secs if x["ticker"] != "SPY"]
    rm, _ = dv.aligned_returns(spy[0], pos, n)
    oil, yld, crd = dv.macro_arrays(macro, master)
    rets = {}
    ssum, scnt = defaultdict(lambda: [0.0] * n), defaultdict(lambda: [0] * n)
    for x in stocks:
        r, _ = dv.aligned_returns(x, pos, n)
        rets[x["id"]] = r
        if x.get("sector"):
            su, sc = ssum[x["sector"]], scnt[x["sector"]]
            for t in range(n):
                if r[t] is not None:
                    su[t] += r[t]
                    sc[t] += 1
    print("cache: %d securities, %d trading days %s .. %s | stride %d | aligned in %.0fs" % (len(stocks), n, master[0], master[-1], stride, time.time() - t0), flush=True)

    SS, W, sec_of = {}, defaultdict(lambda: [0.0] * 5), {}
    todo = stocks[:limit] if limit else stocks
    total = 0
    for k, x in enumerate(todo, 1):
        r, sec = rets[x["id"]], x.get("sector")
        if not sec:
            continue
        su, sc = ssum[sec], scnt[sec]
        sarr = [None] * n
        for t in range(1, n):
            if r[t] is not None and rm[t] is not None and sc[t] - 1 >= dv.MIN_PEERS:
                sarr[t] = (su[t] - r[t]) / (sc[t] - 1) - rm[t]
        SS[x["id"]] = {}
        sec_of[x["id"]] = sec
        total += run_stock(x["id"], r, rm, sarr, oil, yld, crd, master, SS[x["id"]], W, stride)
        if k % 25 == 0 or k == len(todo):
            print("  %d/%d securities, %d stock-days, %.0fs" % (k, len(todo), total, time.time() - t0), flush=True)

    # ---- distinct flag days per era (the effective sample size)
    fd = defaultdict(int)
    for t in range(n):
        if oil[t] is None or yld[t] is None or crd[t] is None:
            continue
        if abs(oil[t]) >= 0.03 or abs(yld[t]) >= 0.10 - 1e-9 or crd[t] >= 0.03 - 1e-9:
            e = era_of_year(int(master[t][:4]))
            if e:
                fd[e] += 1
    print("\ndistinct flag days in the test period: " + " | ".join("%s: %d" % (e[0], fd[e[0]]) for e in ERAS))

    # ---- CENTER candidates, walk-forward
    years = sorted({y for sid in SS for y in SS[sid]})
    test_years = [y for y in years if y >= TEST_START]
    pri_stock = {sid: new_stat() for sid in SS}
    pri_sec, pri_all = defaultdict(new_stat), new_stat()
    res = {c: defaultdict(lambda: [0.0, 0.0]) for c in ("A1", "A2", "A3")}      # candidate -> year -> [base sse, candidate sse]
    for Y in years:
        cur_sec, cur_all = defaultdict(new_stat), new_stat()
        for sid, d in SS.items():
            cur = d.get(Y)
            if not cur or cur[0] == 0:
                continue
            cur_sec[sec_of[sid]] = plus(cur_sec[sec_of[sid]], cur)
            cur_all = plus(cur_all, cur)
            if Y >= TEST_START:
                res["A3"][Y][0] += cur[1]
                res["A3"][Y][1] += sse_with(cur, ridge_beta(pri_stock[sid]))
        if Y >= TEST_START:
            for sec, cur in cur_sec.items():
                res["A1"][Y][0] += cur[1]
                res["A1"][Y][1] += sse_with(cur, ridge_beta(pri_sec[sec]))
            res["A2"][Y][0] += cur_all[1]
            res["A2"][Y][1] += sse_with(cur_all, ridge_beta(pri_all))
        for sid, d in SS.items():
            if Y in d:
                pri_stock[sid] = plus(pri_stock[sid], d[Y])
        for sec, cur in cur_sec.items():
            pri_sec[sec] = plus(pri_sec[sec], cur)
        pri_all = plus(pri_all, cur_all)

    def era_gain(c, lo, hi):
        b = sum(v[0] for y, v in res[c].items() if lo <= y <= hi)
        a = sum(v[1] for y, v in res[c].items() if lo <= y <= hi)
        return (1 - a / b) if b > 0 else None

    names = {"A1": "A1 per-sector pooled (control)", "A2": "A2 all-stock pooled (control)", "A3": "A3 per-stock, long history, ridge"}
    print("\nCENTER (signed) candidates: reduction in squared miss vs chapter 1, on flag days (positive = better)")
    print("  %-34s %10s %10s %10s %10s | years positive" % ("", ERAS[0][0], ERAS[1][0], ERAS[2][0], "all"))
    verdict = {}
    for c in ("A1", "A2", "A3"):
        eg = [era_gain(c, lo, hi) for _, lo, hi in ERAS]
        allg = 1 - sum(v[1] for v in res[c].values()) / max(1e-18, sum(v[0] for v in res[c].values())) if res[c] else None
        pos_y = sum(1 for v in res[c].values() if v[0] > 0 and v[1] < v[0])
        ny = len(res[c])
        fmt = lambda g: "%+9.2f%%" % (100 * g) if g is not None else "       n/a"
        print("  %-34s %10s %10s %10s %10s | %d of %d" % (names[c], fmt(eg[0]).strip(), fmt(eg[1]).strip(), fmt(eg[2]).strip(), fmt(allg).strip(), pos_y, ny))
        have = [g for g in eg if g is not None]
        verdict[c] = bool(have) and all(g >= 0.005 for g in have) and ny > 0 and pos_y / ny >= 0.70

    # ---- WIDTH candidates, walk-forward
    pri = defaultdict(lambda: [0.0] * 5)
    wres = {k: defaultdict(float) for k in ("W1-W0", "W2-W0", "W3-W2")}
    wdays = defaultdict(float)
    wyear = {k: {} for k in ("W1-W0", "W3-W2")}
    for Y in sorted({y for (y, b) in W}):
        if Y >= TEST_START and all(pri[b][0] >= MIN_BIN for b in (0, 1, 2)):
            f2 = {b: pri[b][2] / pri[b][0] for b in (0, 1, 2)}
            g2 = {b: pri[b][4] / pri[b][0] for b in (0, 1, 2)}
            L = defaultdict(float)
            days = 0
            for b in (1, 2):
                cnt, sl1, sz1, sl20, sz20 = W[(Y, b)]
                if cnt == 0:
                    continue
                days += cnt
                ls = lambda c2, sl, sz: -0.5 * cnt * math.log(c2) - sl - sz / (2 * c2)
                L["W0"] += ls(f2[0], sl1, sz1)
                L["W1"] += ls(f2[b], sl1, sz1)
                L["W2"] += ls(g2[0], sl20, sz20)
                L["W3"] += ls(g2[b], sl20, sz20)
            if days:
                e = era_of_year(Y)
                for k, (p, q) in {"W1-W0": ("W1", "W0"), "W2-W0": ("W2", "W0"), "W3-W2": ("W3", "W2")}.items():
                    wres[k][e] += L[p] - L[q]
                    if k in wyear:
                        wyear[k][Y] = (L[p] - L[q]) / days
                wdays[e] += days
        for b in (0, 1, 2):
            pri[b] = [p + q for p, q in zip(pri[b], W[(Y, b)])]
    print("\nWIDTH candidates: log-score gain per stock-day on flag days, nats (positive = better)")
    print("  %-52s %10s %10s %10s | years positive" % ("", ERAS[0][0], ERAS[1][0], ERAS[2][0]))
    desc = {"W1-W0": "W1 - W0  flags widen the slow spread", "W2-W0": "W2 - W0  fast spread vs slow spread", "W3-W2": "W3 - W2  flags add to the fast spread"}
    for k in ("W1-W0", "W2-W0", "W3-W2"):
        vals = [(wres[k][e[0]] / wdays[e[0]]) if wdays[e[0]] else None for e in ERAS]
        fmt = lambda g: "%+.4f" % g if g is not None else "n/a"
        ys = wyear.get(k)
        yp = "%d of %d" % (sum(1 for v in ys.values() if v > 0), len(ys)) if ys else "-"
        print("  %-52s %10s %10s %10s | %s" % (desc[k], fmt(vals[0]), fmt(vals[1]), fmt(vals[2]), yp))
        if k in wyear:
            have = [v for v in vals if v is not None]
            verdict[k] = bool(have) and all(v >= 0.005 for v in have) and ys and sum(1 for v in ys.values() if v > 0) / len(ys) >= 0.70
    if all(pri[b][0] > 0 for b in (0, 1, 2)):
        print("\n  calibrated scale c on all years (1.0 = the spread is right):  slow spread: no flags %.2f, one flag %.2f, two or more %.2f | fast spread: %.2f, %.2f, %.2f" % tuple(
            [math.sqrt(pri[b][2] / pri[b][0]) for b in (0, 1, 2)] + [math.sqrt(pri[b][4] / pri[b][0]) for b in (0, 1, 2)]))

    # ---- descriptive: A3 coefficients by sector (all years)
    by_sec = defaultdict(list)
    for sid, d in SS.items():
        tot = new_stat()
        for st in d.values():
            tot = plus(tot, st)
        b = ridge_beta(tot)
        if b:
            by_sec[sec_of[sid]].append(b)
    print("\nA3 coefficients, median over stocks with >= %d flag-day rows (miss per unit of each flagged factor; descriptive only)" % MIN_PRIOR)
    print("  %-24s %8s %12s %12s %12s" % ("sector", "stocks", "oil (per 1.0)", "yield (per pp)", "credit (per pp)"))
    for sec in sorted(by_sec):
        L = by_sec[sec]
        med = lambda i: sorted(v[i] for v in L)[len(L) // 2]
        print("  %-24s %8d %12.3f %12.3f %12.3f" % (sec, len(L), med(0), med(1), med(2)))

    print("\nVERDICTS under the pre-set rules:")
    lab = {"A1": names["A1"], "A2": names["A2"], "A3": names["A3"], "W1-W0": desc["W1-W0"], "W3-W2": desc["W3-W2"]}
    for k in ("A1", "A2", "A3", "W1-W0", "W3-W2"):
        print("  %-48s %s" % (lab[k], "EARNS ITS PLACE" if verdict.get(k) else "does not"))
    print("\ntotal %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
