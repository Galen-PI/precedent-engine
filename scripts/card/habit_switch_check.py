#!/usr/bin/env python3
"""
habit_switch_check.py -- READ-ONLY (matrices, the OHLC cache, the database for 8-K filings and recorded events, models/earnings_role_band_model.json). Writes nothing.
WHY. The card's role bands use a stock's habit (the majority of its last 4 classifiable quarters). When a stock SWITCHES its release time (before the open <-> after the close), the card shows the narrow 'other day' band on the day the reaction actually lands, until the habit catches up. The out-of-sample coverage of the role bands
already includes such cases, but they were never looked at on their own. QUESTIONS: (1) how often does an isolated earnings release contradict the habit the card would have used; (2) on those releases, how often is the true reaction day's |band unit| beyond the narrow other-day edge (nominally about 10% on an other day, but this is
a reaction day); (3) which recent stocks are examples to run through the card?
DEFINITIONS (same data and rules as build_earnings_role_model.py): an isolated earnings release (no own recorded event, no Regulation FD filing on day i or i+1, finite band units on days i and i+1) with a habit (majority of the last 4 earlier classifiable quarters) whose OWN gap labels it classifiable (gap z >= 2.0 on day i or i+1);
the release CONTRADICTS the habit if its own label differs. The true reaction day is day i for a before-the-open label and i+1 for an after-the-close label. OTHER-DAY EDGE = the deployed role model's other-day 90th percentile of |band units| (ordinary units).
Usage:   python3 -u scripts/card/habit_switch_check.py       Needs data_cache/audit_matrices.npz, data_cache/ohlc, the database, models/earnings_role_band_model.json.
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
EDGE_OTHER = None
SHOW = 12


def main():
    t0 = time.time()
    edge = EDGE_OTHER or json.load(open(os.path.join(ROOT, "models", "earnings_role_band_model.json")))["groups"][er.OTHER]["q90_ordinary_units"]
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
    tick = {r["id"]: (r.get("ticker") or r["id"]) for r in uc.paged(lambda: sb.table("securities").select("id,ticker").order("id"))}
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
    rows = []                              # (stock k, day i, habit before, own label, |bu| on the true reaction day, |bu| on the other day)
    n_hab = n_cls = 0
    for k, lst in raw.items():
        ZG = er.gap_z_1d(O[k], C[k])
        hist = []
        for i in er.thin(lst):
            if i < er.GAP_WIN + 1 or i + 1 >= n or years[i] < TEST_START:
                continue
            a, b = ZG[i], ZG[i + 1]
            habit = er.majority(hist[-er.HIST:]) if len(hist) >= er.HIST else None
            b0, b1 = bu[k, i], bu[k, i + 1]
            classifiable = np.isfinite(a) and np.isfinite(b) and max(a, b) >= er.CLASSIFY_Z
            if habit is not None and not (oth[k, i] or oth[k, i + 1]) and np.isfinite(b0) and np.isfinite(b1):
                n_hab += 1
                if classifiable:
                    n_cls += 1
                    own = 1 if b > a else 0
                    if own != habit:
                        rows.append((k, i, habit, own, abs(float(b1 if own == 1 else b0)), abs(float(b0 if own == 1 else b1))))
            if classifiable:
                hist.append(1 if b > a else 0)
    R = np.array([(r[4], r[5], years[r[1]]) for r in rows])
    print("isolated earnings releases with a habit %d | of which classifiable on their own gap %d | CONTRADICT the habit %d (%.1f%% of classifiable)" % (n_hab, n_cls, len(rows), 100.0 * len(rows) / max(n_cls, 1)))
    if len(rows):
        over = R[:, 0] > edge
        print("on those releases the TRUE REACTION DAY's |band unit| exceeds the narrow other-day edge (%.2f) in %.1f%% of cases (a calibrated other day: about 10%%); median |band unit| on that day %.2f vs %.2f on the other day" % (edge, 100 * over.mean(), np.median(R[:, 0]), np.median(R[:, 1])))
        for lo, hi in ((2006, 2012), (2013, 2019), (2020, 2100)):
            s = (R[:, 2] >= lo) & (R[:, 2] <= hi)
            if s.sum():
                print("   %s: %d contradicting releases, true reaction day beyond the narrow edge %.1f%%" % ("%d-%s" % (lo, "2026" if hi > 2100 - 1 else hi), s.sum(), 100 * (R[s, 0] > edge).mean()))
        print("\nMOST RECENT examples (run the card on the TRUE reaction day: it will show the narrow 'other day' band there):")
        rows.sort(key=lambda r: -r[1])
        for k, i, habit, own, br, bo in rows[:SHOW]:
            rd = i + own
            print("  %-6s release %s | habit %-17s own gap says %-17s | true reaction day %s: |band unit| %.2f%s" % (
                tick.get(ids[k], ids[k]), dl[i], "after the close" if habit else "before the open", "after the close" if own else "before the open", dl[rd], br, "  BEYOND the narrow edge" if br > edge else ""))
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
