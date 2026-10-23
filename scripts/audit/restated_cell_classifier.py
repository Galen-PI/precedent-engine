#!/usr/bin/env python3
"""
restated_cell_classifier.py -- READ-ONLY. For STORED ANNUAL statement rows whose value differs from what the (fixed) parser computes, says WHY, so that a point-in-time repair touches only the cells that are real recasts. Writes nothing.
WHY. The dry runs list hundreds of 'restated' cells, but the parser pools facts from several candidate concepts (by design for revenue: era handoffs; for equity: with and without noncontrolling interest) and takes the earliest-filed fact, so a difference can be (a) a later RECAST of the same figure, (b) a different DEFINITION (another concept), (c) a value no SEC fact carries (older code, rounding, a patch).
Only (a) is a repair candidate. Quarterly Q4 rows copy their annual row (the same period_end), so annual rows are enough.
CLASSES, for each differing cell (computed = the parser's earliest-filed fact; stored = the database value):
  RECAST          the stored value equals a LATER-filed 10-K fact of the SAME concept the computed fact comes from (the stored row holds a later comparative or recast figure; computed is the original)
  CONCEPT_SWITCH  the stored value equals a fact of a DIFFERENT concept (a definition difference: gross vs net sales, equity with vs without noncontrolling interest): NOT a recast, do not repair
  DERIVED         (total_liabilities) the stored value equals the stored assets minus the stored equity (the accounting-identity derivation), no liabilities fact matches
  NO_MATCH        the stored value equals no 10-K fact for that period (older logic, rounding, manual patch)
  LATER_COMPARATIVE (filed_date) the stored date equals the filed date of a LATER 10-K fact for that period; NO_MATCH otherwise
Usage:   python3 scripts/audit/restated_cell_classifier.py AAPL ACGL ATO BF-B        (explicit tickers)
         python3 scripts/audit/restated_cell_classifier.py --all                      (every ticker in CIK_TO_TICKER except SPY; about 8-10 minutes of SEC calls; save the output with > file)
Run with PYTHONHASHSEED=0 like the other statements tools; needs SUPABASE_URL and SUPABASE_KEY.
"""
import os, sys, time, io, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import statements_refresh_dryrun as dr

INSTANT = ["total_assets", "total_liabilities", "total_equity", "cash_and_equivalents"]
FLOW = ["revenue"]
TOL = 0.5


def eq(a, b):
    if a is None or b is None:
        return False
    try:
        return abs(float(a) - float(b)) <= TOL
    except (TypeError, ValueError):
        return False


def tagged_facts(m, data, field, end):
    """every 10-K fact for the field at that period end, tagged with its candidate-concept index and name"""
    us = data.get("facts", {}).get("us-gaap", {})
    out = []
    for idx, name in enumerate(m.CONCEPTS[field]):
        cd = us.get(name)
        if not cd:
            continue
        for f in m.get_usd_facts(cd):
            if f.get("end") != end:
                continue
            ok = m.is_annual_duration_fact(f) if field in FLOW else f.get("form") == "10-K"
            if ok:
                out.append({"idx": idx, "name": name, "val": f.get("val"), "filed": f.get("filed") or "9999-99-99", "accn": f.get("accn") or ""})
    return out


def classify_cell(m, data, field, end, stored, computed, stored_row):
    facts = tagged_facts(m, data, field, end)
    comp = [f for f in facts if eq(f["val"], computed)]
    comp = min(comp, key=lambda f: (f["filed"], f["accn"])) if comp else None
    hits = [f for f in facts if eq(f["val"], stored)]
    if not hits:
        if field == "total_liabilities" and eq(stored, (stored_row.get("total_assets") or 0) - (stored_row.get("total_equity") or 0)):
            return "DERIVED", None, None
        return "NO_MATCH", None, comp
    if comp is not None and any(h["idx"] == comp["idx"] and (h["filed"], h["accn"]) > (comp["filed"], comp["accn"]) for h in hits):
        return "RECAST", min(hits, key=lambda h: (h["filed"], h["accn"])), comp
    if comp is None or any(h["idx"] != comp["idx"] for h in hits):
        return "CONCEPT_SWITCH", hits[0], comp
    return "NO_MATCH", hits[0], comp


def classify_filed(m, data, end, stored, computed):
    later = set()
    us = data.get("facts", {}).get("us-gaap", {})
    for fld in ("revenue", "operating_income", "net_income"):
        for name in m.CONCEPTS[fld]:
            for f in m.get_usd_facts(us.get(name)):
                if f.get("end") == end and m.is_annual_duration_fact(f) and f.get("filed"):
                    later.add(f["filed"])
    return ("LATER_COMPARATIVE" if (str(stored)[:10] in later and str(stored)[:10] > str(computed)[:10]) else "NO_MATCH")


def run_ticker(m, sb, ticker, cik, tally, examples):
    with contextlib.redirect_stdout(io.StringIO()):
        data = m.get_sec_company_facts(str(cik))
        cmap = m.build_concept_map(data)
        annual = m.build_annual_periods(data, cmap)
    sec = sb.table("securities").select("id,ticker").eq("ticker", ticker).limit(1).execute().data
    if not sec:
        return 0
    cols = ",".join(["period_type", "period_end", "filed_date"] + FLOW + INSTANT)
    rows = sb.table("financial_statements").select(cols).eq("security_id", sec[0]["id"]).eq("period_type", "annual").range(0, 999).execute().data or []
    comp = {str(a["period_end"])[:10]: a for a in annual}
    n = 0
    for r in rows:
        end = str(r["period_end"])[:10]
        c = comp.get(end)
        if not c:
            continue
        for field in FLOW + INSTANT:
            s_, c_ = r.get(field), c.get(field)
            if s_ is None or c_ is None or eq(s_, c_):
                continue
            cls, hit, cf = classify_cell(m, data, field, end, s_, c_, r)
            tally[(field, cls)] = tally.get((field, cls), 0) + 1
            n += 1
            ex = examples.setdefault((field, cls), [])
            if len(ex) < 3:
                ex.append("%s %s: stored %s -> computed %s%s" % (ticker, end, s_, c_, (" [stored = %s filed %s; computed = %s filed %s]" % (hit["name"], hit["filed"], cf["name"], cf["filed"])) if hit and cf else ""))
        sf, cfd = r.get("filed_date"), c.get("filed_date")
        if sf and cfd and str(sf)[:10] != str(cfd)[:10]:
            cls = classify_filed(m, data, end, sf, cfd)
            tally[("filed_date", cls)] = tally.get(("filed_date", cls), 0) + 1
            n += 1
            ex = examples.setdefault(("filed_date", cls), [])
            if len(ex) < 3:
                ex.append("%s %s: stored %s -> computed %s" % (ticker, end, str(sf)[:10], str(cfd)[:10]))
    return n


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    m = dr.load_module()
    sb = dr.get_client()
    cik_of = {v: k for k, v in m.CIK_TO_TICKER.items()}
    jobs = [(t, c) for t, c in sorted(cik_of.items()) if t != "SPY"] if "--all" in args else [(a.upper(), cik_of[a.upper()]) for a in args if a.upper() in cik_of]
    tally, examples, tot = {}, {}, 0
    for i, (t, c) in enumerate(jobs, 1):
        try:
            tot += run_ticker(m, sb, t, c, tally, examples)
        except Exception as e:
            print("=== %s: ERROR %s: %s" % (t, type(e).__name__, str(e)[:120]))
        time.sleep(getattr(dr, "PAUSE", 1.0))
        if i % 100 == 0:
            print("  %d / %d tickers" % (i, len(jobs)), flush=True)
    print("\nDIFFERING ANNUAL CELLS by field and class (%d tickers, %d cells)" % (len(jobs), tot))
    for field in FLOW + INSTANT + ["filed_date"]:
        cells = {k[1]: v for k, v in tally.items() if k[0] == field}
        if not cells:
            continue
        print("  %-22s " % field + " | ".join("%s %d" % (k, v) for k, v in sorted(cells.items(), key=lambda kv: -kv[1])))
        for cls in sorted(cells, key=lambda k: -cells[k]):
            for ex in examples.get((field, cls), []):
                print("        %-18s %s" % (cls, ex))
    print("\nREPAIR CANDIDATES (RECAST + LATER_COMPARATIVE): %d of %d differing cells" % (sum(v for k, v in tally.items() if k[1] in ("RECAST", "LATER_COMPARATIVE")), tot))
    return tally


if __name__ == "__main__":
    main()
