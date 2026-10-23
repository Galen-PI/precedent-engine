#!/usr/bin/env python3
"""
ytd_differencing_check.py -- READ-ONLY. INDEPENDENT validation of the year-to-date differencing that ingest_sec_financials_multi.build_quarterly_periods uses (since 2026-10-23) for Q2/Q3 operating_cash_flow and capital_expenditures.
WHY. The differencing only FILLS NULL fields, so wherever a three-month fact exists it never runs, and the agreement of the stored values with the parse there proves nothing about it. This script runs the differencing ANYWAY on every Q2/Q3 period that also carries a reported three-month fact (70-110 days, form 10-Q) and compares the two:
  Q2:  6-month YTD - 3-month YTD   vs  the reported three-month Q2 value
  Q3:  9-month YTD - 6-month YTD   vs  the reported three-month Q3 value
(YTD facts matched on the fiscal-year start of Q1 and the quarter's period_end, earliest-filed fact, exactly as the parser does.) Classes per comparison: exact (within 1 dollar), within 0.5%, MISMATCH.
LIMIT: only companies that report both kinds of fact can be checked (a selected group), and it checks the arithmetic identity of the two reporting conventions, not every possible matching error (a wrong fiscal-year start would show up only if a three-month fact exists for that period).
Usage:   PYTHONHASHSEED=0 python3 scripts/audit/ytd_differencing_check.py AAPL MSFT       (explicit tickers)
         PYTHONHASHSEED=0 python3 scripts/audit/ytd_differencing_check.py --all > /tmp/ytd_check.log        (about 8-10 minutes of SEC calls)
"""
import os, sys, io, time, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import statements_refresh_dryrun as dr

FIELDS = ["operating_cash_flow", "capital_expenditures"]


def check_ticker(m, ticker, cik, tally, examples):
    with contextlib.redirect_stdout(io.StringIO()):
        data = m.get_sec_company_facts(str(cik))
        cmap = m.build_concept_map(data)
        cf = m.build_concept_facts(data, cmap)
        periods = m.build_quarterly_periods(data, cmap, ticker)
    by = {(p["fiscal_year"], p["fiscal_quarter"]): p for p in periods if p.get("fiscal_quarter") in (1, 2, 3) and p.get("start")}
    n_cmp = 0
    for fy in sorted({k[0] for k in by}):
        q = [by.get((fy, n)) for n in (1, 2, 3)]
        if not q[0]:
            continue
        fy_start = q[0]["start"]
        for field in FIELDS:
            ytd, three = {}, {}
            for n, per in enumerate(q, start=1):
                if not per:
                    continue
                end = per["period_end"]
                b = m.choose_earliest_fact([f for f in cf.get(field, []) if f.get("form") == "10-Q" and f.get("start") == fy_start and f.get("end") == end])
                if b is not None and b.get("val") is not None:
                    ytd[n] = b["val"]
                b3 = m.choose_earliest_fact([f for f in cf.get(field, []) if f.get("form") == "10-Q" and f.get("end") == end and f.get("start") and 70 <= (m.duration_days(f["start"], end) or 0) <= 110])
                if b3 is not None and b3.get("val") is not None:
                    three[n] = b3["val"]
            for n, hi, lo in ((2, 2, 1), (3, 3, 2)):
                if n in three and hi in ytd and lo in ytd:
                    diff, ref = ytd[hi] - ytd[lo], three[n]
                    gap = abs(diff - ref)
                    kind = "exact" if gap <= 1.0 else ("within 0.5%" if gap <= 0.005 * max(1.0, abs(ref)) else "MISMATCH")
                    key = (field, "Q%d" % n)
                    tally.setdefault(key, {"exact": 0, "within 0.5%": 0, "MISMATCH": 0})[kind] += 1
                    n_cmp += 1
                    if kind != "exact":
                        ex = examples.setdefault(key, [])
                        if len(ex) < 4:
                            ex.append("%s FY%d: YTD difference %s vs reported three-month %s (%s)" % (ticker, fy, diff, ref, kind))
    return n_cmp


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    m = dr.load_module()
    cik_of = {v: k for k, v in m.CIK_TO_TICKER.items()}
    jobs = [(t, c) for t, c in sorted(cik_of.items()) if t != "SPY"] if "--all" in args else [(a.upper(), cik_of[a.upper()]) for a in args if a.upper() in cik_of]
    tally, examples, tot = {}, {}, 0
    for i, (t, c) in enumerate(jobs, 1):
        try:
            tot += check_ticker(m, t, c, tally, examples)
        except Exception as e:
            print("=== %s: ERROR %s: %s" % (t, type(e).__name__, str(e)[:120]))
        time.sleep(getattr(dr, "PAUSE", 1.0))
        if i % 100 == 0:
            print("  %d / %d tickers" % (i, len(jobs)), flush=True)
    print("\nYTD DIFFERENCING vs REPORTED THREE-MONTH VALUES (%d tickers, %d comparisons)" % (len(jobs), tot))
    for key in sorted(tally):
        c = tally[key]
        n = sum(c.values())
        print("  %-22s %s  compared %5d | exact %5d (%.1f%%) | within 0.5%% %4d | MISMATCH %4d (%.1f%%)" % (key[0], key[1], n, c["exact"], 100.0 * c["exact"] / n, c["within 0.5%"], c["MISMATCH"], 100.0 * c["MISMATCH"] / n))
        for ex in examples.get(key, []):
            print("        " + ex)
    return tally


if __name__ == "__main__":
    main()
