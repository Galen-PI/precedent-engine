#!/usr/bin/env python3
"""
grid_profile.py TICKER [TICKER ...] [--from 1999-01-01] [--to 2002-12-31] [--by quarter|month] -- READ-ONLY, database only (NO vendor credits). For each ticker, our reconstructed as-quoted closes (closes of at least $1) grouped by period, with the share of closes on the 1/16 grid, on the 1/32 grid (both within $0.004) and on the penny grid (within $0.002). A stock that switched from fractions to decimals shows the 1/32 share collapsing and the penny share jumping on the same date; a stock whose history is off every grid shows low shares on all three. Reading aid: on a pure 1/16 series the penny share is about 20-35% (quarters, halves and some eighths are whole cents); on a pure penny series the 1/16 share is about 5-15% and the 1/32 share about 20-32%.
Usage:   python3 scripts/ingestion/grid_profile.py XOM STT KO CLX AOS AAPL --from 1999-01-01 --to 2001-12-31
"""
import os, sys, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_asquoted_accuracy as C


def period(d, by):
    return d[:7] if by == "month" else "%s-Q%d" % (d[:4], (int(d[5:7]) - 1) // 3 + 1)


def main(argv=None, sb=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("tickers", nargs="+")
    ap.add_argument("--from", dest="start", default="1999-01-01")
    ap.add_argument("--to", dest="end", default="2002-12-31")
    ap.add_argument("--by", default="quarter", choices=["quarter", "month"])
    a = ap.parse_args(argv)
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    out = {}
    for t in a.tickers:
        sec = C.paged(sb, "securities", "id,ticker", "ticker", lambda q: q.eq("ticker", t))
        if not sec:
            print("%s: ticker not found" % t); continue
        sid = sec[0]["id"]
        stored = [(str(r["price_date"])[:10], float(r["adjusted_close"])) for r in C.paged(sb, "market_prices", "price_date,adjusted_close", "price_date", lambda q: q.eq("security_id", sid)) if r.get("adjusted_close")]
        fac = [(str(r["effective_date"])[:10], float(r["ratio"])) for r in C.paged(sb, "price_adjustment_factors", "effective_date,ratio", "effective_date", lambda q: q.eq("security_id", sid))]
        cells = collections.OrderedDict()
        for d, p in C.asquoted(stored, fac):
            if p < 1.0 or not (a.start <= d <= a.end):
                continue
            v = cells.setdefault(period(d, a.by), [0, 0, 0, 0])
            v[0] += 1
            v[1] += C.dgrid(p, C.GRID16) <= C.TOL16
            v[2] += C.dgrid(p, C.GRID32) <= C.TOL16
            v[3] += C.dpenny(p) <= C.TOLC
        out[t] = cells
        print("\n%s  (period | closes | on the 1/16 grid | on the 1/32 grid | on the penny grid)" % t)
        for k, v in cells.items():
            print("   %-8s %4d   1/16 %3.0f%%   1/32 %3.0f%%   penny %3.0f%%" % (k, v[0], 100.0 * v[1] / v[0], 100.0 * v[2] / v[0], 100.0 * v[3] / v[0]))
    return out


if __name__ == "__main__":
    main()
