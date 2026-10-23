#!/usr/bin/env python3
"""
event_band_pa_walkforward.py -- READ-ONLY (local matrices; the database is read for event_direction_labels, ev_ent, securities and 8-K filings). Writes nothing.
Registered rule, population, predictions and limits: results/PREREG_previously_announced_walkforward_2026-10-23.md (committed before the first coverage computation for this group; counts came from event_band_pa_population.py).
WHAT IT DOES. For single-event stock-days with timing = previously_announced and an event type other than acquisition: FIT k = (90th percentile of band unit / m) / edge on 2005-2012 only; score the same k, unrefitted, on 2013-2019 and 2020-2026. Reuses the single-event audit's matrices, band unit, model, edge and earnings-window exclusion unchanged (via event_band_multi_event_coverage.load_setup / event_rows).
Usage:   python3 -u scripts/card/event_band_pa_walkforward.py     Needs data_cache/audit_matrices.npz.
"""
import os, sys, time
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_band_multi_event_coverage as mec
import event_band_class_coverage as ebc

TIMING = "previously_announced"
GATE_LO, GATE_HI = 0.88, 0.92


def inside(c):
    return GATE_LO <= c <= GATE_HI


def classify(c_fit, c0, c1):
    if inside(c_fit):
        return "NO SHORTFALL IN THE FIT ERA (nothing to fit)"
    if inside(c0[0]) and inside(c0[1]):
        return "NOT REPLICATED (the shortfall is specific to the fit era)"
    if all(inside(c1[i]) and abs(c1[i] - 0.90) <= abs(c0[i] - 0.90) + 0.01 for i in (0, 1)):
        return "PASS (the multiplier fitted on 2005-2012 transfers to both later eras)"
    return "FAIL (the fitted multiplier does not bring both later eras into 88-92%)"


def evaluate(units, edge):
    labs = [lab for lab, _, _ in mec.ERAS]
    A, B, C = [np.array(units[lab], dtype=float) for lab in labs]
    if min(len(A), len(B), len(C)) < mec.MIN_PER_ERA:
        return None
    k = float(np.quantile(A, 0.90)) / edge
    cA = float(np.mean(A <= edge))
    c0 = [float(np.mean(x <= edge)) for x in (B, C)]
    c1 = [float(np.mean(x <= edge * k)) for x in (B, C)]
    return {"k": k, "cA": cA, "c0": c0, "c1": c1, "n": (len(A), len(B), len(C)), "A": A, "B": B, "C": C}


def show(name, r, edge):
    labs = [lab for lab, _, _ in mec.ERAS]
    print("\n%s  (n %d / %d / %d)   fitted k = %.3f on %s" % (name, r["n"][0], r["n"][1], r["n"][2], r["k"], labs[0]))
    rows_ = [("%s (fit era), unadjusted" % labs[0], r["A"], 1.0)] + [("%s, unadjusted" % labs[i + 1], r["B"] if i == 0 else r["C"], 1.0) for i in (0, 1)] + [("%s, ADJUSTED by k" % labs[i + 1], r["B"] if i == 0 else r["C"], r["k"]) for i in (0, 1)]
    for lab, arr, sc in rows_:
        c = int(np.sum(arr <= edge * sc))
        lo, hi = ebc.wilson(c, len(arr))
        print("  %-34s %5.1f%%  [%4.1f, %4.1f]" % (lab, 100.0 * c / len(arr), 100 * lo, 100 * hi))


def main():
    t0 = time.time()
    dl, ids, years, bu, model, edge, sb, idx, earn = mec.load_setup()
    rows, cnt = mec.event_rows(sb, idx, dl)
    era_of = lambda y: next((lab for lab, lo, hi in mec.ERAS if lo <= y <= hi), None)
    units, units_cr = defaultdict(list), defaultdict(list)
    for k, t, off, eid, pt, sz, tm in rows:
        if len(cnt[(k, t)]) != 1 or earn[k, t] or not np.isfinite(bu[k, t]) or years[t] < 2005 or tm != TIMING or pt == "acquisition":
            continue
        lab = era_of(int(years[t]))
        u = float(bu[k, t] / mec.mult(model, pt, sz, tm, off))
        units[lab].append(u)
        if pt == "capital_raise":
            units_cr[lab].append(u)
    print("non-acquisition %s single-event stock-days by era: %s | edge %.3f | %.0fs" % (TIMING, " / ".join(str(len(units[lab])) for lab, _, _ in mec.ERAS), edge, time.time() - t0), flush=True)
    r = evaluate(units, edge)
    if r is None:
        print("CANNOT TEST (an era has fewer than %d stock-days)" % mec.MIN_PER_ERA)
        return None, "CANNOT TEST"
    show("PRIMARY: non-acquisition previously_announced", r, edge)
    v = classify(r["cA"], r["c0"], r["c1"])
    rc = evaluate(units_cr, edge)
    if rc is not None:
        show("DESCRIPTIVE: capital_raise only (its own fit)", rc, edge)
        print("  capital_raise reads: %s" % classify(rc["cA"], rc["c0"], rc["c1"]))
    print("\nVERDICT (registered rule): %s" % v)
    print("REGISTERED PREDICTIONS: fit-era unadjusted coverage 88.0%% (85-91) | k 1.05 (1.00-1.12) | P(NO SHORTFALL) 35%%, P(NOT REPLICATED) 15%%, P(PASS) 30%%, P(FAIL) 20%%")
    print("total %.0fs" % (time.time() - t0))
    return r, v


if __name__ == "__main__":
    main()
