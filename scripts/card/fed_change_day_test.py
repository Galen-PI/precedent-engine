#!/usr/bin/env python3
"""
fed_change_day_test.py -- READ-ONLY (database: macro_long DFEDTAR / DFEDTARU and sector_day_z). Writes nothing. T3a of the historical line.
QUESTION. On the days the Fed CHANGES its target rate, do rate-sensitive sectors move more than the rest of the market that day? An EXPLANATION lane (same-day, known after the fact), not a forecast. LIMIT: the database holds only change days, not meetings that held, so a change day cannot be told apart from an FOMC meeting day:
any amplification could be the meeting, not the change. Wording: 'on Fed target-change days'.
EVENTS. Days the target changed, 2004 onward: DFEDTAR up to 2008-12-15 and DFEDTARU from 2008-12-16 as one series (the move to the zero bound on 2008-12-16 counts). Eras A = 2004-2008 (27 changes) and B = 2015-2026 (32 changes); 2009-2014 has none. A date maps to the first trading day on or after it.
STATISTIC. sector_day_z (sector, day, n, mean_z): mean_z is the sector's mean |return| / own prior 64-day volatility that day, n its stock count. For sector s: LR(t) = log(mean_z_s(t) / mean_z_rest(t)), the rest = all other sectors weighted by n ('Unclassified' left out). For an event on day i and a window w: LD = LR(i+w) - mean of LR over BASELINE days
21 to 63 trading days away on either side, excluding any change day and the day after. AMPLIFICATION = exp(mean of LD over the era's events); SE = sd / sqrt(events). Primary window: day 0 (the 2:15 p.m. announcement); days -1 and +1 are descriptive.
PLACEBO (the calibration check before any reading): the same statistic on dates shifted +21 and -21 trading days from each change day (skipped when the shifted date is, or is next to, a change day). A placebo with |t| >= 2.5 in either era VOIDS the lane.
PRE-SET RULE (before any real run). PASS for Financials: amplification above 1 with t >= 2.5 in BOTH eras and both placebos clean. LEAD: t >= 2.0 in both eras (placebos clean). Otherwise NULL (no documented effect). Real Estate, Utilities and Health Care are DESCRIPTIVE with intervals; all 11 sectors are shown with the warning that 11 are looked at.
Health Care is NOT a clean control (it moved LESS on big yield days in the long-history lane: 0.857-0.905), so a reading below 1 there would replicate that, not validate the baseline.
CONFOUNDS reported, not hidden: (1) CRISIS CUTS: 2008-09-15..2009-06-30 and 2020-03-01..2020-06-30 are crisis regimes with their own financial-sector volatility; a version without those events is printed (descriptive). (2) HIKE vs CUT split for Financials (descriptive).
POWER (stated before the run): with about 27 and 32 events and a daily log-ratio noise of about 0.2-0.25, one era resolves an amplification of about 10-12% at t 2.5; a true 1.10 gives roughly a coin flip per era; a null excludes only effects above about 1.12-1.15.
PREDICTIONS (before the run): Financials amplification 1.00-1.12 in both eras (PASS probability about 15%); Real Estate and Utilities 1.00-1.10; Health Care 0.93-1.05; placebos clean in both eras (probability about 90%); the crisis-excluded Financials estimate within 0.05 of the full one.
VALIDATION (synthetic worlds with the real change-day counts per year, 11 sectors, a common volatility factor and slow sector drifts; run before the real data): NO EFFECT: Financials 1.010 (t +0.48) / 0.982 (t -0.85), NULL, placebos 1.011 / 1.006. PLANTED 1.15x on Financials day 0: 1.156 (t 6.6) / 1.129 (t 5.7), PASS. CRISIS REGIME (Financials x1.35 during the two crisis windows, no Fed effect): 1.013 / 0.981, NULL; the crisis-excluded version agrees.
TWO ARTIFACTS TO KNOW: (1) when one sector is truly amplified, the OTHER sectors read about 2% below 1 (the rest-of-market includes it; Financials is 15% of stocks): that is the comparison, not a finding about them. (2) With 11 sectors and several subgroups, a chance cell at |t| 2.4 appears in a no-effect world (Health Care t +2.39; Financials cuts-only t -2.44); only the pre-set Financials day-0 cell can pass or fail.
Usage:   python3 -u scripts/card/fed_change_day_test.py
"""
import os, sys, bisect, time, warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import unrecorded_candidates as uc

ERAS = [("2004-2008", 2004, 2008), ("2015-2026", 2015, 2026)]
SECTORS = ["Communication Services", "Consumer Discretionary", "Consumer Staples", "Energy", "Financials", "Health Care", "Industrials", "Information Technology", "Materials", "Real Estate", "Utilities"]
PRIMARY, DESCRIPTIVE = "Financials", ["Real Estate", "Utilities", "Health Care"]
BASE_LO, BASE_HI, SHIFTS, MIN_BASE = 21, 63, (21, -21), 20
CRISIS = [("2008-09-15", "2009-06-30"), ("2020-03-01", "2020-06-30")]
T_PASS, T_LEAD, T_PLACEBO = 2.5, 2.0, 2.5


def load_sector_day(sb):
    rows = {}
    for s in SECTORS:
        rows[s] = list(uc.paged(lambda s=s: sb.table("sector_day_z").select("day,n,mean_z").eq("sector", s).order("day")))
    days = sorted({str(r["day"])[:10] for v in rows.values() for r in v})
    pos = {d: i for i, d in enumerate(days)}
    MZ, NN = np.full((len(SECTORS), len(days)), np.nan), np.full((len(SECTORS), len(days)), np.nan)
    for k, s in enumerate(SECTORS):
        for r in rows[s]:
            if r.get("mean_z") is not None and r.get("n"):
                MZ[k, pos[str(r["day"])[:10]]], NN[k, pos[str(r["day"])[:10]]] = float(r["mean_z"]), float(r["n"])
    return days, MZ, NN


def fed_changes(sb):
    def series(sid):
        return [(str(r["obs_date"])[:10], float(r["value"])) for r in uc.paged(lambda: sb.table("macro_long").select("obs_date,value").eq("series_id", sid).order("obs_date")) if r.get("value") is not None]
    comb = [x for x in series("DFEDTAR") if x[0] <= "2008-12-15"] + [x for x in series("DFEDTARU") if x[0] >= "2008-12-16"]
    out, prev = [], None
    for d, v in comb:
        if prev is not None and abs(v - prev) > 1e-9 and d >= "2004-01-01":
            out.append((d, 1 if v > prev else -1))
        prev = v
    return out


def log_ratio(MZ, NN, k):
    ok = np.isfinite(MZ) & np.isfinite(NN) & (NN > 0)
    num, den = np.where(ok, NN * MZ, 0.0).sum(axis=0), np.where(ok, NN, 0.0).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        rest = (num - np.where(ok[k], NN[k] * MZ[k], 0.0)) / (den - np.where(ok[k], NN[k], 0.0))
        lr = np.log(MZ[k] / rest)
    lr[~(ok[k] & np.isfinite(lr))] = np.nan
    return lr


def ld(lr, i, w, X):
    n = len(lr)
    j = i + w
    if not (0 <= j < n) or not np.isfinite(lr[j]):
        return None
    ids = [i + k for k in range(-BASE_HI, -BASE_LO + 1)] + [i + k for k in range(BASE_LO, BASE_HI + 1)]
    ids = [m for m in ids if 0 <= m < n and m not in X and np.isfinite(lr[m])]
    return None if len(ids) < MIN_BASE else float(lr[j] - np.mean(lr[ids]))


def summ(vals):
    a = np.array([v for v in vals if v is not None], dtype=float)
    if len(a) < 3:
        return len(a), float("nan"), float("nan"), float("nan")
    m, se = float(a.mean()), float(a.std(ddof=1) / np.sqrt(len(a)))
    return len(a), m, se, m / se if se > 0 else float("nan")


def fmt(r):
    n, m, se, t = r
    return "n %2d | %.3f [%.3f, %.3f] | t %+.2f" % (n, np.exp(m), np.exp(m - 1.96 * se), np.exp(m + 1.96 * se), t) if n >= 3 else "n %2d | too few" % n


def run(days, MZ, NN, ev):
    D = len(days)
    idx = [(bisect.bisect_left(days, d), s, d) for d, s in ev]
    idx = [(i, s, d) for i, s, d in idx if i < D]
    X = set()
    for i, _, _ in idx:
        X.update((i, i + 1))
    era_of = lambda d: next((lab for lab, lo, hi in ERAS if lo <= int(d[:4]) <= hi), None)
    in_crisis = lambda d: any(a <= d <= b for a, b in CRISIS)
    LR = {s: log_ratio(MZ, NN, k) for k, s in enumerate(SECTORS)}
    res = {}
    print("CHANGE DAYS: " + ", ".join("%s %d (hikes %d, cuts %d)" % (lab, sum(1 for _, s, d in idx if era_of(d) == lab), sum(1 for _, s, d in idx if era_of(d) == lab and s > 0), sum(1 for _, s, d in idx if era_of(d) == lab and s < 0)) for lab, _, _ in ERAS), flush=True)
    print("\nDAY 0 AMPLIFICATION vs the rest of the market (baseline days 21-63 away), by sector  [11 sectors are looked at: a few will look odd by chance]")
    print("  %-24s %-44s %s" % ("sector", ERAS[0][0], ERAS[1][0]))
    for s in SECTORS:
        cells = []
        for lab, _, _ in ERAS:
            r = summ([ld(LR[s], i, 0, X) for i, _, d in idx if era_of(d) == lab])
            res[(s, lab)] = r
            cells.append(fmt(r))
        print("  %-24s %-44s %s%s" % (s, cells[0], cells[1], "   <- PRIMARY" if s == PRIMARY else ("   (descriptive)" if s in DESCRIPTIVE else "")))
    print("\nFINANCIALS in detail (day 0 unless stated)")
    for lab, _, _ in ERAS:
        ev_l = [(i, s, d) for i, s, d in idx if era_of(d) == lab]
        for nm, sel in (("day -1", lambda e: ld(LR[PRIMARY], e[0], -1, X)), ("day +1", lambda e: ld(LR[PRIMARY], e[0], 1, X)),
                        ("excluding the crisis cuts", lambda e: None if in_crisis(e[2]) else ld(LR[PRIMARY], e[0], 0, X)),
                        ("hikes only", lambda e: ld(LR[PRIMARY], e[0], 0, X) if e[1] > 0 else None), ("cuts only", lambda e: ld(LR[PRIMARY], e[0], 0, X) if e[1] < 0 else None)):
            print("  %-10s %-26s %s" % (lab, nm, fmt(summ([sel(e) for e in ev_l]))))
    print("\nPLACEBO (dates shifted +21 and -21 trading days from each change day; skipped near a change day) for Financials, day 0")
    plc = {}
    for lab, _, _ in ERAS:
        vals = []
        for i, _, d in idx:
            if era_of(d) != lab:
                continue
            for sh in SHIFTS:
                j = i + sh
                if 0 <= j < D and not ({j - 1, j, j + 1} & X):
                    vals.append(ld(LR[PRIMARY], j, 0, X))
        plc[lab] = summ(vals)
        print("  %-10s %s" % (lab, fmt(plc[lab])))
    print("\nPOWER: one era resolves an amplification of about " + " / ".join("%s: %.1f%%" % (lab, 100 * (np.exp(T_PASS * res[(PRIMARY, lab)][2]) - 1)) for lab, _, _ in ERAS) + " at t 2.5 (Financials, from the observed spread)")
    f = [res[(PRIMARY, lab)] for lab, _, _ in ERAS]
    clean = all(abs(plc[lab][3]) < T_PLACEBO for lab, _, _ in ERAS)
    if not clean:
        verdict = "VOID: a placebo reads |t| >= 2.5 (the baseline does not calibrate)"
    elif all(x[1] > 0 and x[3] >= T_PASS for x in f):
        verdict = "PASS: Financials move more on Fed target-change days (explanation lane)"
    elif all(x[1] > 0 and x[3] >= T_LEAD for x in f):
        verdict = "LEAD (t >= 2.0 in both eras, below the pass line)"
    else:
        verdict = "NULL: no documented effect on Financials at this resolution"
    print("\nVERDICT (pre-set: Financials day 0, amplification above 1 with t >= 2.5 in BOTH eras and clean placebos; t >= 2.0 = lead): " + verdict)
    return res, plc, verdict


def main():
    t0 = time.time()
    sb = ew.get_sb()
    days, MZ, NN = load_sector_day(sb)
    ev = fed_changes(sb)
    print("sector-days %d x %d sectors | Fed change days found %d | %.0fs" % (len(days), len(SECTORS), len(ev), time.time() - t0), flush=True)
    out = run(days, MZ, NN, ev)
    print("total %.0fs" % (time.time() - t0))
    return out


if __name__ == "__main__":
    main()
