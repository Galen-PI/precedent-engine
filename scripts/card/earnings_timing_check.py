#!/usr/bin/env python3
"""
earnings_timing_check.py -- READ-ONLY (matrices, the OHLC cache data_cache/ohlc, and the database for 8-K filings). Writes nothing.
THE QUESTION. The earnings window pools day 0 and day +1 (the card's multipliers are 2.72x and 2.47x) because the 8-K filing table has a date but no time: a release BEFORE the open (BMO) reacts on day 0, a release AFTER
the close (AMC) on day +1. The opening gap tells which: a BMO release shows its gap on the filing day, an AMC release on the next day. Timing is a company habit, so it is knowable for the NEXT quarter too.
THE TRAP THIS DESIGN AVOIDS. Calling each event's reaction day the day with the bigger gap picks the bigger day by construction and inflates its size (the same circularity that confounded the lag check). So:
  CLASSIFICATION (only to learn habits): for each earnings filing (item 2.02, day i = the first trading day on or after the filing date) compare |gap| on day i and on day i+1, each in units of the stock's own overnight-gap
     standard deviation over the previous 60 trading days (at least 40 valid); the event is CLASSIFIABLE if the larger is at least 2.0; BMO if day i is larger, AMC if day i+1 is.
  HABIT: for each event, the majority timing among the OTHER classifiable quarters of the same stock (leave one out; at least 5 others); STRONG if the majority share is at least 85%.
  ROLES: the REACTION day is i for a BMO habit and i+1 for an AMC habit; the OTHER day is the remaining one. Roles come from the habit, never from the event's own size.
  MULTIPLIER on a day = sqrt(mean of the squared band units there / the same mean over ordinary stock-days far from any earnings window); the median version uses medians (robust to a few huge moves).
METHOD CHECKS (before any number is believed): (1) leave-one-out agreement of an event's own classification with its habit, for the gap method and for the close-to-close method (the bigger |miss| of the two days) on the same
  events; (2) fourteen tickers whose reporting habits I recall (UNVERIFIED recollection): AMC: AAPL MSFT NVDA INTC TSLA META; BMO: JPM JNJ WMT KO PG XOM BAC HD.
  METHOD VALID if the gap method's leave-one-out agreement is at least 90%, it beats the close-to-close method by at least 3 points, and at least 12 of the 14 recalled tickers agree on 90% or more of their classifiable events.
  TIMING MATTERS if the reaction-day multiplier is at least 1.5x the other-day multiplier (strong-habit events, all eras).
  CALIBRATION OF THESE THRESHOLDS (synthetic worlds with planted habits and gap reactions): agreement with the habit is bounded by how consistent the companies themselves are. With 97% of quarters on the planted habit the method read
  95.1% agreement (close-to-close 87.2%), 14 of 14 tickers, METHOD VALID; with 90% adherence it read 88.5% and failed the 90% threshold although it classified almost every event correctly. So a NOT VALID verdict on real data
  may mean unstable reporting habits, not a bad gap method: the per-ticker line and the close-to-close margin are what separate the two.
Usage:   python3 -u scripts/card/earnings_timing_check.py        Needs: data_cache/audit_matrices.npz, data_cache/ohlc (build_ohlc_cache.py), the database.
DESCRIPTIVE beyond the two verdicts. PREDICTIONS (before the run): 65-80% of earnings events are classifiable; leave-one-out agreement 93-98% for the gap method, 80-88% for the close-to-close method; the recalled tickers
all agree on 90% or more; BMO is 40-60% of classifiable events and its share moves by less than 8 points across eras; strong habits cover 70-90% of events; reaction-day multiplier 3.2-4.0x, other-day multiplier 1.2-1.8x
(ratio 1.7 or more, so TIMING MATTERS); the pooled day-0 and day +1 multipliers from this script are 2.4-2.9x, and the pooled day-0 squared multiplier equals the BMO-share mix of the role multipliers within 5%.
"""
import os, sys, time, bisect, pickle, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc

CACHE_FILE = uc.CACHE_FILE
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OHLC_DIR = os.path.join(ROOT, "data_cache", "ohlc")
TEST_START = 2006
GAP_WIN, GAP_MIN, MAX_GAP = 60, 40, 0.5
CLASSIFY_Z = 2.0
MIN_OTHERS = 5
STRONG = 0.85
BASE_NEAR = (-2, 3)          # ordinary baseline: stock-days at least this far from any earnings day i (days i-2 .. i+3 excluded)
ERAS = [("2006-2012", 2006, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]
RECALL = {"AAPL": 1, "MSFT": 1, "NVDA": 1, "INTC": 1, "TSLA": 1, "META": 1, "JPM": 0, "JNJ": 0, "WMT": 0, "KO": 0, "PG": 0, "XOM": 0, "BAC": 0, "HD": 0}     # 1 = AMC, 0 = BMO


def pct(x):
    return "%5.1f%%" % (100.0 * x) if np.isfinite(x) else "  n/a "


def load_ohlc(ids, dl):
    pos = {x: i for i, x in enumerate(dl)}
    N, n = len(ids), len(dl)
    O, C = np.full((N, n), np.nan), np.full((N, n), np.nan)
    have = 0
    for k, sid in enumerate(ids):
        path = os.path.join(OHLC_DIR, "%s.pkl" % sid)
        if not os.path.exists(path):
            continue
        with open(path, "rb") as fh:
            d = pickle.load(fh)
        if not d["dates"]:
            continue
        have += 1
        ii = np.array([pos.get(x, -1) for x in d["dates"]], dtype=np.int64)
        ok = ii >= 0
        O[k, ii[ok]] = np.array([np.nan if v is None else v for v in d["open"]], dtype=float)[ok]
        C[k, ii[ok]] = np.array([np.nan if v is None else v for v in d["close"]], dtype=float)[ok]
    O[O <= 0] = np.nan
    C[C <= 0] = np.nan
    return O, C, have


def main():
    t0 = time.time()
    if not os.path.exists(CACHE_FILE):
        sys.exit("Run gap_audit.py first: it builds %s." % CACHE_FILE)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, tickers, E, SD = d["dates"], d["ids"].tolist(), [str(x) for x in d["tickers"]], d["E"], d["SD"]
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
    bu2 = bu ** 2

    O, C, have = load_ohlc(ids, dl)
    if have < 400:
        print("WARNING: only %d OHLC files found in %s" % (have, OHLC_DIR))
    G = np.full((N, n), np.nan)
    G[:, 1:] = O[:, 1:] / C[:, :-1] - 1.0
    G[np.abs(G) > MAX_GAP] = np.nan
    V = np.isfinite(G)
    X = np.where(V, G, 0.0)
    z = np.zeros((N, 1))
    c1 = np.concatenate([z, np.cumsum(X, axis=1)], axis=1)
    c2 = np.concatenate([z, np.cumsum(X * X, axis=1)], axis=1)
    cc = np.concatenate([z, np.cumsum(V, axis=1)], axis=1)
    S1, S2, Cn = c1[:, GAP_WIN:n] - c1[:, :n - GAP_WIN], c2[:, GAP_WIN:n] - c2[:, :n - GAP_WIN], cc[:, GAP_WIN:n] - cc[:, :n - GAP_WIN]
    with np.errstate(invalid="ignore", divide="ignore"):
        var = (S2 - S1 * S1 / Cn) / (Cn - 1)
    GSD = np.full((N, n), np.nan)
    GSD[:, GAP_WIN:] = np.where(Cn >= GAP_MIN, np.sqrt(np.maximum(var, 0.0)), np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        ZG = np.abs(G) / GSD
    print("securities with OHLC: %d of %d | overnight gaps computed for %.1f%% of stock-days from %d | %.0fs" % (have, N, 100.0 * float(np.isfinite(ZG[:, years >= TEST_START]).mean()), TEST_START, time.time() - t0), flush=True)

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
    ev = []
    near = np.zeros((N, n), dtype=bool)
    for k, lst in raw.items():
        keep = []
        for i in sorted(lst):
            if not keep or i - keep[-1] >= 20:
                keep.append(i)
        for i in keep:
            near[k, max(i + BASE_NEAR[0], 0): i + BASE_NEAR[1] + 1] = True
            if i >= GAP_WIN + 1 and i + 1 < n and years[i] >= TEST_START:
                ev.append((k, i))
    ek = np.array([e[0] for e in ev])
    ei = np.array([e[1] for e in ev])
    ey = years[ei]
    a, b = ZG[ek, ei], ZG[ek, ei + 1]
    have_gap = np.isfinite(a) & np.isfinite(b)
    cls = have_gap & (np.maximum(np.nan_to_num(a), np.nan_to_num(b)) >= CLASSIFY_Z)
    tim_gap = (np.nan_to_num(b) > np.nan_to_num(a)).astype(int)                  # 1 = AMC
    ab, bb = np.abs(bu[ek, ei]), np.abs(bu[ek, ei + 1])
    tim_bu = (np.nan_to_num(bb) > np.nan_to_num(ab)).astype(int)
    print("earnings events from %d: %d | with gaps on both days: %d (%s) | classifiable (a gap of at least %.1f own sd on a day): %d (%s)" % (
        TEST_START, len(ev), int(have_gap.sum()), pct(have_gap.mean()), CLASSIFY_Z, int(cls.sum()), pct(float(cls.sum() / max(have_gap.sum(), 1)))))
    for lab, lo, hi in ERAS:
        m = have_gap & (ey >= lo) & (ey <= hi)
        c = cls & (ey >= lo) & (ey <= hi)
        print("   %-10s events %6d | gaps on both days %s | classifiable %s | BMO share among classifiable %s" % (lab, int((ey >= lo).sum() - (ey > hi).sum()), pct(float(m.sum() / max(((ey >= lo) & (ey <= hi)).sum(), 1))),
              pct(float(c.sum() / max(m.sum(), 1))), pct(float(1.0 - tim_gap[c].mean())) if c.any() else "n/a"))

    # habits (leave one out) -----------------------------------------------------------------------------------------------------------------------------------
    by_k = defaultdict(list)
    for e in range(len(ev)):
        if cls[e]:
            by_k[ek[e]].append(e)
    habit = np.full(len(ev), -1)
    strength = np.full(len(ev), np.nan)
    agree_gap, agree_bu = [], []
    for k, lst in by_k.items():
        tg = np.array([tim_gap[e] for e in lst])
        tb = np.array([tim_bu[e] for e in lst])
        for j, e in enumerate(lst):
            if len(lst) - 1 < MIN_OTHERS:
                continue
            others = np.delete(tg, j)
            p = others.mean()
            habit[e] = 1 if p >= 0.5 else 0
            strength[e] = max(p, 1 - p)
            agree_gap.append(int(tg[j] == habit[e]))
            ob = np.delete(tb, j)
            pb = ob.mean()
            agree_bu.append(int(tb[j] == (1 if pb >= 0.5 else 0)))
    for e in range(len(ev)):                                              # events that are not classifiable themselves: habit from all classifiable quarters of the stock
        if cls[e] or habit[e] != -1:
            continue
        lst = by_k.get(ek[e], [])
        if len(lst) >= MIN_OTHERS:
            p = float(np.mean([tim_gap[x] for x in lst]))
            habit[e] = 1 if p >= 0.5 else 0
            strength[e] = max(p, 1 - p)
    stk = [max(np.mean([tim_gap[e] for e in lst]), 1 - np.mean([tim_gap[e] for e in lst])) for lst in by_k.values() if len(lst) >= 8]
    print("\nMETHOD CHECK 1: HABIT STABILITY (leave one out, classifiable events whose stock has at least %d other classifiable quarters)" % MIN_OTHERS)
    ag, ab_ = float(np.mean(agree_gap)), float(np.mean(agree_bu))
    print("  gap method:            an event's own classification matches its habit in %s of %d events" % (pct(ag), len(agree_gap)))
    print("  close-to-close method: the same events, the larger |miss| of the two days: %s" % pct(ab_))
    print("  stocks with at least 8 classifiable quarters: %d | median majority share %s | stocks at 90%% or more: %s" % (len(stk), pct(float(np.median(stk))), pct(float(np.mean(np.array(stk) >= 0.9)))))

    print("\nMETHOD CHECK 2: RECALLED REPORTING HABITS (UNVERIFIED recollection; share of each ticker's classifiable events classified as recalled)")
    ok_t, tot_t = 0, 0
    kk = {t: k for k, t in enumerate(tickers)}
    line = []
    for t, want in RECALL.items():
        k = kk.get(t)
        lst = by_k.get(k, []) if k is not None else []
        if len(lst) < 8:
            line.append("%s n/a" % t)
            continue
        share = float(np.mean([int(tim_gap[e] == want) for e in lst]))
        tot_t += 1
        ok_t += int(share >= 0.9)
        line.append("%s %.0f%% (n %d, %s)" % (t, 100 * share, len(lst), "AMC" if want else "BMO"))
    print("  " + " | ".join(line))
    valid_method = ag >= 0.90 and ag - ab_ >= 0.03 and ok_t >= 12
    print("  recalled tickers at 90%% or more: %d of %d testable" % (ok_t, tot_t))
    print("  VERDICT (pre-set): METHOD %s (gap agreement %.1f%% vs 90%%; margin over close-to-close %+.1f points vs 3; tickers %d vs 12)" % ("VALID" if valid_method else "NOT VALID", 100 * ag, 100 * (ag - ab_), ok_t))

    # multipliers by role ---------------------------------------------------------------------------------------------------------------------------------------
    base_mask = np.isfinite(bu2) & ~near & (years >= TEST_START)[None, :]
    base_mean, base_med = float(bu2[base_mask].mean()), float(np.median(bu2[base_mask]))
    print("\nBASELINE (ordinary stock-days at least %d days before and %d days after an earnings day from %d): mean squared band unit %.3f, median %.3f (chi-square(1) would give 1.000 and 0.455)" % (-BASE_NEAR[0], BASE_NEAR[1], TEST_START, base_mean, base_med))

    def stats(idx_days):
        v = bu2[idx_days[0], idx_days[1]]
        v = v[np.isfinite(v)]
        if len(v) < 30:
            return None
        return len(v), float(np.sqrt(v.mean() / base_mean)), float(np.sqrt(np.median(v) / base_med)), float((v >= 9.0).mean())

    def row(lab, sel, role):
        # role: 'R', 'N', 'd0', 'd1'
        ks, ii, hh = ek[sel], ei[sel], habit[sel]
        if role == "R":
            days = ii + (hh == 1)
        elif role == "N":
            days = ii + (hh == 0)
        elif role == "d0":
            days = ii
        else:
            days = ii + 1
        return stats((ks, days))

    strong = (habit != -1) & (strength >= STRONG)
    print("\nMULTIPLIERS BY ROLE (events with a habit that is STRONG: at least %.0f%% among the other classifiable quarters; %d of %d events = %s)" % (100 * STRONG, int(strong.sum()), len(ev), pct(float(strong.mean()))))
    print("  %-10s %-34s %7s | %9s %9s | %s" % ("era", "day", "n", "mult mean", "mult med", "share of days with |miss| >= 3 band units"))
    out = {}
    for lab, lo, hi in [("all years", 0, 9999)] + ERAS:
        sel_e = (ey >= lo) & (ey <= hi)
        for name, sel, role in (("reaction day (by habit)", strong & sel_e, "R"), ("other day (by habit)", strong & sel_e, "N"), ("pooled day 0, all events", sel_e, "d0"), ("pooled day +1, all events", sel_e, "d1")):
            st = row(lab, sel, role)
            if st:
                out[(lab, role)] = st
                print("  %-10s %-34s %7d | %8.2fx %8.2fx | %s" % (lab, name, st[0], st[1], st[2], pct(st[3])))
    if ("all years", "R") in out and ("all years", "N") in out:
        mR, mN = out[("all years", "R")][1], out[("all years", "N")][1]
        pbmo = float(np.mean(habit[strong] == 0))
        m0 = row("all", strong, "d0")
        print("\n  BMO share among strong-habit events %s | identity check on those events: pooled day-0 squared multiplier %.2f vs BMO-share mix of the role multipliers %.2f" % (pct(pbmo), m0[1] ** 2, pbmo * mR ** 2 + (1 - pbmo) * mN ** 2))
        print("  VERDICT (pre-set): TIMING %s (reaction-day multiplier %.2fx vs other-day %.2fx = ratio %.2f; threshold 1.5)" % ("MATTERS" if mR >= 1.5 * mN else "DOES NOT MATTER", mR, mN, mR / mN))
        print("  for reference the committed card uses day 0 = 2.72x and day +1 = 2.47x (a different, likelihood-based construction; the pooled rows above are this script's own version)")
    print("\ntotal %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
