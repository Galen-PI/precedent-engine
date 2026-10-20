#!/usr/bin/env python3
"""
gap_audit.py -- READ-ONLY (local cache; the database is read once for the event days). The all-days GAP AUDIT: how much of what chapter 1 (market + sector)
leaves unexplained is SHARED across stocks (a missing factor: a sub-industry, an exposure, a theme) and how much is ISOLATED (company-specific)?

Usage:
    python3 -u scripts/card/gap_audit.py                (full run; builds and saves the residual matrices the first time, about 2 minutes)
    python3 -u scripts/card/gap_audit.py --rebuild      (rebuild the matrices from the price cache)
Needs:  data_cache/returns (the same cache as the validation scripts), numpy. Saves data_cache/audit_matrices.npz (ignored by git).

SETUP. Chapter 1's miss e (return beyond market and sector, fit on the prior 250 valid days) and its spread sd give a standardized miss z = e / sd for every
stock-day. Returns beyond +/-50% are skipped, as in the validation (59 stock-days; the audit therefore understates the very biggest days).

TEST B: STATISTICAL FACTORS (walk-forward, no labels needed). For each test year Y: take the previous TWO years of z (clipped at +/-5 for fitting only),
estimate the stock-by-stock correlation of misses (pairwise-complete), keep the top K principal components as factor LOADINGS. On each day of Y, estimate
the day's K factor values by least squares across the OTHER stocks and score each stock against its LEAVE-ONE-OUT fitted pull (the same way the sector factor
uses same-day peers). Nothing from year Y or later enters the loadings. K = 5 is the primary; K = 2 and K = 10 are reported as sensitivity, not as verdicts.
  Gain = change in R-squared against predicting zero, in raw return units: (sum e^2 - sum r^2) / sum y^2, the same measure layer 2 failed on (+0.02 needed).
PRE-SET RULES (written before the first run):
  ALL DAYS, K = 5:  EARNS ITS PLACE if the gain is >= +0.02 in EACH of 2005-2012, 2013-2019, 2020-2026 AND positive in >= 70% of test years. Otherwise it does not.
  STRESS DAYS (days when the cross-section's root-mean-square z is >= 1.5, defined in advance): reported with the same bar, needing >= 10 stress days per era and
  >= 5 per year counted; a pass here, with a fail on all days, is a LEAD (the structure exists on stress days only), not an 'earns its place'.
PREDICTIONS (before the run): all days does NOT clear +0.02 (stress days are a minority of days); stress days clear it in most eras; the ordinary-day gain is
  small (under +0.01). About a 40% chance I am wrong on the all-days call.

TEST C: COMPOSITION (descriptive). By regime (stress / ordinary), the share of the unexplained squared miss that sits in (a) stock-days with a recorded own
event, (b) big misses with no recorded event (|z| / day stress > 2), (c) the rest, and the share the K = 5 factors remove.
"""
import os, sys, math, time, warnings
from collections import deque, defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)       # all-NaN days (before the first valid fits) give harmless empty-slice warnings

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import decomp_validation as dv
import event_width_test as ew

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
STATS_START = "1995-01-01"
TEST_START = 2005
TRAIN_YEARS = 2
MIN_TRAIN_DAYS = 400
MIN_STOCK_TRAIN = 200
CLIP = 5.0
STRESS_LINE = 1.5
MIN_YEARS_ALL = 10          # a verdict needs at least this many test years (all days / ordinary days)
MIN_YEARS_STRESS = 8        # ... and this many years with >= 5 stress days (stress days)
MIN_STRESS_DAYS_ERA = 10    # ... and this many stress days in EACH era (stress days)
ERAS = [("2005-2012", 2005, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")


def residuals_for_stock(ret, rm, s, dates):
    n = len(dates)
    E = np.full(n, np.nan, dtype=np.float32)
    SD = np.full(n, np.nan, dtype=np.float32)
    Y = np.full(n, np.nan, dtype=np.float32)
    K = 3
    A = [[0.0] * K for _ in range(K)]
    b = [0.0] * K
    syy = 0.0
    win = deque()
    for t in range(1, n):
        y, xm, xs = ret[t], rm[t], s[t]
        if None in (y, xm, xs):
            continue
        row = (1.0, xm, xs)
        m = len(win)
        if m >= dv.MIN_EST and dates[t] >= STATS_START:
            c = dv.solve(A, b, [0, 1, 2])
            if c:
                E[t] = y - (c[1] * xm + c[2] * xs)
                sse1 = syy - (c[0] * b[0] + c[1] * b[1] + c[2] * b[2])
                SD[t] = math.sqrt(max(sse1, 1e-18) / (m - 3))
                Y[t] = y
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
    return E, SD, Y


def build_matrices():
    t0 = time.time()
    secs, _m = dv.load_cache()
    spy = [x for x in secs if x["ticker"] == "SPY"]
    if not spy:
        sys.exit("SPY is not in the cache.")
    master = list(spy[0]["dates"])
    pos = {d: i for i, d in enumerate(master)}
    n = len(master)
    rm, _ = dv.aligned_returns(spy[0], pos, n)
    stocks = [x for x in secs if x["ticker"] != "SPY" and x.get("sector")]
    rets = {}
    ssum, scnt = defaultdict(lambda: [0.0] * n), defaultdict(lambda: [0] * n)
    for x in stocks:
        r, _ = dv.aligned_returns(x, pos, n)
        rets[x["id"]] = r
        su, sc = ssum[x["sector"]], scnt[x["sector"]]
        for t in range(n):
            if r[t] is not None:
                su[t] += r[t]
                sc[t] += 1
    N = len(stocks)
    E = np.full((N, n), np.nan, dtype=np.float32)
    SD = np.full((N, n), np.nan, dtype=np.float32)
    Y = np.full((N, n), np.nan, dtype=np.float32)
    for k, x in enumerate(stocks):
        r = rets[x["id"]]
        su, sc = ssum[x["sector"]], scnt[x["sector"]]
        sarr = [None] * n
        for t in range(1, n):
            if r[t] is not None and rm[t] is not None and sc[t] - 1 >= dv.MIN_PEERS:
                sarr[t] = (su[t] - r[t]) / (sc[t] - 1) - rm[t]
        E[k], SD[k], Y[k] = residuals_for_stock(r, rm, sarr, master)
        if (k + 1) % 100 == 0 or k + 1 == N:
            print("  residuals: %d/%d stocks, %.0fs" % (k + 1, N, time.time() - t0), flush=True)
    ids = np.array([x["id"] for x in stocks])
    return {"dates": np.array(master), "ids": ids, "tickers": np.array([x["ticker"] for x in stocks]), "E": E, "SD": SD, "Y": Y}


def get_matrices(rebuild):
    if os.path.exists(CACHE_FILE) and not rebuild:
        d = np.load(CACHE_FILE, allow_pickle=False)
        return {k: d[k] for k in d.files}
    m = build_matrices()
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    np.savez_compressed(CACHE_FILE, **m)
    return m


def walk_forward(Z, E, SD, Yr, years, K, test_years):
    """Returns R2 (N x n; squared leave-one-out miss in raw units, NaN where not scored)."""
    N, n = Z.shape
    R2 = np.full((N, n), np.nan, dtype=np.float32)
    for Yt in test_years:
        tr = np.where((years >= Yt - TRAIN_YEARS) & (years < Yt))[0]
        te = np.where(years == Yt)[0]
        if len(tr) < MIN_TRAIN_DAYS or len(te) == 0:
            continue
        Zt = np.clip(Z[:, tr], -CLIP, CLIP)
        M = ~np.isnan(Zt)
        Z0 = np.nan_to_num(Zt)
        den = M.astype(np.float64) @ M.T.astype(np.float64)
        num = Z0.astype(np.float64) @ Z0.T.astype(np.float64)
        C = np.where(den >= 100, num / np.maximum(den, 1), 0.0)
        dg = np.sqrt(np.maximum(np.diag(C), 1e-12))
        C = C / dg[:, None] / dg[None, :]
        good = M.sum(axis=1) >= MIN_STOCK_TRAIN
        C[~good, :] = 0.0
        C[:, ~good] = 0.0
        w, V = np.linalg.eigh(C)
        V = V[:, np.argsort(w)[::-1][:K]]
        V[~good, :] = 0.0
        for t in te:
            z = Z[:, t]
            m = (~np.isnan(z)) & good
            if m.sum() < 5 * K + 10:
                continue
            Vm = V[m]
            G = Vm.T @ Vm + 1e-6 * np.eye(K)
            Ginv = np.linalg.inv(G)
            f = Ginv @ (Vm.T @ z[m])
            e = z[m] - Vm @ f
            h = np.minimum(np.einsum("ik,kl,il->i", Vm, Ginv, Vm), 0.95)
            r = e / (1.0 - h)
            R2[m, t] = (r * SD[m, t]) ** 2
    return R2


def era_of(y):
    for name, lo, hi in ERAS:
        if lo <= y <= hi:
            return name
    return None


def gains(E, Yr, R2, years, day_mask, test_years):
    """Per-year and per-era change in R-squared (raw units): (sum e^2 - sum r^2) / sum y^2, over scored stock-days on the selected days."""
    per_year, era_num, era_den = {}, defaultdict(float), defaultdict(float)
    for Yt in test_years:
        cols = np.where((years == Yt) & day_mask)[0]
        if len(cols) == 0:
            continue
        r2 = R2[:, cols]
        sc = ~np.isnan(r2)
        if sc.sum() == 0:
            continue
        e2 = np.where(sc, E[:, cols].astype(np.float64) ** 2, 0.0)
        y2 = np.where(sc, Yr[:, cols].astype(np.float64) ** 2, 0.0)
        rr = np.where(sc, r2.astype(np.float64), 0.0)
        num, den = (e2 - rr).sum(), y2.sum()
        per_year[Yt] = (num / den, len(cols))
        era = era_of(Yt)
        if era:
            era_num[era] += num
            era_den[era] += den
    era_gain = {e: (era_num[e] / era_den[e]) for e in era_num if era_den[e] > 0}
    return per_year, era_gain


def verdict(per_year, era_gain, min_days_year, min_years):
    yrs = [y for y, (g, nd) in per_year.items() if nd >= min_days_year]
    pos = sum(1 for y in yrs if per_year[y][0] > 0)
    have = [era_gain.get(e[0]) for e in ERAS]
    if len(yrs) < min_years or any(g is None for g in have):
        return "no verdict (too few years or an era is missing)", pos, len(yrs)
    if all(g >= 0.02 for g in have) and pos / len(yrs) >= 0.70:
        return "EARNS ITS PLACE", pos, len(yrs)
    return "does not earn its place", pos, len(yrs)


def main():
    rebuild = "--rebuild" in sys.argv
    t0 = time.time()
    M = get_matrices(rebuild)
    dates, ids, E, SD, Yr = M["dates"], M["ids"], M["E"], M["SD"], M["Y"]
    N, n = E.shape
    years = np.array([int(d[:4]) for d in dates])
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = E / SD
    day_stress = np.sqrt(np.nanmean(np.where(np.isnan(Z), np.nan, Z ** 2), axis=0))
    stress = day_stress >= STRESS_LINE
    test_years = [y for y in sorted(set(years.tolist())) if y >= TEST_START]
    print("matrices: %d stocks x %d days | stress days (>= %.1f): %d of %d since %d | %.0fs" % (
        N, n, STRESS_LINE, int(stress[years >= TEST_START].sum()), int((years >= TEST_START).sum()), TEST_START, time.time() - t0), flush=True)

    allmask = np.ones(n, dtype=bool)
    results = {}
    for K in (5, 2, 10):
        R2 = walk_forward(Z, E, SD, Yr, years, K, test_years)
        results[K] = R2
        print("  K=%d done, %.0fs" % (K, time.time() - t0), flush=True)

    print("\nBASELINE: chapter 1 R-squared against predicting zero, by era (all scored days)")
    R2 = results[5]
    for name, lo, hi in ERAS:
        cols = np.where((years >= lo) & (years <= hi) & np.isfinite(np.nanmean(R2, axis=0)))[0]
        sc = ~np.isnan(R2[:, cols])
        e2 = np.where(sc, E[:, cols].astype(np.float64) ** 2, 0).sum()
        y2 = np.where(sc, Yr[:, cols].astype(np.float64) ** 2, 0).sum()
        print("  %-10s %.3f" % (name, 1 - e2 / y2))

    print("\nGAIN IN R-SQUARED FROM K STATISTICAL FACTORS (walk-forward, leave-one-out; the bar is +0.02 in each era)")
    print("  %-34s %10s %10s %10s | years positive" % ("", ERAS[0][0], ERAS[1][0], ERAS[2][0]))
    verdicts = {}
    for label, mask, mdy, miny in (("ALL DAYS", allmask, 1, MIN_YEARS_ALL), ("STRESS DAYS", stress, 5, MIN_YEARS_STRESS), ("ORDINARY DAYS", ~stress, 1, MIN_YEARS_ALL)):
        for K in (5, 2, 10):
            per_year, era_gain = gains(E, Yr, results[K], years, mask, test_years)
            v, pos, ny = verdict(per_year, era_gain, mdy, miny)
            if label == "STRESS DAYS":
                few = [e[0] for e in ERAS if int(stress[(years >= e[1]) & (years <= e[2])].sum()) < MIN_STRESS_DAYS_ERA]
                if few:
                    v = "no verdict (fewer than %d stress days in %s)" % (MIN_STRESS_DAYS_ERA, ", ".join(few))
            vals = ["%+.4f" % era_gain[e[0]] if e[0] in era_gain else "n/a" for e in ERAS]
            tag = "PRIMARY " if K == 5 else "         "
            print("  %s%-12s K=%-2d %s %10s %10s %10s | %d of %d" % (tag if K == 5 else "         ", label, K, "", vals[0], vals[1], vals[2], pos, ny))
            if K == 5:
                verdicts[label] = v
    print("\nVERDICTS under the pre-set rules (K = 5):")
    print("  all days:      %s" % verdicts["ALL DAYS"])
    print("  stress days:   %s%s" % (verdicts["STRESS DAYS"], "  (a pass here with a fail on all days is a LEAD, not 'earns its place')" if verdicts["STRESS DAYS"].startswith("EARNS") else ""))
    print("  ordinary days: %s" % verdicts["ORDINARY DAYS"])

    # Test C: composition
    try:
        sb = ew.get_sb()
        id_set = set(ids.tolist())
        einfo, use_labels, nlab = ew.load_event_info(sb, list(dates), id_set)
        EV = np.zeros((N, n), dtype=bool)
        idx = {sid: k for k, sid in enumerate(ids.tolist())}
        for sid, days in einfo.items():
            k = idx.get(sid)
            if k is not None:
                for t in days:
                    EV[k, t] = True
        have_ev = True
    except Exception as ex:
        print("\n(composition skipped: could not read events: %s)" % ex)
        have_ev = False
    if have_ev:
        R2 = results[5]
        print("\nCOMPOSITION of the unexplained squared miss (test years %d on; K = 5 factors; shares of the regime's total)" % TEST_START)
        print("  %-14s %9s %12s %14s %12s %10s" % ("regime", "days", "own events", "big, no event", "the rest", "removed by factors"))
        for label, mask in (("stress days", stress), ("ordinary days", ~stress)):
            cols = np.where(mask & (years >= TEST_START) & np.isfinite(day_stress))[0]
            e2 = E[:, cols].astype(np.float64) ** 2
            sc = ~np.isnan(R2[:, cols])
            e2 = np.where(sc, e2, 0.0)
            rr = np.where(sc, R2[:, cols].astype(np.float64), 0.0)
            zb = np.abs(Z[:, cols]) / day_stress[cols][None, :]
            ev = EV[:, cols] & sc
            big = (zb > 2.0) & ~EV[:, cols] & sc
            tot = e2.sum()
            if tot <= 0 or len(cols) == 0:
                print("  %-14s %9d      (no scored days)" % (label, len(cols)))
                continue
            print("  %-14s %9d %11.1f%% %13.1f%% %11.1f%% %9.1f%%" % (label, len(cols), 100 * e2[ev].sum() / tot, 100 * e2[big].sum() / tot,
                                                                      100 * (tot - e2[ev].sum() - e2[big].sum()) / tot, 100 * (tot - rr.sum()) / tot))
        print("  (own events cover only about 1.3% of stock-days; 'big' = more than 2 stress-units with no recorded event)")
    print("\ntotal %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
