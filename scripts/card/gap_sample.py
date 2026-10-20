#!/usr/bin/env python3
"""
gap_sample.py -- READ-ONLY. A reproducible random sample of BIG MISSES WITH NO RECORDED EVENT, to be READ (what was the news that day?), not ruled on by a formula.

Usage:   python3 -u scripts/card/gap_sample.py [N] [SEED] [FROM] [MIN_UNITS] [noearn]
         defaults: 30  20261020  2024-01-01  3.0
         add the word  noearn  as the fifth argument to ALSO exclude earnings days (an 8-K item 2.02 filing on day 0 or the next trading day): the sample
         of what is still missing once the earnings thread is accounted for. Its rows are written to gap_sample_SEED_noearn.csv.
Needs:   data_cache/audit_matrices.npz (gap_audit.py builds it). The database is read once for the event days.
Writes:  results/gap_sample_SEED.csv and prints the sample sorted by date.

THE POPULATION: stock-days since FROM where the standardized miss, divided by that day's market-wide stress (the root-mean-square miss of all stocks that day), is at
least MIN_UNITS in size AND the stock has no recorded own event on day 0 or +1. The sample is drawn with a fixed seed from the sorted population, so the same
command always gives the same rows. Returns beyond +/-50% are not in the matrices.

HOW IT IS USED (rules written before reading any row). For each row, someone looks up what happened to the company on that date and files it in ONE category:
  earnings or guidance | analyst action | product, customer or partnership news | M&A, activist or rumor | legal or regulatory | sector or peer news |
  index change or flows | nothing found.
  Report the counts with the sample size beside them; with N = 30 a category share is uncertain by about +/-9 points (one standard error at 30%), so a count
  under about 5 says little. A row stays 'nothing found' unless a source on that date says otherwise; no row is forced into a category.
PREDICTION (before reading): earnings or guidance plus analyst action make up at least half of the rows, because only a fraction of earnings 8-Ks are in the
  event table; 'nothing found' is under a fifth.
"""
import os, sys, csv, random, time, bisect
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")


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


def main():
    a = sys.argv[1:]
    N = int(a[0]) if len(a) > 0 else 30
    seed = int(a[1]) if len(a) > 1 else 20261020
    start = a[2] if len(a) > 2 else "2024-01-01"
    min_units = float(a[3]) if len(a) > 3 else 3.0
    noearn = len(a) > 4 and a[4] == "noearn"
    if not os.path.exists(CACHE_FILE):
        sys.exit("Run gap_audit.py first: it builds %s." % CACHE_FILE)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, tickers, E, SD, Yr = d["dates"], d["ids"], d["tickers"], d["E"], d["SD"], d["Y"]
    nS, n = E.shape
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = E / SD
    stress = np.sqrt(np.nanmean(np.where(np.isnan(Z), np.nan, Z ** 2), axis=0))
    einfo, use_labels, nlab = ew.load_event_info(ew.get_sb(), list(dates), set(ids.tolist()))
    EV = np.zeros((nS, n), dtype=bool)
    idx = {sid: k for k, sid in enumerate(ids.tolist())}
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                EV[k, t] = True
    EA = np.zeros((nS, n), dtype=bool)
    if noearn:
        dl = [str(x) for x in dates]
        sb = ew.get_sb()
        for r in paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date").like("item_codes", "%2.02%").order("id")):
            k = idx.get(r["security_id"])
            i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
            if k is not None and i < n:
                EA[k, i] = True
                if i + 1 < n:
                    EA[k, i + 1] = True
    first = int(np.searchsorted(dates, start))
    zb = np.abs(Z) / stress[None, :]
    cand = (zb >= min_units) & ~EV & ~EA
    cand[:, :first] = False
    rows = sorted(zip(*np.where(cand)), key=lambda x: (x[1], x[0]))
    total_recent = int((~np.isnan(Z[:, first:])).sum())
    print("population: %d stock-days from %s with a miss of at least %.1f stress-units and no recorded event%s (%.2f%% of the %d scored stock-days since then)" % (
        len(rows), start, min_units, " and no earnings filing on day 0 or +1" if noearn else "", 100.0 * len(rows) / max(total_recent, 1), total_recent))
    if len(rows) < N:
        N = len(rows)
    pick = sorted(random.Random(seed).sample(rows, N), key=lambda x: (x[1], x[0]))
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    out = os.path.join(ROOT, "results", "gap_sample_%d%s.csv" % (seed, "_noearn" if noearn else ""))
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "ticker", "actual_pct", "miss_pct", "stress_units", "day_stress", "category", "what_happened"])
        print("\n%-11s %-7s %9s %9s %7s %7s" % ("date", "ticker", "actual", "miss", "units", "stress"))
        for k, t in pick:
            row = (dates[t], tickers[k], 100 * float(Yr[k, t]), 100 * float(E[k, t]), float(zb[k, t]), float(stress[t]))
            print("%-11s %-7s %8.2f%% %8.2f%% %7.1f %6.2fx" % row)
            w.writerow(["%s" % row[0], row[1], "%.2f" % row[2], "%.2f" % row[3], "%.1f" % row[4], "%.2f" % row[5], "", ""])
    print("\nsaved %s (the last two columns are for the reading)" % out)
    print("seed %d: rerun with the same arguments for the same rows." % seed)


if __name__ == "__main__":
    main()
