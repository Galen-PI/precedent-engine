#!/usr/bin/env python3
"""
check_ingestion_lists.py -- READ-ONLY. Compares the two HARDCODED company lists the ingestion scripts depend on with the securities table:
  - import_8k_filings.COMPANIES  (ticker, cik, security_id), used by import_8k_filings.py and bulk_import_8k.py
  - ingest_sec_financials_multi.CIK_TO_TICKER  (cik -> ticker), used by the financial-statements ingestion and import_10k_10q_filings.py
The lists are read with ast (the files are NOT imported: no network, no environment side effects). Writes nothing.
WHY. A security added to the database after a list was written is silently never fetched, so a refresh before the January forward tests would be incomplete without any error.
Usage:   python3 scripts/audit/check_ingestion_lists.py      (needs SUPABASE_URL and SUPABASE_KEY in the environment, like the ingestion scripts)
"""
import ast, os, sys

EIGHTK = "scripts/ingestion/import_8k_filings.py"
MULTI = "scripts/ingestion/ingest_sec_financials_multi.py"


def literal(path, name):
    try:
        tree = ast.parse(open(path).read())
    except Exception as e:
        print("  could not read %s: %s" % (path, e))
        return None
    for node in tree.body:
        tgt = None
        if isinstance(node, ast.Assign):
            tgt = next((t.id for t in node.targets if isinstance(t, ast.Name) and t.id == name), None)
            val = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            tgt, val = name, node.value
        if tgt:
            try:
                return ast.literal_eval(val)
            except Exception as e:
                print("  %s in %s is not a plain literal (%s): cannot check it without importing the file" % (name, path, e))
                return None
    print("  %s not found in %s" % (name, path))
    return None


def get_client():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def securities(sb):
    out, off = [], 0
    while True:
        page = sb.table("securities").select("id,ticker").order("id").range(off, off + 999).execute().data
        out.extend(page)
        if len(page) < 1000:
            return out
        off += 1000


def norm_cik(c):
    try:
        return str(int(str(c))).zfill(10)
    except ValueError:
        return str(c)


def show(label, items):
    items = sorted(items)
    print("  %-62s %d%s" % (label, len(items), (": " + ", ".join(items[:40]) + (" ... (+%d more)" % (len(items) - 40) if len(items) > 40 else "")) if items else ""))


def main(eightk_path=EIGHTK, multi_path=MULTI):
    sb = get_client()
    db = securities(sb)
    db_by_t = {r["ticker"]: r["id"] for r in db}
    print("securities in the database: %d rows, %d distinct tickers" % (len(db), len(db_by_t)))
    res = {}
    print("\nimport_8k_filings.COMPANIES")
    comp = literal(eightk_path, "COMPANIES")
    if comp is not None:
        tick = [c["ticker"] for c in comp]
        dup = sorted({t for t in tick if tick.count(t) > 1})
        print("  entries %d, distinct tickers %d" % (len(comp), len(set(tick))))
        show("duplicate tickers in the list", dup)
        show("in securities but NOT in the 8-K list (never fetched)", set(db_by_t) - set(tick))
        show("in the 8-K list but NOT in securities", set(tick) - set(db_by_t))
        show("same ticker, different security_id (list vs database)", [t["ticker"] for t in comp if t["ticker"] in db_by_t and t["security_id"] != db_by_t[t["ticker"]]])
        res["8k_missing"] = sorted(set(db_by_t) - set(tick))
    print("\ningest_sec_financials_multi.CIK_TO_TICKER")
    cmap = literal(multi_path, "CIK_TO_TICKER")
    if cmap is not None:
        m = {norm_cik(k): v for k, v in cmap.items()}
        print("  entries %d, distinct tickers %d" % (len(m), len(set(m.values()))))
        show("in securities but NOT in CIK_TO_TICKER (no statements fetched)", set(db_by_t) - set(m.values()))
        show("in CIK_TO_TICKER but NOT in securities", set(m.values()) - set(db_by_t))
        res["cik_missing"] = sorted(set(db_by_t) - set(m.values()))
        if comp is not None:
            c8 = {c["ticker"]: norm_cik(c["cik"]) for c in comp}
            t2c = {v: k for k, v in m.items()}
            show("same ticker, different CIK (8-K list vs CIK_TO_TICKER)", [t for t in c8 if t in t2c and c8[t] != t2c[t]])
    return res


if __name__ == "__main__":
    main()
