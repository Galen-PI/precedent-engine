#!/usr/bin/env python3
"""
check_asquoted_accuracy.py -- READ-ONLY acceptance test of the as-quoted price table (price_adjustment_factors) against a fact the vendor never saw: before decimalization (NYSE 2001-01-29, Nasdaq 2001-04-09) US closes were quoted in sixteenths of a dollar (or finer: 1/32), and since then in whole cents. A correct reconstruction of the AS-TRADED close (stored close / the latest change-point ratio) must sit on those grids to within the table's stated accuracy (5e-5 relative).
ERAS: pre = dates before 2001-01-01; post = dates from 2001-06-01. TOLERANCES: within $0.004 of a multiple of $0.0625 (chance 12.8%), of $0.03125 (chance 25.6%); within $0.002 of a whole cent (chance 40%).
IT PRINTS the share on the grid by era and price bucket, and EVERY ticker whose post-2001 share is below 97% (with enough closes) with the first year from which all later years are clean; --years TICKER ... adds a per-year breakdown for named tickers.
SAFE TO INTERRUPT: transient database errors (502, timeouts) are retried; each ticker's result is appended to data_cache/accuracy_cache.jsonl as it finishes, and a rerun skips tickers already in it (--fresh ignores the cache; delete the file after any change to the factor table).
Usage:   python3 -u scripts/ingestion/check_asquoted_accuracy.py [--tickers 60 | 0 for ALL] [--seed 20261026] [--years DRI GL] [--fresh]
         scripts/ops/bg.sh accuracy python3 -u scripts/ingestion/check_asquoted_accuracy.py --tickers 0        the all-ticker scan (a background job: prints PROGRESS lines)
"""
import os, sys, bisect, random, argparse, collections, json, time

GRID16, GRID32, TOL16, TOLC = 0.0625, 0.03125, 0.004, 0.002
EDGES = [(0, 20), (20, 50), (50, 100), (100, 250), (250, 1e9)]
PRE, POST = "pre-2001 (1/16 grid)", "post-2001 (penny grid)"
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data_cache", "accuracy_cache.jsonl")
TRANSIENT = ("502", "503", "504", "json could not be generated", "timed out", "timeout", "connection", "temporarily")


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


def run_query(q, tries=6):
    for k in range(tries):
        try:
            return q.execute()
        except Exception as e:
            if k == tries - 1 or not any(t in str(e).lower() for t in TRANSIENT):
                raise
            print("  transient database error, retrying in %ds: %s" % (min(60, 5 * (k + 1)), str(e)[:90]), flush=True)
            time.sleep(min(60, 5 * (k + 1)))


def paged(sb, table, cols, order, flt, size=1000):
    out, off = [], 0
    while True:
        page = run_query(flt(sb.table(table).select(cols).order(order)).range(off, off + size - 1)).data
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


def scan_ticker(sb, s):
    """one ticker's counts, JSON-serialisable: {pre: {bucket: [n, hit]}, post: {...}, c32: {...}, years: {year: [n, hit]}, low: [n, hit], all: [n, hit], cps: {year: n}}"""
    stored = [(str(r["price_date"])[:10], float(r["adjusted_close"])) for r in paged(sb, "market_prices", "price_date,adjusted_close", "price_date", lambda q: q.eq("security_id", s["id"])) if r.get("adjusted_close")]
    fac = [(str(r["effective_date"])[:10], float(r["ratio"])) for r in paged(sb, "price_adjustment_factors", "effective_date,ratio", "effective_date", lambda q: q.eq("security_id", s["id"]))]
    rec = {"ticker": s["ticker"], "pre": {}, "post": {}, "c32": {}, "years": {}, "low": [0, 0], "all": [0, 0], "cps": dict(collections.Counter(d[:4] for d, _ in fac))}
    def add(dct, key, hit):
        v = dct.setdefault(key, [0, 0]); v[0] += 1; v[1] += int(hit)
    for d, p in asquoted(stored, fac):
        if p < 1.0:
            continue
        b = bucket(p)
        if d < "2001-01-01":
            add(rec["pre"], b, dgrid(p, GRID16) <= TOL16)
            add(rec["c32"], b, dgrid(p, GRID32) <= TOL16)
        elif d >= "2001-06-01":
            hit = dpenny(p) <= TOLC
            add(rec["post"], b, hit)
            add(rec["years"], d[:4], hit)
            rec["all"][0] += 1; rec["all"][1] += int(hit)
            if p < 100:
                rec["low"][0] += 1; rec["low"][1] += int(hit)
    return rec


def clean_from(years, cutoff=0.97, min_n=50):
    """the first year from which EVERY later year (with at least min_n closes) is at or above the cutoff; 'never' if the last year is not"""
    ys = [y for y in sorted(years) if years[y][0] >= min_n]
    if not ys:
        return "n/a"
    start = None
    for y in reversed(ys):
        if years[y][1] / float(years[y][0]) >= cutoff:
            start = y
        else:
            break
    return start or "never"


def main(argv=None, sb=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", type=int, default=60, help="0 = every ticker with a finished factor table")
    ap.add_argument("--seed", type=int, default=20261026)
    ap.add_argument("--years", nargs="*", default=[], help="per-year breakdown for these tickers (they are added to the sample)")
    ap.add_argument("--fresh", action="store_true", help="ignore the cache file")
    a = ap.parse_args(argv)
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    ok = {r["security_id"] for r in paged(sb, "asquoted_fetch_log", "security_id,status", "security_id", lambda q: q.eq("status", "ok"))}
    secs = [s for s in paged(sb, "securities", "id,ticker", "ticker", lambda q: q) if s["id"] in ok]
    pick = secs if a.tickers == 0 else random.Random(a.seed).sample(secs, min(a.tickers, len(secs)))
    pick = pick + [s for s in secs if s["ticker"] in a.years and s not in pick]
    cache = {}
    if not a.fresh and os.path.exists(CACHE_FILE):
        for line in open(CACHE_FILE):
            try:
                r = json.loads(line); cache[r["ticker"]] = r
            except ValueError:
                pass
    todo = [s for s in pick if s["ticker"] not in cache]
    print("tickers to scan %d (cache holds %d of the %d wanted)" % (len(todo), len(pick) - len(todo), len(pick)), flush=True)
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "a") as fh:
        for idx, s in enumerate(todo):
            if idx % 10 == 0:
                print("PROGRESS %d/%d" % (idx + len(pick) - len(todo), len(pick)), flush=True)
            rec = scan_ticker(sb, s)
            cache[s["ticker"]] = rec
            fh.write(json.dumps(rec) + "\n"); fh.flush()
    print("PROGRESS %d/%d" % (len(pick), len(pick)), flush=True)
    recs = [cache[s["ticker"]] for s in pick]
    cells, c32 = collections.defaultdict(lambda: [0, 0]), collections.defaultdict(lambda: [0, 0])
    for r in recs:
        for era, key in ((PRE, "pre"), (POST, "post")):
            for b, v in r[key].items():
                cells[(era, b)][0] += v[0]; cells[(era, b)][1] += v[1]
        for b, v in r["c32"].items():
            c32[b][0] += v[0]; c32[b][1] += v[1]
    print("tickers scanned %d of %d with a finished factor table%s; closes under $1 skipped" % (len(pick), len(secs), " (ALL)" if a.tickers == 0 else " (sample, seed %d)" % a.seed))
    for era, chance in ((PRE, 2 * TOL16 / GRID16), (POST, 2 * TOLC / 0.01)):
        n = sum(v[0] for k, v in cells.items() if k[0] == era)
        h = sum(v[1] for k, v in cells.items() if k[0] == era)
        print("\n%s: overall %.1f%% of %d closes on the grid (chance %.0f%%)" % (era, 100.0 * h / max(1, n), n, 100 * chance))
        for lo, hi in EDGES:
            v = cells.get((era, bucket(lo)), [0, 0])
            if v[0]:
                extra = ("   on the 1/32 grid %5.1f%% (chance 26%%)" % (100.0 * c32[bucket(lo)][1] / c32[bucket(lo)][0])) if era == PRE and c32[bucket(lo)][0] else ""
                print("   %-9s n %7d  on the grid %5.1f%%%s" % (bucket(lo), v[0], 100.0 * v[1] / v[0], extra))
    weak = sorted(((r["all"][1] / float(r["all"][0]), r["ticker"], r["all"][0], clean_from(r["years"])) for r in recs if r["all"][0] >= 200))
    low = [w for w in weak if w[0] < 0.97]
    print("\npost-2001 tickers BELOW 97%% on the penny grid (all prices; %d of %d tickers with at least 200 closes), each with the first year from which every later year is clean: %s" % (len(low), len(weak), ", ".join("%s %.1f%% (%d) clean from %s" % (t, 100 * f, n, cf) for f, t, n, cf in low[:80]) or "none"))
    for t in a.years:
        r = cache.get(t)
        if not r:
            continue
        print("\nPER YEAR for %s (post-2001): year | closes | on the penny grid | change points that began that year" % t)
        for y in sorted(r["years"]):
            v = r["years"][y]
            print("   %s  %5d  %5.1f%%   %d" % (y, v[0], 100.0 * v[1] / v[0], r["cps"].get(y, 0)))
    return cells, [t for f, t, n, cf in low]


if __name__ == "__main__":
    main()
