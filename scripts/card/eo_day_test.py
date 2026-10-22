#!/usr/bin/env python3
"""
eo_day_test.py -- READ-ONLY (database: government_decisions and sector_day_z). Writes nothing. T3b of the historical line; reuses the functions of fed_change_day_test.py (keep that file).
QUESTION. On the days a RELEVANT executive order is signed, is the whole market's move larger than on surrounding days? A MARKET-WIDE test (orders carry no sector tag). An EXPLANATION lane (same-day), not a forecast. Orders are classified relevant / not relevant by the Haiku relevance classifier (content-based); the date is the SIGNING date.
EVENTS. Distinct signing days of orders with relevance_verdict = relevant (859 orders on 704 distinct days in 1994-2026; from 2004, where the volatility baseline exists: 171 days in 2004-2014 and 360 in 2015-2026, of which 118 in 2025-2026). Eras A = 2004-2014 and B = 2015-2026; robustness subsets B1 = 2015-2024 and RECENT = 2025-2026.
WHY THE SUBSETS. 2025 is a different regime (165 orders on 85 days, including tariff orders that are themselves market-moving news, a reverse-causation case), and orders arrive in bursts, so a few days could carry era B. PASS therefore also requires B1 to hold on its own.
STATISTIC. MKT(t) = n-weighted mean of the 11 sectors' mean |return| / prior 64-day volatility on day t (sector_day_z; 'Unclassified' left out). For an order day i and window w: LD = log MKT(i+w) - mean of log MKT over BASELINE days 21 to 63 trading days away on either side, EXCLUDING every order day and the day after (an event with fewer than 20 clean
baseline days is skipped). AMPLIFICATION = exp(mean LD); SE = sd / sqrt(days); the MEDIAN of LD is printed too (robust to a few huge days). Primary window day 0; day +1 descriptive (orders are often signed late in the day or published the next).
PLACEBO (before any reading): the same statistic on dates shifted +21 and -21 trading days from each order day (skipped when the shifted date is, or is next to, an order day). A placebo with |t| >= 2.5 in either era VOIDS the lane.
PRE-SET RULE (before any real run). PASS: amplification above 1 with t >= 2.5 in BOTH eras A and B, both placebos clean, AND B1 above 1 with t >= 2.0. LEAD: t >= 2.0 in both eras A and B (placebos clean). Otherwise NULL. If B passes but B1 does not, the verdict is printed as 'LEAD, carried by 2025-2026'.
PREDICTIONS (before the run): amplification A 1.00-1.04, B1 1.00-1.05, RECENT 1.03-1.20; PASS probability about 12%; placebos clean in both eras (about 85%); the per-day spread (sd of LD) 0.25-0.35, so one era resolves an amplification of about 4-7% at t 2.5.
VALIDATION (synthetic worlds with the real distinct signing days per year, 11 sectors, a common volatility factor; run before the real data): NO EFFECT: 1.017 (t +0.84) / 1.018 (t +1.42), placebos 0.992 / 0.999, NULL (the small positive reading is chance and is shared by the other worlds, which use the same noise). PLANTED 5% on every order day: 1.068 (t 3.3) / 1.069 (t 5.3), PASS.
TARIFF CLUSTER (x1.8 on 12 days of 2025 only, nothing elsewhere): 2004-2014 1.017 (t 0.84), 2015-2026 1.038 (t 2.75), RECENT alone 1.093 (t 3.45): NULL because era A fails; the 'carried by 2025-2026' branch itself was not exercised by any world.
LIMITS: relevance is the classifier's judgement; signing days coincide with other news; an order's reaction can fall on the day after (day +1 shown); 'relevant' orders are 54% of all orders.
Usage:   python3 -u scripts/card/eo_day_test.py
"""
import os, sys, bisect, time, json, warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fed_change_day_test as fct
import unrecorded_candidates as uc

ERAS = [("2004-2014", 2004, 2014), ("2015-2026", 2015, 2026)]
SUBSETS = [("2015-2024 (robustness)", 2015, 2024), ("2025-2026 (recent)", 2025, 2026)]
SHIFTS, T_PASS, T_LEAD, T_PLACEBO, T_ROBUST = (21, -21), 2.5, 2.0, 2.5, 2.0


def verdict_of(sd):
    for _ in range(2):
        if isinstance(sd, str):
            try:
                sd = json.loads(sd)
            except ValueError:
                return None
    return sd.get("relevance_verdict") if isinstance(sd, dict) else None


def load_order_days(sb):
    out = set()
    for r in uc.paged(lambda: sb.table("government_decisions").select("id,decision_date,structured_data").eq("decision_type", "executive_order").order("id")):
        if verdict_of(r.get("structured_data")) == "relevant" and r.get("decision_date"):
            out.add(str(r["decision_date"])[:10])
    return sorted(out)


def run(days, MZ, NN, order_days):
    D = len(days)
    ok = np.isfinite(MZ) & np.isfinite(NN) & (NN > 0)
    num, den = np.where(ok, NN * MZ, 0.0).sum(axis=0), np.where(ok, NN, 0.0).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        lm = np.log(num / den)
    lm[~(den > 0)] = np.nan
    idx = sorted({bisect.bisect_left(days, d) for d in order_days if d >= "2004-01-01"})
    idx = [i for i in idx if i < D]
    X = set()
    for i in idx:
        X.update((i, i + 1))
    yr = lambda i: int(days[i][:4])
    print("ORDER DAYS (distinct, relevant): " + ", ".join("%s %d" % (lab, sum(1 for i in idx if lo <= yr(i) <= hi)) for lab, lo, hi in ERAS + SUBSETS), flush=True)

    def stat(sel, w, shift=0):
        vals = []
        for i in idx:
            if not sel(yr(i)):
                continue
            j = i + shift
            if shift and ({j - 1, j, j + 1} & X):
                continue
            vals.append(fct.ld(lm, j, w, X))
        return vals
    res = {}
    print("\nAMPLIFICATION of the market-wide move on order days (mean of log difference from baseline days 21-63 away)")
    print("  %-24s %-6s %-46s %s" % ("period", "window", "mean  [95% interval]  t", "median"))
    for lab, lo, hi in ERAS + SUBSETS:
        for w in (0, 1):
            v = stat(lambda y: lo <= y <= hi, w)
            r = fct.summ(v)
            res[(lab, w)] = r
            a = np.array([x for x in v if x is not None])
            print("  %-24s day %+d  %-46s %s" % (lab, w, fct.fmt(r), ("%.3f" % np.exp(np.median(a))) if len(a) else "n/a"))
    print("\nPLACEBO (order days shifted +21 and -21 trading days; skipped near an order day), day 0")
    plc = {}
    for lab, lo, hi in ERAS:
        plc[lab] = fct.summ([x for sh in SHIFTS for x in stat(lambda y: lo <= y <= hi, 0, sh)])
        print("  %-24s %s" % (lab, fct.fmt(plc[lab])))
    spread = {lab: res[(lab, 0)] for lab, _, _ in ERAS}
    print("\nPOWER: one era resolves an amplification of about " + " / ".join("%s: %.1f%%" % (lab, 100 * (np.exp(T_PASS * spread[lab][2]) - 1)) for lab, _, _ in ERAS) + " at t 2.5; the per-day spread (sd of LD) is " + " / ".join("%s: %.2f" % (lab, spread[lab][2] * np.sqrt(spread[lab][0])) for lab, _, _ in ERAS))
    A, B, B1 = res[("2004-2014", 0)], res[("2015-2026", 0)], res[("2015-2024 (robustness)", 0)]
    clean = all(abs(plc[lab][3]) < T_PLACEBO for lab, _, _ in ERAS)
    if not clean:
        verdict = "VOID: a placebo reads |t| >= 2.5 (the baseline does not calibrate)"
    elif A[1] > 0 and B[1] > 0 and A[3] >= T_PASS and B[3] >= T_PASS and B1[1] > 0 and B1[3] >= T_ROBUST:
        verdict = "PASS: the market moves more on days relevant executive orders are signed (explanation lane)"
    elif A[1] > 0 and B[1] > 0 and A[3] >= T_PASS and B[3] >= T_PASS:
        verdict = "LEAD, carried by 2025-2026 (t >= 2.5 in both eras but the 2015-2024 subset does not hold)"
    elif A[1] > 0 and B[1] > 0 and A[3] >= T_LEAD and B[3] >= T_LEAD:
        verdict = "LEAD (t >= 2.0 in both eras, below the pass line)"
    else:
        verdict = "NULL: no documented effect on the market's move at this resolution"
    print("\nVERDICT (pre-set: day 0, t >= 2.5 in both eras A and B with clean placebos AND the 2015-2024 subset t >= 2.0; t >= 2.0 in both = lead): " + verdict)
    return res, plc, verdict


def main():
    t0 = time.time()
    sb = fct.ew.get_sb()
    days, MZ, NN = fct.load_sector_day(sb)
    order_days = load_order_days(sb)
    print("sector-days %d x %d sectors | relevant-order signing days found %d (all years) | %.0fs" % (len(days), len(fct.SECTORS), len(order_days), time.time() - t0), flush=True)
    out = run(days, MZ, NN, order_days)
    print("total %.0fs" % (time.time() - t0))
    return out


if __name__ == "__main__":
    main()
