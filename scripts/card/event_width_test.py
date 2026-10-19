#!/usr/bin/env python3
"""
event_width_test.py -- READ-ONLY (local cache; the database is read for the event list and, if present, the direction labels).
Chapter 3, width: on days with the stock's OWN company event, is the spread wider than on ordinary days, and wider than recent volatility
alone would say? And does it depend on the event type, the day (0 or +1), or the labeler's size and timing fields?

Usage:
    python3 -u scripts/card/event_width_test.py --limit 40 --stride 5     (trial)
    python3 -u scripts/card/event_width_test.py                           (full run)

SETUP (as in chapter2_test.py). Chapter 1 = each stock's market + sector fit over the last 250 valid days, giving a miss e1 for every stock-day
(rows need only the return, SPY and the sector factor). An EVENT DAY is day 0 or day +1 of one of the stock's own events (ev_ent; an event on a
non-trading date snaps to the next trading day). If two events share a day, the first by event_id supplies the type, size and timing; day 0 beats
day +1. Everything else is an ORDINARY day. Walk-forward: every scale is calibrated on years BEFORE the test year and scored on the test year
(test years 2005 on). s_slow = chapter 1's residual sd; s_fast = sd of the stock's last 20 misses (needs >= 10).
  W0 = s_slow x c(ordinary);   E1 = s_slow x c(event days).        Score: Gaussian log score per EVENT stock-day (nats).
  W2 = s_fast x c(ordinary);   E3 = s_fast x c(event days).
  E1 - W0 : do own-event days widen the slow spread?        E3 - W2 : do they add anything beyond RECENT volatility?
  E5 (the market-stress control): the miss is also scaled by that DAY'S cross-section, z5 = e1 / (s_slow x sqrt(q)), q = the mean squared standardized
  miss of all OTHER stocks the same day (two passes over the stocks). Market-wide stress then cancels. Score: log score with the scale calibrated on
  ordinary days vs on event days. E5 asks: are own-event days wider than the same day's other stocks imply?
  (Why: a 20-day spread lags the START of a volatile regime, so E3 - W2 alone can pass even when events add nothing and only happen to occur in
  volatile periods; in a synthetic test of exactly that case E3 - W2 passed and E5 did not.)
  Grouped scales (descriptive, no pass or fail unless stated): E4 = scale by event type; offset (day 0 vs +1); and, only if event_direction_labels
  holds >= 1,000 rows, by the labeler's SIZE hint and TIMING (new vs previously_announced). A group needs >= 200 prior event-days to get its own
  scale, otherwise it falls back to the all-events scale. Gain = group scales minus the single all-events scale, on the same event-days.
PRE-SET RULES (written before the first run): E1 - W0, E3 - W2 and E5 each earn their place if the gain is >= 0.005 nats per event stock-day in each
  of the three eras (2005-2012, 2013-2019, 2020-2026) AND positive in >= 70% of test years. THE CLAIM 'own events widen the band' requires BOTH
  E3 - W2 and E5.
PREDICTIONS (before the run): E1 - W0 large and positive; E3 - W2 and E5 positive and passing (an own event is idiosyncratic: neither recent
  volatility nor the day's market stress can anticipate it, unlike a macro flag); type adds a little; day 0 and day +1 differ; and, if the labels are valid, 'large' size widens more than 'small'
  and 'previously_announced' less than 'new' (a validity check on the labeler that does not use the sign).
READ THE EFFECTIVE SAMPLE: event-days are about 1.5% of stock-days; an event day is not independent of the market around it.
"""
import os, sys, math, time, bisect
from collections import deque, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decomp_validation as dv

STATS_START = "1995-01-01"
TEST_START = 2005
MIN_PRIOR = 300          # prior event-days / ordinary days needed to calibrate the all-events scale
MIN_GROUP = 200
ERAS = [("2005-2012", 2005, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]


def get_sb():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def paged(sb, table, cols, orders):
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


def load_event_info(sb, master, cache_ids):
    """security id -> {day index: (ptype, offset, size, timing)}; plus whether usable labels exist."""
    ent_to_sec = defaultdict(list)
    for r in paged(sb, "securities", "id,entity_id", ["id"]):
        if r["id"] in cache_ids and r.get("entity_id"):
            ent_to_sec[r["entity_id"]].append(r["id"])
    labels = {}
    try:
        for r in paged(sb, "event_direction_labels", "event_id,size,timing", ["event_id"]):
            labels[r["event_id"]] = (r.get("size"), r.get("timing"))
    except Exception as e:
        print("no event_direction_labels (%s); label fields skipped" % str(e)[:60], flush=True)
    use_labels = len(labels) >= 1000
    cand = defaultdict(lambda: defaultdict(list))
    for r in paged(sb, "ev_ent", "event_id,entity_id,d,ptype", ["event_id", "entity_id"]):
        i = bisect.bisect_left(master, str(r["d"])[:10])
        if i >= len(master):
            continue
        size, timing = labels.get(r["event_id"], (None, None)) if use_labels else (None, None)
        for sid in ent_to_sec.get(r["entity_id"], []):
            for off in (0, 1):
                if i + off < len(master):
                    cand[sid][i + off].append((off, r["event_id"], r["ptype"], size, timing))
    info = {}
    for sid, days in cand.items():
        info[sid] = {}
        for t, lst in days.items():
            off, eid, pt, size, timing = min(lst, key=lambda x: (x[0], x[1]))
            info[sid][t] = (pt, off, size, timing)
    return info, use_labels, len(labels)


def acc(W, year, key, e1, sd1, sd20, q):
    w = W[(year, key)]
    w[0] += 1
    w[1] += math.log(sd1)
    w[2] += (e1 / sd1) ** 2
    w[3] += math.log(sd20)
    w[4] += (e1 / sd20) ** 2
    if q is not None:
        w[5] += math.log(sd1 * math.sqrt(q))
        w[6] += (e1 / (sd1 * math.sqrt(q))) ** 2
        w[7] += 1


def run_stock(ret, rm, s, dates, einfo, W, stride, qsum, qcnt, phase):
    n = len(dates)
    K = 3
    A = [[0.0] * K for _ in range(K)]
    b = [0.0] * K
    syy = 0.0
    win = deque()
    recent = deque(maxlen=20)
    cnt = 0
    for t in range(1, n):
        y, xm, xs = ret[t], rm[t], s[t]
        if None in (y, xm, xs):
            continue
        row = (1.0, xm, xs)
        m = len(win)
        if m >= dv.MIN_EST and dates[t] >= STATS_START and t % stride == 0:
            c = dv.solve(A, b, [0, 1, 2])
            if c:
                e1 = y - (c[1] * xm + c[2] * xs)
                sse1 = syy - (c[0] * b[0] + c[1] * b[1] + c[2] * b[2])
                sd1 = math.sqrt(max(sse1, 1e-18) / (m - 3))
                z2 = (e1 / sd1) ** 2
                if phase == 1:
                    qsum[t] += z2
                    qcnt[t] += 1
                elif len(recent) >= 10:
                    sd20 = math.sqrt(max(sum(recent) / len(recent), 1e-18))
                    year = int(dates[t][:4])
                    q = (qsum[t] - z2) / (qcnt[t] - 1) if qcnt[t] > 20 else None
                    if q is not None and q <= 0:
                        q = None
                    ev = einfo.get(t)
                    if ev is None:
                        acc(W, year, "ne", e1, sd1, sd20, q)
                    else:
                        pt, off, size, timing = ev
                        acc(W, year, "ev", e1, sd1, sd20, q)
                        acc(W, year, ("t", pt), e1, sd1, sd20, q)
                        acc(W, year, ("o", off), e1, sd1, sd20, q)
                        if size:
                            acc(W, year, ("s", size), e1, sd1, sd20, q)
                        if timing:
                            acc(W, year, ("m", timing), e1, sd1, sd20, q)
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


def ls(cnt, c2, sl, sz):
    return -0.5 * cnt * math.log(c2) - sl - sz / (2 * c2)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    stride = int(sys.argv[sys.argv.index("--stride") + 1]) if "--stride" in sys.argv else 1
    t0 = time.time()
    secs, _macro = dv.load_cache()
    spy = [x for x in secs if x["ticker"] == "SPY"]
    if not spy:
        sys.exit("SPY is not in the cache.")
    master = list(spy[0]["dates"])
    pos = {d: i for i, d in enumerate(master)}
    n = len(master)
    stocks = [x for x in secs if x["ticker"] != "SPY"]
    rm, _ = dv.aligned_returns(spy[0], pos, n)
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
    einfo, use_labels, nlab = load_event_info(get_sb(), master, {x["id"] for x in stocks})
    print("cache: %d securities, %d trading days %s .. %s | stride %d | events mapped for %d securities | direction labels: %d (%s)" % (
        len(stocks), n, master[0], master[-1], stride, len(einfo), nlab, "used for size and timing" if use_labels else "not used (fewer than 1,000)"), flush=True)

    W = defaultdict(lambda: [0.0] * 8)
    todo = stocks[:limit] if limit else stocks
    qsum, qcnt = [0.0] * n, [0] * n
    for phase in (1, 2):
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
            total += run_stock(r, rm, sarr, master, einfo.get(x["id"], {}), W, stride, qsum, qcnt, phase)
            if k % 100 == 0 or k == len(todo):
                print("  pass %d/2: %d/%d securities, %d stock-days, %.0fs" % (phase, k, len(todo), total, time.time() - t0), flush=True)

    years = sorted({y for (y, key) in W})
    pri = defaultdict(lambda: [0.0] * 8)

    def pooled(key):
        return pri[key]

    names = ["E1-W0", "E3-W2", "E5"]
    gain = {k: defaultdict(float) for k in names}
    days = defaultdict(float)
    yearly = {k: {} for k in names}
    grp_gain = defaultdict(lambda: defaultdict(float))        # group family -> era -> summed gain
    grp_days = defaultdict(lambda: defaultdict(float))
    for Y in years:
        if Y >= TEST_START and pri["ne"][0] >= MIN_PRIOR and pri["ev"][0] >= MIN_PRIOR and ("ev" in {k for (yy, k) in W if yy == Y}):
            f0, fe = pri["ne"][2] / pri["ne"][0], pri["ev"][2] / pri["ev"][0]
            g0, ge = pri["ne"][4] / pri["ne"][0], pri["ev"][4] / pri["ev"][0]
            cnt, sl1, sz1, sl20, sz20, sl5, sz5, cnt5 = W[(Y, "ev")]
            if cnt > 0:
                era = era_of_year(Y)
                d_e1 = ls(cnt, fe, sl1, sz1) - ls(cnt, f0, sl1, sz1)
                d_e3 = ls(cnt, ge, sl20, sz20) - ls(cnt, g0, sl20, sz20)
                tests = [("E1-W0", d_e1, cnt), ("E3-W2", d_e3, cnt)]
                if pri["ne"][7] >= MIN_PRIOR and pri["ev"][7] >= MIN_PRIOR and cnt5 > 0:
                    h0, he = pri["ne"][6] / pri["ne"][7], pri["ev"][6] / pri["ev"][7]
                    tests.append(("E5", ls(cnt5, he, sl5, sz5) - ls(cnt5, h0, sl5, sz5), cnt5))
                for nm, v, c_ in tests:
                    gain[nm][era] += v
                    days[nm + era] += c_
                    yearly[nm][Y] = v / c_
                days[era] += cnt
                # grouped scales vs the single all-events scale, on the same event-days
                for fam in ("t", "o", "s", "m"):
                    keys = [k for (yy, k) in W if yy == Y and isinstance(k, tuple) and k[0] == fam]
                    if not keys:
                        continue
                    for k in keys:
                        c_, a, b_, c2_, d_ = W[(Y, k)][:5]
                        p = pri[k]
                        g2 = (p[4] / p[0]) if p[0] >= MIN_GROUP else ge
                        grp_gain[fam][era] += ls(c_, g2, c2_, d_) - ls(c_, ge, c2_, d_)
                        grp_days[fam][era] += c_
        for key in {k for (yy, k) in W if yy == Y}:
            pri[key] = [p + q for p, q in zip(pri[key], W[(Y, key)])]

    print("\nEVENT-DAY WIDTH, log-score gain per event stock-day on own-event days (nats; positive = better)")
    print("  %-52s %10s %10s %10s | years positive" % ("", ERAS[0][0], ERAS[1][0], ERAS[2][0]))
    desc = {"E1-W0": "E1 - W0  event days widen the slow spread", "E3-W2": "E3 - W2  event days add to the fast spread",
            "E5": "E5       event days vs the same day's other stocks"}
    verdict = {}
    for nm in names:
        vals = [(gain[nm][e[0]] / days[nm + e[0]]) if days[nm + e[0]] else None for e in ERAS]
        ys = yearly[nm]
        fmt = lambda g: "%+.4f" % g if g is not None else "n/a"
        npos = sum(1 for v in ys.values() if v > 0)
        print("  %-52s %10s %10s %10s | %d of %d" % (desc[nm], fmt(vals[0]), fmt(vals[1]), fmt(vals[2]), npos, len(ys)))
        have = [v for v in vals if v is not None]
        verdict[nm] = bool(have) and all(v >= 0.005 for v in have) and len(ys) > 0 and npos / len(ys) >= 0.70
    print("\nGROUPED SCALES vs the single all-events scale (descriptive; gain per event stock-day)")
    fam_name = {"t": "by event type", "o": "by day (0 vs +1)", "s": "by labeler SIZE hint", "m": "by labeler TIMING"}
    for fam in ("t", "o", "s", "m"):
        if not grp_days[fam]:
            continue
        vals = [(grp_gain[fam][e[0]] / grp_days[fam][e[0]]) if grp_days[fam][e[0]] else None for e in ERAS]
        print("  %-52s %10s %10s %10s" % (fam_name[fam], *["%+.4f" % v if v is not None else "n/a" for v in vals]))

    print("\nCALIBRATED SCALES on all years (sqrt of mean squared standardized miss; ordinary days = the reference; band multiplier = scale / ordinary scale)")
    if pri["ne"][0] > 0:
        s0, f0 = math.sqrt(pri["ne"][2] / pri["ne"][0]), math.sqrt(pri["ne"][4] / pri["ne"][0])
        m0 = math.sqrt(pri["ne"][6] / pri["ne"][7]) if pri["ne"][7] else float("nan")
        print("  %-28s %9s %9s | %9s %9s %12s %14s" % ("group", "days", "slow", "x ordinary", "fast", "x ordinary", "x ord. (mkt-adj)"))
        print("  %-28s %9d %9.2f | %9s %9.2f %12s %14s" % ("ordinary days", pri["ne"][0], s0, "1.00", f0, "1.00", "1.00"))
        rows = [("all own-event days", "ev")] + sorted(((str(k[1]), k) for k in pri if isinstance(k, tuple)), key=lambda kv: (kv[1][0], kv[0]))
        for label, k in rows:
            p = pri[k]
            if p[0] >= MIN_GROUP:
                sl, fa = math.sqrt(p[2] / p[0]), math.sqrt(p[4] / p[0])
                fam = "" if k == "ev" else {"t": "type: ", "o": "day ", "s": "size: ", "m": "timing: "}[k[0]]
                ma = (math.sqrt(p[6] / p[7]) / m0) if p[7] else float("nan")
                print("  %-28s %9d %9.2f | %9.2f %9.2f %12.2f %14.2f" % (fam + label, p[0], sl, sl / s0, fa, fa / f0, ma))
    print("\nVERDICTS under the pre-set rules:")
    for nm in names:
        print("  %-52s %s" % (desc[nm], "EARNS ITS PLACE" if verdict.get(nm) else "does not"))
    print("  %-52s %s" % ("CLAIM: own events widen the band (E3 - W2 and E5)", "SUPPORTED" if verdict.get("E3-W2") and verdict.get("E5") else "not supported"))
    print("\ntotal %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
