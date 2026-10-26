#!/usr/bin/env python3
"""
reaction_explorer.py -- EXPLORATION TOOL for the reaction percentages (written 2026-10-26). READ-ONLY. Turns the dials on event_market_reactions_corrected: horizon (0, 1, 5, 20 trading days), threshold, measure (spy = abnormal vs SPY, sector = abnormal vs the sector peer basket, raw), and slices (year, era, corrected date, firm state, storm tier, sector, ticker).
GUARDRAILS (by design): (1) the SEALED companies listed in table explore_sealed_tickers (a seeded 30% of tickers) are EXCLUDED and there is deliberately NO option to include them: they are evaluated once, by a registered test; (2) every call is appended to data_cache/explore_log.jsonl: that line count is the 'descriptive looks' number for the TRIALS line of any later registration; (3) cells with fewer than 30 events are starred (*), and every share carries its 95% binomial margin; (4) nothing here creates a flag: exploration only.
EXAMPLES:
  python3 scripts/models/reaction_explorer.py                                   # horizon x threshold grid, SPY-adjusted
  python3 scripts/models/reaction_explorer.py --measure sector                  # the same, sector-adjusted
  python3 scripts/models/reaction_explorer.py --by year --threshold 0.03 --horizons 1,20
  python3 scripts/models/reaction_explorer.py --by firmstate --horizons 0,1,20 --threshold 0.02
  python3 scripts/models/reaction_explorer.py --by sector --horizons 20
Slices: year, era (<=2000, 2001-2013, 2014+), corrected, firmstate, storm, sector, ticker. Add --refresh to reload the data from the database (otherwise data_cache/explore_events.json is reused).
"""
import os, sys, json, math, time, argparse, datetime

CACHE = "data_cache/explore_events.json"
LOG = "data_cache/explore_log.jsonl"
THIN = 30


def fetch_all(sb, table, select, order, retries=3):
    rows, off = [], 0
    while True:
        for attempt in range(retries):
            try:
                page = sb.table(table).select(select).order(order).range(off, off + 999).execute().data
                break
            except Exception as e:
                if attempt == retries - 1:
                    raise
                time.sleep(2 * (attempt + 1))
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return rows


def load(sb, refresh=False, cache=CACHE):
    try:
        sealed = {r["ticker"] for r in fetch_all(sb, "explore_sealed_tickers", "ticker", "ticker")}
    except Exception as e:
        raise SystemExit("cannot read explore_sealed_tickers (%s): create the sealed table first (see SCRIPTS.md addendum 28); the explorer refuses to run without it" % str(e)[:80])
    if not sealed:
        raise SystemExit("explore_sealed_tickers is empty: refusing to run without a sealed set")
    if os.path.exists(cache) and not refresh:
        d = json.load(open(cache))
        if set(d.get("sealed", [])) == sealed:
            return d
    cols = "event_id,ticker,event_date,date_was_corrected," + ",".join("%s_%dd" % (p, h) for p in ("return", "abnormal_return", "abnormal_return_vs_sector") for h in (0, 1, 5, 20))
    ev = [r for r in fetch_all(sb, "event_market_reactions_corrected", cols, "event_id") if r["ticker"] not in sealed]
    ctx = fetch_all(sb, "event_pre_context", "event_id,firm_state_label,storm_tier", "id")
    state, storm = {}, {}
    for r in ctx:
        if r.get("firm_state_label") and r["event_id"] not in state:
            state[r["event_id"]] = r["firm_state_label"]
        if r.get("storm_tier") and r["event_id"] not in storm:
            storm[r["event_id"]] = r["storm_tier"]
    sector = {r["ticker"]: r["sector"] for r in fetch_all(sb, "securities", "ticker,sector", "ticker")}
    d = {"sealed": sorted(sealed), "events": ev, "state": {k: v for k, v in state.items() if k in {e["event_id"] for e in ev}}, "storm": {k: v for k, v in storm.items() if k in {e["event_id"] for e in ev}}, "sector": sector}
    os.makedirs(os.path.dirname(cache) or ".", exist_ok=True)
    json.dump(d, open(cache, "w"))
    return d


def keyname(measure, h):
    return {"spy": "abnormal_return_%dd", "sector": "abnormal_return_vs_sector_%dd", "raw": "return_%dd"}[measure] % h


def rescale_if_percent(events):
    vals = [abs(float(r["abnormal_return_20d"])) for r in events if r.get("abnormal_return_20d") is not None]
    if vals and max(vals) > 5:
        for r in events:
            for p in ("return", "abnormal_return", "abnormal_return_vs_sector"):
                for h in (0, 1, 5, 20):
                    k = "%s_%dd" % (p, h)
                    if r.get(k) is not None:
                        r[k] = float(r[k]) / 100.0
        return True
    return False


def cell(events, key, thr):
    vals = [float(r[key]) for r in events if r.get(key) is not None]
    n = len(vals); k = sum(1 for v in vals if abs(v) > thr)
    return n, k


def fmt(n, k):
    if n == 0:
        return "-"
    p = k / n; half = 1.96 * math.sqrt(p * (1 - p) / n)
    return "%.1f+-%.1f%s" % (100 * p, 100 * half, "*" if n < THIN else "")


def group_of(r, by, d):
    y = int(str(r["event_date"])[:4])
    if by == "year": return str(y)
    if by == "era": return "a <=2000" if y <= 2000 else ("b 2001-2013" if y <= 2013 else "c 2014+")
    if by == "corrected": return "date corrected" if r.get("date_was_corrected") else "stored date"
    if by == "firmstate": return "has firm state" if d["state"].get(r["event_id"]) else "no firm state"
    if by == "storm": return d["storm"].get(r["event_id"]) or "none"
    if by == "sector": return d["sector"].get(r["ticker"]) or "unknown"
    if by == "ticker": return r["ticker"]
    raise SystemExit("unknown slice: " + by)


def run(d, measure="spy", by="none", horizons=(0, 1, 5, 20), thresholds=(0.01, 0.02, 0.03, 0.05), threshold=0.03, out=print):
    ev = d["events"]; res = {}
    out("EXPLORATION (sealed companies excluded: %d tickers). Events in the explore set: %d, tickers: %d. measure=%s. Cells starred * have n < %d." % (len(d["sealed"]), len(ev), len({e["ticker"] for e in ev}), measure, THIN))
    if by == "none":
        out("share of events whose |return| exceeds the threshold, with the 95%% margin:")
        out("%-10s %6s  " % ("horizon", "n") + "  ".join("%-12s" % (">%g%%" % (100 * t)) for t in thresholds))
        for h in horizons:
            key = keyname(measure, h); n = cell(ev, key, 0)[0]
            cells = [cell(ev, key, t) for t in thresholds]; res[h] = cells
            out("%-10s %6d  " % ("%dd" % h, n) + "  ".join("%-12s" % fmt(*c) for c in cells))
    else:
        groups = {}
        for r in ev:
            groups.setdefault(group_of(r, by, d), []).append(r)
        names = sorted(groups) if by != "ticker" else sorted(groups, key=lambda g: -len(groups[g]))[:15]
        out("share beyond +-%g%% by %s:" % (100 * threshold, by))
        out("%-22s %6s  " % (by, "events") + "  ".join("%-12s" % ("%dd" % h) for h in horizons))
        for g in names:
            cells = [cell(groups[g], keyname(measure, h), threshold) for h in horizons]; res[g] = cells
            out("%-22s %6d  " % (g[:22], len(groups[g])) + "  ".join("%-12s" % fmt(*c) for c in cells))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measure", default="spy", choices=["spy", "sector", "raw"]); ap.add_argument("--by", default="none")
    ap.add_argument("--horizons", default="0,1,5,20"); ap.add_argument("--threshold", type=float, default=0.03)
    ap.add_argument("--thresholds", default="0.01,0.02,0.03,0.05"); ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    from supabase import create_client
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    d = load(sb, a.refresh)
    if rescale_if_percent(d["events"]):
        print("NOTE: the return columns look like PERCENT, not fractions; rescaled by 100 for this run.")
    hz = tuple(int(x) for x in a.horizons.split(",")); th = tuple(float(x) for x in a.thresholds.split(","))
    run(d, a.measure, a.by, hz, th, a.threshold)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    open(LOG, "a").write(json.dumps({"ts": datetime.datetime.utcnow().isoformat() + "Z", "args": vars(a), "events": len(d["events"])}) + "\n")
    n = sum(1 for _ in open(LOG))
    print("\nlooks logged so far: %d (data_cache/explore_log.jsonl) -> the 'descriptive=' number for any later registration" % n)


if __name__ == "__main__":
    main()
