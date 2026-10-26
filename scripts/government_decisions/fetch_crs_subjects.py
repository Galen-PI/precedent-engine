#!/usr/bin/env python3
"""
fetch_crs_subjects.py -- fetches Congress's human-curated SUBJECT TERMS (the CRS policy area and the legislative subject terms) for the RELEVANT enacted laws into government_decision_subjects: an independent signal for validating the tagger's themes and sectors (design step 2, results/DESIGN_government_tag_validation_v1.md). Reads government_decisions; writes only the two new tables, and only with --apply (a dry run still calls the free public API).
SOURCE. Congress.gov v3 /bill/{congress}/{type}/{number}/subjects (needs CONGRESS_API_KEY); asks for 250 terms per page and follows the pages. Each law gets one run row (status ok | none | error; error is retried next run) and one row per term (subject_type policy_area or legislative_subject).
Tables: see the DO block in the instructions. Usage:
   python3 -u scripts/government_decisions/fetch_crs_subjects.py --pilot --show-raw      3 laws, prints the raw response and what was parsed, writes nothing
   python3 -u scripts/government_decisions/fetch_crs_subjects.py --pilot --apply         writes those 3
   python3 -u scripts/government_decisions/fetch_crs_subjects.py --apply                 every relevant law (about 2,200; about 10 minutes)
"""
import os, sys, time, json, argparse, datetime
import requests

BASE = "https://api.congress.gov/v3"
PACE = 0.2
UA = {"User-Agent": "precedent-engine research (contact via GitHub Galen-PI)"}
DONE = ("ok", "none")


def http_json(url, params, tries=5):
    for k in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=60)
        except requests.RequestException:
            time.sleep(5 * (k + 1))
            continue
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(10 * (k + 1))
            continue
        if r.status_code != 200:
            return None, "HTTP %d" % r.status_code
        try:
            return r.json(), None
        except ValueError:
            return None, "response was not JSON"
    return None, "rate limit or network error after %d tries" % tries


def sd_of(row):
    sd = row.get("structured_data")
    if isinstance(sd, str):
        try:
            sd = json.loads(sd)
        except ValueError:
            return {}
    return sd if isinstance(sd, dict) else {}


def fetch_subjects(key, sd, raw=None, page=250, max_pages=40):
    c, t, n = sd.get("congress"), sd.get("bill_type"), sd.get("bill_number")
    if not (c and t and n):
        return {"status": "error", "note": "missing congress / bill_type / bill_number in structured_data"}
    url = "%s/bill/%s/%s/%s/subjects" % (BASE, c, str(t).lower(), n)
    terms, policy, offset, total = [], None, 0, None
    for _ in range(max_pages):
        data, err = http_json(url, {"api_key": key, "format": "json", "limit": page, "offset": offset})
        time.sleep(PACE)
        if err:
            return {"status": "error", "note": err}
        if raw is not None and offset == 0:
            raw.append(json.dumps(data)[:500])
        subj = data.get("subjects") or {}
        got = [x.get("name") for x in (subj.get("legislativeSubjects") or []) if x.get("name")]
        policy = policy or (subj.get("policyArea") or {}).get("name")
        terms += got
        total = (data.get("pagination") or {}).get("count", total)
        if not got or total is None or len(terms) + (1 if policy else 0) >= total:   # the API's count INCLUDES the policy area
            break
        offset += page
    out = ([("policy_area", policy)] if policy else []) + [("legislative_subject", x) for x in dict.fromkeys(terms)]
    if not out:
        return {"status": "none", "note": "the bill has no subject terms"}
    incomplete = total is not None and len(terms) + (1 if policy else 0) < total
    return {"status": "ok", "terms": out, "note": "%d legislative subjects%s" % (len(set(terms)), " (INCOMPLETE: %d of %d)" % (len(terms) + (1 if policy else 0), total) if incomplete else "")}


def paged(sb, table, cols, order, size=1000):
    out, off = [], 0
    while True:
        page = sb.table(table).select(cols).order(order).range(off, off + size - 1).execute().data
        if not page:
            break
        out += page
        if len(page) < size:
            break
        off += size
    return out


def flush(sb, runs, rows):
    """terms first, then the run rows, so a run row never exists without its terms; called every 100 laws so a stopped session loses at most 100"""
    for i in range(0, len(rows), 500):
        sb.table("government_decision_subjects").upsert(rows[i:i + 500], on_conflict="decision_id,subject_type,subject").execute()
    for i in range(0, len(runs), 500):
        sb.table("government_decision_subject_runs").upsert(runs[i:i + 500], on_conflict="decision_id").execute()


def main(argv=None, sb=None, key=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--pilot", action="store_true", help="3 laws")
    ap.add_argument("--show-raw", action="store_true")
    a = ap.parse_args(argv)
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
        key = os.environ["CONGRESS_API_KEY"]
    laws = [r for r in paged(sb, "government_decisions", "id,title,decision_type,structured_data", "id") if r["decision_type"] == "enacted_law" and sd_of(r).get("relevance_verdict") == "relevant"]
    done = {str(r["decision_id"]) for r in paged(sb, "government_decision_subject_runs", "decision_id,status", "decision_id") if r["status"] in DONE}
    todo = [r for r in laws if str(r["id"]) not in done]
    if a.pilot:
        todo = todo[:3]
    print("relevant laws %d | already done %d | to fetch %d | %s" % (len(laws), len(done), len(todo), "WRITING" if a.apply else "DRY RUN (the public API is called, nothing is written)"), flush=True)
    tally, nterms, runs, rows = {"ok": 0, "none": 0, "error": 0}, [], [], []
    for r in todo:
        raw = [] if a.show_raw else None
        res = fetch_subjects(key, sd_of(r), raw)
        tally[res["status"]] += 1
        terms = res.get("terms", [])
        nterms.append(len(terms))
        print("  %-8s %3d terms  %-60s [%s]" % (res["status"], len(terms), (r.get("title") or "")[:60], res.get("note", "")[:70]), flush=True)
        if a.show_raw:
            print("      RAW: " + " || ".join(raw)[:520])
            print("      PARSED: " + "; ".join("%s=%s" % t for t in terms[:6]))
        if a.apply:
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            runs.append({"decision_id": r["id"], "status": res["status"], "n_subjects": len(terms), "note": res.get("note"), "fetched_at": now})
            rows += [{"decision_id": r["id"], "subject_type": ty, "subject": nm, "fetched_at": now} for ty, nm in terms]
            if len(runs) >= 100:
                flush(sb, runs, rows)
                runs, rows = [], []
    if a.apply and runs:
        flush(sb, runs, rows)
    print("\nok %d | none %d | error %d | median terms per law %s" % (tally["ok"], tally["none"], tally["error"], sorted(nterms)[len(nterms) // 2] if nterms else "n/a"))
    return tally


if __name__ == "__main__":
    main()
