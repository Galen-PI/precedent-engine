#!/usr/bin/env python3
"""
extend_caches.py -- extends the local price caches (data_cache/returns and data_cache/ohlc) with the rows added to market_prices since each file was built, instead of re-downloading about 3.4 million rows. build_return_cache.py and build_ohlc_cache.py are 'resume-safe', which means they SKIP a security whose file already exists, so they cannot refresh an existing cache.
Reads the database; writes only local files (gitignored), and ONLY with --apply (the default is a dry run that reports and writes nothing).
HOW. For each security with an existing file: fetch the rows from OVERLAP_DAYS (14) calendar days before the file's last date; compare the overlapping days with the cached values (relative tolerance 1e-6). If they agree, the rows after the last cached date are appended. If they DISAGREE the table's history was restated since the cache was built (a split or dividend adjustment, a repair):
the security is reported as RESTATED and, with --apply, refetched IN FULL (appending to a restated history would leave an inconsistent series). Files are written atomically (a .tmp file, then replace). A security without a file is reported MISSING (run the original builder for it). The macro cache (_macro.pkl, four series, small) is refetched in full with --apply.
FORMATS (as the builders write them): returns {"id", "ticker", "sector", "dates", "adj"} from market_prices(price_date, adjusted_close), rows with a NULL adjusted_close dropped; ohlc {"id", "ticker", "dates", "open", "high", "low", "close"} from market_prices(price_date, open, high, low, close), None kept where a value is missing.
Usage:   python3 -u scripts/card/extend_caches.py                    dry run, both caches
         python3 -u scripts/card/extend_caches.py --apply            write
         python3 -u scripts/card/extend_caches.py --which ohlc --limit 5 --tickers AAPL MSFT        (options combine)
Before the first --apply:  du -sh data_cache/returns data_cache/ohlc  and, if you have the room,  cp -r data_cache/returns data_cache/returns_bak_YYYYMMDD  (same for ohlc).  AFTERWARDS rebuild the matrices:  python3 -u scripts/card/gap_audit.py --rebuild  and check that the last date printed by earnings_role_forward_test.py is current.
"""
import os, sys, time, pickle, datetime

RETURNS, OHLC, MACRO_FILE = "data_cache/returns", "data_cache/ohlc", "_macro.pkl"
MACRO = ["DCOILWTICO", "DGS10", "DAAA", "DBAA"]
OVERLAP_DAYS, TOL = 14, 1e-6


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


def differs(a, b):
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) > TOL * max(1.0, abs(float(a)), abs(float(b)))


def market_rows(sb, sid, cols, start=None):
    flt = [lambda q, i=sid: q.eq("security_id", i)]
    if start:
        flt.append(lambda q, s=start: q.gte("price_date", s))
    return fetch_all(sb, "market_prices", "price_date," + cols, flt, "price_date")


def to_f(v):
    return None if v is None else float(v)


def process(sb, sec, kind, apply):
    d_dir, cols, fields = (RETURNS, "adjusted_close", ["adj"]) if kind == "returns" else (OHLC, "open,high,low,close", ["open", "high", "low", "close"])
    path = os.path.join(d_dir, "%s.pkl" % sec["id"])
    if not os.path.exists(path):
        return "missing", 0, None
    d = pickle.load(open(path, "rb"))
    dates = d.get("dates") or []
    if not dates:
        return "empty", 0, None
    last = dates[-1]
    start = (datetime.date.fromisoformat(last) - datetime.timedelta(days=OVERLAP_DAYS)).isoformat()
    rows = market_rows(sb, sec["id"], cols, start)
    if kind == "returns":
        rows = [r for r in rows if r.get("adjusted_close") is not None]
    cached = {dt: i for i, dt in enumerate(dates) if dt >= start}
    restated = False
    for r in rows:
        i = cached.get(r["price_date"])
        if i is None:
            continue
        for f, col in zip(fields, cols.split(",")):
            if differs(d[f][i], r.get(col)):
                restated = True
    new = [r for r in rows if r["price_date"] > last]
    if restated:
        if apply:
            full = market_rows(sb, sec["id"], cols)
            if kind == "returns":
                full = [r for r in full if r.get("adjusted_close") is not None]
                obj = {"id": sec["id"], "ticker": sec["ticker"], "sector": sec.get("sector"), "dates": [r["price_date"] for r in full], "adj": [float(r["adjusted_close"]) for r in full]}
            else:
                obj = {"id": sec["id"], "ticker": sec["ticker"], "dates": [r["price_date"] for r in full], **{f: [to_f(r.get(c)) for r in full] for f, c in zip(fields, cols.split(","))}}
            save(path, obj)
            return "restated (refetched in full)", len(full), obj["dates"][-1] if full else None
        return "RESTATED (would be refetched in full)", len(new), last
    if not new:
        return "unchanged", 0, last
    if apply:
        d["dates"] = dates + [r["price_date"] for r in new]
        for f, c in zip(fields, cols.split(",")):
            d[f] = list(d[f]) + [to_f(r.get(c)) for r in new]
        save(path, d)
    return ("extended" if apply else "would extend"), len(new), new[-1]["price_date"]


def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    which = args[args.index("--which") + 1] if "--which" in args else "both"
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    tick = []
    if "--tickers" in args:
        for a in args[args.index("--tickers") + 1:]:
            if a.startswith("--"):
                break
            tick.append(a.upper())
    sb = get_sb()
    secs = fetch_all(sb, "securities", "id,ticker,sector", [], "id")
    if tick:
        secs = [s for s in secs if s["ticker"] in tick]
    if limit:
        secs = secs[:limit]
    print("%s | securities %d | caches: %s" % ("APPLY" if apply else "DRY RUN (nothing is written)", len(secs), which), flush=True)
    kinds = ["returns", "ohlc"] if which == "both" else [which]
    t0 = time.time()
    for kind in kinds:
        tally, rows_added, lasts, flagged = {}, 0, [], []
        for n, s in enumerate(secs, 1):
            try:
                st, nn, lastd = process(sb, s, kind, apply)
            except Exception as e:
                st, nn, lastd = "ERROR %s" % type(e).__name__, 0, None
                flagged.append("%s: %s" % (s["ticker"], str(e)[:80]))
            tally[st] = tally.get(st, 0) + 1
            rows_added += nn if st.startswith(("extended", "would extend")) else 0
            if lastd:
                lasts.append(lastd)
            if st.startswith(("RESTATED", "restated", "missing", "ERROR")) and len(flagged) < 40:
                flagged.append("%s: %s" % (s["ticker"], st))
            if n % 100 == 0:
                print("  %s: %d / %d done (%.0fs)" % (kind, n, len(secs), time.time() - t0), flush=True)
        print("\n%s cache: %s" % (kind.upper(), ", ".join("%s %d" % (k, v) for k, v in sorted(tally.items()))))
        print("  rows %s: %d | newest date seen: %s | oldest of the newest dates: %s" % ("added" if apply else "that would be added", rows_added, max(lasts) if lasts else None, min(lasts) if lasts else None))
        for f in flagged[:40]:
            print("  FLAG " + f)
    if "returns" in kinds:
        m = os.path.join(RETURNS, MACRO_FILE)
        if apply and os.path.exists(m):
            macro = {}
            for sid in MACRO:
                rows = fetch_all(sb, "macro_long", "obs_date,value", [lambda q, x=sid: q.eq("series_id", x)], "obs_date")
                macro[sid] = [(r["obs_date"], float(r["value"])) for r in rows if r["value"] is not None]
            save(m, macro)
            print("\nmacro cache refetched: " + ", ".join("%s to %s" % (k, v[-1][0] if v else None) for k, v in macro.items()))
        else:
            print("\nmacro cache: %s" % ("refetched only with --apply" if os.path.exists(m) else "no _macro.pkl found"))
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
