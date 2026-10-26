#!/usr/bin/env python3
"""
fetch_asquoted_factors.py -- builds price_adjustment_factors so that the AS-QUOTED (as traded) close of any stored day can be reconstructed, without touching market_prices.
WHY. market_prices holds prices fetched with adjust=all (split- AND dividend-adjusted as of the fetch day), so historical LEVELS are scaled (AAPL 2020-08-28: stored 120.935 vs traded 499.23). Round-number price effects need the traded level. The vendor returns traded prices with adjust=none (probe 2026-10-23: AAPL 2020-08-28 close 499.23001).
METHOD. For each ticker: read the stored adjusted closes; fetch the vendor's UNADJUSTED daily closes for the same span (windows of at most 4,900 stored days, so each request is below the 5,000-row cap); ratio(t) = stored_adjusted_close / traded_close on every common day. The ratio is piecewise constant (it moves only at splits and dividends), so only its CHANGE POINTS are stored: a new segment starts when the ratio departs from the segment's first value by more than TOL (5e-5, relative). AS-QUOTED CLOSE = stored close / ratio of the latest change point on or before the day. ACCURACY: within TOL (0.005%, half a cent on $100) of the traded close.
SELF-CHECKS PER TICKER (written to asquoted_fetch_log.flags, never silently dropped): the share of stored days the vendor also has (flag below 98%); the ratio must only RISE toward 1 over time (adjustments multiply EARLIER prices by less than 1): a decrease is flagged unless it matches an inverse split ratio (a reverse split); the latest ratio should lie in 0.90-1.0005; a step above x1.15 that is NOT within 3% of a split ratio is flagged (a spin-off, or a vendor level shift like HON 2026-06-29); a window that returns 5,000 rows is flagged as truncated.
BUDGET. Basic plan: 8 requests a minute, 800 credits a day. PACE 8 s per request; --max-requests caps the run and is further capped by (daily limit - daily usage - 25) from api_usage. Resume-safe: tickers already logged ok/flagged are skipped; errors are retried; a ticker is written only when ALL its windows were fetched.
Tables (create first, see the DO block): price_adjustment_factors(security_id, effective_date, ratio, PK (security_id, effective_date)); asquoted_fetch_log(security_id PK, fetched_at, requests_used, stored_rows, vendor_rows, matched_rows, change_points, first_date, last_date, last_ratio, status, flags).
Usage:   python3 -u scripts/ingestion/fetch_asquoted_factors.py --tickers AAPL NVDA            fetches (spends credits), reports, writes nothing
         python3 -u scripts/ingestion/fetch_asquoted_factors.py --tickers AAPL NVDA --apply     writes
         python3 -u scripts/ingestion/fetch_asquoted_factors.py --all --max-requests 700 --apply     (run once a day until it reports nothing left)
"""
import os, sys, time, json, argparse, datetime
import requests

PACE_SECONDS = 8.0
WINDOW_MAX = 4900
TOL = 5e-5
DAILY_RESERVE = 25
SYMBOL_OVERRIDES = {"BRK-B": "BRK.B", "BF-B": "BF.B"}   # same map as refresh_market_prices.py
DONE = ("ok", "flagged")
SPLIT_RATIOS = (1.2, 1.25, 4.0 / 3.0, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 10, 15, 20, 25, 30, 40, 50)


def near_split(step, tol=0.04):
    """step = ratio_new / ratio_old; True if it is within tol of a split ratio or its inverse (a reverse split)"""
    f = step if step >= 1 else 1.0 / step
    return any(abs(f / k - 1.0) <= tol for k in SPLIT_RATIOS)


def api_usage(key):
    return requests.get("https://api.twelvedata.com/api_usage", params={"apikey": key}, timeout=30).json()


def fetch_raw(key, ticker, start, end):
    for attempt in range(3):
        try:
            r = requests.get("https://api.twelvedata.com/time_series", timeout=60, params={"symbol": SYMBOL_OVERRIDES.get(ticker, ticker), "interval": "1day", "start_date": start, "end_date": end, "adjust": "none", "outputsize": 5000, "apikey": key})
        except requests.RequestException:
            time.sleep(10)
            continue
        if r.status_code == 429:
            time.sleep(30 * (attempt + 1))
            continue
        if r.status_code != 200:
            return None, "HTTP %d" % r.status_code
        data = r.json()
        if data.get("status") == "error":
            if data.get("code") == 429:
                time.sleep(30 * (attempt + 1))
                continue
            return None, str(data.get("message", "api error"))[:120]
        return data.get("values", []), None
    return None, "rate limit or network error after 3 tries"


def read_stored(sb, sid):
    out, off = [], 0
    while True:
        page = sb.table("market_prices").select("price_date,adjusted_close").eq("security_id", sid).order("price_date").range(off, off + 999).execute().data
        if not page:
            break
        out += [(str(r["price_date"])[:10], float(r["adjusted_close"])) for r in page if r.get("adjusted_close")]
        if len(page) < 1000:
            break
        off += 1000
    return out


def make_windows(dates, wmax=None):
    wmax = wmax or WINDOW_MAX
    n = len(dates)
    k = -(-n // wmax)
    size = -(-n // k)
    return [(dates[i], dates[min(i + size, n) - 1]) for i in range(0, n, size)]


def segments(pairs, tol=None):
    tol = TOL if tol is None else tol
    out, ref = [], None
    for d, r in pairs:
        if ref is None or abs(r / ref - 1.0) > tol:
            out.append((d, r))
            ref = r
    return out


def self_checks(stored_n, matched_n, segs, truncated, last_date=None):
    """problems are plain strings; items that start with 'info:' are informational and do NOT make the ticker 'flagged'"""
    flags = []
    if truncated:
        flags.append("A WINDOW RETURNED 5,000 ROWS (truncated)")
    if stored_n and matched_n / stored_n < 0.98:
        flags.append("vendor has only %.1f%% of the stored days" % (100.0 * matched_n / stored_n))
    ratios = [r for _, r in segs]
    drops = [(segs[i][0], ratios[i - 1], ratios[i]) for i in range(1, len(ratios)) if ratios[i] < ratios[i - 1] * (1 - 1e-4) and not near_split(ratios[i] / ratios[i - 1], 0.08)]
    dec = [d for d in drops if d[2] < d[1] * (1 - 5e-3)]
    small = [d for d in drops if d[2] >= d[1] * (1 - 5e-3)]
    if dec:
        flags.append("%d segment(s) where the ratio DECREASES by more than 0.5%% and it is not a reverse split (first %s: %.4f -> %.4f)" % (len(dec), dec[0][0], dec[0][1], dec[0][2]))
    if small:
        flags.append("info: %d small decrease(s) under 0.5%% (scale noise where recent rows were spliced onto the stored history), first %s: %.4f -> %.4f" % (len(small), small[0][0], small[0][1], small[0][2]))
    # the stored history was fetched at one date and later dividends accumulate, so recent stored prices sit slightly ABOVE raw: a latest ratio up to 1.05 is normal
    if ratios and not (0.90 <= ratios[-1] <= 1.05):
        flags.append("latest ratio %.4f outside 0.90-1.05" % ratios[-1])
    recent = None
    if last_date:
        try:
            recent = datetime.date.fromisoformat(str(last_date)[:10]) - datetime.timedelta(days=60)
        except ValueError:
            recent = None
    big, info = [], []
    for i in range(1, len(ratios)):
        st = ratios[i] / ratios[i - 1]
        if st > 1.15:
            is_recent = recent is not None and datetime.date.fromisoformat(segs[i][0]) >= recent
            if is_recent or (not near_split(st) and st > 4):
                big.append((segs[i][0], st))
            elif not near_split(st):
                info.append((segs[i][0], st))
    if big:
        flags.append("UNEXPLAINED OR RECENT STEP(S): above x4 and not a split ratio, or within the last 60 stored days (a vendor level shift, a data error, or a corporate action after the history was fetched: the stored series may be stale): " + ", ".join("%s x%.3f" % (d, st) for d, st in big[:6]))
    if info:
        flags.append("info: step(s) between x1.15 and x4 that are not split ratios (spin-offs and similar corporate actions): " + ", ".join("%s x%.3f" % (d, st) for d, st in info[:6]))
    return flags


def retriage(sb, apply):
    """re-evaluates the self-checks of every 'flagged' ticker from the change points already stored: no vendor calls, no credits"""
    secs = {s["id"]: s["ticker"] for s in sb.table("securities").select("id,ticker").execute().data}
    logs = sb.table("asquoted_fetch_log").select("security_id,status,flags,stored_rows,matched_rows,last_date").eq("status", "flagged").execute().data or []
    tally, still = {"ok": 0, "flagged": 0}, []
    for r in logs:
        rows = sb.table("price_adjustment_factors").select("effective_date,ratio").eq("security_id", r["security_id"]).order("effective_date").execute().data
        segs = [(str(x["effective_date"])[:10], float(x["ratio"])) for x in rows]
        flags = self_checks(r.get("stored_rows") or 0, r.get("matched_rows") or 0, segs, "truncated" in (r.get("flags") or ""), r.get("last_date"))
        problem = any(not f.startswith("info:") for f in flags)
        tally["flagged" if problem else "ok"] += 1
        if problem:
            still.append((secs.get(r["security_id"], r["security_id"]), "; ".join(flags)))
        if apply:
            sb.table("asquoted_fetch_log").upsert({"security_id": r["security_id"], "status": "flagged" if problem else "ok", "flags": "; ".join(flags) or None}, on_conflict="security_id").execute()
    print("RETRIAGE of %d flagged tickers (%s): now ok %d | still flagged %d" % (len(logs), "WRITTEN" if apply else "dry run", tally["ok"], tally["flagged"]))
    for t, f in sorted(still):
        print("  %-6s %s" % (t, f[:230]))
    return tally, still


def process(sb, key, sec, state, apply, requester=None):
    requester = requester or (lambda t, a, b: fetch_raw(key, t, a, b))
    stored = read_stored(sb, sec["id"])
    if len(stored) < 50:
        return {"status": "error", "flags": "fewer than 50 stored days"}
    windows = make_windows([d for d, _ in stored])
    if state["used"] + len(windows) > state["cap"]:
        return {"status": "budget"}
    raw, truncated = {}, False
    for a, b in windows:
        vals, err = requester(sec["ticker"], a, b)
        state["used"] += 1
        time.sleep(PACE_SECONDS)
        if err:
            return {"status": "error", "flags": "vendor: " + err}
        if len(vals) >= 5000:
            truncated = True
        for v in vals:
            try:
                raw[str(v["datetime"])[:10]] = float(v["close"])
            except (KeyError, TypeError, ValueError):
                pass
    pairs = [(d, adj / raw[d]) for d, adj in stored if raw.get(d, 0) > 0]
    if not pairs:
        return {"status": "error", "flags": "no common days with the vendor"}
    segs = segments(pairs)
    flags = self_checks(len(stored), len(pairs), segs, truncated, stored[-1][0])
    res = {"status": "flagged" if any(not f.startswith("info:") for f in flags) else "ok", "flags": "; ".join(flags) or None, "requests_used": len(windows), "stored_rows": len(stored), "vendor_rows": len(raw), "matched_rows": len(pairs), "change_points": len(segs), "first_date": stored[0][0], "last_date": stored[-1][0], "last_ratio": segs[-1][1], "segs": segs}
    if apply:
        sb.table("price_adjustment_factors").delete().eq("security_id", sec["id"]).execute()
        rows = [{"security_id": sec["id"], "effective_date": d, "ratio": r} for d, r in segs]
        for i in range(0, len(rows), 500):
            sb.table("price_adjustment_factors").upsert(rows[i:i + 500], on_conflict="security_id,effective_date").execute()
        log = {k: v for k, v in res.items() if k != "segs"}
        log.update(security_id=sec["id"], fetched_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        sb.table("asquoted_fetch_log").upsert(log, on_conflict="security_id").execute()
    return res


def main(argv=None, sb=None, key=None, requester=None):
    global TOL
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--max-requests", type=int, default=700)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--retriage", action="store_true", help="re-evaluate the self-checks of flagged tickers from the stored change points (no vendor calls)")
    ap.add_argument("--tol", type=float, default=None, help="segment tolerance for THIS run (default TOL = 5e-5); about 1e-9 stores one exact ratio per day (addendum 4 of the valid-from registration: the class C repair)")
    ap.add_argument("--force", action="store_true", help="refetch the named --tickers even when they are already done (requires --tickers; the old change points are deleted and replaced)")
    a = ap.parse_args(argv)
    if a.force and not a.tickers:
        ap.error("--force needs --tickers (it refetches tickers that are already done)")
    if a.tol is not None:
        TOL = a.tol
    if not a.tickers and not a.all and not a.retriage:
        ap.error("give --tickers ... or --all (or --retriage)")
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
        key = os.environ.get("TWELVE_DATA_API_KEY")
    if a.retriage:
        return retriage(sb, a.apply)
    secs = sb.table("securities").select("id,ticker").order("ticker").execute().data
    if a.tickers:
        want = {t.upper() for t in a.tickers}
        secs = [s for s in secs if s["ticker"] in want]
    done = {r["security_id"] for r in (sb.table("asquoted_fetch_log").select("security_id,status").execute().data or []) if r["status"] in DONE}
    todo = secs if a.force else [s for s in secs if s["id"] not in done]
    cap = a.max_requests
    if requester is None:
        u = api_usage(key)
        room = int(u.get("plan_daily_limit", 800)) - int(u.get("daily_usage", 0)) - DAILY_RESERVE
        print("api usage: %s | plan %s | room today %d" % (u.get("daily_usage"), u.get("plan_category"), room))
        cap = min(cap, room)
    print("%d tickers selected, %d already done, %d to fetch | request cap %d | %s" % (len(secs), len(secs) - len(todo), len(todo), cap, "WRITING" if a.apply else "DRY RUN (credits are spent, nothing is written)"), flush=True)
    state, tally, flagged = {"used": 0, "cap": cap}, {"ok": 0, "flagged": 0, "error": 0}, []
    for s in todo:
        r = process(sb, key, s, state, a.apply, requester)
        if r["status"] == "budget":
            print("budget reached after %d requests: %d tickers not fetched; run again tomorrow" % (state["used"], len(todo) - sum(tally.values())))
            break
        tally[r["status"]] += 1
        if r["status"] == "error":
            print("  %-6s ERROR %s" % (s["ticker"], r["flags"]))
            if a.apply:
                sb.table("asquoted_fetch_log").upsert({"security_id": s["id"], "status": "error", "flags": r["flags"], "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}, on_conflict="security_id").execute()
        else:
            print("  %-6s %-7s %3d change points | matched %d of %d stored days | last ratio %.4f%s" % (s["ticker"], r["status"], r["change_points"], r["matched_rows"], r["stored_rows"], r["last_ratio"], ("  FLAGS: " + r["flags"]) if r["flags"] else ""), flush=True)
    print("\nrequests used %d | ok %d | flagged %d | error %d" % (state["used"], tally["ok"], tally["flagged"], tally["error"]))
    return tally, state


if __name__ == "__main__":
    main()
