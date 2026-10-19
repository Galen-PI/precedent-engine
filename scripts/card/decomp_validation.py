#!/usr/bin/env python3
"""
decomp_validation.py -- READ-ONLY (local cache; the database is read only for the event list). Cross-stock, out-of-sample check of the day
decomposition: how much of each stock's daily move do the market and sector (layer 1) and the macro factors (layer 2) explain, by era, by
size of day, by sector, by number of active flags, and on days with the stock's own company event?

Usage:
    python3 -u scripts/card/decomp_validation.py --limit 20 --stride 5     (trial)
    python3 -u scripts/card/decomp_validation.py                           (full run, every trading day since 2005)
    options: --limit N (securities)  --stride K (evaluate every K-th day)  --no-events (skip the database event list)

METHOD (same as day_decomp.py v2, run for every stock and day from a local cache of adjusted closes):
  y = the stock's daily return; market = SPY return; sector = (mean return of the OTHER stocks in the same sector, >= 5) - market;
  oil = WTI return; yield = change in the 10-year yield (pp); credit = change in the Baa-Aaa spread (pp).
  Layer 1 = market + sector.  Layer 2 = layer 1 + oil + yield + credit, one joint fit.  Betas = OLS with intercept over the last 250 VALID
  days before the day (the day is never used to fit); hypothetical return = sum of beta x factor (intercept ignored).
  A row is valid when the return and all five factors exist. Days with |return| > 50% (price-adjustment artefacts) are skipped and counted.
  R2_oos = 1 - (sum of squared misses) / (sum of squared actual returns), i.e. against predicting zero.
  Standardized miss z = miss / the model's own in-sample residual sd; the mean of z-squared is about 1.0 when the model is calibrated.
  'Big miss' = |z| > 3 (about 0.3% of days if misses were normal, so a bigger share means fat tails or something missing).
Flags: oil |move| >= 3%, yield |change| >= 0.10 pp, credit widening >= 0.03 pp (same lines as the flag ledger).
Own event: the stock's company event (ev_ent) on day 0 or +1 (a non-trading date snaps to the next trading day).
Descriptive only: no pass or fail. The output is the track record for the 'bottom line' panel and a map of where the equation misses.
"""
import os, sys, pickle, glob, math, json, time, bisect
from collections import deque, defaultdict

CACHE = "data_cache/returns"
EST = 250
MIN_EST = 120
MIN_PEERS = 5
START = "2005-01-01"
MAXRET = 0.5
ERAS = [("2005-2012", "2005-01-01", "2012-12-31"), ("2013-2019", "2013-01-01", "2019-12-31"), ("2020-2026", "2020-01-01", "2100-01-01")]
ZB = [("z<1", 0, 1), ("1<=z<2", 1, 2), ("2<=z<3", 2, 3), ("3<=z<5", 3, 5), ("z>=5", 5, 1e9)]


def get_sb():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def load_cache():
    files = [f for f in glob.glob(os.path.join(CACHE, "*.pkl")) if not f.endswith("_macro.pkl")]
    secs = []
    for f in files:
        with open(f, "rb") as fh:
            secs.append(pickle.load(fh))
    with open(os.path.join(CACHE, "_macro.pkl"), "rb") as fh:
        macro = pickle.load(fh)
    return secs, macro


def macro_arrays(macro, master):
    pos = {d: i for i, d in enumerate(master)}
    n = len(master)
    oil, yld, crd = [None] * n, [None] * n, [None] * n
    o = macro["DCOILWTICO"]
    for i in range(1, len(o)):
        (d, v), pv = o[i], o[i - 1][1]
        if pv > 5 and v > 5 and d in pos:
            oil[pos[d]] = v / pv - 1
    y = macro["DGS10"]
    for i in range(1, len(y)):
        if y[i][0] in pos:
            yld[pos[y[i][0]]] = y[i][1] - y[i - 1][1]
    aaa, baa = dict(macro["DAAA"]), dict(macro["DBAA"])
    sp = sorted((d, baa[d] - aaa[d]) for d in aaa if d in baa)
    for i in range(1, len(sp)):
        if sp[i][0] in pos:
            crd[pos[sp[i][0]]] = sp[i][1] - sp[i - 1][1]
    return oil, yld, crd


def aligned_returns(sec, pos, n):
    adj = [None] * n
    for d, v in zip(sec["dates"], sec["adj"]):
        i = pos.get(d)
        if i is not None:
            adj[i] = v
    ret, bad = [None] * n, 0
    for t in range(1, n):
        a, b = adj[t - 1], adj[t]
        if a is not None and b is not None and a > 0:
            r = b / a - 1
            if abs(r) > MAXRET:
                bad += 1
            else:
                ret[t] = r
    return ret, bad


def solve(A, b, idx):
    k = len(idx)
    M = [[A[i][j] for j in idx] + [b[i]] for i in idx]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-18:
            return None
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        rc = M[c]
        for r in range(c + 1, k):
            f = M[r][c] / pv
            if f:
                rr = M[r]
                for j in range(c, k + 1):
                    rr[j] -= f * rc[j]
    x = [0.0] * k
    for i in range(k - 1, -1, -1):
        x[i] = (M[i][k] - sum(M[i][j] * x[j] for j in range(i + 1, k))) / M[i][i]
    return x


def era_of(d):
    for name, lo, hi in ERAS:
        if lo <= d <= hi:
            return name
    return None


def zbucket(z):
    for name, lo, hi in ZB:
        if lo <= z < hi:
            return name
    return ZB[-1][0]


def add(aggs, key, y, e1, e2, z1, z2):
    a = aggs[key]
    a[0] += 1
    a[1] += y * y
    a[2] += e1 * e1
    a[3] += e2 * e2
    a[4] += z1 * z1
    a[5] += z2 * z2
    a[6] += abs(z1) > 3
    a[7] += abs(z2) > 3


def evaluate_security(ticker, sector, ret, rm, s, oil, yld, crd, dates, ev_days, aggs, stride=1, hook=None):
    n = len(dates)
    K = 6
    A = [[0.0] * K for _ in range(K)]
    b = [0.0] * K
    syy = 0.0
    win = deque()
    evals = 0
    for t in range(1, n):
        y, xm, xs, xo, xy, xc = ret[t], rm[t], s[t], oil[t], yld[t], crd[t]
        if None in (y, xm, xs, xo, xy, xc):
            continue
        row = (1.0, xm, xs, xo, xy, xc)
        m = len(win)
        if m >= MIN_EST and dates[t] >= START and t % stride == 0:
            c5 = solve(A, b, [0, 1, 2, 3, 4, 5])
            c2 = solve(A, b, [0, 1, 2])
            if c5 and c2:
                hyp1 = c2[1] * xm + c2[2] * xs
                hyp2 = c5[1] * xm + c5[2] * xs + c5[3] * xo + c5[4] * xy + c5[5] * xc
                sse1 = syy - (c2[0] * b[0] + c2[1] * b[1] + c2[2] * b[2])
                sse2 = syy - sum(c5[i] * b[i] for i in range(6))
                sd1 = math.sqrt(max(sse1, 1e-18) / (m - 3))
                sd2 = math.sqrt(max(sse2, 1e-18) / (m - 6))
                sdy = math.sqrt(max((syy - b[0] * b[0] / m) / (m - 1), 1e-18))
                e1, e2 = y - hyp1, y - hyp2
                z1, z2 = e1 / sd1, e2 / sd2
                nflags = (abs(xo) >= 0.03) + (abs(xy) >= 0.10 - 1e-9) + (xc >= 0.03 - 1e-9)
                era = era_of(dates[t])
                add(aggs, ("all", "all"), y, e1, e2, z1, z2)
                if era:
                    add(aggs, ("era", era), y, e1, e2, z1, z2)
                add(aggs, ("sector", sector or "(none)"), y, e1, e2, z1, z2)
                add(aggs, ("size", zbucket(abs(y) / sdy)), y, e1, e2, z1, z2)
                add(aggs, ("flags", nflags), y, e1, e2, z1, z2)
                if ev_days is not None:
                    add(aggs, ("event", 1 if t in ev_days else 0), y, e1, e2, z1, z2)
                evals += 1
                if hook:
                    hook(ticker, dates[t], y, hyp1, hyp2, sd1, sd2, c5)
        win.append((y,) + row)
        for i in range(K):
            ri = row[i]
            b[i] += y * ri
            Ai = A[i]
            for j in range(K):
                Ai[j] += ri * row[j]
        syy += y * y
        if len(win) > EST:
            o = win.popleft()
            yo, ro = o[0], o[1:]
            for i in range(K):
                b[i] -= yo * ro[i]
                Ai = A[i]
                for j in range(K):
                    Ai[j] -= ro[i] * ro[j]
            syy -= yo * yo
    return evals


def load_event_days(sb, master, cache_ids):
    def paged(table, cols, orders):
        rows, off = [], 0
        while True:
            q = sb.table(table).select(cols)
            for o in orders:
                q = q.order(o)
            page = q.range(off, off + 999).execute().data
            if not page:
                break
            rows.extend(page)
            if len(page) < 1000:
                break
            off += 1000
        return rows
    ent_to_sec = defaultdict(list)
    for r in paged("securities", "id,entity_id", ["id"]):
        if r["id"] in cache_ids and r.get("entity_id"):
            ent_to_sec[r["entity_id"]].append(r["id"])
    out = defaultdict(set)
    for r in paged("ev_ent", "event_id,entity_id,d", ["event_id", "entity_id"]):
        i = bisect.bisect_left(master, str(r["d"]))
        if i >= len(master):
            continue
        for sid in ent_to_sec.get(r["entity_id"], []):
            out[sid].add(i)
            out[sid].add(i + 1)
    return out


def pct(x):
    return "%6.1f%%" % (100 * x)


def r2(a, which):
    return 1 - a[which] / a[1] if a[1] > 0 else float("nan")


def print_table(title, aggs, kind, order=None, label=lambda k: str(k)):
    keys = [k for k in aggs if k[0] == kind]
    keys.sort(key=(lambda k: order.index(k[1]) if order and k[1] in order else 0) if order else (lambda k: str(k[1])))
    print("\n" + title)
    print("  %-14s %10s | R2_oos layer1  layer2  gain | mean z^2 layer1 layer2 | big misses (|z|>3) layer1 layer2" % ("", "stock-days"))
    for k in keys:
        a = aggs[k]
        if a[0] == 0:
            continue
        print("  %-14s %10d | %13s %7s %6s | %17.2f %6.2f | %24s %6s" % (
            label(k[1]), a[0], "%.3f" % r2(a, 2), "%.3f" % r2(a, 3), "%+.3f" % (r2(a, 3) - r2(a, 2)), a[4] / a[0], a[5] / a[0], pct(a[6] / a[0]), pct(a[7] / a[0])))


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    stride = int(sys.argv[sys.argv.index("--stride") + 1]) if "--stride" in sys.argv else 1
    use_events = "--no-events" not in sys.argv
    t0 = time.time()
    secs, macro = load_cache()
    spy = [s for s in secs if s["ticker"] == "SPY"]
    if not spy:
        sys.exit("SPY is not in the cache (data_cache/returns).")
    master = list(spy[0]["dates"])
    pos = {d: i for i, d in enumerate(master)}
    n = len(master)
    stocks = [s for s in secs if s["ticker"] != "SPY"]
    print("cache: %d securities (+SPY, %d trading days %s .. %s) | stride %d" % (len(stocks), n, master[0], master[-1], stride), flush=True)
    rm, _ = aligned_returns(spy[0], pos, n)
    oil, yld, crd = macro_arrays(macro, master)
    rets, skipped = {}, 0
    ssum, scnt = defaultdict(lambda: [0.0] * n), defaultdict(lambda: [0] * n)
    for s in stocks:
        r, bad = aligned_returns(s, pos, n)
        rets[s["id"]] = r
        skipped += bad
        if s.get("sector"):
            su, sc = ssum[s["sector"]], scnt[s["sector"]]
            for t in range(n):
                if r[t] is not None:
                    su[t] += r[t]
                    sc[t] += 1
    print("returns aligned in %.0fs | days skipped for |return| > 50%%: %d | sectors: %d" % (time.time() - t0, skipped, len(ssum)), flush=True)

    ev = None
    if use_events:
        try:
            ev = load_event_days(get_sb(), master, {s["id"] for s in stocks})
            print("events loaded for %d securities" % len(ev), flush=True)
        except Exception as e:
            print("could not load events (%s); continuing without the event table" % str(e)[:100], flush=True)

    aggs = defaultdict(lambda: [0] * 8)
    todo = stocks[:limit] if limit else stocks
    total = 0
    for k, s in enumerate(todo, 1):
        r = rets[s["id"]]
        sec = s.get("sector")
        sarr = [None] * n
        if sec:
            su, sc = ssum[sec], scnt[sec]
            for t in range(1, n):
                if r[t] is not None and rm[t] is not None and sc[t] - 1 >= MIN_PEERS:
                    sarr[t] = (su[t] - r[t]) / (sc[t] - 1) - rm[t]
        total += evaluate_security(s["ticker"], sec, r, rm, sarr, oil, yld, crd, master, ev.get(s["id"], set()) if ev is not None else None, aggs, stride)
        if k % 25 == 0 or k == len(todo):
            print("  %d/%d securities, %d stock-days scored, %.0fs elapsed" % (k, len(todo), total, time.time() - t0), flush=True)

    print_table("ALL", aggs, "all")
    print_table("BY ERA", aggs, "era", order=[e[0] for e in ERAS])
    print_table("BY SIZE OF DAY (|return| / the stock's own recent sd)", aggs, "size", order=[z[0] for z in ZB])
    print_table("BY NUMBER OF ACTIVE MACRO FLAGS THAT DAY (oil, yield, credit)", aggs, "flags", order=[0, 1, 2, 3], label=lambda k: "%d flag(s)" % k)
    if ev is not None:
        print_table("BY OWN COMPANY EVENT ON DAY 0 OR +1", aggs, "event", order=[0, 1], label=lambda k: "event" if k else "no event")
    print_table("BY SECTOR", aggs, "sector")
    out = {"|".join(map(str, k)): v for k, v in aggs.items()}
    os.makedirs("scripts/card/out", exist_ok=True)
    with open("scripts/card/out/decomp_validation.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("\nsaved scripts/card/out/decomp_validation.json | total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
