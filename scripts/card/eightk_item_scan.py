#!/usr/bin/env python3
"""
eightk_item_scan.py -- READ-ONLY (local matrices; the database is read for ALL 8-K filings and the recorded event days).
THREAD DISCOVERY BY DATA, not by reading: the earnings thread (8-K item 2.02) was found because the 8-K table carries item codes. This scans EVERY other item code the
same way. For each item code: on the day an 8-K with that item was filed and the next trading day (the table has no filing time), does the stock's miss widen beyond an
ordinary day, on years the scale was never fit on, and how much of the 'big, no event' miss mass sits on those days?

Usage:   python3 -u scripts/card/eightk_item_scan.py
Needs:   data_cache/audit_matrices.npz (gap_audit.py builds it). Database: sec_8k_filings (security_id, filing_date, item_codes) and the event tables.

DEFINITIONS (same as earnings_thread_test.py). Day 0 = the first trading day on or after the filing date, day +1 = the next one; the two are pooled. z5 = the standardized
chapter-1 miss over the square root of the other stocks' mean squared miss the same day. Item 9.01 (exhibits, attached with almost every filing) and item 2.02 (earnings,
already tested) are not scanned; a filing with several items counts toward each of them, so the item groups OVERLAP and their mass shares must not be added.
  Stock-days that are recorded event days, or earnings days, are excluded from every item group. The ORDINARY group is every scored stock-day with no 8-K of any kind on
  day 0 or +1, no recorded event and no earnings filing.
PRE-SET RULE (written before the first run), per item code with >= 3,000 scored flagged stock-days:
  EARNS A PLACE if the walk-forward log-score gain (scale fit on years BEFORE the test year, a group needs >= 200 prior days, scored against the ordinary scale) is
  >= 0.005 nats per flagged stock-day in EACH of 2006-2012, 2013-2019, 2020-2026 AND positive in >= 70% of test years.
  Because about two dozen items are scanned, the results are a SCREEN: a pass is a lead to confirm, the way the earnings result was, not a ledger entry by itself.
PREDICTIONS (before the run): item 5.02 (officer or director changes) and 1.01 (material agreements) earn a place with multipliers near 1.2-1.5x; item 7.01 (Reg FD
  disclosures) and 8.01 (other events) widen the band only weakly (under 1.3x); items 2.05 (restructuring costs) and 4.02 (non-reliance on financials) are too rare to
  test or widen strongly; and the items that pass together hold well under half as much of the 'big, no event' mass as earnings days did (16.6 points).
"""
import os, sys, math, time, bisect, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
TEST_START = 2006
MIN_PRIOR = 200
MIN_FLAGGED = 3000
SKIP_ITEMS = ("9.01", "2.02")
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


def era_of(y):
    for name, lo, hi in ERAS:
        if lo <= y <= hi:
            return name
    return None


def parse_items(s):
    out = set()
    for part in str(s or "").replace(";", ",").replace(" ", ",").split(","):
        p = part.strip().lower().replace("item", "").strip()
        if p and p[0].isdigit():
            out.add(p)
    return out


def main():
    t0 = time.time()
    if not os.path.exists(CACHE_FILE):
        sys.exit("Run gap_audit.py first: it builds %s." % CACHE_FILE)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E, SD = d["dates"], d["ids"], d["E"], d["SD"]
    N, n = E.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = E / SD
    Zsq = Z.astype(np.float64) ** 2
    valid = ~np.isnan(Zsq)
    S = np.nansum(Zsq, axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        Z5 = Zsq / qo
        day_stress = np.sqrt(S / np.maximum(cnt, 1))
    ok = valid & np.isfinite(Z5) & (qo > 0) & (cnt[None, :] > 20)

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids.tolist())}
    rows = paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id"))
    seen = set()
    EA = np.zeros((N, n), dtype=bool)
    ANY = np.zeros((N, n), dtype=bool)
    lin_by_item = defaultdict(set)
    for r in rows:
        k = idx.get(r["security_id"])
        f = str(r["filing_date"])[:10]
        if k is None:
            continue
        its = parse_items(r.get("item_codes"))
        key = (k, f, tuple(sorted(its)))
        if key in seen:
            continue
        seen.add(key)
        i = bisect.bisect_left(dl, f)
        if i >= n:
            continue
        for c in (i, i + 1):
            if c < n:
                ANY[k, c] = True
                if "2.02" in its:
                    EA[k, c] = True
                for it in its:
                    if it not in SKIP_ITEMS:
                        lin_by_item[it].add(k * n + c)
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids.tolist()))
    EV = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                EV[k, t] = True
    print("matrices: %d stocks x %d days | 8-K rows read: %d (distinct stock-date-item sets: %d) | distinct item codes seen: %d | %.0fs" % (
        N, n, len(rows), len(seen), len(lin_by_item), time.time() - t0), flush=True)

    ordinary = ok & ~ANY & ~EV & ~EA
    yrs = sorted({int(y) for y in years})
    yidx = {y: j for j, y in enumerate(yrs)}
    year_of_col = np.array([yidx[int(y)] for y in years])

    def stats_for(mask_cells_k, mask_cells_c):
        nn = np.bincount(year_of_col[mask_cells_c], minlength=len(yrs)).astype(float)
        ss = np.bincount(year_of_col[mask_cells_c], weights=Z5[mask_cells_k, mask_cells_c], minlength=len(yrs))
        return nn, ss

    ok_k, ok_c = np.where(ordinary)
    ord_n, ord_s = stats_for(ok_k, ok_c)

    test_cols = years >= TEST_START
    zb = np.abs(Z) / day_stress[None, :]
    big = ok & (zb > 2.0) & ~EV & ~EA
    big[:, ~test_cols] = False
    big_mass = float(np.where(big, E.astype(np.float64) ** 2, 0.0).sum())
    e2 = E.astype(np.float64) ** 2
    tot_mass = float(np.where(ok & test_cols[None, :], e2, 0.0).sum())

    results = []
    for it, lin in lin_by_item.items():
        lin = np.array(sorted(lin))
        kk, cc = lin // n, lin % n
        m = ok[kk, cc] & ~EV[kk, cc] & ~EA[kk, cc]
        kk, cc = kk[m], cc[m]
        if len(kk) < MIN_FLAGGED:
            continue
        gn, gs = stats_for(kk, cc)
        per_year, era_g, era_n = {}, defaultdict(float), defaultdict(float)
        for Y in [y for y in yrs if y >= TEST_START]:
            j = yidx[Y]
            pr = [yidx[y] for y in yrs if y < Y]
            npr, spr = gn[pr].sum(), gs[pr].sum()
            nop, sop = ord_n[pr].sum(), ord_s[pr].sum()
            if npr < MIN_PRIOR or nop < 1000 or gn[j] == 0:
                continue
            sg, so = spr / npr, sop / nop
            if not (sg > 0 and so > 0):
                continue
            gain = (-0.5 * gn[j] * math.log(sg) - 0.5 * gs[j] / sg) - (-0.5 * gn[j] * math.log(so) - 0.5 * gs[j] / so)
            per_year[Y] = gain / gn[j]
            e = era_of(Y)
            if e:
                era_g[e] += gain
                era_n[e] += gn[j]
        vals = [(era_g[e[0]] / era_n[e[0]]) if era_n[e[0]] > 0 else None for e in ERAS]
        npos = sum(1 for v in per_year.values() if v > 0)
        passed = len(per_year) >= 10 and all(v is not None and v >= 0.005 for v in vals) and npos / len(per_year) >= 0.70
        mult = math.sqrt((gs[[yidx[y] for y in yrs if y >= 2004]].sum() / max(gn[[yidx[y] for y in yrs if y >= 2004]].sum(), 1)) / (ord_s.sum() / ord_n.sum()))
        bm = float(e2[kk, cc][big[kk, cc]].sum())
        share_days = len(kk) / max(int(ok[:, test_cols].sum()), 1)
        results.append({"item": it, "days": len(kk), "mult": mult, "vals": vals, "npos": npos, "ny": len(per_year), "passed": passed,
                        "mass_big": 100 * bm / max(big_mass, 1e-12), "mass_all": 100 * float(e2[kk, cc][test_cols[cc]].sum()) / tot_mass, "days_pct": 100 * share_days})
    results.sort(key=lambda r: -r["mult"])
    print("\n8-K ITEM SCAN: %d item codes with >= %d scored flagged stock-days (day 0 + day +1 pooled; no recorded event; no earnings filing; overlapping groups)" % (len(results), MIN_FLAGGED))
    print("  %-6s %9s %7s | %-27s | %-8s | %-11s %-11s | %s" % ("item", "days", "mult", "gain 2006-12 / 13-19 / 20-26", "years +", "% big mass", "% all mass", "verdict"))
    for r in results:
        gv = " / ".join("%+.3f" % v if v is not None else "n/a" for v in r["vals"])
        print("  %-6s %9d %6.2fx | %-27s | %2d of %-2d  | %9.1f%% %10.1f%% | %s" % (r["item"], r["days"], r["mult"], gv, r["npos"], r["ny"], r["mass_big"], r["mass_all"], "EARNS A PLACE" if r["passed"] else "does not"))
    earned = [r for r in results if r["passed"]]
    print("\nitems that pass the pre-set rule: %s" % (", ".join(r["item"] for r in earned) if earned else "none"))
    print("(the earnings days held 16.6 points of the big no-event mass; the 'big mass' column is the share of the big no-event, no-earnings mass on that item's days; groups overlap)")
    print("ordinary-day group: %d scored stock-days with no 8-K at all on day 0 or +1" % int(ordinary.sum()))
    print("\nNOTE: a screen of %d items; a pass is a lead to confirm (e.g. by reading a sample, as with earnings). The filing time is unknown, so days 0 and +1 are pooled." % len(results))
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
