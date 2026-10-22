#!/usr/bin/env python3
"""
build_earnings_role_model.py -- READ-ONLY apart from writing models/earnings_role_band_model.json (matrices, the OHLC cache, the database for 8-K filings and recorded events).
Fits the DEPLOYABLE role bands that earnings_role_band_test.py validated out of sample (verdict ROLE BANDS IMPROVE): on every isolated earnings release from 2006 (no own recorded event, no Regulation FD filing on day i or i+1) that has a forward habit, the reaction day and the other day are
measured on the ordinary band-unit scale. Per role: MULTIPLIER = root-mean-square |band unit| of that role / root-mean-square |band unit| of ordinary stock-days (the card's convention for earnings_band_model.json), and EDGE_90 = the 90th percentile of |band units| of that role divided by the multiplier
(the card's units: half-width = edge x stress scale x multiplier, so edge x multiplier is the ordinary-scale 90th percentile). Fit on ALL years (the walk-forward test already measured the out-of-sample behaviour of this procedure); by-era values are written for transparency.
SELF-CHECKS (it refuses to write unless they pass or --force is given): (1) the number of isolated earnings events and the share with a forward habit match earnings_role_band_test.py (33,023 and 90.0% on 2026-10-21, within 1.5% / 1.5 points: the data has moved a little since); (2) the same events' POOLED day-0 / day-+1 multipliers land near the card's 2.72 / 2.47
(within 0.2: the timing check read 2.75 / 2.53), which shows the multiplier convention and the ordinary baseline match the existing model.
Usage:   python3 -u scripts/card/build_earnings_role_model.py [--out models/earnings_role_band_model.json] [--force]       Needs data_cache/audit_matrices.npz, data_cache/ohlc and the database.
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
REF_ISO, REF_HABIT, REF_DAY0, REF_DAY1, TOL_N, TOL_H, TOL_M = 33023, 0.900, 2.72, 2.47, 0.015, 0.015, 0.20


def main():
    t0 = time.time()
    args = sys.argv[1:]
    out_path = args[args.index("--out") + 1] if "--out" in args else os.path.join(ROOT, "models", "earnings_role_band_model.json")
    force = "--force" in args
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
    print("securities with an OHLC file: %d of %d | %.0fs" % (have, N, time.time() - t0), flush=True)

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids))
    oth = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                oth[k, t] = True
    earnw = np.zeros((N, n), dtype=bool)
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
            earnw[k, i:min(i + 2, n)] = True
        elif "7.01" in its:
            oth[k, i] = True
            if i + 1 < n:
                oth[k, i + 1] = True

    rec, n_iso = [], 0
    for k, lst in raw.items():
        ZG = er.gap_z_1d(O[k], C[k])
        hist = []
        for i in er.thin(lst):
            if i < er.GAP_WIN + 1 or i + 1 >= n or years[i] < TEST_START:
                continue
            a, b = ZG[i], ZG[i + 1]
            habit = er.majority(hist[-er.HIST:]) if len(hist) >= er.HIST else None
            b0, b1 = bu[k, i], bu[k, i + 1]
            if not (oth[k, i] or oth[k, i + 1]) and np.isfinite(b0) and np.isfinite(b1):
                n_iso += 1
                if habit is not None:
                    rec.append((int(years[i]), abs(float(b0)), abs(float(b1)), habit))
            if np.isfinite(a) and np.isfinite(b) and max(a, b) >= er.CLASSIFY_Z:
                hist.append(1 if b > a else 0)
    ordm = np.isfinite(bu) & ~oth & ~earnw & (years >= TEST_START)[None, :]
    rms_ord = float(np.sqrt(np.mean(bu[ordm] ** 2)))
    R = np.array(rec, dtype=float)
    yr, b0, b1, hb = R[:, 0], R[:, 1], R[:, 2], R[:, 3]
    react = np.where(hb == 1, b1, b0)
    other = np.where(hb == 1, b0, b1)
    share = len(rec) / max(n_iso, 1)
    print("isolated earnings events %d (role test: %d) | with a forward habit %.1f%% (role test: %.1f%%) | after-close habit share %.1f%% | ordinary rms %.3f | %.0fs" % (n_iso, REF_ISO, 100 * share, 100 * REF_HABIT, 100 * hb.mean(), rms_ord, time.time() - t0))
    p0, p1 = float(np.sqrt(np.mean(b0 ** 2)) / rms_ord), float(np.sqrt(np.mean(b1 ** 2)) / rms_ord)
    print("POOLED check on the same events: day 0 %.2fx, day +1 %.2fx (the card: %.2f / %.2f)" % (p0, p1, REF_DAY0, REF_DAY1))
    problems = []
    if abs(n_iso / REF_ISO - 1) > TOL_N: problems.append("isolated events differ from the role test by more than %.1f%%" % (100 * TOL_N))
    if abs(share - REF_HABIT) > TOL_H: problems.append("forward-habit share differs from the role test by more than %.1f points" % (100 * TOL_H))
    if abs(p0 - REF_DAY0) > TOL_M or abs(p1 - REF_DAY1) > TOL_M: problems.append("pooled multipliers differ from the card's by more than %.2f: the convention or baseline does not match" % TOL_M)

    def group_stats(x):
        m = float(np.sqrt(np.mean(x ** 2)) / rms_ord)
        q = float(np.percentile(x, 90))
        return {"multiplier": round(m, 3), "edge_90": round(q / m, 3), "q90_ordinary_units": round(q, 3), "n": int(len(x))}
    groups = {er.REACTION: group_stats(react), er.OTHER: group_stats(other)}
    by_era = {er.REACTION: {}, er.OTHER: {}}
    for lab, lo, hi in ERAS:
        s = (yr >= lo) & (yr <= hi)
        by_era[er.REACTION][lab], by_era[er.OTHER][lab] = group_stats(react[s]), group_stats(other[s])
    for g in (er.REACTION, er.OTHER):
        print("  %-30s multiplier %.3fx | edge_90 %.3f (card units) | q90 %.3f (ordinary units) | n %d | by era: %s" % (g, groups[g]["multiplier"], groups[g]["edge_90"], groups[g]["q90_ordinary_units"], groups[g]["n"],
              ", ".join("%s %.2fx" % (lab, by_era[g][lab]["multiplier"]) for lab, _, _ in ERAS)))
    model = {"what": "Role-based earnings bands: for an ISOLATED earnings window (no own recorded event, no Regulation FD filing) of a stock whose release-time habit is known from its last 4 classifiable quarters, the reaction day and the other day get their own multiplier (root-mean-square |band unit| relative to an ordinary day) and 90% edge (card units).",
             "habit_rule": {"gap_window": er.GAP_WIN, "gap_min_obs": er.GAP_MIN, "max_gap": er.MAX_GAP, "classify_z": er.CLASSIFY_Z, "history": er.HIST, "thin_days": er.THIN, "label_1": "after the close (the day-i+1 gap is larger)", "label_0": "before the open"},
             "groups": groups, "by_era": by_era,
             "pooled_check": {"day0": round(p0, 3), "day1": round(p1, 3), "card_day0": REF_DAY0, "card_day1": REF_DAY1},
             "events_used": {"isolated": n_iso, "with_habit": len(rec), "habit_share": round(share, 4)},
             "source": "scripts/card/build_earnings_role_model.py on the isolated earnings releases of 2006-2026; procedure validated out of sample by scripts/card/earnings_role_band_test.py (ROLE BANDS IMPROVE: interval score 0.890 / 0.869 / 0.857 of the pooled bands by era, placebo 1.003).",
             "caveats": ["Fit on all years; the walk-forward test measured the procedure, not these exact numbers.", "A forward use needs the earnings filing date to be known in advance; the card applies it on the day itself from the filing table.",
                         "'Last 4' came from a recency test on the same years (last 3 / 4 / 8 were within 0.1 point). Strong-habit stocks are mostly big-gap names, so the role multipliers may run a few percent high for weak-habit stocks.",
                         "No habit (fewer than 4 classifiable earlier quarters, no OHLC history, an event or a 7.01 filing on the same days) means the card keeps its pooled day-0 / day-+1 band."]}
    if problems and not force:
        print("NOT WRITTEN: " + "; ".join(problems) + " (use --force to write anyway)")
        return
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(model, fh, indent=1)
    print("wrote %s%s | %.0fs" % (out_path, " (FORCED despite: " + "; ".join(problems) + ")" if problems else "", time.time() - t0))


if __name__ == "__main__":
    main()
