#!/usr/bin/env python3
"""
eo_trade_split.py -- READ-ONLY (database: government_decisions and sector_day_z). Writes nothing.
Splits the 2025-2026 executive-order watch item (eo_day_test.py: day 0 1.081 t +2.01, day +1 1.158 t +3.98) into TRADE-order days (T) and all other relevant-order days (N), to the rule PRE-REGISTERED in results/eo_trade_days_2025_2026.txt (commit 44a1148) before any computation:
  T = the 28 hand-read trade/tariff signing days listed in that file; N = every other relevant-order day of 2025-2026; a day that is both counts as T. Weekend signing dates map to the next trading day exactly as eo_day_test.run() maps them (bisect_left).
  CARRIED BY TARIFF ORDERS if T amplification >= 1.10 with t >= 2.0 on day 0 or day +1 AND N has t < 2.0 on both days; BROAD if N has t >= 2.0 on day 0 or day +1; NEITHER otherwise. Sensitivity: T_strict = T without 2025-08-06.
Everything else is unchanged from eo_day_test.py: the statistic (fed_change_day_test.ld on the n-weighted market-wide mean |return| / prior 64-day volatility), the baseline (days 21-63 away, excluding EVERY order day and the day after, i.e. the full set X), the day definitions (day 0 and day +1) and the data guard in load_sector_day. AMPLIFICATION = exp(mean of the log differences); SE = sd / sqrt(days); the median is printed too.
ADDED, NOT IN THE REGISTERED RULE (printed for information): a +21 / -21 trading-day placebo for T and for N, the pooled recent subset as a SELF-CHECK against the recorded 1.081 / 1.158, the share of the 2025-2026 order days that are T, and a SENSITIVITY found by testing on synthetic data BEFORE any real run: a trade order's effect lands on day +1, so a non-trade order signed the trading day after a trade day has its day 0 inflated (contamination of N). N_clean = N without the days directly after a T day. READING RULE, fixed before the real run: the registered verdict (with the full N) STANDS as the verdict; if N_clean gives a different verdict, the difference is reported as contamination, not as a result.
LIMITS (as registered): trade days cluster (Mar 1-6, Apr 2-9, Jul 30-Aug 11, Nov 4-20), so they are not independent; the predictions were written knowing the pooled recent result, so this decomposes a result already seen; a verdict is descriptive, not a claim about tariffs.
Usage:   python3 -u scripts/card/eo_trade_split.py
"""
import os, sys, bisect, math, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fed_change_day_test as fct
import eo_day_test as eo

TRADE_FILE = os.path.join(HERE, "..", "..", "results", "eo_trade_days_2025_2026.txt")
STRICT_DROP = "2025-08-06"
RECORDED = {0: (1.081, 2.01), 1: (1.158, 3.98)}
SHIFTS = (21, -21)


def summarize(vals):
    a = np.array([x for x in vals if x is not None and np.isfinite(x)], dtype=float)
    n = len(a)
    if n < 3:
        return None
    mean, se = float(a.mean()), float(a.std(ddof=1) / math.sqrt(n))
    return {"n": n, "amp": math.exp(mean), "lo": math.exp(mean - 1.96 * se), "hi": math.exp(mean + 1.96 * se), "t": (mean / se) if se > 0 else float("nan"), "med": math.exp(float(np.median(a)))}


def fmt(r):
    return "n/a" if r is None else "n %3d  amplification %.3f [%.3f, %.3f]  t %+.2f  median %.3f" % (r["n"], r["amp"], r["lo"], r["hi"], r["t"], r["med"])


def hit(r):
    return r is not None and r["amp"] >= 1.10 and r["t"] >= 2.0


def verdict(T0, T1, N0, N1):
    n_low = all(r is not None and r["t"] < 2.0 for r in (N0, N1))
    if (hit(T0) or hit(T1)) and n_low:
        return "CARRIED BY TARIFF ORDERS"
    if any(r is not None and r["t"] >= 2.0 for r in (N0, N1)):
        return "BROAD (the other order days show the effect too)"
    return "NEITHER"


def main():
    t0 = time.time()
    t_dates = [ln.strip() for ln in open(TRADE_FILE) if ln.strip() and not ln.startswith("#")]
    if len(t_dates) != 28:
        print("the registered file must hold exactly 28 trade days, found %d: stopping" % len(t_dates))
        sys.exit(1)
    sb = fct.ew.get_sb()
    days, MZ, NN = fct.load_sector_day(sb)
    order_days = eo.load_order_days(sb)
    D = len(days)
    missing = [d for d in t_dates if d not in order_days]
    print("sector-days %d | relevant-order signing days %d | registered trade days %d (not found among relevant orders: %s) | %.0fs" % (D, len(order_days), len(t_dates), missing or "none", time.time() - t0), flush=True)
    ok = np.isfinite(MZ) & np.isfinite(NN) & (NN > 0)
    num, den = np.where(ok, NN * MZ, 0.0).sum(axis=0), np.where(ok, NN, 0.0).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        lm = np.log(num / den)
    lm[~(den > 0)] = np.nan
    idx_all = sorted({bisect.bisect_left(days, d) for d in order_days if d >= "2004-01-01"})
    idx_all = [i for i in idx_all if i < D]
    X = set()
    for i in idx_all:
        X.update((i, i + 1))
    yr = lambda i: int(days[i][:4])
    recent = [i for i in idx_all if 2025 <= yr(i) <= 2026]
    t_idx = {bisect.bisect_left(days, d) for d in t_dates}
    strict_idx = t_idx - {bisect.bisect_left(days, STRICT_DROP)}
    T = [i for i in recent if i in t_idx]
    Ts = [i for i in recent if i in strict_idx]
    N = [i for i in recent if i not in t_idx]
    Nc = [i for i in N if (i - 1) not in t_idx]

    def stat(sel, w, shift=0):
        vals = []
        for i in sel:
            j = i + shift
            if shift and ({j - 1, j, j + 1} & X):
                continue
            if 0 <= j < D:
                vals.append(fct.ld(lm, j, w, X))
        return vals
    print("2025-2026 order days (distinct trading days): %d | T %d (%.0f%%) | N %d (of which %d directly after a T day; N_clean %d) | T_strict %d" % (len(recent), len(T), 100.0 * len(T) / max(1, len(recent)), len(N), len(N) - len(Nc), len(Nc), len(Ts)))
    res = {}
    print("\nAMPLIFICATION on order days (mean of log difference from baseline days 21-63 away, excluding every order day and the day after)")
    for lab, sel in (("T (trade orders)", T), ("T_strict", Ts), ("N (all other)", N), ("N_clean", Nc), ("pooled recent", recent)):
        for w in (0, 1):
            res[(lab, w)] = summarize(stat(sel, w))
            print("  %-18s day %+d  %s" % (lab, w, fmt(res[(lab, w)])))
    print("\nPLACEBO (order days shifted +21 and -21 trading days; skipped near an order day), day 0 [added check, not in the registered rule]")
    for lab, sel in (("T", T), ("N", N)):
        print("  %-18s %s" % (lab, fmt(summarize([x for sh in SHIFTS for x in stat(sel, 0, sh)]))))
    sc = all(res[("pooled recent", w)] is not None and abs(res[("pooled recent", w)]["amp"] - RECORDED[w][0]) <= 0.003 and abs(res[("pooled recent", w)]["t"] - RECORDED[w][1]) <= 0.06 for w in (0, 1))
    print("\nSELF-CHECK (pooled recent vs the recorded eo_day_test result 1.081 t +2.01 / 1.158 t +3.98): %s" % ("OK, reproduces it" if sc else "FAILED: do not read the split until this is explained"))
    v = verdict(res[("T (trade orders)", 0)], res[("T (trade orders)", 1)], res[("N (all other)", 0)], res[("N (all other)", 1)])
    vs = verdict(res[("T_strict", 0)], res[("T_strict", 1)], res[("N (all other)", 0)], res[("N (all other)", 1)])
    vc = verdict(res[("T (trade orders)", 0)], res[("T (trade orders)", 1)], res[("N_clean", 0)], res[("N_clean", 1)])
    print("\nVERDICT (registered rule): %s" % v)
    print("SENSITIVITY 1 (T without %s): %s" % (STRICT_DROP, vs))
    print("SENSITIVITY 2 (N_clean: N without the %d days directly after a T day): %s%s" % (len(N) - len(Nc), vc, "" if vc == v else "   <- differs from the registered verdict: report as contamination, the registered verdict stands"))
    print("REGISTERED PREDICTIONS: T day +1 1.30 (1.10-1.60) | N day +1 1.05 (0.95-1.20) | P(CARRIED) 55%, P(BROAD) 20%, P(NEITHER) 25% | 28 T days")
    print("total %.0fs" % (time.time() - t0))
    return res, v, vs, sc, vc


if __name__ == "__main__":
    main()
