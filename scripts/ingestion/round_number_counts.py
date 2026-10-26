#!/usr/bin/env python3
"""
round_number_counts.py -- OUTCOME-FREE counts for the two round-number tests (clustering of closes; behaviour near round thresholds). READ-ONLY. It computes NO returns and NO cents histogram: only how many closes and zone-days exist, by era, class and zone kind, plus a matched balance check between the round zones and their placebo neighbours.
USE RULE (results/PREREG_asquoted_levels_valid_from_2026-10-26.md, addendum 6): closes on or after 2001-06-01, only tickers with status valid in asquoted_levels_valid_from (rule_version since_2001-06-01), only from each ticker's valid_from.
DEFINITIONS (fixed before any outcome): ERA A = before 2014-01-01, ERA B = from 2014-01-01. For a day t with previous valid close P (as quoted) of at least $5: s = 10^floor(log10 P) (the ORDER OF MAGNITUDE CLASS); the ROUND threshold is k*s with k the integer nearest P/s (k = 1..10); the PLACEBO thresholds are (m + 0.27) s and (m + 0.73) s for integer m, which are the nearest NON-round neighbours of each round number: 27% of the spacing above it (kind P27) and below it (kind P73); a placebo threshold carries the index k of its nearest round number. A day is IN A ZONE when P is within 1% of the threshold, BELOW (P under it) or ABOVE (at or over it). Kinds: R_below, R_above, P27_below, P27_above, P73_below, P73_above. Why s-classes and not price buckets: a stock just below $50 and one just above would fall in different price buckets; the matched comparison (round zone k against its two placebo neighbours) keeps price level, volatility mix and era almost the same. INTERIOR thresholds are k = 2..9 (both neighbours exist inside the class); the DECADE thresholds ($10, $100, $1,000: k = 10 of one class and k = 1 of the next) have one-sided neighbours and are counted separately.
Output: closes by era and price bucket (clustering test); zone-days by era, class and kind (threshold test); the MATCHED BALANCE by k (round zone-days over the mean of the two placebo neighbours: about 1.0 if the placebo is fair); distinct tickers and ticker-years; what the use rule removed. SAFE TO INTERRUPT: each ticker's counts go to data_cache/round_counts_cache.jsonl as it finishes; a rerun resumes (--fresh ignores the cache). Transient database errors are retried.
Usage:   scripts/ops/bg.sh roundcounts python3 -u scripts/ingestion/round_number_counts.py
"""
import os, sys, math, json, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_asquoted_accuracy as C

SINCE, ERA_SPLIT, ZONE, MIN_P = "2001-06-01", "2014-01-01", 0.01, 5.0
OFFSETS = ((0.27, "P27"), (0.73, "P73"))
BUCKETS = [(1, 5), (5, 10), (10, 20), (20, 50), (50, 100), (100, 250), (250, 1000), (1000, 1e12)]
KINDS = ["R_below", "R_above", "P27_below", "P27_above", "P73_below", "P73_above"]
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data_cache", "round_counts_cache.jsonl")


def bucket(p):
    for lo, hi in BUCKETS:
        if lo <= p < hi:
            return "$%d-%s" % (lo, "up" if hi > 1e9 else "%d" % hi)
    return "?"


def era(d):
    return "A" if d < ERA_SPLIT else "B"


def sclass(P):
    return 10 ** math.floor(math.log10(P))


def zones(P):
    """the zones the previous close P falls in: a list of (kind, k); kind is R_/P27_/P73_ + below/above, k the index of the nearest round threshold"""
    out = []
    s = sclass(P)
    k = int(round(P / s))
    L = k * s
    d = (P - L) / L
    if abs(d) <= ZONE:
        out.append(("R_above" if d >= 0 else "R_below", k))
    for o, tag in OFFSETS:
        m = math.floor(P / s - o)
        for T in ((m + o) * s, (m + 1 + o) * s):
            d = (P - T) / T
            if abs(d) <= ZONE:
                out.append((tag + ("_above" if d >= 0 else "_below"), int(round(T / s))))
                break
    return out


def count_ticker(sb, sec, valid_from):
    stored = [(str(r["price_date"])[:10], float(r["adjusted_close"])) for r in C.paged(sb, "market_prices", "price_date,adjusted_close", "price_date", lambda q: q.eq("security_id", sec["id"])) if r.get("adjusted_close")]
    fac = [(str(r["effective_date"])[:10], float(r["ratio"])) for r in C.paged(sb, "price_adjustment_factors", "effective_date,ratio", "effective_date", lambda q: q.eq("security_id", sec["id"]))]
    allc = C.asquoted(stored, fac)
    start = max(SINCE, str(valid_from)[:10]) if valid_from else SINCE
    closes = [(d, p) for d, p in allc if d >= start and p >= 1.0]
    rec = {"ticker": sec["ticker"], "closes": collections.Counter(), "days": collections.Counter(), "zones": collections.Counter(), "years": {"A": [], "B": []}, "removed": sum(1 for d, p in allc if SINCE <= d < start and p >= 1.0)}
    ys = {"A": set(), "B": set()}
    for i, (d, p) in enumerate(closes):
        e = era(d)
        rec["closes"][e + "|" + bucket(p)] += 1
        ys[e].add(d[:4])
        if i == 0:
            continue
        P = closes[i - 1][1]
        if P < MIN_P:
            continue
        sc = "s%d" % sclass(P)
        rec["days"][e + "|" + sc] += 1
        for kind, k in zones(P):
            rec["zones"]["%s|%s|%d|%s" % (e, sc, k, kind)] += 1
    rec["years"] = {e: sorted(v) for e, v in ys.items()}
    return {k: (dict(v) if isinstance(v, collections.Counter) else v) for k, v in rec.items()}


def main(argv=None, sb=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true")
    a = ap.parse_args(argv)
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    vf = C.paged(sb, "asquoted_levels_valid_from", "security_id,ticker,status,valid_from,n_removed,rule_version", "ticker", lambda q: q.eq("rule_version", "since_2001-06-01"))
    usable = [r for r in vf if r["status"] == "valid"]
    secs = {s["id"]: s for s in C.paged(sb, "securities", "id,ticker", "ticker", lambda q: q)}
    cache = {}
    if not a.fresh and os.path.exists(CACHE_FILE):
        for line in open(CACHE_FILE):
            try:
                r = json.loads(line); cache[r["ticker"]] = r
            except ValueError:
                pass
    todo = [r for r in usable if r["ticker"] not in cache]
    print("table rows %d | usable (status valid) %d | not usable %d | already counted %d | to count %d" % (len(vf), len(usable), len(vf) - len(usable), len(usable) - len(todo), len(todo)), flush=True)
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "a") as fh:
        for i, r in enumerate(todo):
            if i % 10 == 0:
                print("PROGRESS %d/%d" % (i + len(usable) - len(todo), len(usable)), flush=True)
            rec = count_ticker(sb, secs[r["security_id"]], r["valid_from"])
            cache[r["ticker"]] = rec
            fh.write(json.dumps(rec) + "\n"); fh.flush()
    print("PROGRESS %d/%d" % (len(usable), len(usable)), flush=True)
    recs = [cache[r["ticker"]] for r in usable]
    tot = {"closes": collections.Counter(), "days": collections.Counter(), "zones": collections.Counter()}
    for rec in recs:
        for k in tot:
            tot[k].update(rec[k])
    names = [bucket(lo) for lo, _ in BUCKETS]
    print("\nUSABLE TICKERS %d; closes removed from them by their valid_from: %d; tickers not usable (never_valid): %s" % (len(recs), sum(r["removed"] for r in recs), ", ".join(r["ticker"] for r in vf if r["status"] != "valid") or "none"))
    classes = ["s1", "s10", "s100", "s1000", "s10000"]
    for e, label in (("A", "ERA A (2001-06 to 2013)"), ("B", "ERA B (2014 to 2026)")):
        tk = sum(1 for r in recs if r["years"][e])
        ty = sum(len(r["years"][e]) for r in recs)
        print("\n%s: tickers with closes %d, ticker-years %d, closes %d" % (label, tk, ty, sum(v for k, v in tot["closes"].items() if k.startswith(e + "|"))))
        print("   CLUSTERING TEST: closes by price bucket: " + ", ".join("%s %d" % (b, tot["closes"].get(e + "|" + b, 0)) for b in names if tot["closes"].get(e + "|" + b, 0)))
        print("   THRESHOLD TEST: zone-days by order-of-magnitude class (summed over k)")
        print("   class      days(P>=5) " + "  ".join("%9s" % k for k in KINDS))
        for sc in classes:
            d = tot["days"].get(e + "|" + sc, 0)
            if not d:
                continue
            tz = [sum(v for kk, v in tot["zones"].items() if kk.startswith("%s|%s|" % (e, sc)) and kk.endswith("|" + kind)) for kind in KINDS]
            print("   %-9s %11d  " % (sc, d) + "  ".join("%9d" % x for x in tz))
        print("   MATCHED BALANCE by interior threshold k = 2..9: round zone-days / mean of the two placebo neighbours (about 1.0 if fair); smallest round count")
        for sc in classes:
            rows = []
            for k in range(2, 10):
                z = lambda kind: tot["zones"].get("%s|%s|%d|%s" % (e, sc, k, kind), 0)
                R_ = z("R_below") + z("R_above"); N_ = (z("P27_below") + z("P27_above") + z("P73_below") + z("P73_above")) / 2.0
                if R_ or N_:
                    rows.append((k, R_, N_, R_ / N_ if N_ else float("nan")))
            if rows:
                rr = sorted(r[3] for r in rows if r[3] == r[3])
                print("   %-7s ratio min %.2f median %.2f max %.2f | smallest round count %d (k=%d) | k with fewer than 1,000 round zone-days: %s" % (sc, rr[0], rr[len(rr) // 2], rr[-1], min(rows, key=lambda r: r[1])[1], min(rows, key=lambda r: r[1])[0], ",".join(str(r[0]) for r in rows if r[1] < 1000) or "none"))
        print("   DECADE thresholds (one-sided neighbours; counted for the record): round-below at k=10 / its placebo neighbour (P73_below at k=10) | round-above at k=1 of the next class")
        for sc in classes:
            z = lambda kk, kind: tot["zones"].get("%s|%s|%d|%s" % (e, sc, kk, kind), 0)
            if z(10, "R_below") or z(1, "R_above"):
                print("   %-7s R_below(k=10) %7d vs P73_below(k=10) %7d | R_above(k=1) %7d vs P27_above(k=1) %7d" % (sc, z(10, "R_below"), z(10, "P73_below"), z(1, "R_above"), z(1, "P27_above")))
    return tot, recs


if __name__ == "__main__":
    main()
