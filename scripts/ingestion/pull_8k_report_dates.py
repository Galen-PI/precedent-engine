#!/usr/bin/env python3
"""
pull_8k_report_dates.py -- READS the SEC submissions feed (one request per company, plus its older-history files), WRITES a local CSV, and only with
--apply loads that CSV into the NEW table sec_8k_report_dates. It never touches sec_8k_filings.

WHY. import_8k_filings.py keeps filingDate and items but not reportDate (the date of the earliest event reported) or acceptanceDateTime (when EDGAR accepted
the filing), although both are in the same response. An 8-K may be filed up to four business days after its event and our event date is the filing date, so
the lag (filing date minus report date) has never been measured.

Usage:
  python3 -u scripts/ingestion/pull_8k_report_dates.py --only ADBE          smoke test: one company, no database
  python3 -u scripts/ingestion/pull_8k_report_dates.py                      all companies listed in import_8k_filings.py -> data_cache/8k_report_dates.csv, prints the lag distribution
  python3 -u scripts/ingestion/pull_8k_report_dates.py --from-csv --apply   load the CSV into sec_8k_report_dates (needs SUPABASE_URL and SUPABASE_KEY; the table must exist)
Flags: --out FILE  --limit N  --sleep SECONDS (default 0.2, about 5 requests a second at most)  --from-csv  --apply
Environment: SEC_USER_AGENT (default: the importer's header; SET A REAL CONTACT for a bulk run).
The company list is READ from the text of import_8k_filings.py (that file is not imported).
"""
import os, re, sys, csv, time, argparse, datetime, collections
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
IMPORTER = os.path.join(HERE, "import_8k_filings.py")
BASE = "https://data.sec.gov/submissions/"
FIELDS = ["ticker", "security_id", "cik", "accession_number", "filing_date", "report_date", "acceptance_datetime", "items"]


def load_companies(path=None):
    text = open(path or IMPORTER, encoding="utf-8").read()
    pat = re.compile(r'\{"ticker":\s*"([^"]+)",\s*"cik":\s*"(\d+)",\s*"security_id":\s*"([0-9a-fA-F-]+)"\}')
    return [{"ticker": t, "cik": c, "security_id": s} for t, c, s in pat.findall(text)]


def get_json(url, headers, sleep, tries=4):
    for k in range(tries):
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            time.sleep(sleep)
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504):
            wait = float(r.headers.get("Retry-After", 2 ** (k + 1)))
            print("  HTTP %d for ...%s, waiting %.0fs" % (r.status_code, url[-28:], wait), flush=True)
            time.sleep(wait)
            continue
        r.raise_for_status()
    raise RuntimeError("giving up on " + url)


def at(arr, i):
    return arr[i] if arr is not None and i < len(arr) and arr[i] is not None else ""


def parse_block(block, company, seen):
    rows = []
    forms = block.get("form", [])
    for i, form in enumerate(forms):
        if form != "8-K":
            continue
        acc = at(block.get("accessionNumber"), i)
        if not acc or acc in seen:
            continue
        seen.add(acc)
        rows.append({"ticker": company["ticker"], "security_id": company["security_id"], "cik": company["cik"], "accession_number": acc,
                     "filing_date": at(block.get("filingDate"), i), "report_date": at(block.get("reportDate"), i),
                     "acceptance_datetime": at(block.get("acceptanceDateTime"), i), "items": at(block.get("items"), i)})
    return rows


def fetch_company(company, headers, sleep):
    data = get_json("%sCIK%s.json" % (BASE, company["cik"]), headers, sleep)
    seen, rows = set(), []
    rows.extend(parse_block(data["filings"]["recent"], company, seen))
    for fi in data["filings"].get("files", []):
        rows.extend(parse_block(get_json(BASE + fi["name"], headers, sleep), company, seen))
    return rows


def item_group(items):
    s = items or ""
    if not s.strip():
        return "no items listed"
    if "2.02" in s:
        return "earnings (2.02)"
    rest = re.sub(r"(7\.01|8\.01|9\.01)", "", s)
    return "voluntary only (7.01, 8.01, 9.01)" if not re.search(r"\d\.\d\d", rest) else "other required items"


def lag_days(r):
    try:
        return (datetime.date.fromisoformat(r["filing_date"]) - datetime.date.fromisoformat(r["report_date"])).days
    except (ValueError, KeyError):
        return None


def bucket(d):
    if d is None: return "report date missing"
    if d < 0: return "negative (report after filing)"
    if d <= 4: return "lag %d day%s" % (d, "" if d == 1 else "s")
    if d <= 7: return "lag 5-7 days"
    if d <= 30: return "lag 8-30 days"
    return "lag over 30 days"


ORDER = ["lag 0 days", "lag 1 day", "lag 2 days", "lag 3 days", "lag 4 days", "lag 5-7 days", "lag 8-30 days", "lag over 30 days", "negative (report after filing)", "report date missing"]


def summarize(rows):
    n = len(rows)
    print("\n8-K filings: %d | companies: %d | filing dates %s to %s" % (n, len({r["ticker"] for r in rows}), min((r["filing_date"] for r in rows if r["filing_date"]), default="-"), max((r["filing_date"] for r in rows if r["filing_date"]), default="-")))
    def table(title, subset):
        c = collections.Counter(bucket(lag_days(r)) for r in subset); m = len(subset)
        print("\n%s (n %d)" % (title, m))
        for b in ORDER:
            if c[b]: print("  %-32s %8d  %5.1f%%" % (b, c[b], 100.0 * c[b] / m))
        known = [lag_days(r) for r in subset if lag_days(r) is not None and lag_days(r) >= 0]
        if known:
            late = sum(1 for d in known if d >= 1)
            print("  share with lag of 1 day or more among filings with a report date: %.1f%% (n %d)" % (100.0 * late / len(known), len(known)))
    table("ALL", rows)
    for g in ["earnings (2.02)", "other required items", "voluntary only (7.01, 8.01, 9.01)", "no items listed"]:
        sub = [r for r in rows if item_group(r["items"]) == g]
        if sub: table("ITEM GROUP: " + g, sub)
    print("\nBY FILING YEAR: share with lag of 1 day or more among filings with a report date | share with report date missing")
    by = collections.defaultdict(list)
    for r in rows:
        if r["filing_date"]: by[r["filing_date"][:4]].append(r)
    for y in sorted(by):
        sub = by[y]; k = [lag_days(r) for r in sub if lag_days(r) is not None and lag_days(r) >= 0]
        print("  %s  n %6d | late %5.1f%% | missing %5.1f%%" % (y, len(sub), 100.0 * sum(1 for d in k if d >= 1) / max(1, len(k)), 100.0 * sum(1 for r in sub if lag_days(r) is None) / len(sub)))
    t = [r["acceptance_datetime"] for r in rows if r["acceptance_datetime"]]
    print("\nfilings with an acceptance time: %d of %d" % (len(t), n))


def apply_load(rows):
    url = os.environ["SUPABASE_URL"] + "/rest/v1/sec_8k_report_dates?on_conflict=security_id,accession_number"
    h = {"apikey": os.environ["SUPABASE_KEY"], "Authorization": "Bearer " + os.environ["SUPABASE_KEY"], "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
    payload = [{"security_id": r["security_id"], "accession_number": r["accession_number"], "filing_date": r["filing_date"] or None, "report_date": r["report_date"] or None,
                "acceptance_datetime": r["acceptance_datetime"] or None, "items": r["items"] or None} for r in rows if r["filing_date"]]
    for i in range(0, len(payload), 200):
        resp = requests.post(url, headers=h, json=payload[i:i + 200], timeout=60)
        if not resp.ok:
            print("  Supabase response (batch %d): %s" % (i // 200 + 1, resp.text[:400]))
        resp.raise_for_status()
        if (i // 200) % 50 == 0: print("  loaded %d of %d" % (min(i + 200, len(payload)), len(payload)), flush=True)
    print("loaded %d rows into sec_8k_report_dates" % len(payload))


def main():
    ap = argparse.ArgumentParser(description="Pull the report date and acceptance time of every 8-K from the SEC submissions feed.")
    ap.add_argument("--out", default=os.path.join(ROOT, "data_cache", "8k_report_dates.csv"))
    ap.add_argument("--only"); ap.add_argument("--limit", type=int); ap.add_argument("--sleep", type=float, default=0.2)
    ap.add_argument("--from-csv", action="store_true"); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if not a.from_csv:
        headers = {"User-Agent": os.environ.get("SEC_USER_AGENT", "Stock Research Project contact@example.com")}
        cos = load_companies()
        print("companies read from the importer: %d | User-Agent: %s" % (len(cos), headers["User-Agent"]), flush=True)
        if a.only: cos = [c for c in cos if c["ticker"] == a.only]
        if a.limit: cos = cos[:a.limit]
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        t0 = time.time(); total = 0
        with open(a.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
            for k, c in enumerate(cos, 1):
                try:
                    rows = fetch_company(c, headers, a.sleep)
                except Exception as e:
                    print("  FAILED %s: %s" % (c["ticker"], str(e)[:120]), flush=True); continue
                w.writerows(rows); fh.flush(); total += len(rows)
                if k % 20 == 0 or k == len(cos): print("  %d/%d companies, %d filings, %.0fs" % (k, len(cos), total, time.time() - t0), flush=True)
        print("wrote %d rows to %s" % (total, a.out))
    rows = list(csv.DictReader(open(a.out, encoding="utf-8")))
    summarize(rows)
    if a.apply:
        apply_load(rows)
    else:
        print("\n(dry: nothing was written to the database; add --from-csv --apply to load %s)" % a.out)


if __name__ == "__main__":
    main()
