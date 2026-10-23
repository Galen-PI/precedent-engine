#!/usr/bin/env python3
"""
event_band_pa_population.py -- READ-ONLY (local matrices; the database is read for event_direction_labels, ev_ent, securities and 8-K filings). Writes nothing and prints COUNTS ONLY (no coverage), so that a rule can be registered before the answer is seen.
WHY. The single-event class audit (event_band_class_coverage.py, commit 18f5c1d) showed 'previously_announced' coverage outside acquisitions of about 87% (post hoc, from the pooled table) while 'acquisition x previously_announced' covers 90.7 / 89.4 / 89.4%. Before registering a held-out test of that, this counts the qualifying single-event stock-days (the audit's own population: 2005+, exactly one labeled event, no earnings window, finite band unit) by event type and era for timing = previously_announced, so the rule's minimum n is set from the counts, not from a guess.
Usage:   python3 -u scripts/card/event_band_pa_population.py     Needs data_cache/audit_matrices.npz.
"""
import os, sys, time
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_band_multi_event_coverage as mec

TIMING = "previously_announced"


def main():
    t0 = time.time()
    dl, ids, years, bu, model, edge, sb, idx, earn = mec.load_setup()
    rows, cnt = mec.event_rows(sb, idx, dl)
    eras = mec.ERAS
    era_of = lambda y: next((lab for lab, lo, hi in eras if lo <= y <= hi), None)
    tab, tim = defaultdict(lambda: defaultdict(int)), defaultdict(int)
    for k, t, off, eid, pt, sz, tm in rows:
        if len(cnt[(k, t)]) != 1 or earn[k, t] or not np.isfinite(bu[k, t]) or years[t] < 2005:
            continue
        lab = era_of(int(years[t]))
        tim[(tm, lab)] += 1
        if tm == TIMING:
            tab[pt][lab] += 1
    print("single-event stock-days (the audit's population) by timing and era, all types [%.0fs]" % (time.time() - t0))
    for tm in sorted({k[0] for k in tim}):
        print("  %-24s " % tm + "  ".join("%s %6d" % (lab, tim[(tm, lab)]) for lab, _, _ in eras))
    print("\ntiming = %s by event type (stock-days per era)" % TIMING)
    non = defaultdict(int)
    for pt in sorted(tab, key=lambda p: -sum(tab[p].values())):
        print("  %-26s " % pt + "  ".join("%s %6d" % (lab, tab[pt][lab]) for lab, _, _ in eras) + "   total %d" % sum(tab[pt].values()))
        if pt != "acquisition":
            for lab, _, _ in eras:
                non[lab] += tab[pt][lab]
    print("\nNON-ACQUISITION %s: " % TIMING + "  ".join("%s %d" % (lab, non[lab]) for lab, _, _ in eras) + "   minimum over eras %d (the audit's per-era minimum is %d)" % (min(non[lab] for lab, _, _ in eras), mec.MIN_PER_ERA))
    print("total %.0fs" % (time.time() - t0))
    return tab, non


if __name__ == "__main__":
    main()
