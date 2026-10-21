#!/usr/bin/env python3
"""
event_date_lag_check.py -- READ-ONLY (local matrices; the database is read for events and 8-K filings). Writes nothing.
THE QUESTION. unrecorded_joins.py found big ordinary misses 2.41x more frequent on the day before a recorded-event window starts and 1.68x in the 5 days before, and 1.71x the day before a Regulation FD
window, but LESS frequent (0.77x) in the 5 days before earnings. One explanation: a company has up to four business days to file an 8-K after an event, so for some recorded events the news precedes the date we use
as day 0 (the event window is then misplaced). Another: leaks and anticipation. This check looks at each event's own surroundings.
METHOD. For every ISOLATED recorded event (no other event, earnings or Regulation FD flagged day in days -6..+3 around its date, from 2006) take the miss in band units (the card's current scale) on the days -5..+2
and find the day of the LARGEST absolute miss: its PEAK OFFSET. Two comparators built the same way:
  EARNINGS: isolated earnings windows (8-K item 2.02), day 0 = the first trading day on or after the filing date: a well-dated benchmark (the release is on or just before that date; the reaction is on day 0 or +1).
  PLACEBO: for each event a random isolated day of the same stock in the same year (no flagged day in days -6..+3). Under no structure each of the 8 offsets would hold 12.5%, so the pre-share (days -5..-1) is about 62.5%.
Reported: the offset distribution; PRE-SHARE (peak on days -5..-1) and AT-EVENT share (peak on day 0 or +1); the pre-share EXCESS of events over earnings with a 95% interval (resampling calendar MONTHS, 500
resamples, because events cluster in time), overall, by event type (types with at least 300 isolated events) and by era; and CANDIDATE MIS-DATED EVENTS: the largest |miss| in days -5..-1 is at least 3.0 band units
AND at least twice the largest on days 0..+1 (with a dozen examples to look at).
NOTE: the pooled excess can cancel out between types (validated on a synthetic world where one type lagged 55% of the time and another 10%: pooled excess -0.1 points, the lagging type +21.7), so only the by-type table is used for a verdict.
RESULT OF THE FIRST RUN (3714231): the rule below fired for ALL nine types (pooled excess +27.6 points), but it is CONFOUNDED: the largest of 8 days falls on the event date only when the reaction is large, so low-signal events look
'early' however they are dated; the offset distribution is a flat background (about 10.4% per day) plus a bump at days 0 and +1, and days -4..-1 are within noise of day -5. The synthetic test had given every event a big shock and
hid this.
RULE v2 (POST HOC: written after seeing the first run; the by-type lag masses had not been seen when the predictions below were written). LAG MASS = the extra share of peaks on days -4..-1 above the background, in points of events,
with two backgrounds: A = the share on day -5; B = the mean of the shares on days -5 and +2 (B is lower for events whose reaction persists). The verdict uses the SMALLER of A and B. A type is LAGGING (v2) if that is at least
3.0 points, its 95% interval (months resampled) is above 0, and n >= 300. q = (share at days 0 and +1 - 0.25) / 0.75 is the model-based share of events whose reaction dominates the window (assumes an even background).
Validated on a synthetic world where 70% of events have NO shock (v1 flagged both types; v2 flagged only the type that lagged).
V2 PREDICTIONS: all recorded events lag mass 0.3-1.9 points (computed from the first run's pooled distribution, post hoc); q about 16% for events and about 56% for earnings; no type reaches 3.0 points, except possibly
legal_settlement, capital_raise or financial_result (filed after the fact); the earnings benchmark and the placebo days about 0.
DEFINITIONS OF 'MATERIAL' (v1, pre-set, now known to be confounded): an event type is POSSIBLY LAGGING if its pre-share exceeds the earnings benchmark's by 10 points or more, the 95% interval excludes 0, and it has at least 300 isolated events.
Usage:   python3 -u scripts/card/event_date_lag_check.py        Needs: data_cache/audit_matrices.npz and the database.
PREDICTIONS (before the run): recorded events: pre-share 28-38%, at-event share 40-55%; earnings: pre-share 15-25%, at-event 60-75%; placebo pre-share 61-64%; the overall excess of events over earnings is 8-15 points;
the types most likely to lag include acquisition, regulatory and legal_settlement (news first, 8-K later), leadership_change least; the excess is similar across the three eras (within 5 points); candidate
mis-dated events are 8-15% of isolated events against 3-6% for earnings and about 10% for placebo dates (the placebo share is high because random days often hold a big miss somewhere in days -5..-1 and little on 0..+1).
"""
import os, sys, time, bisect, warnings
from collections import defaultdict, Counter
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc

CACHE_FILE = uc.CACHE_FILE
TEST_START = 2006
OFFS = list(range(-5, 3))
N_BOOT = 500
SEED = 20261021
MATERIAL_POINTS = 0.10
MIN_N = 300
CAND_BU = 3.0
LAG_POINTS = 3.0
ERAS = [("2006-2012", 2006, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]


def pct(x):
    return "%5.1f%%" % (100.0 * x) if np.isfinite(x) else "  n/a "


def main():
    t0_ = time.time()
    if not os.path.exists(CACHE_FILE):
        sys.exit("Run gap_audit.py first: it builds %s." % CACHE_FILE)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, tickers, E, SD = d["dates"], d["ids"].tolist(), d["tickers"], d["E"], d["SD"]
    N, n = E.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    months = np.array([(int(x[:4]) - TEST_START) * 12 + int(x[5:7]) - 1 for x in dl])
    M = int(months.max()) + 1
    with np.errstate(invalid="ignore", divide="ignore"):
        Zsq = (E.astype(np.float64) / SD.astype(np.float64)) ** 2
    valid = np.isfinite(Zsq)
    S = np.where(valid, Zsq, 0.0).sum(axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        bu = np.sqrt(Zsq / qo)
    bu[~((cnt[None, :] > 20) & np.isfinite(bu))] = np.nan

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids))
    EVany = np.zeros((N, n), dtype=bool)
    ev0 = []
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is None:
            continue
        for t, (pt, off, size, timing) in days.items():
            EVany[k, t] = True
            if off == 0:
                ev0.append((k, t, pt or "(none)"))
    EA0 = np.zeros((N, n), dtype=bool)
    EA1 = np.zeros((N, n), dtype=bool)
    F701 = np.zeros((N, n), dtype=bool)
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is None:
            continue
        its = dc.parse_items(r.get("item_codes"))
        i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
        if i >= n:
            continue
        if "2.02" in its:
            EA0[k, i] = True
            if i + 1 < n:
                EA1[k, i + 1] = True
        elif "7.01" in its:
            F701[k, i] = True
            if i + 1 < n:
                F701[k, i + 1] = True
    EA1 &= ~EA0
    flag_any = EVany | EA0 | EA1 | F701
    cs0 = np.concatenate([np.zeros((N, 1), dtype=np.int32), np.cumsum(flag_any, axis=1, dtype=np.int32)], axis=1)

    def flagged(k, t, a, b):
        return int(cs0[k, t + b + 1] - cs0[k, t + a])

    def window(k, t):
        w = bu[k, t - 5: t + 3]
        return w if len(w) == 8 and np.isfinite(w).all() else None

    def usable(k, t):
        return t - 7 >= 0 and t + 3 < n and years[t] >= TEST_START

    rows = {"event": [], "earnings": [], "placebo": []}      # (k, t, type, peak offset, pre_max, post_max)
    def add(kind, k, t, typ):
        w = window(k, t)
        if w is None:
            return False
        a = np.abs(w)
        rows[kind].append((k, t, typ, OFFS[int(np.argmax(a))], float(a[:5].max()), float(a[5:7].max())))
        return True

    for k, t, pt in ev0:
        if usable(k, t) and flagged(k, t, -6, 3) == 2:
            add("event", k, t, pt)
    for k, t in zip(*np.where(EA0)):
        k, t = int(k), int(t)
        if usable(k, t) and flagged(k, t, -6, 3) == 2:
            add("earnings", k, t, "earnings")
    rng = np.random.RandomState(SEED)
    by_ky = defaultdict(list)
    ok_plc = np.zeros((N, n), dtype=bool)
    for k in range(N):
        for t in range(8, n - 4):
            if years[t] >= TEST_START and flagged(k, t, -6, 3) == 0 and window(k, t) is not None:
                by_ky[(k, int(years[t]))].append(t)
    for k, t, typ, *_ in list(rows["event"]):
        cand = by_ky.get((k, int(years[t])))
        if cand:
            add("placebo", k, int(cand[rng.randint(len(cand))]), typ)
    print("isolated events: %d | isolated earnings windows: %d | placebo days: %d | %.0fs" % (len(rows["event"]), len(rows["earnings"]), len(rows["placebo"]), time.time() - t0_), flush=True)

    def dist(rs):
        c = Counter(r[3] for r in rs)
        tot = max(len(rs), 1)
        return [c.get(o, 0) / tot for o in OFFS]

    print("\nPEAK OFFSET: the day of the largest |miss| (band units) among days -5..+2 (isolated windows)")
    print("  %-26s %7s | %s | %8s %9s" % ("", "n", " ".join("%6s" % ("%+d" % o) for o in OFFS), "pre-share", "at-event"))
    for lab, rs in (("recorded events", rows["event"]), ("earnings windows (benchmark)", rows["earnings"]), ("placebo days", rows["placebo"])):
        ds = dist(rs)
        print("  %-26s %7d | %s | %s %s" % (lab, len(rs), " ".join("%5.1f%%" % (100 * x) for x in ds), pct(sum(ds[:5])), pct(ds[5] + ds[6])))

    def month_arrays(rs, cond):
        tot, hit = np.zeros(M), np.zeros(M)
        for r in rs:
            m = months[r[1]]
            tot[m] += 1
            if cond(r):
                hit[m] += 1
        return hit, tot
    pre = lambda r: r[3] < 0
    rng2 = np.random.RandomState(SEED + 1)

    def diff_ci(rs_a, rs_b):
        ah, at = month_arrays(rs_a, pre)
        bh, bt = month_arrays(rs_b, pre)
        def est(w):
            return (w @ ah) / max(w @ at, 1.0) - (w @ bh) / max(w @ bt, 1.0)
        pt = est(np.ones(M))
        live = np.where(at + bt > 0)[0]
        out = [est(np.bincount(rng2.choice(live, size=len(live)), minlength=M).astype(float)) for _ in range(N_BOOT)]
        lo, hi = np.percentile(out, [2.5, 97.5])
        return pt, lo, hi, float(ah.sum() / max(at.sum(), 1)), float(bh.sum() / max(bt.sum(), 1))

    pt, lo, hi, sa, sb_ = diff_ci(rows["event"], rows["earnings"])
    print("\nPRE-SHARE EXCESS OF RECORDED EVENTS OVER EARNINGS, overall: %s vs %s = %+.1f points [%+.1f, %+.1f]" % (pct(sa), pct(sb_), 100 * pt, 100 * lo, 100 * hi))
    print("  (a pooled figure can hide types with opposite signs, e.g. a type that lags and a type dated exactly: the BY EVENT TYPE table below is the one to read)")

    print("\nBY EVENT TYPE (types with at least %d isolated events; benchmark = all earnings windows)" % MIN_N)
    print("  %-30s %6s | %9s %9s %8s | %s" % ("type", "n", "pre-share", "at-event", "excess", "95% interval"))
    types = [t for t, c in Counter(r[2] for r in rows["event"]).most_common() if c >= MIN_N]
    for typ in types:
        rs = [r for r in rows["event"] if r[2] == typ]
        pt, lo, hi, sa, _ = diff_ci(rs, rows["earnings"])
        ds = dist(rs)
        print("  %-30s %6d | %s %s %+7.1f | [%+.1f, %+.1f] %s" % (typ, len(rs), pct(sa), pct(ds[5] + ds[6]), 100 * pt, 100 * lo, 100 * hi,
              "POSSIBLY LAGGING (v1, confounded)" if (pt >= MATERIAL_POINTS and lo > 0) else ""))

    def offset_counts(rs):
        tot, per = np.zeros(M), np.zeros((8, M))
        for r in rs:
            m = months[r[1]]
            tot[m] += 1
            per[OFFS.index(r[3]), m] += 1
        return per, tot

    def lag_stats(rs):
        per, tot = offset_counts(rs)
        def est(w_):
            sh = (per @ w_) / max(float(w_ @ tot), 1.0)
            a = float(sh[1:5].sum() - 4.0 * sh[0])
            b = float(sh[1:5].sum() - 2.0 * (sh[0] + sh[7]))
            q = float((sh[5] + sh[6] - 0.25) / 0.75)
            return a, b, q
        a, b, q = est(np.ones(M))
        live = np.where(tot > 0)[0]
        out = [min(est(np.bincount(rng2.choice(live, size=len(live)), minlength=M).astype(float))[:2]) for _ in range(N_BOOT)]
        lo, hi = np.percentile(out, [2.5, 97.5])
        return a, b, q, lo, hi

    print("\nLAG MASS (v2, post hoc): the extra share of peaks on days -4..-1 above the background, in points of events")
    print("  background A = the share on day -5; B = the mean of the shares on days -5 and +2; the verdict uses the smaller of the two; q = model-based share of events with a window-dominating reaction")
    print("  %-30s %6s | %6s | %8s %8s | %s" % ("group", "n", "q", "lag A", "lag B", "95% interval of the smaller"))
    groups = [("all recorded events", rows["event"]), ("earnings windows (benchmark)", rows["earnings"]), ("placebo days", rows["placebo"])] + [(t, [r for r in rows["event"] if r[2] == t]) for t in types]
    for lab, rs in groups:
        if len(rs) < 100:
            continue
        a, b, q, lo, hi = lag_stats(rs)
        print("  %-30s %6d | %5.1f%% | %+7.1f %+8.1f | [%+.1f, %+.1f] %s" % (lab, len(rs), 100 * q, 100 * a, 100 * b, 100 * lo, 100 * hi,
              "LAGGING (v2)" if (lab in types and min(a, b) * 100 >= LAG_POINTS and lo > 0) else ""))

    print("\nBY ERA")
    print("  %-10s %9s %9s | %8s | %s" % ("era", "events n", "earn. n", "excess", "95% interval"))
    for lab, lo_y, hi_y in ERAS:
        ra = [r for r in rows["event"] if lo_y <= years[r[1]] <= hi_y]
        rb = [r for r in rows["earnings"] if lo_y <= years[r[1]] <= hi_y]
        if len(ra) >= 100 and len(rb) >= 100:
            pt, lo, hi, sa, sb2 = diff_ci(ra, rb)
            print("  %-10s %9d %9d | %s vs %s = %+.1f | [%+.1f, %+.1f]" % (lab, len(ra), len(rb), pct(sa), pct(sb2), 100 * pt, 100 * lo, 100 * hi))

    print("\nLAG MASS BY ERA (all recorded events, v2)")
    for lab, lo_y, hi_y in ERAS:
        ra = [r for r in rows["event"] if lo_y <= years[r[1]] <= hi_y]
        if len(ra) >= 100:
            a, b, q, lo, hi = lag_stats(ra)
            print("  %-10s n %5d | q %5.1f%% | lag A %+.1f, lag B %+.1f points | 95%% interval of the smaller [%+.1f, %+.1f]" % (lab, len(ra), 100 * q, 100 * a, 100 * b, 100 * lo, 100 * hi))

    def cand(r):
        return r[4] >= CAND_BU and r[4] >= 2.0 * r[5]
    print("\nCANDIDATE MIS-DATED EVENTS (the largest |miss| in days -5..-1 is >= %.1f band units and >= twice the largest on days 0..+1)" % CAND_BU)
    for lab, rs in (("recorded events", rows["event"]), ("earnings windows", rows["earnings"]), ("placebo days", rows["placebo"])):
        c = sum(1 for r in rs if cand(r))
        print("  %-18s %6d of %6d = %s" % (lab, c, len(rs), pct(c / max(len(rs), 1))))
    lag = Counter(r[3] for r in rows["event"] if cand(r))
    print("  lag of the candidates (peak offset): " + "  ".join("%+d: %d" % (o, lag.get(o, 0)) for o in OFFS[:5]))
    ex = [r for r in rows["event"] if cand(r)]
    rng3 = np.random.RandomState(SEED + 2)
    if ex:
        print("  twelve at random (ticker, event date, type, peak offset, |miss| at the peak vs the largest on days 0..+1):")
        for i in rng3.choice(len(ex), size=min(12, len(ex)), replace=False):
            k, t, typ, off, pm, qm = ex[i]
            print("    %-6s %s  %-22s peak %+d  %.1f vs %.1f" % (tickers[k], dl[t], typ, off, pm, qm))
    print("\ntotal %.0fs" % (time.time() - t0_))


if __name__ == "__main__":
    main()
