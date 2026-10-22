#!/usr/bin/env python3
"""
ipo_spinoff_walkforward.py -- READ-ONLY (same inputs as event_band_class_coverage.py, which it imports; keep that file). Writes nothing.
WHY. The audit (commit 18f5c1d) found the card's event band covering only 76.4 / 69.9 / 66.5% of ipo_spinoff event-days (2005-2012 / 2013-2019 / 2020-2026; n 242 / 292 / 182; pooled about 71%). ipo_spinoff is an EXCLUDED type: day_card.band_multiplier returns None, combine_multiplier then returns 1.0, and the edge is the pooled 1.337.
QUESTION. Would a data-driven multiplier for ipo_spinoff event-days, fitted on EARLIER eras only, restore about 90% coverage out of sample and beat the card's current 1.0 on the interval score?
POPULATION. Exactly the audit's: labeled events of type ipo_spinoff in ev_ent, day 0 and +1, from 2005, finite band unit, no earnings window, one labeled event per stock-day (event_band_class_coverage.build_event_days).
METHOD (walk-forward, expanding). Train 2005-2012 -> test 2013-2019; train 2005-2019 -> test 2020-2026. Multiplier m = (empirical 90th percentile of |band unit| over the TRAINING days) / edge, so training coverage is 90% by construction. In a test era the band half-width in band units is h = edge x m (the card's current band is h = edge). Coverage = share of test days with |band unit| <= h (95% Wilson interval).
INTERVAL SCORE (alpha 0.10) per event-day in BAND UNITS (primary, scale-free: every day counts equally): IS(h) = 2h + 20 x max(0, |band unit| - h); the RATIO is mean IS(edge x m) / mean IS(edge); below 1 is better. A paired bootstrap over test days (2,000 resamples, seed 20261022; the multiplier is held fixed) gives a 95% interval for the ratio; in RETURN units (weighting each day by its stress-scaled spread) the ratio is printed as descriptive only.
PRE-SET RULE (before the first real run). PASS: in BOTH test eras the coverage with m lies within 86-94% AND the interval-score ratio is below 1.0. PARTIAL: the ratio is below 1.0 in both eras but coverage is outside 86-94% in at least one. Otherwise NOT SHOWN. The bootstrap interval and the day-0 / day-+1 split are descriptive. Nothing on the card changes from this test alone; a PASS would be followed by a decision about
giving ipo_spinoff its own measured multiplier (with its own era-by-era monitoring, because this class drifts).
PREDICTIONS (point and range, before the run): in-sample implied multiplier by era (q90 / edge) 1.4 (1.2-1.7), 1.7 (1.4-2.0), 1.9 (1.5-2.3); training multiplier used for the 2013-2019 test 1.4 (1.2-1.7) and for the 2020-2026 test 1.6 (1.4-1.9); test coverage with m 88% (84-92) in each era, lower in the last (the class keeps drifting down);
interval-score ratio 0.88 (0.75-0.97) in each era; probability of a PASS 55%.
SELF-CHECK. At multiplier 1.0 the script must reproduce the audit's numbers (n 242 / 292 / 182, coverage 76.4 / 69.9 / 66.5%); a mismatch is printed and means the population differs from the audit's.
VALIDATION (synthetic worlds, 150 stocks, about 1,500 ipo_spinoff event-days, the audit's event-day builder; run before the real data): NO EFFECT (true scale 1.0): fitted multiplier 0.96 / 0.97, coverage 89.4 / 88.2%, ratio 1.001 / 1.003 (bootstrap [0.99, 1.01]): NOT SHOWN. CONSTANT 1.7x: multiplier 1.63 / 1.65, coverage 71.5 / 68.4% at 1.0 and 89.5 / 88.2% fitted, ratio 0.822 / 0.776: PASS.
DRIFTING (1.4 -> 1.7 -> 2.0 by era): multiplier 1.34 / 1.52, coverage 82.6 / 78.1% fitted, ratio 0.854 / 0.766: PARTIAL (a multiplier fitted on the past runs one step behind a drifting class; the rule reports that instead of passing it).
Usage:   python3 -u scripts/card/ipo_spinoff_walkforward.py     Needs data_cache/audit_matrices.npz.
"""
import os, sys, json, bisect, time, warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_band_class_coverage as ebc
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc

TYPE = "ipo_spinoff"
ERAS = ebc.ERAS
SPLITS = [("2013-2019", 2005, 2012, 2013, 2019), ("2020-2026", 2005, 2019, 2020, 2026)]
AUDIT_REF = {"2005-2012": (242, 76.4), "2013-2019": (292, 69.9), "2020-2026": (182, 66.5)}
ALPHA_PEN, BOOT, SEED = 20.0, 2000, 20261022


def interval_score(x, h):
    return 2 * h + ALPHA_PEN * np.maximum(0.0, x - h)


def main():
    t0 = time.time()
    d = np.load(ebc.CACHE_FILE, allow_pickle=False)
    dates, ids, E_, SD = d["dates"], d["ids"].tolist(), d["E"].astype(np.float64), d["SD"].astype(np.float64)
    N, n = E_.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    with np.errstate(invalid="ignore", divide="ignore"):
        Zsq = (E_ / SD) ** 2
    valid0 = np.isfinite(Zsq)
    S = np.where(valid0, Zsq, 0.0).sum(axis=0)
    cnt = valid0.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid0, Zsq, 0.0)) / (cnt[None, :] - 1)
        bu = np.sqrt(Zsq / qo)
        sdeff = SD * np.sqrt(qo)
    bu[~((cnt[None, :] > 20) & np.isfinite(bu))] = np.nan
    model = json.load(open(ebc.MODEL_PATH))
    edge = json.load(open(ebc.CALIB_PATH))["edge_90"][ebc.GROUP]
    m_card, note = dc.band_multiplier(model, TYPE, "small", "new", 0)
    print("card multiplier for %s: %s (%s) -> the card uses 1.0 | edge %.3f" % (TYPE, m_card, note, edge), flush=True)
    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    earn = np.zeros((N, n), dtype=bool)
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is not None and "2.02" in set(dc.parse_items(r.get("item_codes"))):
            i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
            earn[k, i:min(i + 2, n)] = True
    ed, n_all, n_amb = ebc.build_event_days(sb, ids, dl, bu, earn)
    rec = [(int(years[t]), off, float(bu[k, t]), float(sdeff[k, t])) for k, t, off, pt, sz, tm in ed if pt == TYPE and years[t] >= 2005]
    print("ipo_spinoff event-days kept %d (of %d labeled event-days considered; %d ambiguous stock-days left out) | %.0fs" % (len(rec), n_all, n_amb, time.time() - t0), flush=True)
    era = lambda y: next((lab for lab, lo, hi in ERAS if lo <= y <= hi), None)
    by = {lab: np.array([(r[2], r[1], r[3]) for r in rec if era(r[0]) == lab]) for lab, _, _ in ERAS}

    print("\nSELF-CHECK at multiplier 1.0 (the card today) against the audit")
    ok = True
    for lab, _, _ in ERAS:
        x = by[lab][:, 0] if len(by[lab]) else np.array([])
        cov = 100.0 * float((x <= edge).mean()) if len(x) else float("nan")
        ref = AUDIT_REF.get(lab) if AUDIT_REF else None
        good = ref is None or (len(x) == ref[0] and abs(cov - ref[1]) < 0.06)
        ok &= good
        print("  %-10s n %4d coverage %5.1f%%   audit: %s   %s" % (lab, len(x), cov, ("n %d, %.1f%%" % ref) if ref else "n/a", "match" if good else "MISMATCH"))
    if not ok:
        print("  WARNING: the population differs from the audit's; the numbers below are not comparable until this is explained.")

    print("\nIN-SAMPLE implied multiplier (90th percentile of |band unit| / edge) by era: " + ", ".join("%s %.2f (n %d)" % (lab, np.quantile(by[lab][:, 0], 0.9) / edge, len(by[lab])) for lab, _, _ in ERAS if len(by[lab])))
    print("\nWALK-FORWARD (multiplier fitted on earlier eras only)")
    rng = np.random.RandomState(SEED)
    results = {}
    for lab, a, b, c, dd in SPLITS:
        tr = np.concatenate([by[l][:, 0] for l, lo, hi in ERAS if a <= lo and hi <= b])
        te = by[lab]
        m = float(np.quantile(tr, 0.9) / edge)
        x, offs, sd = te[:, 0], te[:, 1], te[:, 2]
        h1, hm = edge, edge * m
        c1, cm = int((x <= h1).sum()), int((x <= hm).sum())
        l1, u1 = ebc.wilson(c1, len(x))
        lm, um = ebc.wilson(cm, len(x))
        is1, ism = interval_score(x, h1), interval_score(x, hm)
        ratio = float(ism.mean() / is1.mean())
        isr1, isrm = sd * is1, sd * ism
        ratio_ret = float(isrm.mean() / isr1.mean())
        bs = []
        for _ in range(BOOT):
            ix = rng.randint(0, len(x), len(x))
            bs.append(ism[ix].mean() / is1[ix].mean())
        lo_, hi_ = np.percentile(bs, [2.5, 97.5])
        results[lab] = (m, cm / len(x), ratio)
        print("  test %-10s trained 2005-%d on %d days: multiplier %.2f | test n %d" % (lab, b, len(tr), m, len(x)))
        print("      coverage at 1.0 (card) %5.1f%% [%4.1f, %4.1f]   with the fitted multiplier %5.1f%% [%4.1f, %4.1f]" % (100 * c1 / len(x), 100 * l1, 100 * u1, 100 * cm / len(x), 100 * lm, 100 * um))
        print("      interval-score ratio (fitted / card) %.3f  [95%% bootstrap %.3f, %.3f]   (return units, descriptive: %.3f)" % (ratio, lo_, hi_, ratio_ret))
        for o in (0, 1):
            s = offs == o
            if s.sum():
                print("      day %+d: n %3d  coverage at 1.0 %5.1f%%  with the fitted multiplier %5.1f%%" % (o, s.sum(), 100 * (x[s] <= h1).mean(), 100 * (x[s] <= hm).mean()))
    cov_ok = all(0.86 <= results[l][1] <= 0.94 for l, *_ in SPLITS)
    better = all(results[l][2] < 1.0 for l, *_ in SPLITS)
    verdict = "PASS: a measured multiplier fitted on earlier eras restores coverage to 86-94% and improves the interval score in both test eras" if (cov_ok and better) else ("PARTIAL: the interval score improves in both test eras but coverage is outside 86-94% in at least one" if better else "NOT SHOWN: no improvement in the interval score in both test eras")
    print("\nVERDICT (pre-set: coverage 86-94%% AND interval-score ratio below 1.0 in BOTH test eras): %s" % verdict)
    allx = np.concatenate([by[l][:, 0] for l, _, _ in ERAS if len(by[l])])
    print("FOR INFORMATION ONLY (not a recommendation, fitted on every era): pooled implied multiplier %.2f on %d days" % (np.quantile(allx, 0.9) / edge, len(allx)))
    print("total %.0fs" % (time.time() - t0))
    return results, verdict


if __name__ == "__main__":
    main()
