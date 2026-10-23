#!/usr/bin/env python3
"""
event_band_multi_event_coverage.py -- READ-ONLY (local matrices; the database is read for event_direction_labels, ev_ent, securities and 8-K filings). Writes nothing.
Registered rule, population, measure, predictions and limits: results/PREREG_multi_event_day_coverage_2026-10-23.md (committed before the first real run).
WHAT IT DOES. event_band_class_coverage.py measures only stock-days with exactly ONE labeled event. This measures the stock-days with TWO OR MORE, where the card uses the lead event's multiplier alone (lead = min over (day offset, event_id), as day_card.own_events sorts). It reuses that audit's matrices, band unit, model, edge, earnings-window exclusion and eras unchanged, and prints the single-event coverage as a reference and a self-check (kept single event-days vs 36,923; edge vs 1.337).
Usage:   python3 -u scripts/card/event_band_multi_event_coverage.py     Needs data_cache/audit_matrices.npz.
"""
import os, sys, json, bisect, time, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_band_class_coverage as ebc

ew, dc, uc = ebc.ew, ebc.dc, ebc.uc
ERAS, MIN_PER_ERA, LO, HI = ebc.ERAS, ebc.MIN_PER_ERA, ebc.LO, ebc.HI
RECORDED_KEPT, RECORDED_EDGE = 36923, 1.337


def load_setup():
    d = np.load(ebc.CACHE_FILE, allow_pickle=False)
    dates, ids, E_, SD = d["dates"], d["ids"].tolist(), d["E"].astype(np.float64), d["SD"].astype(np.float64)
    N, n = E_.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    with np.errstate(invalid="ignore", divide="ignore"):
        Zsq = (E_ / SD) ** 2
    valid0 = np.isfinite(Zsq)
    S = np.where(valid0, Zsq, 0.0).sum(axis=0)
    cnt_ = valid0.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        bu = np.sqrt(Zsq / ((S[None, :] - np.where(valid0, Zsq, 0.0)) / (cnt_[None, :] - 1)))
    bu[~((cnt_[None, :] > 20) & np.isfinite(bu))] = np.nan
    model = json.load(open(ebc.MODEL_PATH))
    edge = json.load(open(ebc.CALIB_PATH))["edge_90"][ebc.GROUP]
    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    earn = np.zeros((N, n), dtype=bool)
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is not None and "2.02" in set(dc.parse_items(r.get("item_codes"))):
            i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
            earn[k, i:min(i + 2, n)] = True
    return dl, ids, years, bu, model, edge, sb, idx, earn


def event_rows(sb, idx, dl):
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
    return rows, cnt


def mult(model, pt, sz, tm, off):
    m, _ = dc.band_multiplier(model, pt, sz, tm, off)
    return 1.0 if m is None else m


def flagged(o):
    if not all(o[lab][0] >= MIN_PER_ERA for lab, _, _ in ERAS):
        return None
    st = []
    for lab, _, _ in ERAS:
        nn, cc = o[lab]
        lo, hi = ebc.wilson(cc, nn)
        p = cc / nn
        st.append(("over" if (p > HI and lo > 0.90) else ("under" if (p < LO and hi < 0.90) else None)))
    return st[0] if st[0] and all(x == st[0] for x in st) else False


def verdict(o):
    if not all(o[lab][0] >= MIN_PER_ERA for lab, _, _ in ERAS):
        return "CANNOT TEST (an era has fewer than %d stock-days)" % MIN_PER_ERA
    f = flagged(o)
    if f == "under":
        return "UNDER-COVERED (the lead-only multiplier is too small on multi-event days)"
    if f == "over":
        return "OVER-COVERED"
    if all(LO <= o[lab][1] / o[lab][0] <= HI for lab, _, _ in ERAS):
        return "CALIBRATED"
    return "UNCLEAR (outside 86-94% in some era, but not in the same direction with intervals excluding 90%)"


def main():
    t0 = time.time()
    dl, ids, years, bu, model, edge, sb, idx, earn = load_setup()
    rows, cnt = event_rows(sb, idx, dl)
    era_of = lambda y: next((lab for lab, lo, hi in ERAS if lo <= y <= hi), None)
    singles_kept = sum(1 for k, t, off, eid, pt, sz, tm in rows if len(cnt[(k, t)]) == 1 and not earn[k, t] and np.isfinite(bu[k, t]))
    by = defaultdict(list)
    for k, t, off, eid, pt, sz, tm in rows:
        if len(cnt[(k, t)]) >= 2:
            by[(k, t)].append((off, eid, pt, sz, tm))
    multi, n_amb = [], len(by)
    for (k, t), evs in by.items():
        if earn[k, t] or not np.isfinite(bu[k, t]) or years[t] < 2005:
            continue
        lead = min(evs, key=lambda e: (e[0], e[1]))
        m = mult(model, lead[2], lead[3], lead[4], lead[0])
        unit = float(bu[k, t] / m)
        multi.append({"year": int(years[t]), "n_ev": len(cnt[(k, t)]), "same_type": len({e[2] for e in evs}) == 1, "lead_off": lead[0], "unit": unit, "cov": unit <= edge})
    sing = [(int(years[t]), bool(bu[k, t] / mult(model, pt, sz, tm, off) <= edge)) for k, t, off, eid, pt, sz, tm in rows if len(cnt[(k, t)]) == 1 and not earn[k, t] and np.isfinite(bu[k, t]) and years[t] >= 2005]
    print("labeled event-days %d | stock-days with >= 2 labeled events %d | kept (2005+, no earnings window, finite band unit) %d | edge %.3f | %.0fs" % (len(rows), n_amb, len(multi), edge, time.time() - t0), flush=True)
    print("SELF-CHECK vs the single-event audit: kept single event-days %d (recorded %d) %s | edge %.3f (recorded %.3f) %s" % (singles_kept, RECORDED_KEPT, "OK" if singles_kept == RECORDED_KEPT else "DIFFERS: explain before reading", edge, RECORDED_EDGE, "OK" if abs(edge - RECORDED_EDGE) < 0.0006 else "DIFFERS"))

    def cell(sel, pool):
        return {lab: (lambda c: (len(c), sum(c)))([r["cov"] if isinstance(r, dict) else r[1] for r in pool if era_of(r["year"] if isinstance(r, dict) else r[0]) == lab and sel(r)]) for lab, _, _ in ERAS}

    def line(name, o):
        parts = []
        for lab, _, _ in ERAS:
            nn, cc = o[lab]
            lo, hi = ebc.wilson(cc, nn)
            parts.append("%5d %5.1f%% [%4.1f,%4.1f]" % (nn, 100.0 * cc / nn if nn else float("nan"), 100 * lo, 100 * hi))
        return "  %-40s " % name + "  |  ".join(parts)
    print("\n  %-40s " % "group (stock-days, coverage, 95% interval)" + "  |  ".join("%-26s" % lab for lab, _, _ in ERAS))
    ref = cell(lambda r: True, sing)
    print(line("REFERENCE: single-event days", ref))
    groups = [("ALL multi-event days (PRIMARY)", lambda r: True), ("exactly 2 events", lambda r: r["n_ev"] == 2), ("3 or more events", lambda r: r["n_ev"] >= 3), ("same event type", lambda r: r["same_type"]), ("mixed event types", lambda r: not r["same_type"]), ("lead on day 0", lambda r: r["lead_off"] == 0), ("lead on day +1", lambda r: r["lead_off"] == 1)]
    out = {}
    for name, sel in groups:
        out[name] = cell(sel, multi)
        print(line(name, out[name]))
    print("\nIMPLIED EXTRA MULTIPLIER on top of the lead's (90th percentile of band unit / m_lead, divided by the edge), by era [descriptive, no adoption]")
    for name, sel in groups[:3]:
        parts = []
        for lab, _, _ in ERAS:
            u = [r["unit"] for r in multi if era_of(r["year"]) == lab and sel(r)]
            parts.append("%s %.3f (n %d)" % (lab, float(np.quantile(u, 0.90)) / edge, len(u)) if len(u) >= 30 else "%s n/a (n %d)" % (lab, len(u)))
        print("  %-34s %s" % (name, " | ".join(parts)))
    pooled = [r["cov"] for r in multi]
    v = verdict(out["ALL multi-event days (PRIMARY)"])
    print("\nPOOLED coverage on multi-event days: %.1f%% (n %d)" % (100.0 * sum(pooled) / max(1, len(pooled)), len(pooled)))
    print("VERDICT (registered rule): %s" % v)
    print("REGISTERED PREDICTIONS: kept 7,000 (2,000-25,000) | pooled coverage 85% (80-89) | P(UNDER) 40%, P(CALIBRATED) 35%, P(UNCLEAR) 20%, P(OVER) 5% | pooled implied extra multiplier 1.08 (1.00-1.20) | P(3+ events lower than exactly 2) 70%")
    print("total %.0fs" % (time.time() - t0))
    return out, v, multi


if __name__ == "__main__":
    main()
