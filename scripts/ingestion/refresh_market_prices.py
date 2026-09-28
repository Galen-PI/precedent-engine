"""
refresh_market_prices.py

Forward-refreshes market_prices from each ticker's last stored date. No incremental
updater existed (ingest_market_prices.py is a manual one-ticker tool, and
bulk_ingest_prices.py only loads tickers with zero rows), which is why prices stopped
in mid/late August.

Overlap check: prices are fetched with adjust=all, so every stored row is adjusted as of
the day it was fetched. A dividend or split with an ex-date after that fetch makes older
stored rows disagree with newly fetched ones. So each ticker is fetched from a few days
BEFORE its last stored date, the overlapping days are compared with what is stored, and
new days are appended only when they agree. Tickers that disagree are reported as
'restated' and NOT written; they need a full-history refetch, decided separately.

Dry run unless --apply. Only appends rows dated after the last stored date and before
today. Never modifies existing rows. Row mapping copies upsert_prices() in
ingest_market_prices.py.

Usage:
    python refresh_market_prices.py --tickers AAPL MSFT SPY
    python refresh_market_prices.py --all --max-requests 200
    python refresh_market_prices.py --tickers AAPL --apply
"""
import argparse, csv, os, sys, time
from collections import Counter
from datetime import date, datetime, timedelta, timezone
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
API_KEY = os.environ["TWELVE_DATA_API_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
PACE_SECONDS = 8.0  # plan limit is 8 requests per minute


def api_usage():
    return requests.get("https://api.twelvedata.com/api_usage",
                        params={"apikey": API_KEY}, timeout=30).json()


def fetch(ticker, start, end):
    for attempt in range(3):
        try:
            r = requests.get("https://api.twelvedata.com/time_series", timeout=60, params={
                "symbol": ticker, "interval": "1day", "start_date": start, "end_date": end,
                "adjust": "all", "outputsize": 5000, "apikey": API_KEY})
        except requests.RequestException:
            time.sleep(10)
            continue
        if r.status_code == 429:
            time.sleep(30 * (attempt + 1))
            continue
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        data = r.json()
        if data.get("status") == "error":
            if data.get("code") == 429:
                time.sleep(30 * (attempt + 1))
                continue
            return None, str(data.get("message", "api error"))[:120]
        return data.get("values", []), None
    return None, "rate limit or network error after 3 tries"


def build_rows(security_id, values):
    by_date = {}
    for v in values:
        by_date[v["datetime"]] = v  # last entry wins, as in ingest_market_prices.py
    rows = []
    for v in by_date.values():
        close = float(v["close"])
        adj = v.get("adjusted_close")
        rows.append({
            "security_id": security_id, "price_date": v["datetime"],
            "open": float(v["open"]), "high": float(v["high"]), "low": float(v["low"]),
            "close": close, "adjusted_close": float(adj) if adj is not None else close,
            "volume": int(v["volume"]),
        })
    return rows


def load_securities(tickers=None):
    out, offset = {}, 0
    while True:
        q = supabase.table("securities").select("ticker,id")
        if tickers:
            q = q.in_("ticker", tickers)
        page = q.order("ticker").range(offset, offset + 999).execute().data
        if not page:
            break
        for r in page:
            out[r["ticker"]] = r["id"]
        if len(page) < 1000:
            break
        offset += 1000
    return out


def last_stored(sid):
    r = (supabase.table("market_prices").select("price_date").eq("security_id", sid)
         .order("price_date", desc=True).limit(1).execute().data)
    return str(r[0]["price_date"])[:10] if r else None


def stored_window(sid, start, end):
    out, offset = {}, 0
    while True:
        page = (supabase.table("market_prices").select("price_date,adjusted_close")
                .eq("security_id", sid).gte("price_date", start).lte("price_date", end)
                .order("price_date").range(offset, offset + 999).execute().data)
        if not page:
            break
        for r in page:
            out[str(r["price_date"])[:10]] = r["adjusted_close"]
        if len(page) < 1000:
            break
        offset += 1000
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="+")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--overlap-days", type=int, default=10)
    ap.add_argument("--tolerance", type=float, default=0.001)
    ap.add_argument("--max-requests", type=int, default=25)
    args = ap.parse_args()
    if not args.tickers and not args.all:
        sys.exit("Give --tickers or --all")

    usage = api_usage()
    print("Twelve Data usage:", usage)
    if "plan_daily_limit" not in usage:
        sys.exit("Could not read plan limits; stopping before spending credits.")
    remaining = usage["plan_daily_limit"] - usage.get("daily_usage", 0)
    print(f"Credits left today: {remaining}; this run is capped at {args.max_requests} requests.")
    if args.max_requests > remaining - 5:
        sys.exit("--max-requests would leave too little of today's credits. Lower it.")

    wanted = [t.upper() for t in args.tickers] if args.tickers else None
    secs = load_securities(wanted)
    tickers = wanted if wanted else sorted(secs)
    today = datetime.now(timezone.utc).date()
    fresh_cutoff = (today - timedelta(days=3)).isoformat()

    results, made = [], 0
    for t in tickers:
        res = {"ticker": t, "status": "", "last_stored": "", "new_rows": 0,
               "common_days": 0, "max_dev": "", "note": ""}
        results.append(res)
        sid = secs.get(t)
        if not sid:
            res["status"] = "no_security"
            continue
        last = last_stored(sid)
        if last is None:
            res["status"], res["note"] = "no_history", "use bulk_ingest_prices.py"
            continue
        res["last_stored"] = last
        if args.all and last >= fresh_cutoff:
            res["status"] = "fresh"
            continue
        if made >= args.max_requests:
            res["status"] = "not_attempted"
            continue

        start = (date.fromisoformat(last) - timedelta(days=args.overlap_days)).isoformat()
        values, err = fetch(t, start, today.isoformat())
        made += 1
        time.sleep(PACE_SECONDS)
        if values is None:
            res["status"], res["note"] = "api_error", err
            print(f"{t:6s} api_error: {err}")
            continue

        fresh = {r["price_date"]: r for r in build_rows(sid, values)}
        stored = stored_window(sid, start, last)
        common = [d for d in stored if d in fresh and stored[d]]
        res["common_days"] = len(common)
        new_rows = [r for d, r in fresh.items() if last < d < today.isoformat()]
        res["new_rows"] = len(new_rows)
        if len(common) < 3:
            res["status"] = "cannot_verify"
            print(f"{t:6s} last={last} overlap_days={len(common)} -> cannot_verify")
            continue
        maxdev = max(abs(fresh[d]["adjusted_close"] / stored[d] - 1) for d in common)
        res["max_dev"] = f"{maxdev:.6f}"
        res["status"] = "ok" if maxdev <= args.tolerance else "restated"
        print(f"{t:6s} last={last} new={len(new_rows)} overlap_days={len(common)} "
              f"max_dev={maxdev:.5f} -> {res['status']}")
        if res["status"] == "ok" and new_rows and args.apply:
            for i in range(0, len(new_rows), 500):
                supabase.table("market_prices").upsert(
                    new_rows[i:i + 500], on_conflict="security_id,price_date").execute()
            res["note"] = "written"

    print(f"\nRequests made: {made}. Status counts: {dict(Counter(r['status'] for r in results))}")
    print("APPLIED" if args.apply else "DRY RUN -- nothing written.")
    os.makedirs("output", exist_ok=True)
    out = f"output/price_refresh_{datetime.now():%Y%m%d_%H%M}.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    print(f"Per-ticker results written to {out}")


if __name__ == "__main__":
    main()
