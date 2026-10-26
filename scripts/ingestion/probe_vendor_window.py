#!/usr/bin/env python3
"""
probe_vendor_window.py TICKER START END -- READ-ONLY (database untouched). Two vendor requests (2 credits): the daily closes for a short window with adjust=none and with adjust=all, to see whether the 'unadjusted' series is really as-traded around a corporate action. It prints RUNS of consecutive days that are ON or OFF the penny grid (an as-traded post-2001 close must be on it), and the days around each flip with the day-over-day change and the ratio of the adjusted to the 'unadjusted' close.
Usage:   python3 scripts/ingestion/probe_vendor_window.py DRI 2015-10-01 2015-12-15
"""
import os, sys, requests

OVERRIDES = {"BRK-B": "BRK.B", "BF-B": "BF.B"}


def fetch(key, ticker, start, end, adjust):
    r = requests.get("https://api.twelvedata.com/time_series", timeout=60, params={"symbol": OVERRIDES.get(ticker, ticker), "interval": "1day", "start_date": start, "end_date": end, "adjust": adjust, "outputsize": 5000, "apikey": key})
    data = r.json()
    if data.get("status") == "error":
        raise SystemExit("vendor error: %s" % data.get("message"))
    return {v["datetime"][:10]: float(v["close"]) for v in data.get("values", [])}


def on_penny(p, tol=0.002):
    return abs(p * 100 - round(p * 100)) / 100.0 <= tol


def runs(rows):
    out = []
    for d, p, g in rows:
        if out and out[-1][2] == g:
            out[-1][1] = d
            out[-1][3] += 1
        else:
            out.append([d, d, g, 1])
    return out


def main(argv=None, key=None, fetcher=fetch):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3:
        raise SystemExit("usage: probe_vendor_window.py TICKER START END")
    ticker, start, end = argv
    key = key or os.environ["TWELVE_DATA_API_KEY"]
    raw, adj = fetcher(key, ticker, start, end, "none"), fetcher(key, ticker, start, end, "all")
    days = sorted(raw)
    rows = [(d, raw[d], on_penny(raw[d])) for d in days]
    print("%s %s to %s: %d days with adjust=none, %d with adjust=all" % (ticker, start, end, len(raw), len(adj)))
    rr = runs(rows)
    for a, b, g, n in rr:
        print("  %-10s to %-10s  %3d days  %s" % (a, b, n, "ON the penny grid (as traded)" if g else "OFF the penny grid (not an as-traded price)"))
    for i in range(1, len(rr)):
        flip = rr[i][0]
        j = days.index(flip)
        print("\nAROUND THE FLIP at %s: date | 'unadjusted' close | change from the previous day | adjusted/'unadjusted'" % flip)
        for k in range(max(1, j - 3), min(len(days), j + 3)):
            d, p0 = days[k], raw[days[k - 1]]
            print("   %s  %10.4f  %+6.2f%%   %s" % (days[k], raw[days[k]], 100.0 * (raw[days[k]] / p0 - 1), ("%.5f" % (adj[days[k]] / raw[days[k]])) if days[k] in adj else "n/a"))
    return rr


if __name__ == "__main__":
    main()
