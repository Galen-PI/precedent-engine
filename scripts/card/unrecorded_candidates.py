#!/usr/bin/env python3
"""
unrecorded_candidates.py -- READ-ONLY (local matrices and caches; the database is read for events, 8-K filings, securities and the news-article counts). Writes two CSV files in results/.
THE QUESTION. About three quarters of the squared miss we cannot explain sits on ORDINARY days (no own recorded event, no earnings or Regulation FD window), and the gap samples we read showed real
news there that nobody recorded (an activist stake, a failed drug trial, a guidance cut, a mine accident) next to aftershocks of an earlier shock and some days with nothing found. How much of the
big ordinary-day miss mass carries a SIGNATURE of real information, and which rows are the candidates to read? Three signatures we already hold, none of them derived from the miss itself:
  AFTERSHOCK (mechanical): the previous day was itself a big miss, or the day falls within 5 trading days after an own event / earnings / Regulation FD window.
  VOLUME SPIKE: volume on the day >= 2.0x the median of the previous 20 trading days (market_prices.volume, via data_cache/volume from build_volume_cache.py). Days within 25 trading days of a stock
                split (a jump in close / adjusted_close of 15% or more) are excluded, because split-day volume changes are artefacts.
  ARTICLE SPIKE: the day's article count (company_sentiment_timeline, 2015 on) >= 3 and >= 3x the mean of the previous 28 trading days (floor 0.5). Weekend counts are added to the next trading day.
DEFINITIONS. Ordinary = no own recorded event, earnings (2.02) or Regulation FD (7.01) window on day 0 or +1. BIG = |miss| >= 3.0 band units (the card's current scale: standardized miss scaled by the
day's market-wide stress); CALM = under 1.0; MID = 1.0-3.0. Test years from 2006.

Usage:   python3 -u scripts/card/unrecorded_candidates.py [SEED] [N_PER_STRATUM] [SAMPLE_FROM]        defaults: 20261020  12  2024-01-01
Needs:   data_cache/audit_matrices.npz (gap_audit.py), data_cache/volume (build_volume_cache.py), and the database.
Writes:  results/unrecorded_candidates.csv (every ordinary big miss with its category) and results/unrecorded_reading_sample_SEED.csv (a reproducible stratified sample to READ, columns to fill in).
DESCRIPTIVE: no pass/fail rule on the counts; they map the big ordinary misses. The only judgement is the READING RULE below.

READING RULE (written before any row is read). Each sampled row is read for what happened that day (a specific, dated item that plausibly explains the move: guidance or pre-announcement, analyst
action, activist or insider filing, clinical or regulatory result, accident or outage, M&A or financing news, legal item, sector or macro news, index change, ...) and recorded as FOUND (with the
item and its source) or NOT FOUND. The volume signature counts as a VALIDATED detector of unrecorded information if the FOUND rate in the volume-spike strata is at least 2x the FOUND rate in the
quiet stratum, with the sample sizes and an exact test reported. With about 12 rows per stratum the interval will be wide, so any conclusion is labeled a LEAD, not a result.
PREDICTIONS (before the run): BIG ordinary misses are 0.6-0.9% of ordinary stock-days (the calibrated tail share beyond 3.0 band units was 0.71%); a volume spike marks 5-12% of CALM days and
55-80% of BIG misses (enrichment at least 5x); an article spike marks 2-6% of CALM days and 10-30% of BIG misses (enrichment at least 3x); aftershocks are 10-25% of BIG misses; among the
non-aftershock BIG misses, 10-25% are QUIET (no volume spike); the pool 'volume spike, not an aftershock' is 45-65% of BIG misses; the pool grows with the years because volume data and news coverage
improve.
"""
import os, sys, time, bisect, csv, random, pickle, warnings
from collections import defaultdict
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
VOL_DIR = os.path.join(ROOT, "data_cache", "volume")
RESULTS = os.path.join(ROOT, "results")
TEST_START = 2006
BIG, CALM = 3.0, 1.0
VR_SPIKE, VR_BIG = 2.0, 3.0
VOL_WIN, MIN_VOL_OBS = 20, 10
SPLIT_JUMP, SPLIT_PAD = 0.15, 25
ART_WIN, ART_MIN, ART_MULT, ART_FLOOR = 28, 3, 3.0, 0.5
POST_FLAG_DAYS = 5
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


def load_volume(ids, dl):
    N, n = len(ids), len(dl)
    pos = {d: i for i, d in enumerate(dl)}
    VOL = np.full((N, n), np.nan)
    SPL = np.zeros((N, n), dtype=bool)
    have = 0
    for k, sid in enumerate(ids):
        path = os.path.join(VOL_DIR, "%s.pkl" % sid)
        if not os.path.exists(path):
            continue
        with open(path, "rb") as fh:
            d = pickle.load(fh)
        have += 1
        ii = np.array([pos.get(x, -1) for x in d["dates"]])
        cl = np.array([np.nan if v is None else v for v in d["close"]], dtype=np.float64)
        ad = np.array([np.nan if v is None else v for v in d["adj"]], dtype=np.float64)
        vv = np.array([np.nan if v is None else v for v in d["vol"]], dtype=np.float64)
        ok = ii >= 0
        VOL[k, ii[ok]] = np.where(vv[ok] > 0, vv[ok], np.nan)
        with np.errstate(invalid="ignore", divide="ignore"):
            lf = np.log(cl / ad)
        valid = np.where(np.isfinite(lf))[0]
        if valid.size > 1:
            jumps = np.abs(np.diff(lf[valid])) >= SPLIT_JUMP
            for j in valid[1:][jumps]:
                t = ii[j]
                if t >= 0:
                    SPL[k, max(0, t - SPLIT_PAD): t + SPLIT_PAD + 1] = True
    return VOL, SPL, have


def vol_ratio(VOL):
    N, n = VOL.shape
    VR = np.full((N, n), np.nan)
    for k in range(N):
        v = VOL[k]
        if np.isfinite(v).sum() < 100:
            continue
        W = sliding_window_view(v, VOL_WIN)
        cnt = np.isfinite(W).sum(axis=1)
        med = np.where(cnt >= MIN_VOL_OBS, np.nanmedian(W, axis=1), np.nan)
        VR[k, VOL_WIN:] = v[VOL_WIN:] / med[:n - VOL_WIN]
    return VR


def load_articles(sb, ids, dl):
    N, n = len(ids), len(dl)
    sec = paged(lambda: sb.table("securities").select("id,entity_id").order("id"))
    ent_of = {r["id"]: r["entity_id"] for r in sec if r.get("entity_id")}
    k_of_ent = defaultdict(list)
    for k, sid in enumerate(ids):
        e = ent_of.get(sid)
        if e:
            k_of_ent[e].append(k)
    rows = paged(lambda: sb.table("company_sentiment_timeline").select("entity_id,date,article_count").order("id"))
    per = defaultdict(dict)
    for r in rows:
        e = r["entity_id"]
        if e not in k_of_ent or r.get("article_count") is None:
            continue
        t = bisect.bisect_left(dl, str(r["date"])[:10])
        if t < n:
            per[e][t] = per[e].get(t, 0) + int(r["article_count"])
    AC = np.full((N, n), np.nan)
    for e, dct in per.items():
        ts = sorted(dct)
        lo, hi = ts[0], ts[-1]
        arr = np.zeros(hi - lo + 1)
        for t, c in dct.items():
            arr[t - lo] = c
        for k in k_of_ent[e]:
            AC[k, lo:hi + 1] = arr
    return AC, len(per), len(rows)


def article_spike(AC):
    N, n = AC.shape
    SP = np.zeros((N, n), dtype=bool)
    COV = np.zeros((N, n), dtype=bool)
    for k in range(N):
        a = AC[k]
        if np.isfinite(a).sum() < 100:
            continue
        W = sliding_window_view(a, ART_WIN)
        cnt = np.isfinite(W).sum(axis=1)
        base = np.where(cnt >= ART_WIN // 2, np.nanmean(W, axis=1), np.nan)[:n - ART_WIN]
        cur = a[ART_WIN:]
        okc = np.isfinite(cur) & np.isfinite(base)
        COV[k, ART_WIN:] = okc
        SP[k, ART_WIN:] = okc & (cur >= ART_MIN) & (cur >= ART_MULT * np.maximum(base, ART_FLOOR))
    return SP, COV


def pct(x, d=1):
    return ("%." + str(d) + "f%%") % (100.0 * x)


def main():
    t0 = time.time()
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261020
    n_per = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    sample_from = sys.argv[3] if len(sys.argv) > 3 else "2024-01-01"
    if not os.path.exists(CACHE_FILE):
        sys.exit("Run gap_audit.py first: it builds %s." % CACHE_FILE)
    if not os.path.isdir(VOL_DIR):
        sys.exit("Run build_volume_cache.py first: it builds %s." % VOL_DIR)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, tickers, E, SD, Yr = d["dates"], d["ids"].tolist(), d["tickers"], d["E"], d["SD"], d["Y"]
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
    EA = np.zeros((N, n), dtype=bool)
    F701 = np.zeros((N, n), dtype=bool)
    for r in paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is None:
            continue
        its = dc.parse_items(r.get("item_codes"))
        i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
        if i >= n:
            continue
        tgt = EA if "2.02" in its else (F701 if "7.01" in its else None)
        if tgt is not None:
            tgt[k, i] = True
            if i + 1 < n:
                tgt[k, i + 1] = True
    flag_any = EV | EA | F701
    ordinary = ~flag_any
    cs = np.cumsum(flag_any, axis=1)
    post_flag = np.zeros((N, n), dtype=bool)
    post_flag[:, POST_FLAG_DAYS + 1:] = (cs[:, POST_FLAG_DAYS:-1] - cs[:, :-POST_FLAG_DAYS - 1]) > 0     # any flagged day among t-5 .. t-1
    prev_big = np.zeros((N, n), dtype=bool)
    prev_big[:, 1:] = np.nan_to_num(bu[:, :-1], nan=0.0) >= BIG

    VOL, SPL, have = load_volume(ids, dl)
    VR = vol_ratio(VOL)
    VR[SPL] = np.nan
    AC, n_ent, n_rows = load_articles(sb, ids, dl)
    ASP, ACOV = article_spike(AC)
    print("securities with a volume file: %d of %d | volume ratio available on %s of the stock-days scored | article rows read: %d for %d entities, coverage on %s of scored stock-days | %.0fs" % (
        have, N, pct(float(np.isfinite(VR[ok]).mean())), n_rows, n_ent, pct(float(ACOV[ok].mean())), time.time() - t0), flush=True)

    base = ok & ordinary & ~SPL
    big, calm, mid = base & (bu >= BIG), base & (bu < CALM), base & (bu >= CALM) & (bu < BIG)
    vs2, vs3 = np.isfinite(VR) & (VR >= VR_SPIKE), np.isfinite(VR) & (VR >= VR_BIG)
    vfin = np.isfinite(VR)
    print("\nORDINARY STOCK-DAYS BY SIZE OF THE MISS: %d scored | BIG (>= %.1f band units) %d (%s) | MID %d | CALM %d" % (
        int(base.sum()), BIG, int(big.sum()), pct(float(big.sum()) / base.sum(), 2), int(mid.sum()), int(calm.sum())))
    print("\nHOW OFTEN EACH SIGNATURE APPEARS (the rate on CALM days is the baseline; enrichment = BIG / CALM)")
    print("  %-8s %10s | %14s %14s | %10s %14s" % ("", "days", "volume >= 2x", "volume >= 3x", "days(art.)", "article spike"))
    rates = {}
    for lab, m in (("CALM", calm), ("MID", mid), ("BIG", big)):
        mv, ma = m & vfin, m & ACOV
        rates[lab] = (float(vs2[mv].mean()) if mv.any() else float("nan"), float(vs3[mv].mean()) if mv.any() else float("nan"), float(ASP[ma].mean()) if ma.any() else float("nan"))
        print("  %-8s %10d | %14s %14s | %10d %14s" % (lab, int(m.sum()), pct(rates[lab][0]), pct(rates[lab][1]), int(ma.sum()), pct(rates[lab][2])))
    print("  enrichment BIG / CALM: volume >= 2x %.1fx | volume >= 3x %.1fx | article spike %.1fx" % (rates["BIG"][0] / rates["CALM"][0], rates["BIG"][1] / rates["CALM"][1], rates["BIG"][2] / rates["CALM"][2]))

    after_prev = big & prev_big
    after_flag = big & ~after_prev & post_flag
    rest = big & ~after_prev & ~after_flag
    qv = rest & vfin
    print("\nANATOMY OF THE %d BIG ORDINARY MISSES" % int(big.sum()))
    print("  aftershock, previous day was a big miss:                 %7d  %s" % (int(after_prev.sum()), pct(float(after_prev.sum()) / big.sum())))
    print("  aftershock, within %d days after an event/earnings/7.01:  %7d  %s" % (POST_FLAG_DAYS, int(after_flag.sum()), pct(float(after_flag.sum()) / big.sum())))
    print("  everything else:                                         %7d  %s" % (int(rest.sum()), pct(float(rest.sum()) / big.sum())))
    print("    of which with a volume ratio available:                %7d" % int(qv.sum()))
    print("      volume spike (>= 2x):                                %7d  %s of those" % (int((qv & vs2).sum()), pct(float((qv & vs2).sum()) / max(qv.sum(), 1))))
    print("      QUIET (no volume spike):                             %7d  %s of those" % (int((qv & ~vs2).sum()), pct(float((qv & ~vs2).sum()) / max(qv.sum(), 1))))
    cx = qv & ACOV
    print("    with BOTH volume ratio and article coverage (2015 on): %7d" % int(cx.sum()))
    for lab, a_, b_ in (("volume spike + article spike", True, True), ("volume spike only", True, False), ("article spike only", False, True), ("neither (quiet)", False, False)):
        m = cx & (vs2 == a_) & (ASP == b_)
        print("      %-30s %7d  %s" % (lab, int(m.sum()), pct(float(m.sum()) / max(cx.sum(), 1))))
    print("\nBY ERA: share of the non-aftershock big misses that carry a volume spike (the candidate pool) and how large it is")
    for lab, lo, hi in ERAS:
        m = qv & ((years >= lo) & (years <= hi))[None, :]
        print("  %-10s %6d with a volume ratio | spike %s | pool size %d" % (lab, int(m.sum()), pct(float((m & vs2).sum()) / max(m.sum(), 1)), int((m & vs2).sum())))
    print("  pool by year (volume spike, no aftershock): " + " ".join("%d:%d" % (y, int((qv & vs2 & (years == y)[None, :]).sum())) for y in range(TEST_START, int(years.max()) + 1)))

    # the list and the reading sample
    cat = np.full((N, n), "", dtype=object)
    cat[after_prev] = "aftershock: previous day big"
    cat[after_flag] = "aftershock: within %d days after an event/earnings/7.01" % POST_FLAG_DAYS
    cat[rest & vfin & vs2 & ACOV & ASP] = "volume spike + article spike"
    cat[rest & vfin & vs2 & ~(ACOV & ASP)] = "volume spike only"
    cat[rest & vfin & ~vs2 & ACOV & ASP] = "article spike only"
    cat[rest & vfin & ~vs2 & ~(ACOV & ASP)] = "quiet (neither)"
    cat[rest & ~vfin] = "no volume data"
    os.makedirs(RESULTS, exist_ok=True)
    rows_big = sorted(zip(*np.where(big)), key=lambda x: (x[1], x[0]))
    path_all = os.path.join(RESULTS, "unrecorded_candidates.csv")
    with open(path_all, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "ticker", "return_pct", "miss_pct", "band_units", "volume_ratio", "article_count", "category"])
        for k, t in rows_big:
            w.writerow([dl[t], tickers[k], "%.2f" % (100 * float(Yr[k, t])), "%.2f" % (100 * float(E[k, t])), "%.2f" % bu[k, t],
                        "" if not np.isfinite(VR[k, t]) else "%.2f" % VR[k, t], "" if not np.isfinite(AC[k, t]) else int(AC[k, t]), cat[k, t]])
    strata = ["volume spike + article spike", "volume spike only", "quiet (neither)", "aftershock: previous day big"]
    first = bisect.bisect_left(dl, sample_from)
    rng = random.Random(seed)
    path_s = os.path.join(RESULTS, "unrecorded_reading_sample_%d.csv" % seed)
    print("\nREADING SAMPLE (from %s; %d per stratum; seed %d)" % (sample_from, n_per, seed))
    with open(path_s, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stratum", "date", "ticker", "return_pct", "miss_pct", "band_units", "volume_ratio", "article_count", "found (yes/no)", "category", "what_happened_and_source"])
        for s_ in strata:
            pool = [(k, t) for k, t in rows_big if t >= first and cat[k, t] == s_]
            pick = sorted(rng.sample(pool, min(n_per, len(pool))), key=lambda x: (x[1], x[0]))
            print("  %-32s available %5d | sampled %d" % (s_, len(pool), len(pick)))
            for k, t in pick:
                w.writerow([s_, dl[t], tickers[k], "%.2f" % (100 * float(Yr[k, t])), "%.2f" % (100 * float(E[k, t])), "%.2f" % bu[k, t],
                            "" if not np.isfinite(VR[k, t]) else "%.2f" % VR[k, t], "" if not np.isfinite(AC[k, t]) else int(AC[k, t]), "", "", ""])
    print("\nwrote %s and %s | total %.0fs" % (path_all, path_s, time.time() - t0))


if __name__ == "__main__":
    main()
