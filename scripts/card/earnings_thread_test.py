#!/usr/bin/env python3
"""
earnings_thread_test.py -- READ-ONLY (local matrices; the database is read for 8-K item 2.02 filings and for recorded event days).
THREAD: EARNINGS-RELEASE DAYS. The gap sample found that about a third of the big misses with no recorded event were earnings days whose 8-K is in
sec_8k_filings but was never promoted to an event. This asks three questions over every stock and every year:
  1. Do earnings days widen the miss (the band), beyond an ordinary day, on years the scale was never fit on?
  2. How many times more often than chance do big misses with no recorded event fall on earnings days?
  3. How much of the unexplained squared miss, and of the 'big, no event' part of it, sits on earnings days?

Usage:   python3 -u scripts/card/earnings_thread_test.py
Needs:   data_cache/audit_matrices.npz (gap_audit.py builds it). Database: sec_8k_filings (item_codes, filing_date) and the event tables.

DEFINITIONS. The 8-K table stores only the filing DATE, not the time, so the reaction can fall on the filing day (a pre-market release) or the next trading day
(an after-close release). Both are flagged: DAY 0 = the first trading day on or after the filing date, DAY +1 = the day after. A stock-day that is also a RECORDED
event day (day 0 or +1 of an event in ev_ent) goes in its own group, so earnings and events are never double counted. Duplicate filing rows are collapsed.
  z5 = the standardized chapter-1 miss divided by the square root of the other stocks' mean squared miss the same day (market-wide stress removed), as in the
  event-day width test. A group's scale is the mean of z5^2 over its days.
PRE-SET RULE (written before the first run). Walk-forward: the scales are fit on years BEFORE the test year (a group needs >= 200 prior days) and scored on the
  test year with the Gaussian log score, against one ordinary-day scale. PRIMARY = earnings days with no recorded event, day 0 and day +1 TOGETHER.
  EARNS ITS PLACE if the gain is >= 0.005 nats per earnings stock-day in EACH of 2006-2012, 2013-2019, 2020-2026 AND positive in >= 70% of test years.
PREDICTIONS (before the run): it earns its place by a wide margin (gain above 0.05); the combined earnings-day band multiplier is 1.5-2.2x ordinary; earnings days
  hold at least a fifth of the 'big, no event' mass; and big no-event misses are at least 5x more likely on earnings days than chance.
"""
import os, sys, math, time, bisect, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
TEST_START = 2006
MIN_PRIOR = 200
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
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = E / SD
    Zsq = Z.astype(np.float64) ** 2
    valid = ~np.isnan(Zsq)
    S = np.nansum(Zsq, axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        Z5 = Zsq / qo
        day_stress = np.sqrt(S / np.maximum(cnt, 1))
    ok = valid & np.isfinite(Z5) & (qo > 0) & (cnt[None, :] > 20)

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids.tolist())}
    rows = paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date").like("item_codes", "%2.02%").order("id"))
    seen, EA0, EA1 = set(), np.zeros((N, n), dtype=bool), np.zeros((N, n), dtype=bool)
    for r in rows:
        k = idx.get(r["security_id"])
        f = str(r["filing_date"])[:10]
        if k is None or (k, f) in seen:
            continue
        seen.add((k, f))
        i = bisect.bisect_left(dl, f)
        if i < n:
            EA0[k, i] = True
            if i + 1 < n:
                EA1[k, i + 1] = True
    EA1 &= ~EA0
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids.tolist()))
    EV = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                EV[k, t] = True
    EA = EA0 | EA1
    print("matrices: %d stocks x %d days | item 2.02 filings read: %d (distinct stock-dates: %d) | earnings stock-days flagged: day 0 %d, day +1 %d | recorded event days: %d | %.0fs" % (
        N, n, len(rows), len(seen), int((EA0 & ok).sum()), int((EA1 & ok).sum()), int((EV & ok).sum()), time.time() - t0), flush=True)

    groups = {"ordinary": ok & ~EA & ~EV, "earn_day0": ok & EA0 & ~EV, "earn_day1": ok & EA1 & ~EV,
              "event_only": ok & EV & ~EA, "event+earnings": ok & EV & EA}
    yrs = sorted({int(y) for y in years})
    stats = {g: {y: (0.0, 0.0) for y in yrs} for g in groups}
    for g, m in groups.items():
        for y in yrs:
            cols = np.where(years == y)[0]
            mm = m[:, cols]
            stats[g][y] = (float(mm.sum()), float(Z5[:, cols][mm].sum()))

    # calibrated multipliers, all years and by era
    def scale(g, ys):
        nn = sum(stats[g][y][0] for y in ys)
        ss = sum(stats[g][y][1] for y in ys)
        return ss / nn if nn > 0 else float("nan"), nn
    print("\nCALIBRATED BAND MULTIPLIER vs an ordinary day (sqrt of the ratio of mean squared stress-adjusted miss; days in brackets)")
    print("  %-18s %16s %16s %16s %16s" % ("", "all years", ERAS[0][0], ERAS[1][0], ERAS[2][0]))
    for g in ("earn_day0", "earn_day1", "event_only", "event+earnings"):
        cells = []
        for ys in ([y for y in yrs if y >= 2004], [y for y in yrs if ERAS[0][1] <= y <= ERAS[0][2]], [y for y in yrs if ERAS[1][1] <= y <= ERAS[1][2]], [y for y in yrs if y >= ERAS[2][1]]):
            sg, ng = scale(g, ys)
            so, _ = scale("ordinary", ys)
            cells.append("%.2fx (%d)" % (math.sqrt(sg / so), ng) if ng > 0 else "n/a")
        print("  %-18s %16s %16s %16s %16s" % (g, *cells))

    # walk-forward log-score gain of separate earnings scales vs one ordinary scale
    def gain_year(g_list, Y):
        pr = [y for y in yrs if y < Y]
        so, no = scale("ordinary", pr)
        tot_gain, tot_n = 0.0, 0.0
        for g in g_list:
            sg, ng = scale(g, pr)
            if ng < MIN_PRIOR or not (sg > 0):
                return None
            n_t, s_t = stats[g][Y]
            if n_t == 0:
                continue
            tot_gain += (-0.5 * n_t * math.log(sg) - 0.5 * s_t / sg) - (-0.5 * n_t * math.log(so) - 0.5 * s_t / so)
            tot_n += n_t
        return (tot_gain, tot_n) if tot_n > 0 else None

    print("\nGAIN IN LOG SCORE PER EARNINGS STOCK-DAY, walk-forward (nats; positive = better than treating them as ordinary days)")
    print("  %-34s %10s %10s %10s | years positive" % ("", ERAS[0][0], ERAS[1][0], ERAS[2][0]))
    verdict = None
    for label, gl in (("PRIMARY day 0 + day +1 together", ["earn_day0", "earn_day1"]), ("day 0 alone", ["earn_day0"]), ("day +1 alone", ["earn_day1"])):
        era_g, era_n, per_year = defaultdict(float), defaultdict(float), {}
        for Y in [y for y in yrs if y >= TEST_START]:
            r = gain_year(gl, Y)
            if r:
                per_year[Y] = r[0] / r[1]
                e = era_of(Y)
                if e:
                    era_g[e] += r[0]
                    era_n[e] += r[1]
        vals = [(era_g[e[0]] / era_n[e[0]]) if era_n[e[0]] > 0 else None for e in ERAS]
        npos = sum(1 for v in per_year.values() if v > 0)
        print("  %-34s %10s %10s %10s | %d of %d" % (label, *["%+.4f" % v if v is not None else "n/a" for v in vals], npos, len(per_year)))
        if label.startswith("PRIMARY"):
            if len(per_year) >= 10 and all(v is not None and v >= 0.005 for v in vals) and npos / len(per_year) >= 0.70:
                verdict = "EARNS ITS PLACE"
            else:
                verdict = "does not earn its place"
    print("\nVERDICT under the pre-set rule (earnings days with no recorded event, day 0 and +1 together): %s" % verdict)

    # enrichment and mass
    test_cols = years >= TEST_START
    colmask = np.zeros((N, n), dtype=bool)
    colmask[:, test_cols] = True
    zb = np.abs(Z) / day_stress[None, :]
    big_noev = ok & colmask & (zb > 2.0) & ~EV
    nonev = ok & colmask & ~EV
    share_big_earn = (big_noev & EA).sum() / max(big_noev.sum(), 1)
    share_all_earn = (nonev & EA).sum() / max(nonev.sum(), 1)
    e2 = np.where(ok & colmask, E.astype(np.float64) ** 2, 0.0)
    tot = e2.sum()
    print("\nENRICHMENT AND MASS (test years %d on)" % TEST_START)
    print("  stock-days that are earnings days (no recorded event): %.2f%% of all stock-days without a recorded event" % (100 * share_all_earn))
    print("  big misses (beyond 2 stress-units) with no recorded event that fall on earnings days: %.1f%%  -> %.1fx more often than chance" % (
        100 * share_big_earn, share_big_earn / max(share_all_earn, 1e-12)))
    print("  share of ALL the unexplained squared miss: on earnings days %.1f%% | in big no-event misses %.1f%% | in big no-event misses ON earnings days %.1f%%" % (
        100 * e2[ok & colmask & EA & ~EV].sum() / tot, 100 * e2[big_noev].sum() / tot, 100 * e2[big_noev & EA].sum() / tot))
    print("  so earnings days hold %.0f%% of the 'big, no event' mass" % (100 * e2[big_noev & EA].sum() / max(e2[big_noev].sum(), 1e-12)))
    print("\nNOTE: the 8-K table has no filing time, so some flagged days are filed after the reaction (the SNPS row in the sample: its drop came before its release).")
    print("      The test treats day 0 and +1 as one window; it does not know the sign, which would need the surprise (not in the database).")
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
