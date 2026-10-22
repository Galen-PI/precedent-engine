#!/usr/bin/env python3
"""
statements_refresh_dryrun.py -- READ-ONLY. Shows what re-running scripts/ingestion/ingest_sec_financials_multi.ingest_ticker() would change for the tickers you name, WITHOUT writing anything.
WHY. ingest_ticker() DELETES all of a security's quarterly financial_statements rows and then upserts the freshly parsed set (not atomic; the re-inserted rows get NEW ids, which financial_metrics.financial_statement_id points at). A refresh before the January forward tests should therefore be preceded by a look at its effect.
HOW. The ingestion module is imported by path (like bulk_ingest_financials.py does; no network at import); for each ticker the SAME functions are called: get_sec_company_facts, build_concept_map, build_annual_periods, build_quarterly_periods, then prepare_database_record. The result is compared with the stored rows (statement_type, period_type, period_end is the key).
REPORTS per ticker: stored vs computed rows (annual / quarterly); NEW periods (what a refresh would add); QUARTERLY periods stored but NOT recomputed (they would be deleted with no replacement); CHANGED values on existing periods, by field (fiscal_year, fiscal_quarter, filed_date, revenue, operating_income, net_income), with the first examples;
and a DANGER line when the parse returns NO quarterly rows for a security that has some (ingest_ticker would delete them all and insert none).
Usage:   python3 scripts/audit/statements_refresh_dryrun.py AAPL MSFT XOM
         python3 scripts/audit/statements_refresh_dryrun.py --sample 25            (25 tickers spread evenly across CIK_TO_TICKER, deterministic)
         python3 scripts/audit/statements_refresh_dryrun.py FOX=1754301              (a ticker that shares a CIK: TICKER=CIK, as ticker_override does)
Needs SUPABASE_URL and SUPABASE_KEY in the environment; calls SEC's companyfacts API once per ticker (1 second apart).
"""
import os, sys, time, importlib.util

INGEST_PATH = "scripts/ingestion/ingest_sec_financials_multi.py"
COMPARE = ["fiscal_year", "fiscal_quarter", "filed_date", "revenue", "operating_income", "net_income"]
PAUSE = 1.0


def load_module():
    spec = importlib.util.spec_from_file_location("ingest_sec_financials_multi", INGEST_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def get_client():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def same(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    try:
        fa, fb = float(a), float(b)
        return abs(fa - fb) <= 1e-9 * max(1.0, abs(fa), abs(fb))
    except (TypeError, ValueError):
        return str(a)[:10] == str(b)[:10]


def key(r):
    return (r.get("statement_type"), r.get("period_type"), str(r.get("period_end"))[:10])


def compare(computed, stored):
    c = {key(r): r for r in computed}
    s = {key(r): r for r in stored}
    new = sorted(k for k in c if k not in s)
    lost = sorted(k for k in s if k not in c and k[1] == "quarterly")
    stale_annual = sorted(k for k in s if k not in c and k[1] == "annual")
    changed = {f: [] for f in COMPARE}
    for k in c:
        if k in s:
            for f in COMPARE:
                if not same(c[k].get(f), s[k].get(f)):
                    changed[f].append((k, s[k].get(f), c[k].get(f)))
    return new, lost, stale_annual, changed


def ticker_job(m, sb, ticker, cik):
    data = m.get_sec_company_facts(str(cik))
    cmap = m.build_concept_map(data)
    annual = m.build_annual_periods(data, cmap)
    quarterly = m.build_quarterly_periods(data, cmap, ticker)
    computed = [m.prepare_database_record(dict(r)) for r in annual + quarterly]
    sec = sb.table("securities").select("id,ticker").eq("ticker", ticker).limit(1).execute().data
    if not sec:
        return None, "no security found for ticker %s" % ticker
    stored = sb.table("financial_statements").select("statement_type,period_type,period_end," + ",".join(COMPARE)).eq("security_id", sec[0]["id"]).range(0, 999).execute().data or []
    note = "WARNING: 1,000 stored rows returned; a second page may exist" if len(stored) == 1000 else ""
    return (computed, stored), note


def report(ticker, computed, stored):
    new, lost, stale, changed = compare(computed, stored)
    sa, sq = sum(1 for r in stored if r.get("period_type") == "annual"), sum(1 for r in stored if r.get("period_type") == "quarterly")
    ca, cq = sum(1 for r in computed if r.get("period_type") == "annual"), sum(1 for r in computed if r.get("period_type") == "quarterly")
    print("=== %s: stored %d annual + %d quarterly | computed %d annual + %d quarterly" % (ticker, sa, sq, ca, cq))
    danger = cq == 0 and sq > 0
    if danger:
        print("  DANGER: the parse returned NO quarterly rows but %d are stored: ingest_ticker would delete them all and insert none" % sq)
    print("  new periods %d%s" % (len(new), (": " + ", ".join(k[2] for k in new[-4:])) if new else ""))
    print("  quarterly periods stored but NOT recomputed (deleted, no replacement) %d%s" % (len(lost), (": " + ", ".join(k[2] for k in lost[:4])) if lost else ""))
    if stale:
        print("  annual periods stored but not recomputed (kept: annual rows are not deleted) %d" % len(stale))
    tot = sum(len(v) for v in changed.values())
    print("  changed values on existing periods: %d%s" % (tot, "" if tot == 0 else " (" + ", ".join("%s %d" % (f, len(v)) for f, v in changed.items() if v) + ")"))
    for f, v in changed.items():
        for k, old, newv in v[:2]:
            print("      %-17s %s %s: %s -> %s" % (f, k[1], k[2], old, newv))
    return dict(new=len(new), lost=len(lost), changed=tot, danger=danger)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    m = load_module()
    sb = get_client()
    cik_of = {v: k for k, v in m.CIK_TO_TICKER.items()}
    jobs = []
    if args[0] == "--sample":
        k = int(args[1]) if len(args) > 1 else 25
        tickers = sorted(cik_of)
        step = max(len(tickers) // k, 1)
        jobs = [(t, cik_of[t]) for t in tickers[::step][:k]]
    else:
        for a in args:
            if "=" in a:
                t, c = a.upper().split("=", 1)
                jobs.append((t.strip(), c.strip()))
            elif a.upper() in cik_of:
                jobs.append((a.upper(), cik_of[a.upper()]))
            else:
                print("%s is not in CIK_TO_TICKER (use TICKER=CIK for a ticker that shares a CIK)" % a)
    tot = dict(new=0, lost=0, changed=0, danger=0, n=0)
    for t, c in jobs:
        try:
            res, note = ticker_job(m, sb, t, c)
        except Exception as e:
            print("=== %s: ERROR %s: %s" % (t, type(e).__name__, str(e)[:160]))
            continue
        if res is None:
            print("=== %s: %s" % (t, note))
            continue
        if note:
            print("  " + note)
        r = report(t, *res)
        tot["n"] += 1
        for k_ in ("new", "lost", "changed"):
            tot[k_] += r[k_]
        tot["danger"] += int(r["danger"])
        time.sleep(PAUSE)
    print("\nSUMMARY over %d tickers: new periods %d | quarterly rows that would be deleted with no replacement %d | changed values %d | DANGER tickers %d" % (tot["n"], tot["new"], tot["lost"], tot["changed"], tot["danger"]))
    return tot


if __name__ == "__main__":
    main()
