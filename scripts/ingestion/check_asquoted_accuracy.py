#!/usr/bin/env python3
"""
check_asquoted_accuracy.py -- READ-ONLY acceptance test of the as-quoted price table (price_adjustment_factors) against a fact the vendor never saw: before decimalization (NYSE 2001-01-29, Nasdaq 2001-04-09) US closes were quoted in sixteenths of a dollar (or coarser), and since then in whole cents. A correct reconstruction of the AS-TRADED close (stored close / the latest change-point ratio) must sit on the 1/16 grid before 2001 and on the penny grid after mid-2001, to within the table's stated accuracy (5e-5 relative).
ERAS: pre = dates before 2001-01-01; post = dates from 2001-06-01. TOLERANCES: within $0.004 of a multiple of $0.0625 (chance 12.8%); within $0.002 of a whole cent (chance 40%).
IT PRINTS the share on the grid by era and price bucket (accuracy falls as the price rises, because a fixed relative error is a larger dollar error), and the tickers with the weakest post-2001 grid share among prices under $100, which would point to a wrong factor for that ticker.
Usage:   python3 -u scripts/ingestion/check_asquoted_accuracy.py [--tickers 60] [--seed 20261026]
"""
import os, sys, bisect, random, argparse, collections

GRID16, TOL16, TOLC = 0.0625, 0.004, 0.002
EDGES = [(0, 20), (20, 50), (50, 100), (100, 250), (250, 1e9)]


def bucket(p):
    for lo, hi in EDGES:
        if lo <= p < hi:
            return "$%d-%s" % (lo, "up" if hi > 1e8 else "%d" % hi)
    return "?"


def d16(p):
    r = p / GRID16
    return abs(r - round(r)) * GRID16


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
    ap.add_argument("--tickers", type=int, default=60)
    ap.add_argument("--seed", type=int, default=20261026)
    a = ap.parse_args(argv)
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    ok = {r["security_id"] for r in paged(sb, "asquoted_fetch_log", "security_id,status", "security_id", lambda q: q.eq("status", "ok"))}
    secs = [s for s in paged(sb, "securities", "id,ticker", "ticker", lambda q: q) if s["id"] in ok]
    pick = random.Random(a.seed).sample(secs, min(a.tickers, len(secs)))
    cells, per_ticker = collections.defaultdict(lambda: [0, 0]), collections.defaultdict(lambda: [0, 0])
    for s in pick:
        stored = [(str(r["price_date"])[:10], float(r["adjusted_close"])) for r in paged(sb, "market_prices", "price_date,adjusted_close", "price_date", lambda q: q.eq("security_id", s["id"])) if r.get("adjusted_close")]
        fac = [(str(r["effective_date"])[:10], float(r["ratio"])) for r in paged(sb, "price_adjustment_factors", "effective_date,ratio", "effective_date", lambda q: q.eq("security_id", s["id"]))]
        for d, p in asquoted(stored, fac):
            if p < 1.0:
                continue
            if d < "2001-01-01":
                k = ("pre-2001 (1/16 grid)", bucket(p)); hit = d16(p) <= TOL16
            elif d >= "2001-06-01":
                k = ("post-2001 (penny grid)", bucket(p)); hit = dpenny(p) <= TOLC
                if p < 100:
                    per_ticker[s["ticker"]][0] += 1
                    per_ticker[s["ticker"]][1] += hit
            else:
                continue
            cells[k][0] += 1
            cells[k][1] += hit
    print("tickers sampled %d of %d with a finished factor table (seed %d); closes under $1 skipped" % (len(pick), len(secs), a.seed))
    for era, chance in (("pre-2001 (1/16 grid)", 2 * TOL16 / GRID16), ("post-2001 (penny grid)", 2 * TOLC / 0.01)):
        n = sum(v[0] for k, v in cells.items() if k[0] == era)
        h = sum(v[1] for k, v in cells.items() if k[0] == era)
        print("\n%s: overall %.1f%% of %d closes on the grid (chance %.0f%%)" % (era, 100.0 * h / max(1, n), n, 100 * chance))
        for lo, hi in EDGES:
            v = cells.get((era, bucket(lo)), [0, 0])
            if v[0]:
                print("   %-9s n %7d  on the grid %5.1f%%" % (bucket(lo), v[0], 100.0 * v[1] / v[0]))
    worst = sorted(((v[1] / float(v[0]), t, v[0]) for t, v in per_ticker.items() if v[0] >= 200))[:5]
    print("\nweakest post-2001 grid share among prices under $100 (ticker, share, closes): " + ", ".join("%s %.1f%% (%d)" % (t, 100 * f, n) for f, t, n in worst))
    return cells


if __name__ == "__main__":
    main()
