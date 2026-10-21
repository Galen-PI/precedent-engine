#!/usr/bin/env python3
"""
earnings_role_band_test.py -- READ-ONLY (matrices, the OHLC cache, the database for 8-K filings and recorded events). Writes nothing.
THE QUESTION. The card's earnings band uses one multiplier for day 0 and one for day +1 because the filing table has no release time. earnings_timing_check.py found that, given the company's habit, the reaction day
is about 3.7x the ordinary scale and the other day about 1.35x, and earnings_timing_recency.py found that the habit can be predicted from earlier quarters (majority of the last 4 classifiable quarters: 88.8% agreement overall,
93.1% where the gap is clean). Would BANDS built on that role beat the pooled day-0 / day +1 bands OUT OF SAMPLE?
METHOD (walk-forward, like band_calibrate.py). Units: band units on the ORDINARY scale (|miss| / (own spread x sqrt of the other stocks' mean squared standardized miss that day)), which is the card's band without its event
multiplier; with a constant multiplier per group, the calibrated edge in the card's units times the multiplier equals the 90th percentile of |band units| in ordinary units, so a group's edge here is simply the 90th percentile of |band
units| over that group's earlier days. For each test year Y (from 2009) every group's edge is the 90th percentile over the years BEFORE Y (a group needs at least 500 earlier observations; a year is scored only if every group of
every model has them). Evaluated events: earnings releases (8-K item 2.02, day i = the first trading day on or after the filing date) from 2006 with NO own recorded event and NO Regulation FD filing on day i or i+1 (the card
treats those combinations separately), with a FORWARD HABIT: the majority timing (ties to the most recent) among the stock's last 4 EARLIER classifiable quarters (classifiable = an overnight gap of at least 2 own-sd on day i or i+1;
BMO if day i has the larger gap, AMC if day i+1). The reaction day is i for a BMO habit and i+1 for an AMC habit. Each event gives two observations (days i and i+1).
MODELS (each day's half-width is its group's edge): POOLED = two groups, day i and day i+1 (the card's structure); ROLES = two groups, habit-assigned reaction day and other day; FOUR = four groups (BMO or AMC habit x
reaction or other day); PLACEBO = the ROLES model with the habits shuffled at random across events (the same BMO share), which cannot carry real information.
SCORE: the interval score for a 90% band, IS = 2 x edge + (2 / 0.10) x max(|band units| - edge, 0) (the same score as the robust-stress test), averaged over all observations; and the coverage of each model on habit-assigned
reaction days and on other days, by era (2009-2012, 2013-2019, 2020-2026).
PRE-SET RULE (written before the first run): ROLE BANDS IMPROVE if, in EACH of the three eras, the mean interval score of ROLES is at least 2.0% below POOLED, AND ROLES coverage is within 88-92% on reaction days and on other days
in each era. The PLACEBO must not beat POOLED by 1% or more (ratio at least 0.99) in any era; a few tenths of a percent of noise either way is expected (on a synthetic world with random timing the ratios were 0.998-1.002); if it does beat POOLED
by 1% or more, the rule's verdict is void (the gain is an artifact). FOUR is descriptive.
PREDICTIONS (before the run): POOLED covers habit-assigned reaction days only 78-86% and other days 96-99.5% (calibrated on average but not conditionally); ROLES covers each 88-92%; the ROLES / POOLED interval-score ratio is 0.88-0.97
in each era; FOUR improves on ROLES by a further 0.3-2%; the PLACEBO ratio is 0.995-1.08; about 65-80% of isolated earnings events have a forward habit; verdict ROLE BANDS IMPROVE (probability about 70%).
Usage:   python3 -u scripts/card/earnings_role_band_test.py       Needs: data_cache/audit_matrices.npz, data_cache/ohlc, the database.
LIMIT: the choice of 'last 4' came from the recency test on the same years (last 3 / 4 / 8 were within 0.1 point of each other), and band units come from the same matrices the card uses, so this is an out-of-sample test of the
EDGES, not of the matrices; a forward use also needs the filing date known in advance (earnings dates are scheduled, but the 8-K date is only certain once filed).
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
GAP_WIN, GAP_MIN, MAX_GAP, CLASSIFY_Z = etc.GAP_WIN, etc.GAP_MIN, etc.MAX_GAP, etc.CLASSIFY_Z
FIRST_TEST_YEAR = 2009
MIN_PRIOR = 500
HIST = 4
ALPHA, Q = 0.10, 0.90
IMPROVE_BY = 0.02
PLACEBO_MIN = 0.99
LOW, HIGH = 0.88, 0.92
ERAS = [("2009-2012", 2009, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]
SEED = 20261021


def pct(x):
    return "%5.1f%%" % (100.0 * x) if np.isfinite(x) else "  n/a "


def majority(v):
    s, m = sum(v), len(v)
    return 1 if 2 * s > m else (0 if 2 * s < m else v[-1])


def main():
    t0 = time.time()
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E, SD = d["dates"], d["ids"].tolist(), d["E"], d["SD"]
    N, n = E.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    with np.errstate(invalid="ignore", divide="ignore"):
        Zsq = (E.astype(np.float64) / SD.astype(np.float64)) ** 2
    valid = np.isfinite(Zsq)
    S = np.where(valid, Zsq, 0.0).sum(axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        bu = np.sqrt(Zsq / qo)
    bu[~((cnt[None, :] > 20) & np.isfinite(bu))] = np.nan

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
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids))
    oth = np.zeros((N, n), dtype=bool)                                   # own recorded event or Regulation FD filing flagged
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                oth[k, t] = True
    raw = defaultdict(list)
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is None:
            continue
        its = dc.parse_items(r.get("item_codes"))
        i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
        if i >= n:
            continue
        if "2.02" in its:
            raw[k].append(i)
        elif "7.01" in its:
            oth[k, i] = True
            if i + 1 < n:
                oth[k, i + 1] = True

    # events with a forward habit ---------------------------------------------------------------------------------------------------------------------------------
    rec = []                             # (year, |bu| day i, |bu| day i+1, habit)
    n_iso = n_all = 0
    for k, lst in raw.items():
        keep = []
        for i in sorted(lst):
            if not keep or i - keep[-1] >= 20:
                keep.append(i)
        hist = []
        for i in keep:
            if i < GAP_WIN + 1 or i + 1 >= n or years[i] < TEST_START:
                continue
            a, b = ZG[k, i], ZG[k, i + 1]
            habit = majority(hist[-HIST:]) if len(hist) >= HIST else None
            isolated = not (oth[k, i] or oth[k, i + 1])
            b0, b1 = bu[k, i], bu[k, i + 1]
            if isolated and np.isfinite(b0) and np.isfinite(b1):
                n_iso += 1
                if habit is not None:
                    rec.append((int(years[i]), abs(float(b0)), abs(float(b1)), habit))
            if np.isfinite(a) and np.isfinite(b) and max(a, b) >= CLASSIFY_Z:
                hist.append(1 if b > a else 0)
    ev_year = np.array([r[0] for r in rec])
    ev_b0, ev_b1, ev_h = np.array([r[1] for r in rec]), np.array([r[2] for r in rec]), np.array([r[3] for r in rec])
    print("isolated earnings events from %d: %d | with a forward habit (at least %d earlier classifiable quarters): %d (%s) | %.0fs" % (TEST_START, n_iso, HIST, len(rec), pct(len(rec) / max(n_iso, 1)), time.time() - t0), flush=True)
    print("  habit-assigned BMO share among those events: %s" % pct(float(1 - ev_h.mean())))

    # observations: two per event ---------------------------------------------------------------------------------------------------------------------------------
    def obs_arrays(h):
        yr = np.concatenate([ev_year, ev_year])
        val = np.concatenate([ev_b0, ev_b1])
        day = np.concatenate([np.zeros(len(ev_h), dtype=int), np.ones(len(ev_h), dtype=int)])        # 0 = day i, 1 = day i+1
        hh = np.concatenate([h, h])
        reaction = (day == hh).astype(int)                                                           # habit 0 (BMO): reaction on day i; habit 1 (AMC): reaction on day i+1  -> reaction = (day == habit)
        g_pool = day
        g_roles = 1 - reaction                                                                       # 0 = reaction day, 1 = other day
        g_four = hh * 2 + g_roles                                                                    # (habit, role)
        return yr, val, g_pool, g_roles, g_four, reaction

    yr, val, g_pool, g_roles, g_four, reaction = obs_arrays(ev_h)
    rng = np.random.RandomState(SEED)
    h_plc = rng.permutation(ev_h)
    _, _, _, g_plc, _, _ = obs_arrays(h_plc)

    models = {"POOLED": (g_pool, 2), "ROLES": (g_roles, 2), "FOUR": (g_four, 4), "PLACEBO": (g_plc, 2)}
    acc = {}                                                    # (era, model) -> dict of sums
    skipped = []
    for Y in range(FIRST_TEST_YEAR, int(yr.max()) + 1):
        tr, te = yr < Y, yr == Y
        if te.sum() < 50:
            continue
        edges, ok = {}, True
        for name, (g, ng) in models.items():
            e = []
            for gi in range(ng):
                v = val[tr & (g == gi)]
                if len(v) < MIN_PRIOR:
                    ok = False
                    break
                e.append(float(np.quantile(v, Q)))
            edges[name] = np.array(e) if ok else None
            if not ok:
                break
        if not ok:
            skipped.append(Y)
            continue
        era = next((lab for lab, lo, hi in ERAS if lo <= Y <= hi), None)
        if era is None:
            continue
        for name, (g, ng) in models.items():
            ed = edges[name][g[te]]
            v = val[te]
            cov = (v <= ed).astype(float)
            sc = 2.0 * ed + (2.0 / ALPHA) * np.maximum(v - ed, 0.0)
            r_te = reaction[te]
            a = acc.setdefault((era, name), defaultdict(float))
            a["n"] += len(v)
            a["cov_R"] += cov[r_te == 1].sum()
            a["nR"] += (r_te == 1).sum()
            a["cov_N"] += cov[r_te == 0].sum()
            a["nN"] += (r_te == 0).sum()
            a["IS"] += sc.sum()
            a["half"] += ed.sum()
    if skipped:
        print("  test years skipped (a group had fewer than %d earlier observations): %s" % (MIN_PRIOR, ", ".join(str(y) for y in skipped)))

    print("\nWALK-FORWARD RESULTS (edges from earlier years only; coverage by the habit-assigned role; IS = mean interval score in band units, lower is better)")
    print("  %-10s %-8s %7s | %9s %9s | %8s %8s | %s" % ("era", "model", "obs", "cov reac.", "cov other", "mean IS", "half-w", "IS ratio vs POOLED"))
    ratios = {}
    for lab, _, _ in ERAS + [("all", 0, 0)]:
        eras = [e[0] for e in ERAS] if lab == "all" else [lab]
        for name in models:
            tot = defaultdict(float)
            for e_ in eras:
                for k_, v_ in acc.get((e_, name), {}).items():
                    tot[k_] += v_
            if tot["n"] == 0:
                continue
            base = defaultdict(float)
            for e_ in eras:
                for k_, v_ in acc.get((e_, "POOLED"), {}).items():
                    base[k_] += v_
            ratio = (tot["IS"] / tot["n"]) / (base["IS"] / base["n"])
            ratios[(lab, name)] = ratio
            print("  %-10s %-8s %7d | %9s %9s | %8.3f %8.3f | %s" % (lab, name, int(tot["n"]), pct(tot["cov_R"] / max(tot["nR"], 1)), pct(tot["cov_N"] / max(tot["nN"], 1)), tot["IS"] / tot["n"], tot["half"] / tot["n"], "%.3f" % ratio if name != "POOLED" else "1.000"))

    print("\nREADING (pre-set rule)")
    improve, void = True, False
    for lab, _, _ in ERAS:
        r = ratios.get((lab, "ROLES"))
        p = ratios.get((lab, "PLACEBO"))
        a = acc.get((lab, "ROLES"))
        if r is None or a is None:
            improve = False
            continue
        cr, cn = a["cov_R"] / max(a["nR"], 1), a["cov_N"] / max(a["nN"], 1)
        ok_cov = LOW <= cr <= HIGH and LOW <= cn <= HIGH
        ok_is = r <= 1.0 - IMPROVE_BY
        if not (ok_cov and ok_is):
            improve = False
        if p is not None and p < PLACEBO_MIN:
            void = True
        print("  %-10s ROLES / POOLED interval score %.3f (needs <= %.3f: %s) | ROLES coverage reaction %s, other %s (needs %.0f-%.0f%%: %s) | PLACEBO ratio %s" % (
            lab, r, 1.0 - IMPROVE_BY, "yes" if ok_is else "no", pct(cr), pct(cn), 100 * LOW, 100 * HIGH, "yes" if ok_cov else "no", "%.3f" % p if p is not None else "n/a"))
    print("  VERDICT: %s%s" % ("ROLE BANDS IMPROVE" if improve else "ROLE BANDS DO NOT clear the rule", " -- VOID: the placebo beat POOLED by 1% or more in at least one era, so the gain is not attributable to the habit" if void else ""))
    print("\ntotal %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
