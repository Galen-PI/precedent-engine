#!/usr/bin/env python3
"""
tone_data_check.py -- READ-ONLY, local caches only (data_cache/audit_matrices.npz and data_cache/gdelt_ac_tone.npz; no database). Writes nothing. A DATA DIAGNOSTIC, not a lane test: no verdict row.
WHY. tone_lane_test.py found NO LANE, but also that a 2-sd tone shock does not even track the SAME day's miss: after POS flags the stock's day-t-1 miss was positive 50% / 49% of the time, after NEG flags 48% / 49% (sampling error about 0.5 points). My prediction was 58-70% / 30-42%, so either the
series is uninformative or the construction hides a relationship. Candidates: (1) SYSTEM-WIDE tone days dilute the flag (the miss is idiosyncratic, the flag is not demeaned across stocks; NEG flags are 1.57x as frequent as POS); (2) tone on small article counts is composition noise; (3) the tone is misaligned by a day; (4) a loader problem.
WHAT IT MEASURES (all days with a tone z-score and a band unit, events and earnings days INCLUDED on purpose: a validity check wants the strongest chance of seeing a relationship): the rank (Spearman) correlation between the tone z-score on day t and the SIGNED band unit on day t+L for L = -3..+3, computed within each calendar year; an era figure is the mean of the
yearly correlations with its standard error across years (about 6 years per era). Then, at L = 0: by article-count stratum (3-4, 5-9, 10-29, 30+); the day-effect share of tone variance (R-squared of day means) and the correlation of DEMEANED tone (tone z minus that day's cross-sectional mean, on days with at least 20 stocks) with the same-day and next-day miss;
and how clustered the flags are (the share of POS / NEG flags on days when at least 10% of covered stocks carry the same flag).
READING GUIDE (written before the real run). ALIGNMENT PROBLEM if in BOTH eras the largest |correlation| over L = -3..+3 is away from L = 0 and exceeds the L = 0 value by at least 0.01. NOISE DILUTION if the same-day correlation rises across the four count strata and the 30+ stratum reads at least 0.03. SYSTEMATIC DILUTION if demeaned tone's same-day
correlation exceeds raw tone's by at least 0.01 in both eras. UNINFORMATIVE if every same-day correlation (raw, demeaned, each stratum) lies within +-0.01. These can co-occur; none of them is a lane. A follow-up lane test, if any, is a NEW ledger row with its own pre-set rule; gdelt_tone_shock_next_day_direction stays as recorded.
PREDICTIONS (before the real run): same-day raw correlation 0.00 to +0.04 in both eras; the lag profile peaks at L = 0; day effects explain 10-30% of tone variance; at least 30% of NEG flags sit on clustered days; demeaned tone correlates higher than raw (by 0.01-0.03); the 30+ stratum reads 0.02-0.08. Probabilities: a clear alignment problem 10%; noise or systematic dilution 50%; everything about zero 40%.
Usage:   python3 -u scripts/card/tone_data_check.py       Needs data_cache/audit_matrices.npz and data_cache/gdelt_ac_tone.npz (written by tone_lane_test.py).
"""
import os, sys, time, warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import unrecorded_candidates as uc
import tone_lane_test as tlt

ERAS = [("2015-2020", 2015, 2020), ("2021-2026", 2021, 2026)]
LAGS = [-3, -2, -1, 0, 1, 2, 3]
STRATA = [(3, 4), (5, 9), (10, 29), (30, 10 ** 9)]
CACHE_FILE = uc.CACHE_FILE
TONE_CACHE = tlt.TONE_CACHE


def spearman(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 200:
        return np.nan, int(ok.sum())
    ra = np.argsort(np.argsort(a[ok])).astype(float)
    rb = np.argsort(np.argsort(b[ok])).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1]), int(ok.sum())


def lagged(A, B, L):
    """pairs (A[:, t], B[:, t+L]) and the tone-day index of each column."""
    n = A.shape[1]
    if L >= 0:
        return A[:, :n - L], B[:, L:], np.arange(0, n - L)
    return A[:, -L:], B[:, :n + L], np.arange(-L, n)


def yearly(A, B, L, years, lo, hi, mask=None):
    a, b, tidx = lagged(A, B, L)
    ys = years[tidx]
    out = []
    for y in range(lo, hi + 1):
        s = ys == y
        if not s.any():
            continue
        aa, bb = a[:, s], b[:, s]
        if mask is not None:
            m = mask[:, tidx][:, s]
            aa = np.where(m, aa, np.nan)
        c, nn = spearman(aa.ravel(), bb.ravel())
        if np.isfinite(c):
            out.append(c)
    out = np.array(out)
    return (out.mean(), out.std(ddof=1) / np.sqrt(len(out)) if len(out) > 1 else np.nan, len(out)) if len(out) else (np.nan, np.nan, 0)


def main():
    t0 = time.time()
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, E_, SD = d["dates"], d["E"].astype(np.float64), d["SD"].astype(np.float64)
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    N, n = E_.shape
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = E_ / SD
    Zsq = Z ** 2
    valid = np.isfinite(Zsq)
    S = np.where(valid, Zsq, 0.0).sum(axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        sbu = Z / np.sqrt(qo)
    sbu[~((cnt[None, :] > 20) & np.isfinite(sbu))] = np.nan
    c = np.load(TONE_CACHE, allow_pickle=False)
    AC, TN = c["AC"], c["TN"]
    assert AC.shape == (N, n), "the tone cache does not match the matrices"
    Zt = np.full((N, n), np.nan)
    for k in range(N):
        Zt[k] = tlt.tone_z(TN[k], AC[k])
    print("stock-days with a tone z-score %d | with a band unit as well %d | %.0fs" % (np.isfinite(Zt).sum(), (np.isfinite(Zt) & np.isfinite(sbu)).sum(), time.time() - t0), flush=True)
    print("\nLAG PROFILE: rank correlation of tone z (day t) with the signed band unit on day t+L; mean of yearly values +- standard error across years")
    prof = {}
    for lab, lo, hi in ERAS:
        prof[lab] = {L: yearly(Zt, sbu, L, years, lo, hi) for L in LAGS}
    print("  L     " + "    ".join("%-18s" % e[0] for e in ERAS))
    for L in LAGS:
        print("  %+d    " % L + "    ".join("%+.4f +- %.4f   " % (prof[e[0]][L][0], prof[e[0]][L][1]) for e in ERAS))
    peak = {lab: max(LAGS, key=lambda L: abs(prof[lab][L][0])) for lab, _, _ in ERAS}
    align = all(peak[lab] != 0 and abs(prof[lab][peak[lab]][0]) - abs(prof[lab][0][0]) >= 0.01 for lab, _, _ in ERAS)
    print("  largest |correlation| at L = %s -> ALIGNMENT PROBLEM: %s" % (", ".join("%+d (%s)" % (peak[l], l) for l, _, _ in ERAS), "YES" if align else "no"))

    print("\nSAME-DAY (L = 0) BY ARTICLE-COUNT STRATUM (all days of the era pooled)")
    strat = {}
    for lab, lo, hi in ERAS:
        em = ((years >= lo) & (years <= hi))[None, :]
        row = []
        for a, b in STRATA:
            m = em & (AC >= a) & (AC <= b)
            r, nn = spearman(np.where(m, Zt, np.nan).ravel(), sbu.ravel())
            row.append((r, nn))
        strat[lab] = row
        print("  %s: " % lab + " | ".join("%s articles: %+.4f (n %d)" % (("%d-%d" % (a, b)) if b < 10 ** 8 else "%d+" % a, r, nn) for (a, b), (r, nn) in zip(STRATA, row)))
    noise = all(strat[lab][3][0] >= 0.03 and strat[lab][3][0] > strat[lab][0][0] for lab, _, _ in ERAS)
    print("  rises with count and the 30+ stratum reads >= 0.03 in both eras -> NOISE DILUTION: %s" % ("YES" if noise else "no"))

    dc = np.isfinite(Zt).sum(axis=0)
    dm = np.where(dc >= 20, np.nanmean(Zt, axis=0), np.nan)
    Zd = Zt - dm[None, :]
    ok = np.isfinite(Zd)
    r2 = 1.0 - np.nanvar(Zd[ok]) / np.nanvar(Zt[ok])
    print("\nSYSTEMATIC COMPONENT: the day's cross-sectional mean explains %.1f%% of the variance of tone z (days with >= 20 covered stocks)" % (100 * r2))
    dem = {}
    for lab, lo, hi in ERAS:
        dem[lab] = (yearly(Zd, sbu, 0, years, lo, hi), yearly(Zd, sbu, 1, years, lo, hi))
        print("  %s: DEMEANED tone vs same-day miss %+.4f +- %.4f (raw %+.4f) | vs next-day miss %+.4f +- %.4f (raw %+.4f)" % (lab, dem[lab][0][0], dem[lab][0][1], prof[lab][0][0], dem[lab][1][0], dem[lab][1][1], prof[lab][1][0]))
    syst = all(dem[lab][0][0] - prof[lab][0][0] >= 0.01 for lab, _, _ in ERAS)
    print("  demeaned same-day correlation exceeds raw by >= 0.01 in both eras -> SYSTEMATIC DILUTION: %s" % ("YES" if syst else "no"))

    print("\nFLAG CLUSTERING (days with >= 20 covered stocks)")
    big = dc >= 20
    for nm, fl in (("NEG (z <= -2)", Zt <= -tlt.TONE_Z), ("POS (z >= +2)", Zt >= tlt.TONE_Z)):
        fl = fl & np.isfinite(Zt)
        frac = np.where(big, fl.sum(axis=0) / np.maximum(dc, 1), np.nan)
        cl = big & (frac >= 0.10)
        tot = fl[:, big].sum()
        print("  %s: median share of covered stocks flagged %.1f%%, 99th percentile %.1f%% | %d days have >= 10%% flagged and hold %.1f%% of all such flags" % (nm, 100 * np.nanmedian(frac), 100 * np.nanpercentile(frac, 99), int(cl.sum()), 100 * fl[:, cl].sum() / max(tot, 1)))
    uninf = all(abs(prof[lab][0][0]) <= 0.01 and abs(dem[lab][0][0]) <= 0.01 and all(abs(r) <= 0.01 for r, _ in strat[lab] if np.isfinite(r)) for lab, _, _ in ERAS)
    print("\nEVERY same-day correlation (raw, demeaned, each stratum) within +-0.01 in both eras -> UNINFORMATIVE: %s" % ("YES" if uninf else "no"))
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
