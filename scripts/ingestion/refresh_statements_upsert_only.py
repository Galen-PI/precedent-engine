#!/usr/bin/env python3
"""
refresh_statements_upsert_only.py -- refreshes financial_statements WITHOUT deleting anything. DRY RUN unless --apply.
WHY. ingest_sec_financials_multi.ingest_ticker() deletes all of a security's quarterly rows and then upserts, which (a) is not atomic and (b) gives the re-inserted rows NEW ids, and financial_metrics.financial_statement_id references financial_statements.id with ON DELETE CASCADE, so the delete step silently erases the matching financial_metrics rows.
This script calls the SAME parsing functions (get_sec_company_facts, build_concept_map, build_annual_periods, build_quarterly_periods, prepare_database_record) and then upserts ONLY the rows that are NEW or DIFFER from the stored row in ANY column of FINANCIAL_COLUMNS. An upsert updates an existing row in place (the id is not sent), so ids and the metrics that point at them survive.
It NEVER deletes. Stored quarterly rows that the parser no longer produces are reported as STALE and left alone (review them separately). A ticker whose parse returns NO quarterly rows while quarterly rows are stored is skipped (DANGER: a parse failure).
Uses scripts/audit/statements_refresh_dryrun.py for the module loader and the key; run from the repository root.
ADDED 2026-10-22 (after the first whole-universe dry run showed 4,202 changed rows, mostly free_cash_flow, total_equity, total_assets, total_liabilities): the summary now classifies every changed CELL as FILLED (stored NULL, computed value), CLEARED (stored value, computed NULL) or RESTATED (both present and different, with examples), and --additive writes ONLY new rows and FILLS (the stored row is kept and only its NULL columns are completed): it never overwrites a stored value.
Usage:   python3 scripts/ingestion/refresh_statements_upsert_only.py AAPL SYY                dry run for these tickers
         python3 scripts/ingestion/refresh_statements_upsert_only.py --additive --all       dry run of the additive mode (add --apply to write)
         python3 scripts/ingestion/refresh_statements_upsert_only.py --all                  dry run for every ticker in CIK_TO_TICKER (about 8 minutes of SEC calls)
         python3 scripts/ingestion/refresh_statements_upsert_only.py --apply --all          write
         python3 scripts/ingestion/refresh_statements_upsert_only.py FOX=1754301 NWSA=1564708     dual-class tickers (TICKER=CIK writes that CIK's data to that ticker's own security)
ORDER IN JANUARY: (1) back up: CREATE TABLE financial_statements_backup_YYYYMMDD AS SELECT * FROM financial_statements;  same for financial_metrics;  (2) dry run --all and read it;  (3) --apply --all;  (4) python3 scripts/financial_pipeline/populate_financial_metrics.py  (recomputes metrics from all statements and upserts).
"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "audit"))
import statements_refresh_dryrun as dr

PAUSE = 1.0
SKIP_COLS = ("security_id", "source")


def same(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    try:
        fa, fb = float(a), float(b)
        return abs(fa - fb) <= 1e-9 * max(1.0, abs(fa), abs(fb))
    except (TypeError, ValueError):
        return str(a) == str(b)


def plan(m, sb, ticker, cik):
    data = m.get_sec_company_facts(str(cik))
    cmap = m.build_concept_map(data)
    annual = m.build_annual_periods(data, cmap)
    quarterly = m.build_quarterly_periods(data, cmap, ticker)
    sec = sb.table("securities").select("id,ticker").eq("ticker", ticker).limit(1).execute().data
    if not sec:
        return None
    sid = sec[0]["id"]
    cols = list(m.FINANCIAL_COLUMNS)
    computed = []
    for r in annual + quarterly:
        d = dict(r)
        d["security_id"], d["source"] = sid, "SEC"
        computed.append(m.prepare_database_record(d))
    stored = sb.table("financial_statements").select(",".join(cols)).eq("security_id", sid).range(0, 999).execute().data or []
    s = {dr.key(r): r for r in stored}
    new, changed = [], []
    for r in computed:
        k = dr.key(r)
        if k not in s:
            new.append(r)
        else:
            diff = [c for c in cols if c not in SKIP_COLS and not same(r.get(c), s[k].get(c))]
            if diff:
                changed.append((r, diff, s[k]))
    ckeys = {dr.key(r) for r in computed}
    stale = sorted(k for k in s if k not in ckeys)
    cq = sum(1 for r in computed if r.get("period_type") == "quarterly")
    sq = sum(1 for r in stored if r.get("period_type") == "quarterly")
    return dict(new=new, changed=changed, stale=stale, danger=(cq == 0 and sq > 0), stored=len(stored), computed=len(computed))


def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    additive = "--additive" in args
    args = [a for a in args if a not in ("--apply", "--additive")]
    if not args:
        print(__doc__)
        sys.exit(1)
    m = dr.load_module()
    sb = dr.get_client()
    cik_of = {v: k for k, v in m.CIK_TO_TICKER.items()}
    jobs = []
    if "--all" in args:
        jobs = [(t, c) for t, c in sorted(cik_of.items())]
        args = [a for a in args if a != "--all"]
    for a in args:
        if "=" in a:
            t, c = a.upper().split("=", 1)
            jobs.append((t.strip(), c.strip()))
        elif a.upper() in cik_of:
            jobs.append((a.upper(), cik_of[a.upper()]))
        else:
            print("%s is not in CIK_TO_TICKER (use TICKER=CIK)" % a)
    tot = dict(tickers=0, new=0, changed=0, stale=0, danger=0, written=0, errors=0, to_write=0)
    kinds, examples = {}, {}
    for t, c in jobs:
        try:
            p = plan(m, sb, t, c)
        except Exception as e:
            print("=== %s: ERROR %s: %s" % (t, type(e).__name__, str(e)[:140]))
            tot["errors"] += 1
            continue
        if p is None:
            print("=== %s: no security found" % t)
            continue
        tot["tickers"] += 1
        nw, ch, st = len(p["new"]), len(p["changed"]), len(p["stale"])
        if p["danger"]:
            tot["danger"] += 1
            print("=== %s: DANGER skipped: the parse returned no quarterly rows but quarterly rows are stored" % t)
            continue
        if nw or ch or st:
            print("=== %s: stored %d, computed %d | new %d | changed %d%s | stale (stored, not recomputed; NOT touched) %d" % (t, p["stored"], p["computed"], nw, ch, (" (" + ", ".join(sorted({f for _, d, _s in p["changed"] for f in d})) + ")") if ch else "", st))
        tot["new"] += nw
        tot["changed"] += ch
        tot["stale"] += st
        for r, d, srow in p["changed"]:
            for col in d:
                old, newv = srow.get(col), r.get(col)
                kind = "filled" if old is None else ("cleared" if newv is None else "restated")
                kinds.setdefault(col, {"filled": 0, "cleared": 0, "restated": 0})[kind] += 1
                if kind == "restated" and len(examples.setdefault(col, [])) < 3:
                    examples[col].append("%s %s %s: %s -> %s" % (t, srow.get("period_type"), str(srow.get("period_end"))[:10], old, newv))
        if additive:
            fills = []
            for r, d, srow in p["changed"]:
                fc = [c for c in d if srow.get(c) is None and r.get(c) is not None]
                if fc:
                    merged = dict(srow)
                    for c in fc:
                        merged[c] = r[c]
                    fills.append(m.prepare_database_record(merged))
            payload = p["new"] + fills
        else:
            payload = p["new"] + [r for r, _, _ in p["changed"]]
        tot["to_write"] += len(payload)
        if payload and apply:
            m.upsert_financial_records(payload)
            tot["written"] += len(payload)
        time.sleep(dr.PAUSE if hasattr(dr, "PAUSE") else PAUSE)
    if kinds:
        print("\nCHANGED CELLS by column (filled = stored NULL; cleared = computed NULL; restated = both present and different)")
        for col, k in sorted(kinds.items(), key=lambda kv: -sum(kv[1].values())):
            print("  %-22s filled %5d | cleared %5d | restated %5d" % (col, k["filled"], k["cleared"], k["restated"]))
            for ex in examples.get(col, []):
                print("        e.g. " + ex)
    print("\nSUMMARY (%s%s) over %d tickers: new rows %d | changed rows %d | rows %s %d | stale rows left alone %d | DANGER tickers skipped %d | errors %d" % ("APPLIED" if apply else "DRY RUN", " ADDITIVE: new rows and fills only" if additive else "", tot["tickers"], tot["new"], tot["changed"], "written" if apply else "that would be written", tot["to_write"], tot["stale"], tot["danger"], tot["errors"]))
    if apply:
        print("NEXT: python3 scripts/financial_pipeline/populate_financial_metrics.py")
    return tot


if __name__ == "__main__":
    main()
