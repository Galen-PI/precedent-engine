#!/usr/bin/env python3
"""
pull_long_macro.py -- long-history macro series into macro_long (and nothing else).

Daily market series: known_on = observation date (same_day).
Scheduled releases: value = FIRST-RELEASE value and known_on = first-release date from ALFRED (output_type=4) where the
archive has it ('first_release'); observations older than the archive keep today's value with known_on NULL ('month_level').
Context series (NBER recessions): known_on NULL ('hindsight') -- never a live flag.
Gold/silver daily from Alpha Vantage (history starts 2011).

Usage:
  python3 -u scripts/macro/pull_long_macro.py                       # DRY RUN: fetches everything, prints a summary, writes nothing
  python3 -u scripts/macro/pull_long_macro.py --only DGS10,PAYEMS   # dry run for named series
  python3 -u scripts/macro/pull_long_macro.py --live               # writes to macro_long (upsert, safe to rerun)
"""
import os, sys, time
from collections import Counter
import requests
from supabase import create_client

FK = os.environ["FRED_API_KEY"]
AK = os.environ.get("ALPHAVANTAGE_API_KEY")
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
FRED = "https://api.stlouisfed.org/fred/series/observations"

DAILY = ("DGS10 DGS2 DGS3MO DGS30 T10Y2Y T10Y3M DFF DFEDTAR DFEDTARU DFEDTARL DBAA DAAA "
         "DCOILWTICO DCOILBRENTEU DHHNGSP DEXUSUK DEXJPUS DEXUSEU VIXCLS").split()
RELEASES = ("CPIAUCSL CPILFESL PCEPI UNRATE PAYEMS ICSA INDPRO TCU HOUST PERMIT UMCSENT M2SL RSAFS DGORDER "
            "WPU081 WPU0811 PPIACO WPU101 CSUSHPINSA NFCI MORTGAGE30US GDPC1").split()
CONTEXT = ["USREC"]
AV = [("GOLD", "GOLD_USD_AV"), ("SILVER", "SILVER_USD_AV")]


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def fred(series_id, **extra):
    p = {"series_id": series_id, "api_key": FK, "file_type": "json"}
    p.update(extra)
    for i in range(5):
        try:
            r = requests.get(FRED, params=p, timeout=90)
        except requests.RequestException:
            time.sleep(5 * (i + 1))
            continue
        if r.status_code == 429 or r.status_code >= 500:
            print("    FRED %s -> HTTP %d, retry %d" % (series_id, r.status_code, i + 1), flush=True)
            time.sleep(20 * (i + 1) if r.status_code == 429 else 8 * (i + 1))
            continue
        if r.status_code != 200:
            print("    FRED %s -> HTTP %d %s" % (series_id, r.status_code, r.text[:120].replace("\n", " ")))
            return None
        time.sleep(0.6)
        return r.json().get("observations", [])
    return None


def row(s, d, value, latest, known_on, basis, source):
    return {"series_id": s, "obs_date": d, "value": value, "value_latest": latest, "known_on": known_on,
            "known_on_basis": basis, "source": source}


def daily_rows(s):
    obs = fred(s)
    if obs is None:
        return None
    return [row(s, o["date"], fnum(o["value"]), fnum(o["value"]), o["date"], "same_day", "FRED") for o in obs if fnum(o["value"]) is not None]


def release_rows(s):
    latest = fred(s)
    if latest is None:
        return None
    first = fred(s, realtime_start="1776-07-04", realtime_end="9999-12-31", output_type=4)
    if first is None:
        print("    %s: first-release lookup FAILED (not stored; rerun with --only %s)" % (s, s), flush=True)
        return None
    fm = {o["date"]: (o["realtime_start"], fnum(o["value"])) for o in first if fnum(o["value"]) is not None}
    out = []
    for o in latest:
        lv = fnum(o["value"])
        if lv is None:
            continue
        if o["date"] in fm:
            out.append(row(s, o["date"], fm[o["date"]][1], lv, fm[o["date"]][0], "first_release", "FRED/ALFRED"))
        else:
            out.append(row(s, o["date"], lv, lv, None, "month_level", "FRED"))
    return out


def context_rows(s):
    obs = fred(s)
    if obs is None:
        return None
    return [row(s, o["date"], fnum(o["value"]), fnum(o["value"]), None, "hindsight", "FRED") for o in obs if fnum(o["value"]) is not None]


def av_rows(symbol, sid):
    if not AK:
        print("    no ALPHAVANTAGE_API_KEY")
        return None
    j = requests.get("https://www.alphavantage.co/query", params={"function": "GOLD_SILVER_HISTORY", "symbol": symbol,
                     "interval": "daily", "apikey": AK}, timeout=90).json()
    d = j.get("data") or []
    if not d:
        print("    Alpha Vantage returned no data:", str(j)[:150])
        return None
    time.sleep(1.5)
    keyname = next((k for k in ("value", "price", "close") if k in d[0]), None) or next((k for k in d[0] if k != "date" and fnum(d[0][k]) is not None), None)
    print("    %s: using field %r; first row %s; keys %s" % (sid, keyname, d[0], list(d[0].keys())), flush=True)
    return [row(sid, x["date"], fnum(x.get(keyname)), fnum(x.get(keyname)), x["date"], "same_day", "AlphaVantage") for x in d if keyname and fnum(x.get(keyname)) is not None]


def write(rows):
    for i in range(0, len(rows), 1000):
        sb.table("macro_long").upsert(rows[i:i + 1000], on_conflict="series_id,obs_date").execute()


def main():
    args = sys.argv[1:]
    live = "--live" in args
    only = set(args[args.index("--only") + 1].split(",")) if "--only" in args else None
    plan = [(s, "daily", lambda s=s: daily_rows(s)) for s in DAILY] + \
           [(s, "release", lambda s=s: release_rows(s)) for s in RELEASES] + \
           [(s, "context", lambda s=s: context_rows(s)) for s in CONTEXT] + \
           [(sid, "alphavantage", lambda a=a, sid=sid: av_rows(a, sid)) for a, sid in AV]
    print("%s: %d series planned" % ("LIVE (writes to macro_long)" if live else "DRY RUN (writes nothing)", len(plan)), flush=True)
    total, failed = 0, []
    for s, kind, fn in plan:
        if only and s not in only:
            continue
        rows = fn()
        if not rows:
            print("%-14s %-12s FAILED or empty" % (s, kind), flush=True)
            failed.append(s)
            continue
        dates = [r["obs_date"] for r in rows]
        basis = dict(Counter(r["known_on_basis"] for r in rows))
        print("%-14s %-12s rows=%6d  %s .. %s  %s" % (s, kind, len(rows), min(dates), max(dates), basis), flush=True)
        total += len(rows)
        if live:
            write(rows)
    print("\n%s %d rows from %d series; failed or empty: %s" % ("WROTE" if live else "WOULD WRITE", total, len(plan) - len(failed), failed or "none"))


if __name__ == "__main__":
    main()
