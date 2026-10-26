#!/usr/bin/env python3
"""
build_levels_valid_from.py -- applies, with NO new thresholds, the rule registered in results/PREREG_asquoted_levels_valid_from_2026-10-26.md: for each ticker with a finished as-quoted factor table, the date from which its as-quoted CLOSES (levels) can be trusted at the cent level.
RULE (as registered). Eligible closes: as-quoted close of at least $1, dated before 2001-01-01 (on the grid = within $0.004 of a multiple of 1/32) or from 2001-06-01 (on the grid = within $0.002 of a whole cent); 2001-01-01 to 2001-05-31 skipped. A WINDOW is 20 consecutive eligible closes; BAD if fewer than 70% (at most 13 of 20) are on the grid. valid_from = the first eligible close after the end of the LAST bad window; no bad window = valid from the first eligible close; the last bad window ending inside the final 250 eligible closes = never_valid; fewer than 20 eligible closes = unassessed.
Writes asquoted_levels_valid_from (one row per ticker) only with --apply; a rerun skips tickers already in it (--redo recomputes). A dry run recomputes everything and writes nothing.
Usage:   python3 -u scripts/ingestion/build_levels_valid_from.py [--apply] [--redo] [--show DRI GL] [--limit N]
         scripts/ops/bg.sh validfrom python3 -u scripts/ingestion/build_levels_valid_from.py --apply
"""
import os, sys, argparse, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_asquoted_accuracy as C

WIN, BAD_MAX_HITS, TAIL = 20, 13, 250


def assess(closes):
    """closes: [(date, as-quoted close)] ascending -> dict(status, valid_from, last_bad_end, n_eligible, n_bad, n_removed, first_eligible)"""
    el = []
    for d, p in closes:
        if p < 1.0:
            continue
        if d < "2001-01-01":
            el.append((d, int(C.dgrid(p, C.GRID32) <= C.TOL16)))
        elif d >= "2001-06-01":
            el.append((d, int(C.dpenny(p) <= C.TOLC)))
    n = len(el)
    base = {"n_eligible": n, "first_eligible": el[0][0] if el else None, "valid_from": None, "last_bad_end": None, "n_bad": 0, "n_removed": n}
    if n < WIN:
        return dict(base, status="unassessed")
    ps = [0]
    for _, h in el:
        ps.append(ps[-1] + h)
    last_bad, nbad = None, 0
    for i in range(WIN - 1, n):
        if ps[i + 1] - ps[i + 1 - WIN] <= BAD_MAX_HITS:
            last_bad, nbad = i, nbad + 1
    if last_bad is None:
        return dict(base, status="valid", valid_from=el[0][0], n_removed=0)
    if last_bad >= n - TAIL:
        return dict(base, status="never_valid", last_bad_end=el[last_bad][0], n_bad=nbad)
    return dict(base, status="valid", valid_from=el[last_bad + 1][0], last_bad_end=el[last_bad][0], n_bad=nbad, n_removed=last_bad + 1)


def main(argv=None, sb=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--show", nargs="*", default=[])
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args(argv)
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    ok = {r["security_id"] for r in C.paged(sb, "asquoted_fetch_log", "security_id,status", "security_id", lambda q: q.eq("status", "ok"))}
    secs = [s for s in C.paged(sb, "securities", "id,ticker", "ticker", lambda q: q) if s["id"] in ok]
    done = set() if a.redo or not a.apply else {r["security_id"] for r in C.paged(sb, "asquoted_levels_valid_from", "security_id", "security_id", lambda q: q)}
    todo = [s for s in secs if s["id"] not in done]
    if a.limit:
        todo = todo[:a.limit]
    print("tickers with a finished factor table %d | already in the table %d | to assess %d | %s" % (len(secs), len(done), len(todo), "WRITING" if a.apply else "DRY RUN (nothing written)"), flush=True)
    res, batch = {}, []
    for idx, s in enumerate(todo):
        if idx % 10 == 0:
            print("PROGRESS %d/%d" % (idx, len(todo)), flush=True)
        stored = [(str(r["price_date"])[:10], float(r["adjusted_close"])) for r in C.paged(sb, "market_prices", "price_date,adjusted_close", "price_date", lambda q: q.eq("security_id", s["id"])) if r.get("adjusted_close")]
        fac = [(str(r["effective_date"])[:10], float(r["ratio"])) for r in C.paged(sb, "price_adjustment_factors", "effective_date,ratio", "effective_date", lambda q: q.eq("security_id", s["id"]))]
        r = assess(C.asquoted(stored, fac))
        res[s["ticker"]] = r
        batch.append({"security_id": s["id"], "ticker": s["ticker"], "status": r["status"], "valid_from": r["valid_from"], "last_bad_window_end": r["last_bad_end"], "n_eligible": r["n_eligible"], "n_removed": r["n_removed"], "n_bad_windows": r["n_bad"], "first_eligible": r["first_eligible"], "assessed_at": datetime.datetime.now(datetime.timezone.utc).isoformat()})
        if a.apply and len(batch) >= 20:
            C.run_query(sb.table("asquoted_levels_valid_from").upsert(batch, on_conflict="security_id")); batch = []
    if a.apply and batch:
        C.run_query(sb.table("asquoted_levels_valid_from").upsert(batch, on_conflict="security_id"))
    print("PROGRESS %d/%d" % (len(todo), len(todo)), flush=True)
    by = {}
    for t, r in res.items():
        by.setdefault(r["status"], []).append(t)
    n_el, n_rm = sum(r["n_eligible"] for r in res.values()), sum(r["n_removed"] for r in res.values())
    late = sorted(((r["valid_from"], t) for t, r in res.items() if r["status"] == "valid" and r["valid_from"] and r["valid_from"] > "2002-01-01"), reverse=True)
    print("\nstatus counts: " + ", ".join("%s %d" % (k, len(v)) for k, v in sorted(by.items())))
    print("tickers valid only from after 2002-01-01 (a real loss of post-2001 levels): %d" % len(late))
    print("   " + ", ".join("%s %s" % (t, d) for d, t in late[:60]))
    print("after 2005-01-01: %d | never_valid: %s | unassessed: %s" % (sum(1 for d, t in late if d > "2005-01-01"), ", ".join(by.get("never_valid", [])) or "none", ", ".join(by.get("unassessed", [])) or "none"))
    print("share of all eligible closes removed by the rule: %.2f%% (%d of %d)" % (100.0 * n_rm / max(1, n_el), n_rm, n_el))
    for t in a.show:
        if t in res:
            r = res[t]
            print("%s: %s, valid from %s, last bad window ended %s, %d bad windows, %d of %d eligible closes removed" % (t, r["status"], r["valid_from"], r["last_bad_end"], r["n_bad"], r["n_removed"], r["n_eligible"]))
    return res


if __name__ == "__main__":
    main()
