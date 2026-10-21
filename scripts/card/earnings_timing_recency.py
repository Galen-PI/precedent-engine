#!/usr/bin/env python3
"""
earnings_timing_recency.py -- READ-ONLY (matrices, the OHLC cache, the database for 8-K filings). Writes nothing. Companion of earnings_timing_check.py and earnings_timing_diagnostics.py.
WHAT THE DIAGNOSTICS LEFT OPEN. Leave-one-out habit agreement was 85.0% (89.6% even where the larger gap is at least 5 own-sd, 77.9% where it is 2-3), and it rose by year from 76-79% in 2006-2008 to about 90% in 2019 with a dip to 82%
in 2020. A gap of 5 own-sd is almost surely the earnings reaction, so a mismatch there means the reaction day relative to the FILING DATE differs from the stock's pooled habit: either habits drift over time (companies change
release timing, or when they file the 8-K) or the pattern flips quarter to quarter (TSLA files sometimes the evening of the release and sometimes the next morning: its largest gap is on day i 38% and on day i+1 38% of the time).
THE TEST. For each stock, classifiable earnings events in time order (classifiable = a gap of at least 2 own overnight-gap sd on day i or i+1, BMO if day i is larger, AMC if i+1; the same definitions as the check). Predict each
event's own classification from EARLIER quarters only, which is all a forecast could use: LAST1 (the previous quarter), LAST3 and LAST4 and LAST8 (the majority of the last 3 / 4 / 8, ties go to the most recent), ALLPAST (the majority of
all earlier ones, at least 8). Compared on the SAME events (those with at least 8 earlier classifiable quarters) with POOLED (the check's leave-one-out majority over the stock's other quarters on both sides in time, which a
forecast could not use). Reported: agreement overall, by the event's own gap strength (2-3, 3-5, 5 or more sd) and by era; the SWITCH RATE between consecutive classifiable quarters where BOTH have a gap of at least 5 sd
(clean pairs), overall and by era of the later quarter; and the twelve stocks with the highest switch rate (at least 8 clean pairs).
PRE-SET READING: HABIT DRIFT is SUPPORTED if the best forward rule (the best of LAST3, LAST4, LAST8) beats POOLED by at least 3 points overall (the decisive test: the pooled rule is the best a time-blind habit can do, so a forward
rule that beats it must be tracking change over time; it does NOT depend on WHEN the change happens). The switch rate by era is printed as a descriptive line only. FORWARD HABITS ARE USABLE if the best forward rule reaches at least 90%
agreement among events whose own gap is at least 5 sd. Both verdicts are printed; neither changes the earlier NOT VALID verdict of the check. (An earlier draft of the rule also required the switch rate to be higher in 2006-2012 than
in 2013-2019; it was dropped before any real run because it assumed the direction seen in the by-year agreement and would miss drift that happens later. Validated on synthetic worlds with a planted flip.)
PREDICTIONS (before the run): on the shared events POOLED reads about 86-88% and the best forward rule (most likely LAST4 or LAST8) 87-92%, so HABIT DRIFT is supported with probability about 45%; in the 5-or-more tier the best
forward rule reads 91-95%; clean-pair switch rate 5-9% overall, higher in 2006-2012 than in 2013-2019 (probability about 55%); TSLA is among the highest-switch stocks with a rate of 30% or more; LAST1 is the weakest forward rule.
Usage:   python3 -u scripts/card/earnings_timing_recency.py       Needs: data_cache/audit_matrices.npz, data_cache/ohlc, the database.
"""
import os, sys, time, bisect, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc
import earnings_timing_check as etc

CACHE_FILE = uc.CACHE_FILE
TEST_START = etc.TEST_START
GAP_WIN, GAP_MIN, MAX_GAP, CLASSIFY_Z, MIN_OTHERS = etc.GAP_WIN, etc.GAP_MIN, etc.MAX_GAP, etc.CLASSIFY_Z, etc.MIN_OTHERS
MIN_PAST = 8
CLEAN_Z = 5.0
TIERS = [(2.0, 3.0), (3.0, 5.0), (5.0, 1e9)]
ERAS = [("2006-2012", 2006, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]
RULES = ["LAST1", "LAST3", "LAST4", "LAST8", "ALLPAST"]


def pct(x):
    return "%5.1f%%" % (100.0 * x) if np.isfinite(x) else "  n/a "


def majority(v):
    v = list(v)
    s = sum(v)
    if 2 * s > len(v):
        return 1
    if 2 * s < len(v):
        return 0
    return v[-1]                      # a tie goes to the most recent quarter


def main():
    t0 = time.time()
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, tickers, E, SD = d["dates"], d["ids"].tolist(), [str(x) for x in d["tickers"]], d["E"], d["SD"]
    N, n = E.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    O, C, have = etc.load_ohlc(ids, dl)
    G = np.full((N, n), np.nan)
    G[:, 1:] = O[:, 1:] / C[:, :-1] - 1.0
    G[np.abs(G) > MAX_GAP] = np.nan
    V = np.isfinite(G)
    X = np.where(V, G, 0.0)
    z = np.zeros((N, 1))
    c1, c2, cc = (np.concatenate([z, np.cumsum(a_, axis=1)], axis=1) for a_ in (X, X * X, V))
    S1, S2, Cn = c1[:, GAP_WIN:n] - c1[:, :n - GAP_WIN], c2[:, GAP_WIN:n] - c2[:, :n - GAP_WIN], cc[:, GAP_WIN:n] - cc[:, :n - GAP_WIN]
    with np.errstate(invalid="ignore", divide="ignore"):
        var = (S2 - S1 * S1 / Cn) / (Cn - 1)
    GSD = np.full((N, n), np.nan)
    GSD[:, GAP_WIN:] = np.where(Cn >= GAP_MIN, np.sqrt(np.maximum(var, 0.0)), np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        ZG = np.abs(G) / GSD

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    raw = defaultdict(list)
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is None or "2.02" not in dc.parse_items(r.get("item_codes")):
            continue
        i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
        if i < n:
            raw[k].append(i)
    series = {}
    for k, lst in raw.items():
        keep = []
        for i in sorted(lst):
            if not keep or i - keep[-1] >= 20:
                keep.append(i)
        rows = []
        for i in keep:
            if i >= GAP_WIN + 1 and i + 1 < n and years[i] >= TEST_START:
                a, b = ZG[k, i], ZG[k, i + 1]
                if np.isfinite(a) and np.isfinite(b) and max(a, b) >= CLASSIFY_Z:
                    rows.append((i, 1 if b > a else 0, max(a, b)))
        if rows:
            series[k] = rows
    n_cls = sum(len(v) for v in series.values())
    print("stocks with classifiable earnings events: %d | classifiable events %d | %.0fs" % (len(series), n_cls, time.time() - t0), flush=True)

    # forward rules and the pooled leave-one-out rule on the same events ------------------------------------------------------------------------------------------
    res = defaultdict(list)             # rule -> list of (agree, zmax, year)
    for k, rows in series.items():
        tg = [r[1] for r in rows]
        for j in range(MIN_PAST, len(rows)):
            past = tg[:j]
            own, zm, yr = tg[j], rows[j][2], years[rows[j][0]]
            preds = {"LAST1": past[-1], "LAST3": majority(past[-3:]), "LAST4": majority(past[-4:]), "LAST8": majority(past[-8:]), "ALLPAST": majority(past)}
            others = tg[:j] + tg[j + 1:]
            preds["POOLED"] = majority(others) if sum(others) * 2 != len(others) else 1
            for name, p in preds.items():
                res[name].append((int(p == own), zm, yr))
    names = RULES + ["POOLED"]
    nev = len(res["LAST1"])
    print("\nAGREEMENT ON THE SAME %d EVENTS (those with at least %d earlier classifiable quarters); a forward rule uses earlier quarters only, POOLED also uses later ones" % (nev, MIN_PAST))
    print("  %-9s %8s | %9s %9s %9s | %s" % ("rule", "overall", "2-3 sd", "3-5 sd", "5+ sd", "by era: " + "  ".join(e[0] for e in ERAS)))
    best_name, best_val = None, -1.0
    for name in names:
        arr = np.array(res[name], dtype=float)
        ov = float(arr[:, 0].mean())
        tiers = [float(arr[(arr[:, 1] >= lo) & (arr[:, 1] < hi), 0].mean()) if ((arr[:, 1] >= lo) & (arr[:, 1] < hi)).any() else float("nan") for lo, hi in TIERS]
        eras = [float(arr[(arr[:, 2] >= lo) & (arr[:, 2] <= hi), 0].mean()) if ((arr[:, 2] >= lo) & (arr[:, 2] <= hi)).any() else float("nan") for _, lo, hi in ERAS]
        print("  %-9s %8s | %9s %9s %9s | %s" % (name, pct(ov), pct(tiers[0]), pct(tiers[1]), pct(tiers[2]), "  ".join(pct(x) for x in eras)))
        if name in ("LAST3", "LAST4", "LAST8") and ov > best_val:
            best_name, best_val = name, ov
    pooled = float(np.array(res["POOLED"], dtype=float)[:, 0].mean())
    arr_b = np.array(res[best_name], dtype=float)
    best5 = float(arr_b[arr_b[:, 1] >= CLEAN_Z, 0].mean())

    # switch rate between consecutive clean quarters ------------------------------------------------------------------------------------------------------------
    sw, tot = defaultdict(int), defaultdict(int)
    per_stock = {}
    for k, rows in series.items():
        s_, t_ = 0, 0
        for j in range(1, len(rows)):
            if rows[j][2] >= CLEAN_Z and rows[j - 1][2] >= CLEAN_Z:
                sw_ = int(rows[j][1] != rows[j - 1][1])
                yr = int(years[rows[j][0]])
                for lab, lo, hi in ERAS:
                    if lo <= yr <= hi:
                        sw[lab] += sw_
                        tot[lab] += 1
                sw["all"] += sw_
                tot["all"] += 1
                s_ += sw_
                t_ += 1
        if t_ >= 8:
            per_stock[tickers[k]] = (s_ / t_, t_)
    print("\nSWITCH RATE between consecutive classifiable quarters when BOTH have a gap of at least %.0f own-sd (clean pairs): the share where the timing flips" % CLEAN_Z)
    print("  " + " | ".join("%s %s (%d pairs)" % (lab, pct(sw[lab] / max(tot[lab], 1)), tot[lab]) for lab in ["all"] + [e[0] for e in ERAS]))
    top = sorted(per_stock.items(), key=lambda kv: -kv[1][0])[:12]
    print("  the twelve stocks with the highest switch rate (at least 8 clean pairs): " + " | ".join("%s %.0f%% (%d)" % (t, 100 * v[0], v[1]) for t, v in top))
    if "TSLA" in per_stock:
        print("  TSLA: %.0f%% of %d clean pairs" % (100 * per_stock["TSLA"][0], per_stock["TSLA"][1]))

    s_early, s_mid = sw["2006-2012"] / max(tot["2006-2012"], 1), sw["2013-2019"] / max(tot["2013-2019"], 1)
    drift = best_val - pooled >= 0.03
    print("\nREADING (pre-set rules)")
    print("  HABIT DRIFT: %s (best forward rule %s %s vs pooled %s = %+.1f points, threshold 3)" % ("SUPPORTED" if drift else "NOT supported", best_name, pct(best_val), pct(pooled), 100 * (best_val - pooled)))
    print("  (descriptive: switch rate between clean pairs 2006-2012 %s vs 2013-2019 %s = %+.1f points)" % (pct(s_early), pct(s_mid), 100 * (s_early - s_mid)))
    print("  FORWARD HABITS USABLE: %s (best forward rule %s reads %s among events whose own gap is at least %.0f sd; threshold 90%%)" % ("YES" if best5 >= 0.90 else "NO", best_name, pct(best5), CLEAN_Z))
    print("\ntotal %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
