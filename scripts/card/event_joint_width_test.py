#!/usr/bin/env python3
"""
event_joint_width_test.py -- READ-ONLY (local cache; the database is read for the event list and the direction labels).
Chapter 3, width, JOINT model: the event-day band multiplier from ONE fit on event type, the labeler's size hint, its timing field and the day (0 or +1),
instead of a product of separately measured effects (the factors overlap: large events are more often 'new', types differ in size, and so on).

Usage:
    python3 -u scripts/card/event_joint_width_test.py --limit 40 --stride 5     (trial)
    python3 -u scripts/card/event_joint_width_test.py                           (full run)

MEASURE (as in event_width_test.py, the market-stress-controlled one). Chapter 1 = each stock's market + sector fit over the last 250 valid days, giving a
miss e1 and a slow spread s. q = the mean squared standardized miss of all OTHER stocks the same day (two passes over the stocks). z5 = e1 / (s x sqrt(q)).
An EVENT DAY is day 0 or +1 of a stock's own event with a direction label (first event by event_id, day 0 beats +1; systemic_shock excluded).
MODELS (each predicts E[z5^2] for an event day; scored by the Gaussian log score, nats per event stock-day; walk-forward: fit on years BEFORE the test
year, scored on the test year, test years 2005 on):
  M0 = one scale for all event days.      M1 = by size only.   M2 = by type only.   M3 = by timing only.   M4 = by day only.
  MJ = JOINT: log E[z5^2] = intercept + type + size + timing + day (additive effects, ridge-shrunk, Fisher scoring on the cell counts).
  A single-factor model uses the prior mean of z5^2 per level (a level needs >= 30 prior event-days, else the all-events mean).
PRE-SET RULE (written before the first run): MJ earns its place if it beats the BEST single-factor model of that year (the comparator is the maximum of
  M1-M4, chosen each year in hindsight, a conservative comparator) by >= 0.005 nats per event stock-day in EACH of 2005-2012, 2013-2019, 2020-2026 AND
  the gain is positive in >= 70% of test years. Otherwise it does not, and the band keeps the single best factor.
PREDICTIONS (before the run): MJ beats the best single factor by a small positive margin (about 0.01-0.03 nats), because size and type overlap but timing and
  day carry separate information; the joint effects are smaller than the single-factor ones (the overlap shrinks them).
OUTPUT also gives the main effects (the ratio of the band for each level against a reference level, from the all-years fit) and the implied band multiplier
  against an ordinary day for typical combinations. Do not multiply the single-factor multipliers from event_width_test.py; use these.
"""
import os, sys, math, time
from collections import deque, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decomp_validation as dv
import event_width_test as ew

STATS_START = "1995-01-01"
TEST_START = 2005
MIN_LEVEL = 30
LAMBDA = 5.0
ERAS = [("2005-2012", 2005, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]


def run_stock(ret, rm, s, dates, einfo, C, stride, qsum, qcnt, phase):
    n = len(dates)
    K = 3
    A = [[0.0] * K for _ in range(K)]
    b = [0.0] * K
    syy = 0.0
    win = deque()
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
                elif qcnt[t] > 20:
                    q = (qsum[t] - z2) / (qcnt[t] - 1)
                    if q > 0:
                        year = int(dates[t][:4])
                        ev = einfo.get(t)
                        z5 = z2 / q
                        if ev is None:
                            k = (year, "ne")
                        else:
                            pt, off, size, timing = ev
                            if size is None or timing is None:
                                k = None
                            else:
                                k = (year, (pt, size, timing, off))
                        if k is not None:
                            w = C[k]
                            w[0] += 1
                            w[1] += z5
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


class Joint:
    """log m = intercept + type + size + timing + day (reference = the most frequent level of each factor); ridge-shrunk Fisher scoring."""

    def __init__(self, cells):
        self.fac = []
        for fi in range(3):
            cnts = defaultdict(float)
            for k, (n_, s_) in cells.items():
                cnts[k[fi]] += n_
            levels = sorted(cnts, key=lambda l: -cnts[l])
            self.fac.append(levels)
        self.names = ["intercept"]
        for fi, label in enumerate(("type", "size", "timing")):
            for lev in self.fac[fi][1:]:
                self.names.append("%s: %s" % (label, lev))
        self.names.append("day: +1")
        self.idx = {nm: i for i, nm in enumerate(self.names)}
        k = len(self.names)
        tot_n = sum(v[0] for v in cells.values())
        tot_s = sum(v[1] for v in cells.values())
        beta = [0.0] * k
        beta[0] = math.log(tot_s / tot_n)
        for _ in range(30):
            g, H = [0.0] * k, [[0.0] * k for _ in range(k)]
            for key, (n_, s_) in cells.items():
                x = self.vec(key)
                m = math.exp(sum(beta[i] for i in x))
                gi = 0.5 * (s_ / m - n_)
                for i in x:
                    g[i] += gi
                    for j in x:
                        H[i][j] += 0.5 * n_
            for i in range(1, k):
                g[i] -= LAMBDA * beta[i]
                H[i][i] += LAMBDA
            delta = dv.solve(H, g, list(range(k)))
            if delta is None:
                break
            step = max(abs(d) for d in delta)
            damp = 1.0 if step < 1.0 else 1.0 / step
            beta = [b_ + damp * d for b_, d in zip(beta, delta)]
            if step < 1e-8:
                break
        self.beta = beta

    def vec(self, key):
        idx = [0]
        for fi, label in enumerate(("type", "size", "timing")):
            nm = "%s: %s" % (label, key[fi])
            if nm in self.idx:
                idx.append(self.idx[nm])
        if key[3] == 1:
            idx.append(self.idx["day: +1"])
        return idx

    def predict(self, key):
        return math.exp(sum(self.beta[i] for i in self.vec(key)))


def levelmeans(cells, fi):
    agg = defaultdict(lambda: [0.0, 0.0])
    for k, (n_, s_) in cells.items():
        agg[k[fi]][0] += n_
        agg[k[fi]][1] += s_
    tot_n = sum(a[0] for a in agg.values())
    tot_s = sum(a[1] for a in agg.values())
    overall = tot_s / tot_n
    return {lev: (a[1] / a[0] if a[0] >= MIN_LEVEL else overall) for lev, a in agg.items()}, overall


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    stride = int(sys.argv[sys.argv.index("--stride") + 1]) if "--stride" in sys.argv else 1
    t0 = time.time()
    secs, _m = dv.load_cache()
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
    einfo, use_labels, nlab = ew.load_event_info(ew.get_sb(), master, {x["id"] for x in stocks})
    if not use_labels:
        sys.exit("Fewer than 1,000 direction labels; the size and timing fields are needed.")
    print("cache: %d securities | stride %d | labels: %d | securities with event days: %d" % (len(stocks), stride, nlab, len(einfo)), flush=True)

    C = defaultdict(lambda: [0.0, 0.0])
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
            total += run_stock(r, rm, sarr, master, einfo.get(x["id"], {}), C, stride, qsum, qcnt, phase)
            if k % 100 == 0 or k == len(todo):
                print("  pass %d/2: %d/%d securities, %d day-records, %.0fs" % (phase, k, len(todo), total, time.time() - t0), flush=True)

    years = sorted({y for (y, key) in C})
    pri = defaultdict(lambda: [0.0, 0.0])           # prior event cells
    pri_ne = [0.0, 0.0]
    models = ("M0", "M1 size", "M2 type", "M3 timing", "M4 day", "MJ joint")
    sc_by = {m: defaultdict(float) for m in models + ("best single",)}
    ndays = defaultdict(float)
    yearly = {}
    for Y in years:
        test = {k: v for (yy, k), v in C.items() if yy == Y and k != "ne"}
        if Y >= TEST_START and sum(v[0] for v in pri.values()) >= 500 and test:
            era = era_of_year(Y)
            lm = [levelmeans(pri, fi) for fi in (0, 1, 2)]
            day_cells = defaultdict(lambda: [0.0, 0.0])         # SUM the cells of each day (a dict comprehension kept only one cell per day)
            for k_, v_ in pri.items():
                day_cells[(k_[3],)][0] += v_[0]
                day_cells[(k_[3],)][1] += v_[1]
            dm, dov = levelmeans(day_cells, 0)
            jt = Joint(dict(pri))
            overall = lm[0][1]
            tot = {m: 0.0 for m in models}
            nd = 0.0
            for key, (n_, s_) in test.items():
                preds = {"M0": overall, "M1 size": lm[1][0].get(key[1], overall), "M2 type": lm[0][0].get(key[0], overall),
                         "M3 timing": lm[2][0].get(key[2], overall), "M4 day": dm.get(key[3], dov), "MJ joint": jt.predict(key)}
                for m in models:
                    mm = max(preds[m], 1e-9)
                    tot[m] += -0.5 * n_ * math.log(mm) - s_ / (2 * mm)
                nd += n_
            if nd > 0:
                best_single = max(tot[m] for m in ("M1 size", "M2 type", "M3 timing", "M4 day"))
                for m in models:
                    sc_by[m][era] += tot[m]
                sc_by["best single"][era] += best_single
                ndays[era] += nd
                yearly[Y] = (tot["MJ joint"] - best_single) / nd
        for key, v in test.items():
            pri[key][0] += v[0]
            pri[key][1] += v[1]
        ne = C.get((Y, "ne"))
        if ne:
            pri_ne[0] += ne[0]
            pri_ne[1] += ne[1]

    print("\nGAIN IN LOG SCORE PER EVENT STOCK-DAY (nats; positive = better)")
    print("  %-40s %10s %10s %10s" % ("", ERAS[0][0], ERAS[1][0], ERAS[2][0]))
    def era_val(num, den):
        return [((num[e[0]] - den[e[0]]) / ndays[e[0]]) if ndays[e[0]] else None for e in ERAS]
    fmt = lambda v: "%+.4f" % v if v is not None else "n/a"
    for m in models[1:]:
        v = era_val(sc_by[m], sc_by["M0"])
        print("  %-40s %10s %10s %10s" % (m + " vs M0 (one all-events scale)", *[fmt(x) for x in v]))
    primary = era_val(sc_by["MJ joint"], sc_by["best single"])
    print("  %-40s %10s %10s %10s" % ("PRIMARY  MJ vs the best single factor", *[fmt(x) for x in primary]))
    npos = sum(1 for v in yearly.values() if v > 0)
    print("  years where MJ beats that year's best single factor: %d of %d" % (npos, len(yearly)))
    have = [v for v in primary if v is not None]
    ok = len(have) == 3 and all(v >= 0.005 for v in have) and yearly and npos / len(yearly) >= 0.70
    print("\nVERDICT under the pre-set rule: %s" % ("MJ EARNS ITS PLACE" if ok else "MJ does not earn its place (the band keeps the best single factor)"))

    allc = {}
    for (yy, key), v in C.items():
        if key != "ne":
            a = allc.setdefault(key, [0.0, 0.0])
            a[0] += v[0]
            a[1] += v[1]
    jt = Joint(allc)
    m_ne = pri_ne[1] / pri_ne[0] if pri_ne[0] else float("nan")
    print("\nJOINT MODEL, all years: main effects as a band ratio against the reference level (exp(beta/2); reference = the most common level of each factor)")
    print("  references: type = %s, size = %s, timing = %s, day = 0" % (jt.fac[0][0], jt.fac[1][0], jt.fac[2][0]))
    for nm in jt.names[1:]:
        print("   %-34s %6.2f" % (nm, math.exp(jt.beta[jt.idx[nm]] / 2)))
    print("\nIMPLIED BAND MULTIPLIER against an ordinary day (sqrt of the joint prediction over the ordinary-day mean of z5^2, %.3f)" % m_ne)
    combos = [(jt.fac[0][0], jt.fac[1][0], jt.fac[2][0], 0)]
    for pt in ("regulatory", "restructuring", "accounting_investigation", "legal_settlement", "capital_raise", "leadership_change"):
        for sz in ("large", "small"):
            combos.append((pt, sz, "new", 0))
    combos.append(("capital_raise", "small", "previously_announced", 1))
    print("  %-26s %-10s %-22s %-5s %10s" % ("type", "size", "timing", "day", "multiplier"))
    for key in combos:
        if key[0] in jt.fac[0] and key[1] in jt.fac[1] and key[2] in jt.fac[2]:
            print("  %-26s %-10s %-22s %-5s %9.2fx" % (key[0], key[1], key[2], "+1" if key[3] else "0", math.sqrt(jt.predict(key) / m_ne)))
    import json
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"), exist_ok=True)
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "event_band_model.json")
    with open(model_path, "w") as fh:
        json.dump({"model": "joint additive log-variance of z5^2 = (miss / (slow spread x sqrt(same-day cross-section)))^2 on own-event days",
                   "references": {"type": jt.fac[0][0], "size": jt.fac[1][0], "timing": jt.fac[2][0], "day": 0},
                   "coef": {nm: jt.beta[jt.idx[nm]] for nm in jt.names}, "ordinary_day_mean_z5sq": m_ne,
                   "multiplier_rule": "max(1.0, sqrt(exp(intercept + sum of the matching coefficients) / ordinary_day_mean_z5sq)); do not use for ipo_spinoff, systemic_shock, geopolitical, natural_disaster",
                   "event_days_fit": int(sum(v[0] for v in allc.values())), "fit_years": "all years in the cache"}, fh, indent=1)
    print("\nsaved " + model_path)
    print("\ntotal %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
