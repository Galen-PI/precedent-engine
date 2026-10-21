#!/usr/bin/env python3
"""
unrecorded_joins.py -- READ-ONLY (local matrices and caches; the database is read for events and ALL 8-K filings). Writes nothing.
THE QUESTION. About 12,700 big ordinary misses (>= 3.0 band units, no own event / earnings / Regulation FD window, not an aftershock) have no recorded explanation. Three explanations may already be in
data we hold, and each is a join, not new data:
  1. OUR OWN 8-Ks. 'Ordinary' only means no recorded event and no 2.02 (earnings) or 7.01 (Regulation FD) filing. A routine-looking 8-K on the day (items 8.01, 5.02, 1.01, 2.03 and so on) may carry the
     news. An 8-K filed on date f is attached to stock-days i and i+1, i = the first trading day on or after f (the same convention as the earnings flags). Filings that list 2.02 or 7.01 are skipped (they
     are already flagged), and item 9.01 (exhibits) is ignored. Shown: the share of stock-days with any other 8-K for CALM / MID / BIG, and per item code the enrichment BIG / CALM.
  2. CALENDAR AND FLOW DAYS. Monthly and quarterly options expiry (third Friday, and the third Friday of Mar / Jun / Sep / Dec), quarter-end, the Russell reconstitution (last Friday of June), the day after
     Thanksgiving and Dec 24. Volume rises on these days for every stock without any stock-specific news, which would inflate volume spikes. Shown: the rate of big misses, and of volume spikes on CALM days, on each
     day type against ordinary days of none of the listed types.
  3. PRE-EVENT WINDOWS. Big ordinary misses in the 5 trading days (and the 1 day) BEFORE the first flagged day of an own earnings, recorded-event or Regulation FD window: leakage, anticipation, or the story
     starting before the filing.
Populations are those of volume_calibration.py: stock-days from 2006 with a volume ratio (split-masked); ordinary non-aftershock (the previous day was not a big miss, no flagged window ended in the previous 5
trading days); CALM < 1.0 band unit, MID 1.0-3.0, BIG >= 3.0. A volume spike is a ratio >= 2.0x the median of the previous 20 days.
Usage:   python3 -u scripts/card/unrecorded_joins.py        Needs: data_cache/audit_matrices.npz, data_cache/volume, the database.
DESCRIPTIVE: no verdict. A result is called NOTABLE only if the point estimate of an enrichment is >= 1.30 (or <= 0.77) AND its 95% interval (resampling calendar MONTHS, 500 resamples, because misses cluster
in time) excludes 1.0. PREDICTIONS (before the run): any other 8-K marks about 5-8% of CALM days and 15-30% of BIG misses (enrichment 2-4x); the most enriched items include 8.01, 1.01, 2.03, 5.02 and 1.02;
quarterly options expiry and the Russell day lift the volume-spike rate on CALM days by 1.5x or more but change the rate of big misses by less than 1.2x; the 5 days before a recorded-event window show an
enrichment of 1.2-1.5x, before earnings and Regulation FD windows 1.0-1.2x.
"""
import os, sys, time, bisect, datetime, warnings
from collections import Counter
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc

CACHE_FILE = uc.CACHE_FILE
TEST_START = 2006
BIG, CALM = 3.0, 1.0
VR_SPIKE = 2.0
SKIP_ITEMS = {"2.02", "7.01", "9.01"}
TOP_ITEMS = 14
N_BOOT = 500
SEED = 20261021


def pct(x):
    return "%5.1f%%" % (100.0 * x) if np.isfinite(x) else "  n/a "


def main():
    t0 = time.time()
    if not os.path.exists(CACHE_FILE):
        sys.exit("Run gap_audit.py first: it builds %s." % CACHE_FILE)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E, SD = d["dates"], d["ids"].tolist(), d["E"], d["SD"]
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
    ok = valid & (cnt[None, :] > 20) & np.isfinite(bu) & (years >= TEST_START)[None, :]

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids))
    EV = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                EV[k, t] = True
    EA0 = np.zeros((N, n), dtype=bool)
    EA1 = np.zeros((N, n), dtype=bool)
    F701 = np.zeros((N, n), dtype=bool)
    other = []                      # (stock index, day index, set of items) for filings with no 2.02 / 7.01
    item_count = Counter()
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
        else:
            its2 = set(its) - SKIP_ITEMS
            if its2:
                other.append((k, i, its2))
                item_count.update(its2)
    EA1 &= ~EA0
    flag_any = EV | EA0 | EA1 | F701
    cs = np.cumsum(flag_any, axis=1)
    post_flag = np.zeros((N, n), dtype=bool)
    post_flag[:, uc.POST_FLAG_DAYS + 1:] = (cs[:, uc.POST_FLAG_DAYS:-1] - cs[:, :-uc.POST_FLAG_DAYS - 1]) > 0
    prev_big = np.zeros((N, n), dtype=bool)
    prev_big[:, 1:] = np.nan_to_num(bu[:, :-1], nan=0.0) >= BIG
    VOL, SPL, have = uc.load_volume(ids, dl)
    VR = uc.vol_ratio(VOL)
    VR[SPL] = np.nan
    base = ok & ~SPL & np.isfinite(VR)
    ord_na = base & ~flag_any & ~prev_big & ~post_flag
    calm, mid, big = ord_na & (bu < CALM), ord_na & (bu >= CALM) & (bu < BIG), ord_na & (bu >= BIG)
    spike = np.isfinite(VR) & (VR >= VR_SPIKE)

    any8k = np.zeros((N, n), dtype=bool)
    top_items = [it for it, _ in item_count.most_common(TOP_ITEMS)]
    item_mask = {it: np.zeros((N, n), dtype=bool) for it in top_items}
    for k, i, its in other:
        any8k[k, i] = True
        if i + 1 < n:
            any8k[k, i + 1] = True
        for it in its:
            if it in item_mask:
                item_mask[it][k, i] = True
                if i + 1 < n:
                    item_mask[it][k, i + 1] = True
    rng = np.random.RandomState(SEED)

    def per_month(mask):
        return np.bincount(months[np.where(mask)[1]], minlength=M).astype(float)

    def ratio(hit_a, pop_a, hit_b, pop_b):
        """(rate_a / rate_b, 95% interval, rate_a, rate_b, hits in a) with a month-block bootstrap."""
        ah, at, bh, bt = per_month(hit_a & pop_a), per_month(pop_a), per_month(hit_b & pop_b), per_month(pop_b)
        def est(w):
            ra, rb = (w @ ah) / max(w @ at, 1.0), (w @ bh) / max(w @ bt, 1.0)
            return ra / rb if rb > 0 else float("nan")
        pt = est(np.ones(M))
        live = np.where(at + bt > 0)[0]
        out = []
        for _ in range(N_BOOT):
            w = np.bincount(rng.choice(live, size=len(live)), minlength=M).astype(float)
            out.append(est(w))
        lo, hi = np.nanpercentile(out, [2.5, 97.5])
        return pt, lo, hi, float(ah.sum() / max(at.sum(), 1)), float(bh.sum() / max(bt.sum(), 1)), int(ah.sum())

    def notable(pt, lo, hi):
        return "NOTABLE" if ((pt >= 1.30 and lo > 1.0) or (pt <= 0.77 and hi < 1.0)) else ""

    print("securities with volume: %d of %d | filings other than 2.02 / 7.01: %d | %.0fs" % (have, N, len(other), time.time() - t0), flush=True)
    print("\nPOPULATIONS: CALM %d | MID %d | BIG %d (ordinary, non-aftershock, with a volume ratio)" % (int(calm.sum()), int(mid.sum()), int(big.sum())))

    print("\n1. OWN 8-K FILINGS OTHER THAN 2.02 / 7.01, on the stock-day or attached to it (filing day and the next trading day)")
    pt, lo, hi, ra, rb, nh = ratio(any8k, big, any8k, calm)
    print("  any other 8-K:   CALM %s | MID %s | BIG %s | enrichment BIG / CALM %.2fx [%.2f, %.2f] %s" % (pct(rb), pct(float((any8k & mid).sum() / mid.sum())), pct(ra), pt, lo, hi, notable(pt, lo, hi)))
    for lab, m in (("BIG with a volume spike", big & spike), ("BIG quiet (no spike)", big & ~spike)):
        print("  %-24s with another 8-K: %s  (%d of %d)" % (lab, pct(float((any8k & m).sum() / max(m.sum(), 1))), int((any8k & m).sum()), int(m.sum())))
    print("  %-8s %9s %9s %9s | %-26s %7s" % ("item", "CALM", "MID", "BIG", "enrichment BIG / CALM", "n BIG"))
    rows = []
    for it in top_items:
        pt, lo, hi, ra, rb, nh = ratio(item_mask[it], big, item_mask[it], calm)
        rows.append((pt, it, lo, hi, ra, rb, nh))
    for pt, it, lo, hi, ra, rb, nh in sorted(rows, reverse=True):
        print("  %-8s %9s %9s %9s | %5.2fx [%5.2f, %5.2f] %-8s %7d" % (it, pct(rb), pct(float((item_mask[it] & mid).sum() / mid.sum())), pct(ra), pt, lo, hi, notable(pt, lo, hi), nh))
    ms = big & spike
    unexpl = ms & ~any8k
    print("  BIG misses with a volume spike: %d | of those with NO other 8-K on the day: %d (%s) -> still unexplained by anything we hold" % (int(ms.sum()), int(unexpl.sum()), pct(float(unexpl.sum() / max(ms.sum(), 1)))))

    print("\n2. CALENDAR AND FLOW DAYS (among ordinary non-aftershock stock-days)")
    dts = [datetime.date.fromisoformat(x) for x in dl]
    wd, dom, mon = np.array([x.weekday() for x in dts]), np.array([x.day for x in dts]), np.array([x.month for x in dts])
    last_of_month = np.array([(i + 1 < n and dts[i + 1].month != dts[i].month) for i in range(n)])
    third_fri = (wd == 4) & (dom >= 15) & (dom <= 21)
    kinds = [("third Friday (monthly options expiry)", third_fri), ("quarterly expiry (third Friday of Mar/Jun/Sep/Dec)", third_fri & np.isin(mon, (3, 6, 9, 12))),
             ("last trading day of the month", last_of_month), ("quarter-end (last trading day of Mar/Jun/Sep/Dec)", last_of_month & np.isin(mon, (3, 6, 9, 12))),
             ("Russell reconstitution (last Friday of June)", (mon == 6) & (wd == 4) & (dom >= 24)), ("day after Thanksgiving", (mon == 11) & (wd == 4) & (dom >= 23) & (dom <= 29)),
             ("December 24", (mon == 12) & (dom == 24))]
    pop = ord_na
    special = np.zeros(n, dtype=bool)
    for _, tm in kinds:
        special |= tm
    C = np.broadcast_to((~special)[None, :], (N, n))
    print("  (each day type is compared with ordinary days of NONE of these types: %d days)" % int((~special).sum()))
    print("  %-52s %6s | %-34s | %-34s | %s" % ("day type", "days", "big-miss rate vs clean days", "spike rate on CALM stock-days", "spike rate among BIG"))
    for lab, tm in kinds:
        T = np.broadcast_to(tm[None, :], (N, n))
        if int((T & pop).sum()) < 1000:
            continue
        pt, lo, hi, ra, rb, nh = ratio(big, pop & T, big, pop & C)
        pt2, lo2, hi2, ra2, rb2, nh2 = ratio(spike, calm & T, spike, calm & C)
        bs_t, bs_o = float((spike & big & T).sum() / max((big & T).sum(), 1)), float((spike & big & C).sum() / max((big & C).sum(), 1))
        print("  %-52s %6d | %s vs %s = %.2fx [%.2f, %.2f] %-8s | %s vs %s = %.2fx [%.2f, %.2f] %-8s | %s vs %s" % (
            lab, int(tm.sum()), pct(ra), pct(rb), pt, lo, hi, notable(pt, lo, hi), pct(ra2), pct(rb2), pt2, lo2, hi2, notable(pt2, lo2, hi2), pct(bs_t), pct(bs_o)))

    print("\n3. PRE-EVENT WINDOWS (ordinary non-aftershock stock-days shortly BEFORE the first flagged day of a window)")
    def starts(m):
        s = m.copy()
        s[:, 1:] &= ~m[:, :-1]
        return s
    def within_next(S_, h):
        c = np.cumsum(S_, axis=1)
        out = np.zeros((N, n), dtype=bool)
        out[:, :n - h] = (c[:, h:] - c[:, :n - h]) > 0
        return out
    kinds3 = [("earnings (2.02) window", starts(EA0)), ("recorded-event window", starts(EV)), ("Regulation FD (7.01) window", starts(F701)), ("any of the three", starts(flag_any))]
    print("  %-30s %-9s %9s | %-36s | %s" % ("window about to start", "within", "days", "big-miss rate vs other days", "spike rate among those BIG"))
    for lab, S_ in kinds3:
        for h in (1, 5):
            P = within_next(S_, h)
            if int((P & pop).sum()) < 1000:
                continue
            pt, lo, hi, ra, rb, nh = ratio(big, pop & P, big, pop & ~P)
            bsp = float((spike & big & P).sum() / max((big & P).sum(), 1))
            print("  %-30s %-9s %9d | %s vs %s = %.2fx [%.2f, %.2f] %-8s | %s (n %d)" % (lab, "%d day%s" % (h, "" if h == 1 else "s"), int((P & pop).sum()), pct(ra), pct(rb), pt, lo, hi, notable(pt, lo, hi), pct(bsp), int((big & P).sum())))
    print("\ntotal %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
