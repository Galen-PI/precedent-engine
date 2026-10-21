#!/usr/bin/env python3
"""
build_review_queue.py -- READ-ONLY (results/unrecorded_candidates.csv, the flag CSVs if present, data_cache/audit_matrices.npz for the trading calendar; the database is read for 8-K filings and tickers). Writes results/human_review_queue.csv.
WHAT IT IS. A worklist of big ordinary misses (>= 3.0 band units, no recorded event or earnings window, not an aftershock) that a person could resolve from material we already hold or can point to:
  TIER A  big VOLUME-SPIKE miss with an 8-K already in the database attached to the day (filed on the day or the trading day before; items other than 2.02 / 7.01 / 9.01) that was NOT promoted to an event: open the filing (URL in the file) and decide.
  TIER B  big volume-spike miss with NO such filing but a SECTOR THEME or peer GROUP MOVE flag: probably a sub-industry or macro story; review as a group event (the flag file lists the stocks that moved with it).
  TIER C  any other category (quiet etc.) with an attached 8-K, lower priority.
Not queued: stock-specific volume-spike misses with no filing and no group evidence (nothing to open; they need an outside source). Their count is printed.
Rows are ordered within a tier by volume ratio x band units. Nothing is written to the database.
Usage:   python3 -u scripts/card/build_review_queue.py [max_rows_per_tier]
"""
import os, sys, csv, bisect, warnings
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RESULTS = os.path.join(ROOT, "results")
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
SKIP_ITEMS = {"2.02", "7.01", "9.01"}
VOLUME_CATS = ("volume spike only", "volume spike + article spike")


def read_flags(name, col):
    p = os.path.join(RESULTS, name)
    out = {}
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            out[(r["date"], r["ticker"])] = (int(r[col]), r)
    return out


def main():
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    dl = [str(x) for x in np.load(CACHE_FILE, allow_pickle=False)["dates"]]
    cands = list(csv.DictReader(open(os.path.join(RESULTS, "unrecorded_candidates.csv"))))
    grp, sec = read_flags("unrecorded_group_flags.csv", "group_move"), read_flags("unrecorded_sector_cluster_flags.csv", "sector_theme")
    sb = ew.get_sb()
    tick_of = {r["id"]: r["ticker"] for r in uc.paged(lambda: sb.table("securities").select("id,ticker").order("id"))}
    by_day = defaultdict(list)                      # (ticker, trading-day index) -> filings attached to that day (filing day i and i+1)
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes,accession_number,primary_document_url,promoted_to_event").order("id")):
        tk = tick_of.get(r["security_id"])
        its = set(dc.parse_items(r.get("item_codes"))) - SKIP_ITEMS
        if not tk or not its or {"2.02", "7.01"} & set(dc.parse_items(r.get("item_codes"))):
            continue
        i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
        for day in (i, i + 1):
            by_day[(tk, day)].append((",".join(sorted(its)), str(r["filing_date"])[:10], r.get("accession_number") or "", r.get("primary_document_url") or "", bool(r.get("promoted_to_event"))))
    queue, no_evidence = [], 0
    for c in cands:
        t = bisect.bisect_left(dl, c["date"])
        if t >= len(dl) or dl[t] != c["date"]:
            continue
        fil = [f for f in by_day.get((c["ticker"], t), []) if not f[4]]
        g, s = grp.get((c["date"], c["ticker"]), (0, None))[0], sec.get((c["date"], c["ticker"]), (0, None))
        sector_theme = s[0] if s else 0
        vs = c["category"] in VOLUME_CATS
        why = []
        if fil and vs:
            tier = "A"
        elif vs and (g or sector_theme):
            tier = "B"
        elif fil:
            tier = "C"
        else:
            if vs:
                no_evidence += 1
            continue
        if fil:
            why.append("unpromoted 8-K: " + " | ".join("%s filed %s %s" % (f[0], f[1], f[3] or f[2]) for f in fil))
        if g:
            why.append("peer group move (%s)" % grp[(c["date"], c["ticker"])][1].get("peers_moved", ""))
        if sector_theme:
            why.append("sector theme (%s)" % (s[1].get("participants", "")[:80]))
        vr = float(c["volume_ratio"]) if c["volume_ratio"] else 0.0
        queue.append((tier, -vr * float(c["band_units"]), c, "; ".join(why)))
    queue.sort(key=lambda x: (x[0], x[1]))
    out = []
    counts = Counter(q[0] for q in queue)
    seen = Counter()
    for tier, _, c, why in queue:
        seen[tier] += 1
        if seen[tier] <= cap:
            out.append([tier, c["date"], c["ticker"], c["return_pct"], c["miss_pct"], c["band_units"], c["volume_ratio"], c["article_count"], c["category"], why, "", ""])
    path = os.path.join(RESULTS, "human_review_queue.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["tier", "date", "ticker", "return_pct", "miss_pct", "band_units", "volume_ratio", "article_count", "category", "evidence", "reviewer_decision (event / not an event / need more)", "notes"])
        w.writerows(out)
    print("queue: %s | up to %d per tier written to results/human_review_queue.csv (%d rows)" % (", ".join("tier %s %d" % (k, counts[k]) for k in sorted(counts)), cap, len(out)))
    print("not queued: stock-specific big volume-spike misses with no filing and no group evidence: %d (they need an outside source)" % no_evidence)
    for r in out[:8]:
        print("  %s %s %-6s %6s%% miss %s bu %s vr | %s" % (r[0], r[1], r[2], r[3], r[5], r[6], r[9][:150]))


if __name__ == "__main__":
    main()
