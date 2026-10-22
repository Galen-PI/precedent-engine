#!/usr/bin/env python3
"""
earnings_role_701_check.py -- READ-ONLY (matrices, the OHLC cache, the database for 8-K filings and recorded events, models/*.json). Writes nothing.
WHY. earnings_role_band_test.py excluded every earnings window with a same-day Regulation FD (Item 7.01) filing, saying the card treats those separately. It does not: day_card.band_group applies the pooled day-0 / day-+1 earnings band to them. So the card's role bands (models/earnings_role_band_model.json,
fit on ISOLATED windows) currently step aside for windows with a 7.01 filing (JPM 2018-01-12), leaving the pooled band, which covers reaction days only about 81% and other days about 98%, on a group nobody tested. QUESTIONS: (1) how large is that group; (2) do the deployed role edges also calibrate it?
GROUPS (earnings releases from 2006 with finite band units on days i and i+1; day i = the first trading day on or after the 2.02 filing date; thinned to 20 days apart; habit = majority of the last 4 earlier classifiable quarters, the same rule as earnings_roles.py):
ISOLATED (no own recorded event, no 7.01 on day i or i+1) | WITH 7.01 (no own recorded event, a 7.01 filing on day i or i+1) | WITH EVENT (an own recorded event on day i or i+1: not evaluated, the card uses the joint event model).
MODELS on the WITH-7.01 group's habit-assigned days: CURRENT = the pooled edges the card uses now (calibrated edge x pooled multiplier for day 0 and day +1, from band_calibration.json and earnings_band_model.json); ROLES = the DEPLOYED role edges (q90 of |band units| by role, from earnings_role_band_model.json, fit on isolated windows only,
so the 7.01 events are fully out of sample). SCORE: coverage by role and era, and the interval score IS = 2 x edge + 20 x max(|band units| - edge, 0), averaged over both days of each event; ratio ROLES / CURRENT.
PRE-SET RULE (before the first real run; revised after the synthetic validation, see below): EXTEND ROLE BANDS TO WINDOWS WITH A 7.01 FILING if, in EACH era (2006-2012, 2013-2019, 2020-2026) and with at least 500 habit-assigned events in each, the 99% Wilson interval of ROLES coverage contains 90% for the reaction days AND for the other days
(not detectably miscalibrated), and the ROLES / CURRENT interval-score ratio is at most 0.98. Otherwise keep the pooled band for those days (and say so on the card).
REVISION NOTE: the first draft required each era's coverage point estimate to fall inside 88-92%. On a synthetic world where the 7.01 windows were EXACTLY like the isolated ones, that rule said 'keep pooled' (one era read 92.3% on 1,016 events: the sampling error of a coverage at this size is about +-2 points), so it would reject a perfectly calibrated
model about a quarter of the time. The interval rule says EXTEND on that world and KEEP on a world where the 7.01 windows have a weaker reaction (the deployed edges then over-cover them at 97-99%). Both worlds were written and run before the real data was touched.
PREDICTIONS (before the run): 20-35% of habit-eligible, event-free earnings windows carry a 7.01 filing; ROLES coverage on the 7.01 group is 86-94% on both roles in every era (verdict EXTEND with probability about 55%); the ratio is 0.85-0.97; CURRENT covers reaction days 78-86% and other days 96-99.5% on this group too.
Usage:   python3 -u scripts/card/earnings_role_701_check.py       Needs data_cache/audit_matrices.npz, data_cache/ohlc, the database, models/earnings_role_band_model.json, models/band_calibration.json, models/earnings_band_model.json.
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
MIN_EVENTS, RATIO_MAX, Z99 = 500, 0.98, 2.576
EDGES = None                          # (role reaction q90, role other q90, pooled day-0 q90, pooled day-+1 q90) in ordinary units; None = read the model files


def wilson(p, n, z=Z99):
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def load_edges():
    rm = json.load(open(os.path.join(ROOT, "models", "earnings_role_band_model.json")))["groups"]
    cal = json.load(open(os.path.join(ROOT, "models", "band_calibration.json")))["edge_90"]
    mm = json.load(open(os.path.join(ROOT, "models", "earnings_band_model.json")))["multipliers_vs_ordinary_day"]
    return (rm[er.REACTION]["q90_ordinary_units"], rm[er.OTHER]["q90_ordinary_units"],
            cal["earnings window, day 0 (no event)"] * mm["earnings_day0"], cal["earnings window, day +1 (no event)"] * mm["earnings_day1"])


def main():
    t0 = time.time()
    qr, qo_, p0, p1 = EDGES or load_edges()
    print("edges in ordinary units: ROLES reaction %.3f, other %.3f | CURRENT pooled day 0 %.3f, day +1 %.3f" % (qr, qo_, p0, p1), flush=True)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E, SD = d["dates"], d["ids"].tolist(), d["E"], d["SD"]
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
    O, C, have = etc.load_ohlc(ids, dl)
    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids))
    evf = np.zeros((N, n), dtype=bool)
    f701 = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                evf[k, t] = True
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
            f701[k, i] = True
            if i + 1 < n:
                f701[k, i + 1] = True
    rec = []                                   # (year, group, |bu| day i, |bu| day i+1, habit or -1)
    for k, lst in raw.items():
        ZG = er.gap_z_1d(O[k], C[k])
        hist = []
        for i in er.thin(lst):
            if i < er.GAP_WIN + 1 or i + 1 >= n or years[i] < TEST_START:
                continue
            a, b = ZG[i], ZG[i + 1]
            habit = er.majority(hist[-er.HIST:]) if len(hist) >= er.HIST else -1
            b0, b1 = bu[k, i], bu[k, i + 1]
            if np.isfinite(b0) and np.isfinite(b1):
                g = 2 if (evf[k, i] or evf[k, i + 1]) else (1 if (f701[k, i] or f701[k, i + 1]) else 0)
                rec.append((int(years[i]), g, abs(float(b0)), abs(float(b1)), habit))
            if np.isfinite(a) and np.isfinite(b) and max(a, b) >= er.CLASSIFY_Z:
                hist.append(1 if b > a else 0)
    R = np.array(rec, dtype=float)
    yr, grp, b0, b1, hb = R[:, 0], R[:, 1], R[:, 2], R[:, 3], R[:, 4]
    print("earnings windows with finite band units %d | isolated %d | with 7.01 (no event) %d | with an own event %d | %.0fs" % (len(R), (grp == 0).sum(), (grp == 1).sum(), (grp == 2).sum(), time.time() - t0))
    free = (grp == 0) | (grp == 1)
    print("share with a 7.01 filing among event-free windows: %.1f%% (all years); with a habit: isolated %.1f%%, with 7.01 %.1f%%" % (100 * (grp == 1).sum() / free.sum(), 100 * (hb[grp == 0] >= 0).mean(), 100 * (hb[grp == 1] >= 0).mean()))

    def score(g, lo, hi):
        s = (grp == g) & (hb >= 0) & (yr >= lo) & (yr <= hi)
        if s.sum() == 0:
            return None
        react = np.where(hb[s] == 1, b1[s], b0[s])
        other = np.where(hb[s] == 1, b0[s], b1[s])
        IS = lambda x, e: 2 * e + 20.0 * np.maximum(x - e, 0.0)
        roles = (IS(react, qr).mean() + IS(other, qo_).mean()) / 2
        cur = (IS(b0[s], p0).mean() + IS(b1[s], p1).mean()) / 2
        rcur = np.where(hb[s] == 1, b1[s] <= p1, b0[s] <= p0)                    # current pooled edge on the reaction day
        ocur = np.where(hb[s] == 1, b0[s] <= p0, b1[s] <= p1)
        return dict(n=int(s.sum()), cov_r=float((react <= qr).mean()), cov_o=float((other <= qo_).mean()), cur_r=float(rcur.mean()), cur_o=float(ocur.mean()), ratio=float(roles / cur))
    ok_all = True
    for g, name in ((0, "ISOLATED (reference: edges were fit on these)"), (1, "WITH 7.01 (out of sample)")):
        print("\n%s" % name)
        for lab, lo, hi in ERAS:
            r = score(g, lo, hi)
            if r is None:
                print("  %s: none" % lab); continue
            print("  %s | habit-assigned events %5d | ROLES coverage: reaction %.1f%%, other %.1f%% | CURRENT pooled coverage: reaction %.1f%%, other %.1f%% | interval-score ratio ROLES/CURRENT %.3f" % (lab, r["n"], 100 * r["cov_r"], 100 * r["cov_o"], 100 * r["cur_r"], 100 * r["cur_o"], r["ratio"]))
            if g == 1:
                wr, wo = wilson(r["cov_r"], r["n"]), wilson(r["cov_o"], r["n"])
                print("      99%% intervals of ROLES coverage: reaction [%.1f, %.1f], other [%.1f, %.1f]" % (100 * wr[0], 100 * wr[1], 100 * wo[0], 100 * wo[1]))
                if not (r["n"] >= MIN_EVENTS and wr[0] <= 0.90 <= wr[1] and wo[0] <= 0.90 <= wo[1] and r["ratio"] <= RATIO_MAX):
                    ok_all = False
    print("\nVERDICT (pre-set: each era >= %d events, the 99%% interval of ROLES coverage contains 90%% on both roles, ratio <= %.2f): %s" % (MIN_EVENTS, RATIO_MAX, "EXTEND ROLE BANDS TO WINDOWS WITH A 7.01 FILING" if ok_all else "KEEP THE POOLED BAND FOR 7.01 WINDOWS"))
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
