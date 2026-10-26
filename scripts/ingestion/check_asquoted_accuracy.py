#!/usr/bin/env python3
"""
check_asquoted_accuracy.py -- READ-ONLY acceptance test of the as-quoted price table (price_adjustment_factors) against a fact the vendor never saw: before decimalization (NYSE 2001-01-29, Nasdaq 2001-04-09) US closes were quoted in sixteenths of a dollar (or finer: 1/32), and since then in whole cents. A correct reconstruction of the AS-TRADED close (stored close / the latest change-point ratio) must sit on those grids to within the table's stated accuracy (5e-5 relative).
ERAS: pre = dates before 2001-01-01; post = dates from 2001-06-01. TOLERANCES: within $0.004 of a multiple of $0.0625 (chance 12.8%), of $0.03125 (chance 25.6%); within $0.002 of a whole cent (chance 40%).
IT PRINTS the share on the grid by era and price bucket, and EVERY ticker whose post-2001 share is below 97% (with enough closes), which points to a wrong factor for that ticker; --years TICKER ... adds a per-year breakdown (with the number of change points that began in each year) for named tickers.
Usage:   python3 -u scripts/ingestion/check_asquoted_accuracy.py [--tickers 60 | 0 for ALL] [--seed 20261026] [--years DRI GL]
         scripts/ops/bg.sh accuracy python3 -u scripts/ingestion/check_asquoted_accuracy.py --tickers 0        the all-ticker scan (a background job: prints PROGRESS lines)
"""
import os, sys, bisect, random, argparse, collections

GRID16, GRID32, TOL16, TOLC = 0.0625, 0.03125, 0.004, 0.002
EDGES = [(0, 20), (20, 50), (50, 100), (100, 250), (250, 1e9)]


def bucket(p):
    for lo, hi in EDGES:
        if lo <= p < hi:
            return "$%d-%s" % (lo, "up" if hi > 1e8 else "%d" % hi)
    return "?"


def dgrid(p, g):
    r = p / g
    return abs(r - round(r)) * g


def dpenny(p):
    return abs(p * 100 - round(p * 100)) / 100.0


def paged(sb, table, cols, order, flt, size=1000):
    out, off = [], 0
    while True:
        page = flt(sb.table(table).select(cols).order(order)).range(off, off + size - 1).execute().data
        if not page:
            break
        out += page
        if len(page) < size:
            break
        off += size
    return out


def asquoted(stored, factors):
    """stored: [(date, adjusted close)] ; factors: [(effective_date, ratio)] ascending. Returns [(date, as-quoted close)] for days on or after the first change point"""
    dates = [d for d, _ in factors]
    out = []
    for d, c in stored:
        i = bisect.bisect_right(dates, d) - 1
        if i >= 0:
            out.append((d, c / factors[i][1]))
    return out


def main(argv=None, sb=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", type=int, default=60, help="0 = every ticker with a finished factor table")
    ap.add_argument("--seed", type=int, default=20261026)
    ap.add_argument("--years", nargs="*", default=[], help="per-year breakdown for these tickers (they are added to the sample)")
    a = ap.parse_args(argv)
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    ok = {r["security_id"] for r in paged(sb, "asquoted_fetch_log", "security_id,status", "security_id", lambda q: q.eq("status", "ok"))}
    secs = [s for s in paged(sb, "securities", "id,ticker", "ticker", lambda q: q) if s["id"] in ok]
    pick = secs if a.tickers == 0 else random.Random(a.seed).sample(secs, min(a.tickers, len(secs)))
    pick = pick + [s for s in secs if s["ticker"] in a.years and s not in pick]
    cells, per_all, per_low = collections.defaultdict(lambda: [0, 0]), collections.defaultdict(lambda: [0, 0]), collections.defaultdict(lambda: [0, 0])
    c32, by_year, cps = collections.defaultdict(lambda: [0, 0]), collections.defaultdict(lambda: [0, 0]), {}
    for idx, s in enumerate(pick):
        if idx % 10 == 0:
            print("PROGRESS %d/%d" % (idx, len(pick)), flush=True)
        stored = [(str(r["price_date"])[:10], float(r["adjusted_close"])) for r in paged(sb, "market_prices", "price_date,adjusted_close", "price_date", lambda q: q.eq("security_id", s["id"])) if r.get("adjusted_close")]
        fac = [(str(r["effective_date"])[:10], float(r["ratio"])) for r in paged(sb, "price_adjustment_factors", "effective_date,ratio", "effective_date", lambda q: q.eq("security_id", s["id"]))]
        if s["ticker"] in a.years:
            cps[s["ticker"]] = collections.Counter(d[:4] for d, _ in fac)
        for d, p in asquoted(stored, fac):
            if p < 1.0:
                continue
            if d < "2001-01-01":
                k = ("pre-2001 (1/16 grid)", bucket(p)); hit = dgrid(p, GRID16) <= TOL16
                c32[bucket(p)][0] += 1
                c32[bucket(p)][1] += dgrid(p, GRID32) <= TOL16
            elif d >= "2001-06-01":
                k = ("post-2001 (penny grid)", bucket(p)); hit = dpenny(p) <= TOLC
                per_all[s["ticker"]][0] += 1
                per_all[s["ticker"]][1] += hit
                if p < 100:
                    per_low[s["ticker"]][0] += 1
                    per_low[s["ticker"]][1] += hit
                if s["ticker"] in a.years:
                    by_year[(s["ticker"], d[:4])][0] += 1
                    by_year[(s["ticker"], d[:4])][1] += hit
            else:
                continue
            cells[k][0] += 1
            cells[k][1] += hit
    print("PROGRESS %d/%d" % (len(pick), len(pick)), flush=True)
    print("tickers scanned %d of %d with a finished factor table%s; closes under $1 skipped" % (len(pick), len(secs), " (ALL)" if a.tickers == 0 else " (sample, seed %d)" % a.seed))
    for era, chance in (("pre-2001 (1/16 grid)", 2 * TOL16 / GRID16), ("post-2001 (penny grid)", 2 * TOLC / 0.01)):
        n = sum(v[0] for k, v in cells.items() if k[0] == era)
        h = sum(v[1] for k, v in cells.items() if k[0] == era)
        print("\n%s: overall %.1f%% of %d closes on the grid (chance %.0f%%)" % (era, 100.0 * h / max(1, n), n, 100 * chance))
        for lo, hi in EDGES:
            v = cells.get((era, bucket(lo)), [0, 0])
            if v[0]:
                extra = ("   on the 1/32 grid %5.1f%% (chance 26%%)" % (100.0 * c32[bucket(lo)][1] / c32[bucket(lo)][0])) if era.startswith("pre") and c32[bucket(lo)][0] else ""
                print("   %-9s n %7d  on the grid %5.1f%%%s" % (bucket(lo), v[0], 100.0 * v[1] / v[0], extra))
    weak = sorted(((v[1] / float(v[0]), t, v[0]) for t, v in per_all.items() if v[0] >= 200))
    low = [(f, t, n) for f, t, n in weak if f < 0.97]
    print("\npost-2001 tickers BELOW 97%% on the penny grid (all prices; %d of %d tickers with at least 200 closes): %s" % (len(low), len(weak), ", ".join("%s %.1f%% (%d)" % (t, 100 * f, n) for f, t, n in low[:60]) or "none"))
    for t in a.years:
        print("\nPER YEAR for %s (post-2001): year | closes | on the penny grid | change points that began that year" % t)
        for y in sorted(k[1] for k in by_year if k[0] == t):
            v = by_year[(t, y)]
            print("   %s  %5d  %5.1f%%   %d" % (y, v[0], 100.0 * v[1] / v[0], cps.get(t, {}).get(y, 0)))
    return cells, [t for f, t, n in low]


if __name__ == "__main__":
    main()
