#!/usr/bin/env python3
"""
event_band_class_coverage.py -- READ-ONLY (local matrices; the database is read for event_direction_labels, ev_ent, securities and 8-K filings; models/event_band_model.json and models/band_calibration.json). Writes nothing.
WHY. The card's event band is half-width = edge x stress scale x multiplier, where the multiplier comes from an ADDITIVE log model (type + size + timing + day, no interactions; models/event_band_model.json, applied by day_card.band_multiplier) and the edge is ONE pooled number ('recorded event, no earnings', 1.337; walk-forward coverage 89.15%).
The earnings bands had the same structure and hid a conditional miscalibration (pooled bands covered a stock's reaction day 81% and its other day 98%; role bands then improved the interval score by 13%). The event band's coverage was never checked WITHIN its label classes.
POPULATION. Labeled events (event_direction_labels: type, size, timing) that are in ev_ent (non-bundled company events), at day 0 (the first trading day on or after the event date) and day +1, from 2005; stock-days with finite band units; EXCLUDING earnings windows (an 8-K item 2.02 on day i or i+1: those use the earnings groups); only stock-days with EXACTLY ONE
labeled event (the card takes one lead event; ambiguous days are left out). Excluded types (ipo_spinoff, systemic_shock, geopolitical, natural_disaster) get multiplier 1.0, as on the card.
MEASURE. Covered = |band unit| / multiplier <= edge, with the multiplier from the card's own function (type, size, timing, day) and the edge from band_calibration.json; coverage by class in three eras (2005-2012, 2013-2019, 2020-2026) with 95% Wilson intervals. Classes: all; timing; size; type; size x timing; type x timing; type x size (every class with at least 100 stock-days in total is shown; only those with >= 300 in every era can be flagged).
PRE-SET RULE (before the first real run). A class is MISCALIBRATED if in EVERY era it has >= 300 stock-days, its coverage is outside 86-94% in the SAME direction, and the 95% interval excludes 90%. GATE: overall coverage must lie within 88-92% in each era, otherwise the audit is reported but not interpreted.
If any class is miscalibrated, the follow-up (a separate pre-registered walk-forward test, as for the role bands) is a class-specific edge or an interaction term; nothing on the card changes from this audit alone.
PREDICTIONS (point and range, before the run): overall coverage 89.2% (88.0-90.5) in every era; classes with >= 300 stock-days in every era: 18 (10-30); classes MISCALIBRATED: 2 (0-5), probability that at least one is flagged 55%; previously_announced x acquisition coverage above 90% (point 93, range 90-96); size 'large' coverage below 90% (point 88, range 85-91).
VALIDATION (synthetic world, 150 stocks, 9,000 labeled events with the real model; run before the real data): CONTROL (the additive model exactly right): overall 90.5 / 89.9 / 89.3%, 26 classes testable, 0 flagged. PLANTED interactions (acquisition x previously_announced truly 30% calmer than the model; restructuring x large truly 30% wilder): acquisition x previously_announced flagged over-covered (96.3 / 97.3 / 95.2%);
restructuring x large was NOT flagged because that class has only about 100 stock-days per era (under the 300 minimum): the audit finds miscalibration in the large classes and says 'cannot tell' for small ones.
Usage:   python3 -u scripts/card/event_band_class_coverage.py     Needs data_cache/audit_matrices.npz.
"""
import os, sys, json, bisect, time, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = uc.CACHE_FILE
MODEL_PATH = os.path.join(ROOT, "models", "event_band_model.json")
CALIB_PATH = os.path.join(ROOT, "models", "band_calibration.json")
GROUP = "recorded event, no earnings"
ERAS = [("2005-2012", 2005, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2026)]
MIN_PER_ERA, LO, HI, Z = 300, 0.86, 0.94, 1.96
GATE_LO, GATE_HI = 0.88, 0.92


def wilson(c, n, z=Z):
    if n == 0:
        return float("nan"), float("nan")
    p = c / n
    d = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return ctr - h, ctr + h


def build_event_days(sb, ids, dl, bu, earn):
    idx = {sid: k for k, sid in enumerate(ids)}
    labels = {r["event_id"]: r for r in uc.paged(lambda: sb.table("event_direction_labels").select("event_id,ptype,size,timing").order("event_id"))}
    ent = defaultdict(list)
    for r in uc.paged(lambda: sb.table("securities").select("id,entity_id").order("id")):
        if r.get("entity_id") and r["id"] in idx:
            ent[r["entity_id"]].append(idx[r["id"]])
    rows = []
    for r in uc.paged(lambda: sb.table("ev_ent").select("event_id,entity_id,d").order("event_id").order("entity_id")):
        lab = labels.get(r["event_id"])
        if lab is None:
            continue
        i = bisect.bisect_left(dl, str(r["d"])[:10])
        for k in ent.get(r["entity_id"], []):
            for off in (0, 1):
                if i + off < len(dl):
                    rows.append((k, i + off, off, r["event_id"], lab.get("ptype"), lab.get("size") or "unknown", lab.get("timing") or "unknown"))
    cnt = defaultdict(set)
    for k, t, off, eid, pt, sz, tm in rows:
        cnt[(k, t)].add(eid)
    out = []
    for k, t, off, eid, pt, sz, tm in rows:
        if len(cnt[(k, t)]) == 1 and not earn[k, t] and np.isfinite(bu[k, t]):
            out.append((k, t, off, pt, sz, tm))
    return out, len(rows), sum(1 for v in cnt.values() if len(v) > 1)


def main():
    t0 = time.time()
    d = np.load(CACHE_FILE, allow_pickle=False)
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
        bu = np.sqrt(Zsq / ((S[None, :] - np.where(valid0, Zsq, 0.0)) / (cnt[None, :] - 1)))
    bu[~((cnt[None, :] > 20) & np.isfinite(bu))] = np.nan
    model = json.load(open(MODEL_PATH))
    edge = json.load(open(CALIB_PATH))["edge_90"][GROUP]
    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    earn = np.zeros((N, n), dtype=bool)
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is not None and "2.02" in set(dc.parse_items(r.get("item_codes"))):
            i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
            earn[k, i:min(i + 2, n)] = True
    ed, n_all, n_amb = build_event_days(sb, ids, dl, bu, earn)
    print("labeled event-days considered %d | ambiguous stock-days (more than one labeled event) %d | kept (one event, no earnings window, finite band unit) %d | edge %.3f | %.0fs" % (n_all, n_amb, len(ed), edge, time.time() - t0), flush=True)
    rec = []
    for k, t, off, pt, sz, tm in ed:
        if years[t] < 2005:
            continue
        m, _ = dc.band_multiplier(model, pt, sz, tm, off)
        m = 1.0 if m is None else m
        rec.append((int(years[t]), pt, sz, tm, bool(bu[k, t] / m <= edge)))
    era_of = lambda y: next((lab for lab, lo, hi in ERAS if lo <= y <= hi), None)

    def cell(sel):
        out = {}
        for lab, _, _ in ERAS:
            c = [r[4] for r in rec if era_of(r[0]) == lab and sel(r)]
            out[lab] = (len(c), sum(c))
        return out
    def line(name, o):
        parts = []
        for lab, _, _ in ERAS:
            nn, cc = o[lab]
            lo, hi = wilson(cc, nn)
            parts.append("%5d %5.1f%% [%4.1f,%4.1f]" % (nn, 100.0 * cc / nn if nn else float("nan"), 100 * lo, 100 * hi))
        return "  %-46s " % name + "  |  ".join(parts)
    def flagged(o):
        if not all(o[lab][0] >= MIN_PER_ERA for lab, _, _ in ERAS):
            return None
        st = []
        for lab, _, _ in ERAS:
            nn, cc = o[lab]
            lo, hi = wilson(cc, nn)
            p = cc / nn
            st.append(("over" if (p > HI and lo > 0.90) else ("under" if (p < LO and hi < 0.90) else None)))
        return st[0] if st[0] and all(x == st[0] for x in st) else False
    print("\n" + "  %-46s " % "class (stock-days, coverage, 95% interval)" + "  |  ".join("%-26s" % lab for lab, _, _ in ERAS))
    allc = cell(lambda r: True)
    print(line("ALL labeled event-days", allc))
    gate = all(GATE_LO <= allc[lab][1] / allc[lab][0] <= GATE_HI for lab, _, _ in ERAS if allc[lab][0])
    classes = []
    for nm, f in (("timing", lambda r: r[3]), ("size", lambda r: r[2]), ("type", lambda r: r[1]), ("size x timing", lambda r: (r[2], r[3])), ("type x timing", lambda r: (r[1], r[3])), ("type x size", lambda r: (r[1], r[2]))):
        vals = sorted({f(r) for r in rec}, key=str)
        print("\n  by %s" % nm)
        for v in vals:
            o = cell(lambda r, v=v, f=f: f(r) == v)
            if sum(o[lab][0] for lab, _, _ in ERAS) < 100:
                continue
            fl = flagged(o)
            classes.append((nm, v, o, fl))
            print(line("%s" % (v if isinstance(v, str) else " x ".join(v)), o) + ("   <-- MISCALIBRATED (%s-covered)" % fl if fl else ("" if fl is None else "")) + ("   (under 300 in some era)" if fl is None else ""))
    testable = [c for c in classes if c[3] is not None]
    bad = [c for c in testable if c[3]]
    print("\nSUMMARY: overall gate (88-92%% in every era): %s | classes with >= %d stock-days in every era: %d | MISCALIBRATED: %d%s" % ("PASS" if gate else "FAIL (not interpreted)", MIN_PER_ERA, len(testable), len(bad), (": " + ", ".join("%s=%s (%s)" % (c[0], c[1] if isinstance(c[1], str) else "x".join(c[1]), c[3]) for c in bad)) if bad else ""))
    print("total %.0fs" % (time.time() - t0))
    return rec, classes, gate


if __name__ == "__main__":
    main()
