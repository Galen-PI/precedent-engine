#!/usr/bin/env python3
"""
classify_loss_tickers.py -- applies the DECISION RULE registered in SCRIPTS.md addendum 18 to every LOSS ticker of asquoted_levels_valid_from (a LOSS ticker: valid_from later than first_eligible, or status never_valid). ONE vendor request (1 credit) per ticker: adjust=none daily closes from 60 days before to 14 days after the end of the ticker's LAST BAD WINDOW. The STRETCH = the matched days in the 42 calendar days up to and including that date (needs at least 15 matched days, else THIN).
CLASSES (tested in this order; the order is a choice made here, because B is unreachable if A comes first: every B case also has a vendor series off the grid).
  B  ours equals the vendor's (|ours/vendor - 1| < 1e-4 on at least 90% of the stretch), the vendor's OWN series is off the grid on more than 30% of the stretch (an on-grid series passes any times-k test trivially), and the SMALLEST k of {1.5, 2, 3, 4, 5, 10, 20} puts at least 97% of vendor x k on the grid: recoverable (a separate registered step would apply k).
  A  the vendor's own series is off the grid on more than 30% of the stretch and no k does it: the vendor's feed, not fixable. A seam candidate (a one-day vendor move of 15% or more inside the stretch) is flagged for a hand read.
  C  the vendor's series is on the grid on at least 95% of the stretch while ours differ from it by more than $0.002 on more than 30% of it: OUR precision.
  OTHER  none of the above (read by hand).     THIN  fewer than 15 matched days.     TRANSITION  the last bad window ends between 2001-01-01 and 2001-05-31 (no clean grid).
GRID: pre-2001 = within $0.004 of a multiple of 1/32; from 2001-06-01 = within $0.002 of a whole cent.
SAFE TO INTERRUPT: results are written every 10 tickers with --apply and a rerun skips tickers already classified (--redo recomputes); vendor rate limits wait 61 s and retry, the DAILY credit limit stops the run cleanly; pacing 8 s per request (the plan allows 8 a minute). A dry run (no --apply) STILL SPENDS credits and writes nothing.
Usage:   python3 -u scripts/ingestion/classify_loss_tickers.py [--apply] [--only T1 T2] [--limit N] [--redo] [--after 2005-01-01]   (ALWAYS give --after 2005-01-01 until the pre-2005 rule question is settled)
         scripts/ops/bg.sh lossclass python3 -u scripts/ingestion/classify_loss_tickers.py --apply
"""
import os, sys, time, argparse, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_asquoted_accuracy as C
import probe_vendor_window as P

KS = [1.5, 2, 3, 4, 5, 10, 20]
STRETCH_DAYS, FETCH_BEFORE, FETCH_AFTER, MIN_MATCHED, PACE = 42, 60, 14, 15, 8.0


def on_grid(p, era):
    return C.dgrid(p, C.GRID32) <= C.TOL16 if era == "pre" else C.dpenny(p) <= C.TOLC


def classify(rows, era):
    """rows: [(date, ours, vendor)] on the stretch, ascending -> dict"""
    n = len(rows)
    out = {"n": n, "cls": "THIN", "v_grid": None, "ours_diff": None, "same": None, "k": None, "k_share": None, "seam": False}
    if n < MIN_MATCHED:
        return out
    v_grid = sum(on_grid(v, era) for _, _, v in rows) / float(n)
    diff = sum(abs(o - v) > 0.002 for _, o, v in rows) / float(n)
    same = sum(abs(o / v - 1) < 1e-4 for _, o, v in rows) / float(n)
    shares = {k: sum(on_grid(v * k, era) for _, _, v in rows) / float(n) for k in KS}
    k_ok = next((k for k in KS if shares[k] >= 0.97), None)
    seam = any(abs(rows[i][2] / rows[i - 1][2] - 1) >= 0.15 for i in range(1, n))
    out.update(v_grid=v_grid, ours_diff=diff, same=same, seam=seam, k=k_ok, k_share=shares[k_ok] if k_ok else max(shares.values()))
    if same >= 0.9 and v_grid < 0.70 and k_ok:
        out["cls"] = "B"
    elif v_grid < 0.70:
        out["cls"] = "A"
    elif v_grid >= 0.95 and diff > 0.30:
        out["cls"] = "C"
    else:
        out["cls"] = "OTHER"
    return out


def fetch_retry(key, ticker, start, end, fetcher):
    for k in range(5):
        try:
            return fetcher(key, ticker, start, end, "none"), None
        except (SystemExit, Exception) as e:
            msg = str(e).lower()
            if "for the day" in msg:
                return None, "DAILY"
            if "minute" in msg or "credit" in msg or "limit" in msg:
                print("  vendor rate limit, waiting 61 s", flush=True); time.sleep(61); continue
            if any(t in msg for t in C.TRANSIENT):
                time.sleep(10 * (k + 1)); continue
            return None, str(e)[:120]
    return None, "retries exhausted"


def main(argv=None, sb=None, key=None, fetcher=P.fetch):
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--after", default=None, help="only LOSS tickers whose valid_from is later than this date (YYYY-MM-DD), plus every never_valid ticker")
    a = ap.parse_args(argv)
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    key = key or os.environ.get("TWELVE_DATA_API_KEY")
    vf = C.paged(sb, "asquoted_levels_valid_from", "security_id,ticker,status,valid_from,first_eligible,last_bad_window_end", "ticker", lambda q: q)
    loss = [r for r in vf if r["status"] == "never_valid" or (r["valid_from"] and r["first_eligible"] and str(r["valid_from"])[:10] > str(r["first_eligible"])[:10])]
    if a.after:
        loss = [r for r in loss if r["status"] == "never_valid" or (r["valid_from"] and str(r["valid_from"])[:10] > a.after)]
    done = set() if a.redo else {r["security_id"] for r in C.paged(sb, "asquoted_loss_classification", "security_id", "security_id", lambda q: q)}
    todo = [r for r in loss if r["security_id"] not in done and (not a.only or r["ticker"] in a.only)]
    if a.limit:
        todo = todo[:a.limit]
    print("tickers in the table %d | LOSS tickers %d | already classified %d | to classify %d | %s" % (len(vf), len(loss), len(done), len(todo), "WRITING" if a.apply else "DRY RUN (nothing written; credits ARE spent)"), flush=True)
    results, batch = [], []
    for idx, r in enumerate(todo):
        if idx % 10 == 0:
            print("PROGRESS %d/%d" % (idx, len(todo)), flush=True)
        E = str(r["last_bad_window_end"])[:10]
        res = {"cls": "TRANSITION", "n": 0, "v_grid": None, "ours_diff": None, "same": None, "k": None, "k_share": None, "seam": False}
        if "2001-01-01" <= E < "2001-06-01":
            pass
        else:
            era = "pre" if E < "2001-01-01" else "post"
            d0 = datetime.date.fromisoformat(E)
            stored = [(str(x["price_date"])[:10], float(x["adjusted_close"])) for x in C.paged(sb, "market_prices", "price_date,adjusted_close", "price_date", lambda q: q.eq("security_id", r["security_id"])) if x.get("adjusted_close")]
            fac = [(str(x["effective_date"])[:10], float(x["ratio"])) for x in C.paged(sb, "price_adjustment_factors", "effective_date,ratio", "effective_date", lambda q: q.eq("security_id", r["security_id"]))]
            ours = dict(C.asquoted(stored, fac))
            vend, err = fetch_retry(key, r["ticker"], (d0 - datetime.timedelta(days=FETCH_BEFORE)).isoformat(), (d0 + datetime.timedelta(days=FETCH_AFTER)).isoformat(), fetcher)
            time.sleep(PACE)
            if err == "DAILY":
                print("DAILY vendor credit limit reached: stopping; rerun after the reset (finished tickers are saved)", flush=True)
                break
            if vend is None:
                res = dict(res, cls="ERROR"); res["note"] = err
            else:
                lo = (d0 - datetime.timedelta(days=STRETCH_DAYS)).isoformat()
                rows = [(d, ours[d], vend[d]) for d in sorted(vend) if d in ours and lo <= d <= E and vend[d] > 0]
                res = classify(rows, era)
        results.append((r, res))
        print("  %-6s %-10s ends %s  n %3d  vendor on grid %s  ours differ %s  k %s  %s" % (r["ticker"], res["cls"], E, res["n"], "n/a" if res["v_grid"] is None else "%3.0f%%" % (100 * res["v_grid"]), "n/a" if res["ours_diff"] is None else "%3.0f%%" % (100 * res["ours_diff"]), res["k"] or "-", "SEAM? " if res["seam"] else ""), flush=True)
        batch.append({"security_id": r["security_id"], "ticker": r["ticker"], "cls": res["cls"], "last_bad_window_end": E, "valid_from": str(r["valid_from"])[:10] if r["valid_from"] else None, "n_matched": res["n"], "vendor_grid_share": res["v_grid"], "ours_diff_share": res["ours_diff"], "ours_same_share": res["same"], "best_k": res["k"], "best_k_share": res["k_share"], "seam_flag": res["seam"], "classified_at": datetime.datetime.now(datetime.timezone.utc).isoformat()})
        if a.apply and len(batch) >= 10:
            C.run_query(sb.table("asquoted_loss_classification").upsert(batch, on_conflict="security_id")); batch = []
    if a.apply and batch:
        C.run_query(sb.table("asquoted_loss_classification").upsert(batch, on_conflict="security_id"))
    print("PROGRESS %d/%d" % (len(results), len(todo)), flush=True)
    by = {}
    for r, res in results:
        by.setdefault(res["cls"], []).append(r["ticker"] + (" (k=%s)" % res["k"] if res["cls"] == "B" else ""))
    print("\nclass counts: " + ", ".join("%s %d" % (k, len(v)) for k, v in sorted(by.items())))
    for k in sorted(by):
        print("   %s: %s" % (k, ", ".join(by[k])))
    return results


if __name__ == "__main__":
    main()
