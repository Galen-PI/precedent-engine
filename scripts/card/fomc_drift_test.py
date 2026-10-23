#!/usr/bin/env python3
"""
fomc_drift_test.py -- READ-ONLY (database: fomc_meetings, securities, market_prices). Writes nothing.
Registered rule, windows, predictions and limits: results/PREREG_fomc_drift_test_2026-10-23.md (committed before the first real run).
QUESTION. Is SPY's log return over the two days up to a scheduled FOMC decision unusually high (the 'pre-FOMC drift')? Baseline and exclusion as the size tests (fed_change_day_test.ld, days 21-63 away, every meeting day and the day after excluded).
Usage:   python3 -u scripts/card/fomc_drift_test.py
"""
import os, sys, bisect, math, time, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fed_change_day_test as fct

WINDOWS = [("1994-2011 (replication)", 1994, 2011), ("2012-2026 (persistence)", 2012, 2026)]
PROJECT = [("2004-2014", 2004, 2014), ("2015-2026", 2015, 2026)]
SHIFTS = (21, -21)


def summarize(vals):
    a = np.array([x for x in vals if x is not None and np.isfinite(x)], dtype=float)
    n = len(a)
    if n < 3:
        return None
    m, se = float(a.mean()), float(a.std(ddof=1) / math.sqrt(n))
    return {"n": n, "mean": 100 * m, "lo": 100 * (m - 1.96 * se), "hi": 100 * (m + 1.96 * se), "t": (m / se) if se > 0 else float("nan"), "med": 100 * float(np.median(a))}


def fmt(r):
    return "n/a" if r is None else "n %3d  mean excess %+.3f%% [%+.3f, %+.3f]  t %+.2f  median %+.3f%%" % (r["n"], r["mean"], r["lo"], r["hi"], r["t"], r["med"])


def spy_series(sb):
    sid = sb.table("securities").select("id,ticker").eq("ticker", "SPY").execute().data[0]["id"]
    rows, off = [], 0
    while True:
        page = sb.table("market_prices").select("price_date,adjusted_close").eq("security_id", sid).order("price_date").range(off, off + 999).execute().data
        if not page:
            break
        rows += [(str(r["price_date"])[:10], float(r["adjusted_close"])) for r in page if r.get("adjusted_close")]
        if len(page) < 1000:
            break
        off += 1000
    return rows


def load_meetings(sb):
    rows = sb.table("fomc_meetings").select("kind,start_date,end_date,announcement_date,flags,confirmed").execute().data
    sched, unsched = [], []
    for r in rows:
        if r.get("confirmed") is False or r["kind"] == "cancelled":
            continue
        fl = r.get("flags") or ""
        end = datetime.date.fromisoformat(str(r["end_date"])[:10])
        ann = r.get("announcement_date")
        if r["kind"] == "conference_call" or "UNSCHEDULED" in fl:
            if ann:
                unsched.append(datetime.date.fromisoformat(str(ann)[:10]))
        elif r["kind"] == "meeting" and (ann or end.year <= 1999):
            sched.append(datetime.date.fromisoformat(str(ann)[:10]) if ann else end)
    return sorted(set(sched)), sorted(set(unsched))


def main(sb=None):
    t0 = time.time()
    sb = sb or fct.ew.get_sb()
    spy = spy_series(sb)
    days = [d for d, _ in spy]
    px = np.array([p for _, p in spy], dtype=float)
    n = len(days)
    lr = np.full(n, np.nan)
    lr[1:] = np.log(px[1:] / px[:-1])
    lr2 = np.full(n, np.nan)
    lr2[1:] = lr[:-1] + lr[1:]
    sched, unsched = load_meetings(sb)
    idx = lambda d: bisect.bisect_left(days, d.isoformat())
    S = sorted({idx(d) for d in sched if idx(d) < n})
    U = sorted({idx(d) for d in unsched if idx(d) < n})
    X = set()
    for i in S + U:
        X.update((i, i + 1))
    yr = lambda i: int(days[i][:4])
    print("SPY days %d (%s to %s) | scheduled meetings %d | unscheduled actions excluded from the baseline %d | %.0fs" % (n, days[0], days[-1], len(S), len(U), time.time() - t0), flush=True)

    def stat(idxs, ser, w, shift=0, back=0):
        vals = []
        for i in idxs:
            j = i + shift
            if shift and ({j - 1, j, j + 1} & X):
                continue
            if 0 <= j - back < n:
                vals.append(fct.ld(ser, j - back, w, X))
        return vals
    res, plc = {}, {}
    print("\nPRIMARY: two-day return (decision day -1 and 0) in excess of baseline days 21-63 away (percent)")
    for lab, lo, hi in WINDOWS:
        idxs = [i for i in S if lo <= yr(i) <= hi]
        res[lab] = summarize(stat(idxs, lr2, 0))
        plc[lab] = summarize([x for sh in SHIFTS for x in stat(idxs, lr2, 0, sh)])
        print("  %-26s %s" % (lab, fmt(res[lab])))
    print("PLACEBO (meetings shifted +21 and -21 trading days; skipped near a meeting)")
    for lab, _, _ in WINDOWS:
        print("  %-26s %s" % (lab, fmt(plc[lab])))
    R, P = res["1994-2011 (replication)"], res["2012-2026 (persistence)"]
    pl = plc["1994-2011 (replication)"]
    if R is None or P is None or pl is None:
        verdict = "CANNOT TEST (too few meetings)"
    elif abs(pl["t"]) >= 2.5:
        verdict = "VOID: the replication-window placebo reads |t| >= 2.5 (the baseline does not calibrate)"
    else:
        rep, per = R["mean"] > 0 and R["t"] >= 2.5, P["mean"] > 0 and P["t"] >= 2.0
        verdict = "REPLICATES AND PERSISTS" if rep and per else ("REPLICATES, FADED" if rep else "NOT REPLICATED")
    print("\nDESCRIPTIVE (exploratory): each day's return in excess of the same baseline, percent")
    for lab, lo, hi in WINDOWS + PROJECT:
        idxs = [i for i in S if lo <= yr(i) <= hi]
        print("  %-26s day -1 %s" % (lab, fmt(summarize(stat(idxs, lr, 0, 0, 1)))))
        print("  %-26s day  0 %s" % ("", fmt(summarize(stat(idxs, lr, 0)))))
        print("  %-26s day +1 %s" % ("", fmt(summarize(stat(idxs, lr, 1)))))
    print("\nVERDICT (registered rule): %s" % verdict)
    print("REGISTERED PREDICTIONS: 1994-2011 two-day excess +0.30%% (+0.05 to +0.55), P(t >= 2.5) 40%%; 2012-2026 +0.08%% (-0.20 to +0.35), P(t >= 2.0) 12%%; P(REPLICATES AND PERSISTS) 8%%, P(REPLICATES, FADED) 32%%, P(NOT REPLICATED or VOID) 60%%; scheduled meetings about 260 (250-270)")
    print("total %.0fs" % (time.time() - t0))
    return res, plc, verdict, S


if __name__ == "__main__":
    main()
