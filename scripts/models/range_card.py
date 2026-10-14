"""
range_card.py -- FROZEN METHOD v1_6mo_recal_2026-10-14. Do not edit the method; changes get
a new METHOD_VERSION and a new freeze date.

Calibrated range for a stock's move RELATIVE TO SPY over the next 21 trading days.
  sigma     = (stddev of the last 64 daily returns) * sqrt(20)
  k         = 80th percentile of past |abnormal 20d move| / sigma over the previous 6 months,
              lagged >= 1 month (range_k6() in the database; only already-known outcomes)
  half-width = k * sigma
The "20d" window is really close(day before event) -> close(20 trading days after the event
day) = 21 trading days of returns; k absorbs this. Not a direction forecast.

Usage: python range_card.py TICKER [--asof YYYY-MM-DD] [--event]
"""
import os
import sys
import argparse
import statistics
from datetime import date, timedelta
from supabase import create_client

METHOD_VERSION = "v1_6mo_recal_2026-10-14"
SQRT_20 = 20 ** 0.5
WINDOW = 64
MIN_RETURNS = 50
MIN_WINDOW_ROWS = 50000


def next_weekday(d):
    d = d + timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("--asof", default=None, help="use closes up to this date (YYYY-MM-DD)")
    ap.add_argument("--event", action="store_true", help="print the event-day note")
    args = ap.parse_args()

    supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    ticker = args.ticker.upper()
    sec = supabase.table("securities").select("id,ticker").eq("ticker", ticker).execute().data
    if not sec:
        print(f"No security found for ticker {ticker}")
        sys.exit(1)
    if len(sec) > 1:
        print(f"Warning: {len(sec)} securities share ticker {ticker}; using the first.")
    sec_id = sec[0]["id"]

    q = supabase.table("market_prices").select("price_date,adjusted_close").eq("security_id", sec_id)
    if args.asof:
        q = q.lte("price_date", args.asof)
    rows = q.order("price_date", desc=True).limit(WINDOW + 6).execute().data
    rows = [r for r in reversed(rows) if r["adjusted_close"] is not None]
    if len(rows) < MIN_RETURNS + 1:
        print(f"Not enough price history for {ticker} ({len(rows)} closes).")
        sys.exit(1)

    dates = [date.fromisoformat(r["price_date"][:10]) for r in rows]
    closes = [float(r["adjusted_close"]) for r in rows]
    returns = [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]
    rets = returns[-WINDOW:]
    if len(rets) < MIN_RETURNS:
        print(f"Only {len(rets)} daily returns for {ticker}; need at least {MIN_RETURNS}.")
        sys.exit(1)

    v64 = statistics.stdev(rets)
    t0, last_close = dates[-1], closes[-1]
    sigma = v64 * SQRT_20

    origin = next_weekday(t0)
    m = origin.replace(day=1)
    res = supabase.rpc("range_k6", {"m": m.isoformat()}).execute().data
    if not res or res[0].get("k") is None:
        print(f"No calibration factor for month {m} (vol_estimators has no usable history).")
        sys.exit(1)
    k, n_w = res[0]["k"], res[0]["n"]
    half = k * sigma

    print(f"RANGE CARD  [{METHOD_VERSION}]  {ticker}")
    print(f"Last close used: {t0}  (${last_close:,.2f}), {len(rets)} daily returns in the volatility window")
    if not args.asof and (date.today() - t0).days > 7:
        print(f"  WARNING: that close is {(date.today() - t0).days} days old (price data lags).")
    print(f"Recent volatility: {100 * v64:.2f}% per day  ->  {100 * sigma:.1f}% over the horizon")
    print(f"Calibration factor k = {k:.3f}  (previous-6-month 80th percentile; {n_w:,} stock-days; month {m})")
    if n_w < MIN_WINDOW_ROWS:
        print(f"  WARNING: only {n_w:,} stock-days in the calibration window (< {MIN_WINDOW_ROWS:,}); k is less reliable.")
    print()
    print(f"ABOUT 80% RANGE for the stock's return RELATIVE TO the S&P 500 (SPY),")
    print(f"over the next 21 trading days after {t0}:  +/- {100 * half:.1f}%")
    print(f"  If the market were flat, that is ${last_close * (1 - half):,.2f} to ${last_close * (1 + half):,.2f}.")
    print(f"  The market itself also moves, so the real price range is wider than this.")
    print()
    print("Backtest of this recipe (6-month recalibration), actual coverage of the 80% label:")
    print("  2023: 77.1%  2024: 78.8%  2025: 79.6%  2026 (to July): 77.1%.  One path; yearly noise is several points.")
    print("Not a direction forecast. Direction tests were null.")
    if args.event:
        print("Event day note: events move ~5% more than ordinary days at the same volatility;")
        print("  this range is NOT widened for that (measured coverage effect ~1.4 points).")


if __name__ == "__main__":
    main()
