#!/usr/bin/env python3
"""
fomc_day_test.py -- READ-ONLY (database: fomc_meetings, macro_long and sector_day_z). Writes nothing.
Registered rule, statistic, populations, predictions and limits: results/PREREG_fomc_day_test_2026-10-23.md (committed before the first real run).
QUESTION. On the days an FOMC decision becomes public, is the whole market's move larger than on surrounding days? Reuses eo_day_test.py's statistic and baseline unchanged (fed_change_day_test.ld, baseline days 21-63 away excluding every announcement day and the day after).
Usage:   python3 -u scripts/card/fomc_day_test.py
"""
import os, sys, bisect, math, time, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fed_change_day_test as fct

ERAS = [("2004-2014", 2004, 2014), ("2015-2026", 2015, 2026)]
SUBERAS = [("2004-2007", 2004, 2007), ("2008-2014", 2008, 2014), ("2015-2019", 2015, 2019), ("2020-2026", 2020, 2026)]
T_PASS, T_LEAD, T_PLACEBO, T_ROBUST = 2.5, 2.0, 2.5, 2.0
SHIFTS = (21, -21)
SPLICE = datetime.date(2008, 12, 15)


def summarize(vals):
    a = np.array([x for x in vals if x is not None and np.isfinite(x)], dtype=float)
    n = len(a)
    if n < 3:
        return None
    mean, se = float(a.mean()), float(a.std(ddof=1) / math.sqrt(n))
    return {"n": n, "amp": math.exp(mean), "lo": math.exp(mean - 1.96 * se), "hi": math.exp(mean + 1.96 * se), "t": (mean / se) if se > 0 else float("nan"), "med": math.exp(float(np.median(a)))}


def fmt(r):
    return "n/a" if r is None else "n %3d  amplification %.3f [%.3f, %.3f]  t %+.2f  median %.3f" % (r["n"], r["amp"], r["lo"], r["hi"], r["t"], r["med"])


def series(sb, sid):
    rows, off = [], 0
    while True:
        page = sb.table("macro_long").select("obs_date,value").eq("series_id", sid).order("obs_date").range(off, off + 999).execute().data
        if not page:
            break
        rows += [(datetime.date.fromisoformat(str(r["obs_date"])[:10]), float(r["value"])) for r in page if r.get("value") is not None]
        if len(page) < 1000:
            break
        off += 1000
    return rows


def target_change_dates(sb):
    """dates on which the target-rate midpoint differs from the previous observation: DFEDTAR up to 2008-12-15, (DFEDTARU + DFEDTARL) / 2 from 2008-12-16"""
    old = {d: v for d, v in series(sb, "DFEDTAR") if d <= SPLICE}
    up, lo = dict(series(sb, "DFEDTARU")), dict(series(sb, "DFEDTARL"))
    mid = dict(old)
    for d in up:
        if d > SPLICE and d in lo:
            mid[d] = (up[d] + lo[d]) / 2.0
    out, prev = set(), None
    for d in sorted(mid):
        if prev is not None and abs(mid[d] - prev) > 1e-9:
            out.add(d)
        prev = mid[d]
    return out


def is_change(a, changes):
    """FRED's range series change the DAY AFTER the announcement, DFEDTAR on the day itself: either counts"""
    return a in changes or (a + datetime.timedelta(days=1)) in changes


def load_announcements(sb):
    rows = sb.table("fomc_meetings").select("kind,start_date,end_date,announcement_date,flags,confirmed").execute().data
    out = []
    for r in rows:
        if not r.get("announcement_date") or r.get("confirmed") is False:
            continue
        fl = r.get("flags") or ""
        out.append({"date": datetime.date.fromisoformat(str(r["announcement_date"])[:10]), "kind": r["kind"], "unsched": r["kind"] == "conference_call" or "UNSCHEDULED" in fl})
    return out


def main(sb=None):
    t0 = time.time()
    sb = sb or fct.ew.get_sb()
    days, MZ, NN = fct.load_sector_day(sb)
    D = len(days)
    ann = [a for a in load_announcements(sb) if a["date"] >= datetime.date(2004, 1, 1)]
    changes = target_change_dates(sb)
    print("sector-days %d | announcements from 2004 %d (scheduled %d, unscheduled %d) | target-change dates %d | %.0fs" % (D, len(ann), sum(not a["unsched"] for a in ann), sum(a["unsched"] for a in ann), len(changes), time.time() - t0), flush=True)
    ok = np.isfinite(MZ) & np.isfinite(NN) & (NN > 0)
    num, den = np.where(ok, NN * MZ, 0.0).sum(axis=0), np.where(ok, NN, 0.0).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        lm = np.log(num / den)
    lm[~(den > 0)] = np.nan
    idx_of = lambda a: bisect.bisect_left(days, a.isoformat())
    for a in ann:
        a["i"] = idx_of(a["date"])
        a["change"] = is_change(a["date"], changes)
    ann = [a for a in ann if a["i"] < D]
    X = set()
    for a in ann:
        X.update((a["i"], a["i"] + 1))
    yr = lambda i: int(days[i][:4])
    weekend = [a["date"] for a in ann if a["date"].weekday() >= 5]
    print("announcements on a weekend, mapped to the next trading day: %s" % ([str(d) for d in weekend] or "none"))

    def uniq(sel):
        return sorted({a["i"] for a in ann if sel(a)})

    def stat(idxs, w, shift=0):
        vals = []
        for i in idxs:
            j = i + shift
            if shift and ({j - 1, j, j + 1} & X):
                continue
            if not (0 <= j < D):
                continue
            vals.append(fct.ld(lm, j - 1, 0, X) if w == -1 else fct.ld(lm, j, w, X))
        return vals
    sched = uniq(lambda a: not a["unsched"])
    res = {}
    print("\nPRIMARY: scheduled meetings with a statement, day 0 (amplification of the market-wide move; baseline days 21-63 away excluding every announcement day and the day after)")
    for lab, lo, hi in ERAS + [("2015-2026 without 2020", 2015, 2026)]:
        idxs = [i for i in sched if lo <= yr(i) <= hi and not (lab.endswith("2020") and yr(i) == 2020)]
        res[lab] = summarize(stat(idxs, 0))
        print("  %-24s %s" % (lab, fmt(res[lab])))
    plc = {}
    print("PLACEBO (announcement days shifted +21 and -21 trading days; skipped near an announcement), day 0")
    for lab, lo, hi in ERAS:
        plc[lab] = summarize([x for sh in SHIFTS for x in stat([i for i in sched if lo <= yr(i) <= hi], 0, sh)])
        print("  %-24s %s" % (lab, fmt(plc[lab])))
    A, B, B1 = res["2004-2014"], res["2015-2026"], res["2015-2026 without 2020"]
    clean = all(plc[lab] is not None and abs(plc[lab]["t"]) < T_PLACEBO for lab, _, _ in ERAS)
    if A is None or B is None or B1 is None:
        verdict = "CANNOT TEST (too few days)"
    elif not clean:
        verdict = "VOID: a placebo reads |t| >= 2.5 (the baseline does not calibrate)"
    elif A["amp"] > 1 and B["amp"] > 1 and A["t"] >= T_PASS and B["t"] >= T_PASS and B1["amp"] > 1 and B1["t"] >= T_ROBUST:
        verdict = "PASS: the market moves more on days a scheduled FOMC decision is announced (explanation lane)"
    elif A["amp"] > 1 and B["amp"] > 1 and A["t"] >= T_LEAD and B["t"] >= T_LEAD:
        verdict = "LEAD (t >= 2.0 in both eras, below the pass line or without the 2020-free subset holding)"
    else:
        verdict = "NULL: no documented effect on the market's move at this resolution"
    print("\nDESCRIPTIVE (no pass line; exploratory)")
    for w, name in ((-1, "day -1"), (0, "day 0"), (1, "day +1")):
        for lab, lo, hi in ERAS:
            print("  scheduled %-7s %-10s %s" % (name, lab, fmt(summarize(stat([i for i in sched if lo <= yr(i) <= hi], w)))))
    for name, sel in (("HOLD", lambda a: not a["unsched"] and not a["change"]), ("CHANGE", lambda a: not a["unsched"] and a["change"]), ("UNSCHEDULED", lambda a: a["unsched"])):
        for lab, lo, hi in ERAS:
            print("  %-11s day 0 %-10s %s" % (name, lab, fmt(summarize(stat([i for i in uniq(sel) if lo <= yr(i) <= hi], 0)))))
    for lab, lo, hi in SUBERAS:
        print("  scheduled sub-era %-10s %s" % (lab, fmt(summarize(stat([i for i in sched if lo <= yr(i) <= hi], 0)))))
    print("\nVERDICT (registered rule): %s" % verdict)
    print("REGISTERED PREDICTIONS: scheduled day 0 A 1.12 (1.04-1.25), B 1.10 (1.03-1.22); P(PASS) 55%%, P(LEAD) 15%%; day -1 0.97 (0.92-1.02); day +1 1.04 (0.98-1.12); CHANGE 1.20 (1.05-1.45) vs HOLD 1.07 (1.00-1.15); UNSCHEDULED 1.8 (1.3-3.0); scheduled meetings about 180 (160-190)")
    print("total %.0fs" % (time.time() - t0))
    return res, plc, verdict, ann


if __name__ == "__main__":
    main()
