#!/usr/bin/env python3
"""
build_ohlc_cache.py -- reads the database, writes only local files (data_cache/ohlc/, gitignored). The companion of build_volume_cache.py.
Downloads every security's OPEN, HIGH, LOW and CLOSE history ONCE, so that the earnings-timing check can tell from the opening gap whether a release came before the open (the gap is on the filing day)
or after the close (the gap is on the next day) without any further database reads.

Usage:
    python3 -u scripts/card/build_ohlc_cache.py --limit 3                                 (trial: 3 securities, shows the speed)
    nohup python3 -u scripts/card/build_ohlc_cache.py > /tmp/ohlc_cache.log 2>&1 &        (full run in the background)
    tail -3 /tmp/ohlc_cache.log                                                               (progress)

Resume-safe: a security whose file already exists is skipped. Each file holds {"id", "ticker", "dates", "open", "high", "low", "close"} (oldest first; None where a value is missing).
Offset paging ordered by price_date, 1,000 rows per request, like build_return_cache.py. Expect it to take about as long as that cache did (about 3.4 million rows in all).
"""
import os, sys, time, pickle

OUT = "data_cache/ohlc"


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


def num(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    os.makedirs(OUT, exist_ok=True)
    sb = get_sb()
    secs = fetch_all(sb, "securities", "id,ticker,sector", [], "id")
    print("securities: %d" % len(secs), flush=True)
    t0, done, new = time.time(), 0, 0
    for s in secs:
        path = os.path.join(OUT, "%s.pkl" % s["id"])
        if os.path.exists(path):
            done += 1
            continue
        if limit is not None and new >= limit:
            break
        rows = fetch_all(sb, "market_prices", "price_date,open,high,low,close", [lambda q, sid=s["id"]: q.eq("security_id", sid)], "price_date")
        if not rows:
            print("   %-6s returned NO rows: not saved, so a rerun retries it" % s["ticker"], flush=True)
            continue
        save(path, {"id": s["id"], "ticker": s["ticker"], "dates": [str(r["price_date"])[:10] for r in rows], "open": [num(r["open"]) for r in rows], "high": [num(r["high"]) for r in rows],
                    "low": [num(r["low"]) for r in rows], "close": [num(r["close"]) for r in rows]})
        new += 1
        done += 1
        el = time.time() - t0
        print("%d/%d  %-6s %6d rows | %.0fs elapsed, about %.0fs left" % (done, len(secs), s["ticker"], len(rows), el, el / new * (len(secs) - done)), flush=True)
    print("finished: %d files in %s | %.0fs" % (len([f for f in os.listdir(OUT) if f.endswith(".pkl")]), OUT, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
