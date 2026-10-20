#!/usr/bin/env python3
"""
vol_regime_audit.py -- READ-ONLY (local matrices; the database is read for recorded event days and earnings filings, optionally).
QUESTION: how much of the 'big miss' tail is a stock being in a high-volatility REGIME (a spread problem the band should absorb) and how much is genuine surprise?
Every earlier standardized miss used each stock's SLOW spread (the residual spread over the last 250 valid days). A stock that has just had a big move, or sits in a
turbulent stretch, has a much larger RECENT spread, so its next big miss looks 'big' only against the slow spread. The day card's band also uses the slow spread, although
the chapter-2 decision was that the band is volatility-aware (the recent 20-day spread). This tests that decision and re-measures the tail.

Usage:   python3 -u scripts/card/vol_regime_audit.py
Needs:   data_cache/audit_matrices.npz (gap_audit.py builds it).

DEFINITIONS. e = the chapter-1 miss; slow variance S2 = the 250-day residual variance already in the matrices; fast variance F2 = the mean of e^2 over the previous 20
trading days that have a miss (at least 10 needed; the day itself is never included). The blended spread squared is  w x S2 + (1 - w) x F2  (w = 1 is today's slow spread).
SCORE: the Gaussian log score per stock-day, -0.5 ln(spread^2) - 0.5 e^2 / spread^2, on stock-days where F2 exists, compared with w = 1.
PRE-SET RULE (written before the first run). The blend w = 0.5 EARNS ITS PLACE as the band's base spread if its gain over w = 1 is >= 0.005 nats per stock-day in EACH of
2006-2012, 2013-2019, 2020-2026 AND positive in >= 70% of test years. w = 0.75, 0.25 and 0 (fast only) are reported to show the shape, not as verdicts.
PREDICTIONS (before the run): it earns its place (volatility clusters; the gain is above 0.02); the blend shrinks the big-miss tail's share of the unexplained squared
miss by at least 5 points (from about 46% to 41% or less); and big no-event misses are at least twice as likely to occur when the recent spread is already well above
the slow one (fast/slow variance > 2) as chance.
"""
import os, sys, math, time, bisect, warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
TEST_START = 2006
L = 20
MIN_FAST = 10
W_PRIMARY = 0.5
WS = (1.0, 0.75, 0.5, 0.25, 0.0)
ERAS = [("2006-2012", 2006, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]


def paged(make_query):
    rows, off = [], 0
    while True:
        page = make_query().range(off, off + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return rows


def era_of(y):
    for name, lo, hi in ERAS:
        if lo <= y <= hi:
            return name
    return None


def main():
    t0 = time.time()
    if not os.path.exists(CACHE_FILE):
        sys.exit("Run gap_audit.py first: it builds %s." % CACHE_FILE)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E, SD = d["dates"], d["ids"], d["E"], d["SD"]
    N, n = E.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    E2 = E.astype(np.float64) ** 2
    S2 = SD.astype(np.float64) ** 2
    valid = ~np.isnan(E2)
    cs = np.concatenate([np.zeros((N, 1)), np.cumsum(np.where(valid, E2, 0.0), axis=1)], axis=1)
    cc = np.concatenate([np.zeros((N, 1)), np.cumsum(valid, axis=1)], axis=1)
    F2 = np.full((N, n), np.nan)
    for t in range(L, n):
        s = cs[:, t] - cs[:, t - L]
        c = cc[:, t] - cc[:, t - L]
        F2[:, t] = np.where(c >= MIN_FAST, s / np.maximum(c, 1), np.nan)
    F2 = np.maximum(F2, 1e-12)
    base = valid & np.isfinite(F2) & np.isfinite(S2) & (S2 > 0)
    test_cols = years >= TEST_START
    print("matrices: %d stocks x %d days | stock-days with both a slow and a fast spread (test years): %d | %.0fs" % (
        N, n, int((base[:, test_cols]).sum()), time.time() - t0), flush=True)

    def ls(w):
        s2 = w * S2 + (1 - w) * F2
        return -0.5 * np.log(s2) - 0.5 * E2 / s2

    ls1 = ls(1.0)
    yrs = [y for y in sorted(set(years.tolist())) if y >= TEST_START]
    print("\nGAIN IN LOG SCORE PER STOCK-DAY vs today's slow spread (nats; positive = better)")
    print("  %-26s %10s %10s %10s | years positive" % ("", ERAS[0][0], ERAS[1][0], ERAS[2][0]))
    verdict = None
    for w in WS[1:]:
        lw = ls(w)
        per_year, era_g, era_n = {}, {}, {}
        for Y in yrs:
            cols = np.where(years == Y)[0]
            m = base[:, cols]
            if m.sum() == 0:
                continue
            diff = (lw[:, cols] - ls1[:, cols])[m]
            per_year[Y] = diff.mean()
            e = era_of(Y)
            if e:
                era_g[e] = era_g.get(e, 0.0) + diff.sum()
                era_n[e] = era_n.get(e, 0) + m.sum()
        vals = [(era_g[e[0]] / era_n[e[0]]) if era_n.get(e[0]) else None for e in ERAS]
        npos = sum(1 for v in per_year.values() if v > 0)
        label = "w = %.2f%s" % (w, " (PRIMARY)" if w == W_PRIMARY else (" (fast only)" if w == 0 else ""))
        print("  %-26s %10s %10s %10s | %d of %d" % (label, *["%+.4f" % v if v is not None else "n/a" for v in vals], npos, len(per_year)))
        if w == W_PRIMARY:
            verdict = "EARNS ITS PLACE" if (len(per_year) >= 10 and all(v is not None and v >= 0.005 for v in vals) and npos / len(per_year) >= 0.70) else "does not earn its place"
    print("\nVERDICT under the pre-set rule (w = %.2f, the equal blend of slow and fast variance): %s" % (W_PRIMARY, verdict))

    # tail composition under different base spreads
    ev = ea = None
    try:
        sb = ew.get_sb()
        idx = {sid: k for k, sid in enumerate(ids.tolist())}
        einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids.tolist()))
        ev = np.zeros((N, n), dtype=bool)
        for sid, days in einfo.items():
            k = idx.get(sid)
            if k is not None:
                for t in days:
                    ev[k, t] = True
        ea = np.zeros((N, n), dtype=bool)
        for r in paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date").like("item_codes", "%2.02%").order("id")):
            k = idx.get(r["security_id"])
            i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
            if k is not None and i < n:
                ea[k, i] = True
                if i + 1 < n:
                    ea[k, i + 1] = True
    except Exception as ex:
        print("\n(event and earnings masks skipped: %s)" % ex)
    cells = base & test_cols[None, :]
    tot = E2[cells].sum()
    clean = cells & ~ev & ~ea if ev is not None else None
    print("\nTAIL SHARE OF THE UNEXPLAINED SQUARED MISS: stock-days whose miss is beyond 2 market-stress units (stress = that day's root-mean-square standardized miss)")
    print("  %-30s %14s %26s" % ("base spread", "all stock-days", "no event, no earnings days"))
    for w in (1.0, W_PRIMARY, 0.0):
        s2 = w * S2 + (1 - w) * F2
        z2 = np.where(base, E2 / s2, np.nan)
        stress2 = np.nanmean(z2, axis=0)
        big = base & (z2 / stress2[None, :] > 4.0) & test_cols[None, :]
        a = E2[big].sum() / tot
        b = (E2[big & clean].sum() / E2[clean].sum()) if clean is not None else float("nan")
        print("  %-30s %13.1f%% %25.1f%%" % ("w = %.2f%s" % (w, " (today: slow)" if w == 1.0 else (" (fast only)" if w == 0 else " (blend)")), 100 * a, 100 * b))
    print("  (a Gaussian benchmark would put 26.1%% of the squared miss beyond 2 units)")

    # aftershock / regime share among big no-event misses (defined on the SLOW spread, as in every earlier result)
    z2s = np.where(base, E2 / S2, np.nan)
    st2 = np.nanmean(z2s, axis=0)
    big_s = base & (z2s / st2[None, :] > 4.0) & test_cols[None, :]
    if clean is not None:
        big_s &= clean
    ratio = F2 / S2
    hi = base & (ratio > 2.0) & test_cols[None, :]
    base_share = hi.sum() / max((base & test_cols[None, :]).sum(), 1)
    big_share = (big_s & hi).sum() / max(big_s.sum(), 1)
    mass_share = E2[big_s & hi].sum() / max(E2[big_s].sum(), 1e-12)
    print("\nREGIME SHARE among the big misses (measured against the slow spread%s)" % (", no event, no earnings" if clean is not None else ""))
    print("  stock-days whose recent variance is already more than 2x the slow variance: %.1f%% of all stock-days" % (100 * base_share))
    print("  big misses that fall on such days: %.1f%% by count (%.1fx more often than chance) and %.1f%% of the big-miss mass" % (100 * big_share, big_share / max(base_share, 1e-12), 100 * mass_share))
    print("\nNOTE: the fast spread uses the previous 20 days' misses, which include any earlier event or earnings reaction; a stock 'in a regime' may be in one BECAUSE of news")
    print("      a few days ago (an aftershock). The audit separates the band's job (width after a regime shift) from the search for information; it cannot say which came first.")
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
