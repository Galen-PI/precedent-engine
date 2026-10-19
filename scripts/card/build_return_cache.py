#!/usr/bin/env python3
"""
build_return_cache.py -- reads the database, writes only local files (data_cache/returns/, which is gitignored).
Downloads every security's adjusted-close history ONCE (plus SPY and the four macro series) so that cross-stock validation of the
day decomposition can run locally in minutes instead of making millions of database requests.

Usage:
    python3 -u scripts/card/build_return_cache.py --limit 3        (trial: 3 securities, shows the speed)
    nohup python3 -u scripts/card/build_return_cache.py > /tmp/ret_cache.log 2>&1 &     (full run in the background)
    tail -3 /tmp/ret_cache.log                                      (progress)

Resume-safe: a security whose file already exists is skipped, so an interrupted run (for example a Codespace restart) simply continues.
Each file holds {"id", "ticker", "sector", "dates", "adj"} (adjusted closes, oldest first). Returns are computed later.
Uses keyset-free offset paging ordered by price_date (a unique key per security), 1,000 rows per request.
"""
import os, sys, time, pickle

OUT = "data_cache/returns"
MACRO = ["DCOILWTICO", "DGS10", "DAAA", "DBAA"]


def get_sb():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def retry(fn, tries=4, base=2.0):
    for k in range(tries):
        try:
            return fn()
        except Exception as e:
            if k == tries - 1:
                raise
            print("   retry %d after error: %s" % (k + 1, str(e)[:120]), flush=True)
            time.sleep(base * (k + 1))


def fetch_all(sb, table, cols, filters, order):
    rows, off = [], 0
    while True:
        def go():
            q = sb.table(table).select(cols)
            for f in filters:
                q = f(q)
            return q.order(order).range(off, off + 999).execute().data
        page = retry(go)
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return rows


def save(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        pickle.dump(obj, fh, protocol=4)
    os.replace(tmp, path)


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    os.makedirs(OUT, exist_ok=True)
    sb = get_sb()
    secs = fetch_all(sb, "securities", "id,ticker,sector", [], "id")
    print("securities: %d" % len(secs), flush=True)

    mpath = os.path.join(OUT, "_macro.pkl")
    if not os.path.exists(mpath):
        macro = {}
        for sid in MACRO:
            rows = fetch_all(sb, "macro_long", "obs_date,value", [lambda q, s=sid: q.eq("series_id", s)], "obs_date")
            macro[sid] = [(r["obs_date"], float(r["value"])) for r in rows if r["value"] is not None]
            print("macro %s: %d rows" % (sid, len(macro[sid])), flush=True)
        save(mpath, macro)
    else:
        print("macro cache exists, skipped", flush=True)

    todo = [s for s in secs if not os.path.exists(os.path.join(OUT, "%s.pkl" % s["id"]))]
    print("to download: %d (already cached: %d)" % (len(todo), len(secs) - len(todo)), flush=True)
    if limit is not None:
        todo = todo[:limit]
    t0, done, nrows = time.time(), 0, 0
    for s in todo:
        rows = fetch_all(sb, "market_prices", "price_date,adjusted_close", [lambda q, i=s["id"]: q.eq("security_id", i)], "price_date")
        rows = [r for r in rows if r["adjusted_close"] is not None]
        save(os.path.join(OUT, "%s.pkl" % s["id"]),
             {"id": s["id"], "ticker": s["ticker"], "sector": s.get("sector"), "dates": [r["price_date"] for r in rows], "adj": [float(r["adjusted_close"]) for r in rows]})
        done += 1
        nrows += len(rows)
        if done % 10 == 0 or done == len(todo):
            el = time.time() - t0
            eta = el / done * (len(todo) - done)
            print("  %d/%d securities, %d price rows, %.0fs elapsed, about %.0f min left (last: %s)" % (done, len(todo), nrows, el, eta / 60, s["ticker"]), flush=True)
    print("done: %d securities this run, %d price rows" % (done, nrows), flush=True)


if __name__ == "__main__":
    main()
