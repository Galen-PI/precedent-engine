#!/usr/bin/env python3
"""
compare_asquoted_to_vendor.py TICKER START END -- READ-ONLY (database untouched; ONE vendor request = 1 credit). For each day: our reconstructed as-quoted close (stored adjusted close / the latest change-point ratio) next to the vendor's CURRENT adjust=none close, their ratio, and whether each is on the penny grid. Answers: does the table still reproduce what the vendor serves today, and if not, where do they part and by what factor (a factor of 2 or 10 points at a split the vendor adjusts in one place and not the other; a factor of about 1.00x points at a dividend-sized difference or a feed that changed).
Output: the RUNS of consecutive days with the same ratio (rounded to 4 decimals), the penny-grid shares of both series, the largest relative difference, and every day when the window is 40 days or shorter.
Usage:   python3 scripts/ingestion/compare_asquoted_to_vendor.py NVDA 2024-05-28 2024-06-28
"""
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_asquoted_accuracy as C
import probe_vendor_window as P


def runs_of_ratio(rows):
    out = []
    for d, ours, v in rows:
        r = round(ours / v, 4)
        if out and out[-1][2] == r:
            out[-1][1] = d; out[-1][3] += 1
        else:
            out.append([d, d, r, 1])
    return out


def main(argv=None, sb=None, key=None, fetcher=P.fetch):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3:
        raise SystemExit("usage: compare_asquoted_to_vendor.py TICKER START END")
    ticker, start, end = argv
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    key = key or os.environ.get("TWELVE_DATA_API_KEY")
    sec = C.paged(sb, "securities", "id,ticker", "ticker", lambda q: q.eq("ticker", ticker))
    if not sec:
        raise SystemExit("ticker not found: %s" % ticker)
    sid = sec[0]["id"]
    stored = [(str(r["price_date"])[:10], float(r["adjusted_close"])) for r in C.paged(sb, "market_prices", "price_date,adjusted_close", "price_date", lambda q: q.eq("security_id", sid)) if r.get("adjusted_close")]
    fac = [(str(r["effective_date"])[:10], float(r["ratio"])) for r in C.paged(sb, "price_adjustment_factors", "effective_date,ratio", "effective_date", lambda q: q.eq("security_id", sid))]
    ours = dict(C.asquoted(stored, fac))
    vend = fetcher(key, ticker, start, end, "none")
    days = sorted(d for d in vend if d in ours and start <= d <= end)
    rows = [(d, ours[d], vend[d]) for d in days]
    print("%s %s to %s: ours %d days, vendor %d days, matched %d" % (ticker, start, end, sum(1 for d in ours if start <= d <= end), len(vend), len(rows)))
    if not rows:
        return rows
    pen = lambda x: abs(x * 100 - round(x * 100)) / 100.0 <= 0.002
    print("on the penny grid: ours %d of %d, vendor %d of %d" % (sum(pen(o) for _, o, _ in rows), len(rows), sum(pen(v) for _, _, v in rows), len(rows)))
    print("largest relative difference: %.4f%% (on %s)" % (100 * max(abs(o / v - 1) for _, o, v in rows), max(rows, key=lambda r: abs(r[1] / r[2] - 1))[0]))
    print("RUNS of (ours / vendor): from | to | days | ratio")
    for a, b, r, n in runs_of_ratio(rows):
        print("   %s  %s  %3d days  %.4f" % (a, b, n, r))
    if len(rows) <= 40:
        print("DAYS: date | ours | vendor | ratio")
        for d, o, v in rows:
            print("   %s  %12.4f  %12.4f  %.4f" % (d, o, v, o / v))
    return rows


if __name__ == "__main__":
    main()
