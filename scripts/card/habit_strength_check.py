#!/usr/bin/env python3
"""
habit_strength_check.py -- READ-ONLY (matrices, the OHLC cache, the database for 8-K filings and recorded events, models/*.json). Writes nothing.
WHY. The card's role bands use a stock's habit: the majority of its last 4 classifiable quarters, ties going to the most recent. The TPL example (2026-08-06) was a 2-2 TIE broken by the latest quarter, and the stock reported in the other slot this time. The validated out-of-sample coverage averages over all habit strengths, so ties were never
measured separately; the card now labels them WEAK HABIT. QUESTION: how reliable is a habit by strength, and are the role bands still better than the pooled bands on 2-2 ties?
GROUPS (isolated earnings releases from 2006: no own recorded event, no Regulation FD filing on day i or i+1, finite band units on days i and i+1, a habit; the same data and rules as build_earnings_role_model.py): by the split of the last 4 classifiable quarters: 4-0 (all four the same), 3-1, and 2-2 (a tie).
MEASURES per group and era (2006-2012, 2013-2019, 2020-2026): the share of releases; AGREEMENT = among releases classifiable on their own gap (gap z >= 2 on day i or i+1), the share whose own label equals the habit; coverage of the DEPLOYED role edges (reaction and other day); coverage of the CURRENT pooled edges on the same days; and the interval score
IS = 2 x edge + 20 x max(|band units| - edge, 0), averaged over both days of each release, as the ratio ROLES / POOLED (below 1 = roles better). The pooled-eras tie ratio carries a 95% interval (calendar months resampled, 500). MATERIALITY: the overall ROLES / POOLED ratio with roles everywhere versus roles everywhere EXCEPT ties (ties on the pooled band).
PRE-SET RULE (before the first real run). TIE GUARD JUSTIFIED (2-2 ties use the pooled band) if the ROLES / POOLED ratio on 2-2 releases is above 1.00 over all eras together AND above 1.00 in at least two of the three eras. KEEP ROLES ON TIES (keep the WEAK HABIT label) if it is below 1.00 over all eras together AND below 1.00 in at least two eras. Otherwise INCONCLUSIVE: the status quo stands.
If the guard is justified the card patch is two lines (apply_role returns None on a tie) and the role model should be refit without ties.
PREDICTIONS (before the real run): shares of releases 4-0 62-78%, 3-1 14-24%, 2-2 7-14%; AGREEMENT 95% or more for 4-0, 80-90% for 3-1, 55-70% for 2-2; roles coverage on 2-2 ties: reaction day 90-97%, other day 72-88% (when the habit is wrong the 'other' day is the real reaction day); the tie ratio 0.93-1.06 (a close call: the guard is justified with probability about 35%);
the overall ratio changes by less than 0.01 whichever way ties are treated.
VALIDATION (synthetic worlds, 120 stocks, 2004-2024, run before the real data): CLEAN habits (no switching): ties are 0.1% of releases, verdict INCONCLUSIVE (too few); MIXED (40% of stocks release in a random slot): tie agreement 49.7%, tie ratio 1.057 [1.038, 1.080], verdict GUARD; NOISY (a 25% chance each quarter of the other slot): tie agreement 50.9%, ratio 1.023 [1.012, 1.033], GUARD;
REGIME (permanent flips every 6-14 quarters, so a tie is the first quarter after a flip): tie agreement 95.4%, ratio 0.909 [0.895, 0.922], verdict KEEP ROLES (the guard would have worsened the overall ratio by 0.012). In that last world the damage sits in the 3-1 group (agreement 55%, ratio 1.028): the pre-set rule does not cover 3-1; if the real 3-1 group reads above 1.00 it needs its own pre-registered rule, not a post-hoc switch.
Usage:   python3 -u scripts/card/habit_strength_check.py       Needs data_cache/audit_matrices.npz, data_cache/ohlc, the database, models/earnings_role_band_model.json, models/band_calibration.json, models/earnings_band_model.json.
"""
import os, sys, json, time, bisect, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc
import earnings_timing_check as etc
import earnings_roles as er

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = uc.CACHE_FILE
TEST_START = etc.TEST_START
ERAS = [("2006-2012", 2006, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]
N_BOOT, SEED = 500, 20261028
EDGES = None                       # (role reaction q90, role other q90, pooled day-0 q90, pooled day-+1 q90) in ordinary units; None = read the model files
EDGES_FROM_DATA = False            # test worlds only: fit all four edges on the data itself
GROUPS = [("4-0", (0, 4)), ("3-1", (1, 3)), ("2-2", (2,))]


def load_edges():
    rm = json.load(open(os.path.join(ROOT, "models", "earnings_role_band_model.json")))["groups"]
    cal = json.load(open(os.path.join(ROOT, "models", "band_calibration.json")))["edge_90"]
    mm = json.load(open(os.path.join(ROOT, "models", "earnings_band_model.json")))["multipliers_vs_ordinary_day"]
    return (rm[er.REACTION]["q90_ordinary_units"], rm[er.OTHER]["q90_ordinary_units"],
            cal["earnings window, day 0 (no event)"] * mm["earnings_day0"], cal["earnings window, day +1 (no event)"] * mm["earnings_day1"])


def IS(x, e):
    return 2 * e + 20.0 * np.maximum(x - e, 0.0)


def main():
    t0 = time.time()
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E, SD = d["dates"], d["ids"].tolist(), d["E"], d["SD"]
    N, n = E.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    months = np.array([int(x[:4]) * 12 + int(x[5:7]) - 1 for x in dl])
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
    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids))
    oth = np.zeros((N, n), dtype=bool)
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
    rec = []                                   # (year, month, |bu| day i, |bu| day i+1, habit, after-close count of the last 4, own label or -1)
    for k, lst in raw.items():
        ZG = er.gap_z_1d(O[k], C[k])
        hist = []
        for i in er.thin(lst):
            if i < er.GAP_WIN + 1 or i + 1 >= n or years[i] < TEST_START:
                continue
            a, b = ZG[i], ZG[i + 1]
            habit = er.majority(hist[-er.HIST:]) if len(hist) >= er.HIST else None
            b0, b1 = bu[k, i], bu[k, i + 1]
            classifiable = bool(np.isfinite(a) and np.isfinite(b) and max(a, b) >= er.CLASSIFY_Z)
            if habit is not None and not (oth[k, i] or oth[k, i + 1]) and np.isfinite(b0) and np.isfinite(b1):
                rec.append((int(years[i]), int(months[i]), abs(float(b0)), abs(float(b1)), habit, int(sum(hist[-er.HIST:])), (1 if b > a else 0) if classifiable else -1))
            if classifiable:
                hist.append(1 if b > a else 0)
    R = np.array(rec, dtype=float)
    yr, mo, b0, b1, hb, sa, own = R[:, 0], R[:, 1].astype(int), R[:, 2], R[:, 3], R[:, 4], R[:, 5], R[:, 6]
    react = np.where(hb == 1, b1, b0)
    other = np.where(hb == 1, b0, b1)
    if EDGES_FROM_DATA:
        qr, qo_, p0, p1 = np.percentile(react, 90), np.percentile(other, 90), np.percentile(b0, 90), np.percentile(b1, 90)
    else:
        qr, qo_, p0, p1 = EDGES or load_edges()
    print("edges in ordinary units: ROLES reaction %.3f, other %.3f | POOLED day 0 %.3f, day +1 %.3f | habit-assigned isolated releases %d | %.0fs" % (qr, qo_, p0, p1, len(R), time.time() - t0), flush=True)
    isr = (IS(react, qr) + IS(other, qo_)) / 2
    isp = (IS(b0, p0) + IS(b1, p1)) / 2
    cov_pr = np.where(hb == 1, b1 <= p1, b0 <= p0)
    cov_po = np.where(hb == 1, b0 <= p0, b1 <= p1)
    gm = {g: np.isin(sa, vals) for g, vals in GROUPS}
    for g, _ in GROUPS:
        print("  %s: %.1f%% of releases" % (g, 100 * gm[g].mean()))
    ratios = {}
    for g, _ in GROUPS:
        print("\nGROUP %s" % g)
        for lab, lo, hi in ERAS:
            s = gm[g] & (yr >= lo) & (yr <= hi)
            if s.sum() < 20:
                print("  %s: %d releases (too few)" % (lab, s.sum())); ratios[(g, lab)] = None; continue
            cl = s & (own >= 0)
            ratios[(g, lab)] = float(isr[s].sum() / isp[s].sum())
            print("  %s | releases %5d | agreement %5.1f%% (classifiable %d) | ROLES coverage: reaction %.1f%%, other %.1f%% | POOLED coverage: reaction %.1f%%, other %.1f%% | ratio ROLES/POOLED %.3f" % (
                lab, s.sum(), 100 * (own[cl] == hb[cl]).mean() if cl.sum() else float("nan"), cl.sum(), 100 * (react[s] <= qr).mean(), 100 * (other[s] <= qo_).mean(), 100 * cov_pr[s].mean(), 100 * cov_po[s].mean(), ratios[(g, lab)]))
        s = gm[g]
        if s.sum() >= 20:
            cl = s & (own >= 0)
            ratios[(g, "all")] = float(isr[s].sum() / isp[s].sum())
            print("  all eras | releases %5d | agreement %5.1f%% | ROLES coverage: reaction %.1f%%, other %.1f%% | ratio %.3f" % (s.sum(), 100 * (own[cl] == hb[cl]).mean(), 100 * (react[s] <= qr).mean(), 100 * (other[s] <= qo_).mean(), ratios[(g, "all")]))
    t = gm["2-2"]
    if t.sum() >= 20:
        Mn = int(mo.max()) + 1
        sr_m, sp_m = np.bincount(mo[t], weights=isr[t], minlength=Mn), np.bincount(mo[t], weights=isp[t], minlength=Mn)
        present = np.where(np.bincount(mo[t], minlength=Mn) > 0)[0]
        brng = np.random.RandomState(SEED)
        bs = []
        for _ in range(N_BOOT):
            W = np.bincount(brng.choice(present, size=len(present)), minlength=Mn).astype(float)
            bs.append((W @ sr_m) / (W @ sp_m))
        lo_, hi_ = np.percentile(bs, [2.5, 97.5])
        print("\nTIES, all eras: ratio ROLES/POOLED %.3f, 95%% interval [%.3f, %.3f]" % (ratios[("2-2", "all")], lo_, hi_))
    all_roles = float(isr.sum() / isp.sum())
    all_guard = float((isr[~t].sum() + isp[t].sum()) / isp.sum())
    print("MATERIALITY: overall ratio ROLES/POOLED with roles everywhere %.4f | with ties on the pooled band %.4f | difference %+.4f" % (all_roles, all_guard, all_guard - all_roles))
    tie_ok = t.sum() >= 20 and all(ratios.get(("2-2", lab)) is not None for lab, _, _ in ERAS)
    if tie_ok:
        r_all = ratios[("2-2", "all")]
        n_above = sum(ratios[("2-2", lab)] > 1.0 for lab, _, _ in ERAS)
        if r_all > 1.0 and n_above >= 2:
            verdict = "TIE GUARD JUSTIFIED: 2-2 ties should use the pooled band (and the role model should be refit without ties)"
        elif r_all < 1.0 and n_above <= 1:
            verdict = "KEEP ROLES ON TIES (keep the WEAK HABIT label)"
        else:
            verdict = "INCONCLUSIVE: the status quo stands (roles on ties, labelled WEAK HABIT)"
    else:
        verdict = "INCONCLUSIVE: too few ties in one era"
    print("\nVERDICT (pre-set: pooled-eras tie ratio above 1.00 and above 1.00 in at least two of three eras -> guard; below 1.00 and above 1.00 in at most one era -> keep roles; else inconclusive): %s" % verdict)
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
