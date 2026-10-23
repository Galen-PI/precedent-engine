#!/usr/bin/env python3
"""
fetch_decision_text.py -- fetches the SOURCE TEXT the government-decision tagger will read, for the RELEVANT decisions (structured_data.relevance_verdict = relevant), into the new table government_decision_text. Reads government_decisions; writes only government_decision_text, and only with --apply (a dry run still calls the free public APIs).
WHY. The tagging input must be real text: not the title ('Addressing Risks From Susman Godfrey' cannot be sector-tagged by anyone) and not the classifier's own reasoning (circular).
SOURCES. Laws: Congress.gov v3 /bill/{congress}/{type}/{number}/summaries (CRS summaries; the version with the latest actionDate; HTML stripped); needs CONGRESS_API_KEY. Executive orders: Federal Register /api/v1/documents/{document_number}.json, then its raw_text_url (plain text), else body_html_url; the cleaned text (HTML wrapper and header boilerplate removed); abstract first when present. Stored in FULL (caps 400,000 characters for laws and 40,000 for orders, recorded in the note when hit): the tagging step, not this script, decides how much of a long text to read, because the first N characters of an omnibus bill are not representative of it.
STATUS per decision: ok | no_text (the source has no summary or text: the tagger must treat the title alone as low confidence) | error (retried on the next run). Resume-safe: decisions already ok or no_text are skipped.
Table: government_decision_text(decision_id PK, source, text_chars, body, fetched_at, status, note); see the DO block in the instructions.
Usage:   python3 -u scripts/government_decisions/fetch_decision_text.py --pilot --show-raw          3 laws + 3 orders, prints what came back, writes nothing
         python3 -u scripts/government_decisions/fetch_decision_text.py --pilot --apply             writes those 6
         python3 -u scripts/government_decisions/fetch_decision_text.py --apply                     everything relevant (about 3,000 decisions, about 25 minutes)
"""
import os, sys, re, time, html, json, argparse, datetime
import requests

CONGRESS_BASE = "https://api.congress.gov/v3"
FR_BASE = "https://www.federalregister.gov/api/v1"
PACE_CONGRESS, PACE_FR = 0.2, 0.5
MAX_CHARS_LAW, MAX_CHARS_ORDER = 400000, 40000   # storage caps only: the tagging step decides how much of a long text it reads
UA = {"User-Agent": "precedent-engine research (contact via GitHub Galen-PI)"}
DONE = ("ok", "no_text")


def strip_html(t):
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t or "")
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return " ".join(re.sub(r"[\x00-\x08\x0e-\x1b\x7f]", " ", html.unescape(t)).split())   # NUL and other control characters are removed: Postgres text cannot hold NUL


FR_NOISE = [r"Federal Register, Volume \d+ Issue \d+ \([^)]*\)", r"\[\[Page [^\]]*\]\]", r"\[Federal Register Volume[^\]]*\]", r"\[Presidential Documents\]", r"\[Pages? [^\]]*\]", r"From the Federal Register Online via the Government Publishing Office \[[^\]]*\]", r"\[FR Doc[^\]]*\]", r"\[Billing code[^\]]*\]", r"Vol\. \d+ [A-Za-z]+, No\. \d+ [A-Za-z]+ \d{1,2}, \d{4}", r"Part [IVX]+ The President", r"-{10,}", r"={10,}"]


def clean_fr(t):
    """the Federal Register 'raw text' URL returns an HTML page wrapped around a <pre> block with header boilerplate: strip the tags and the bracketed header and page markers"""
    t = strip_html(t)
    for pat in FR_NOISE:
        t = re.sub(pat, " ", t)
    return " ".join(t.split())


def http_get(url, params=None, tries=5, as_json=True):
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
        if not as_json:
            return r.text, None
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


def law_text(key, sd, raw=None):
    c, t, n = sd.get("congress"), sd.get("bill_type"), sd.get("bill_number")
    if not (c and t and n):
        return {"status": "error", "note": "missing congress / bill_type / bill_number in structured_data"}
    data, err = http_get("%s/bill/%s/%s/%s/summaries" % (CONGRESS_BASE, c, str(t).lower(), n), {"api_key": key, "format": "json"})
    time.sleep(PACE_CONGRESS)
    if err:
        return {"status": "error", "note": err}
    if raw is not None:
        raw.append(json.dumps(data)[:400])
    sums = [s for s in (data.get("summaries") or []) if strip_html(s.get("text"))]
    if not sums:
        return {"status": "no_text", "source": "congress_crs_summary", "note": "the bill has no CRS summary"}
    s = max(sums, key=lambda x: (x.get("actionDate") or "", x.get("updateDate") or ""))
    body = strip_html(s["text"])
    return {"status": "ok", "source": "congress_crs_summary", "body": body[:MAX_CHARS_LAW], "note": "version %s | %s | %s | %d summaries | %d characters" % (s.get("versionCode"), s.get("actionDesc"), s.get("actionDate"), len(sums), len(body)) + (" | TRUNCATED at %d" % MAX_CHARS_LAW if len(body) > MAX_CHARS_LAW else "")}


def order_text(sd, srcdoc, raw=None):
    doc = sd.get("document_number") or srcdoc
    if not doc:
        return {"status": "error", "note": "no Federal Register document number"}
    data, err = http_get("%s/documents/%s.json" % (FR_BASE, doc))
    time.sleep(PACE_FR)
    if err:
        return {"status": "error", "note": err}
    if raw is not None:
        raw.append(json.dumps({k: data.get(k) for k in ("title", "abstract", "raw_text_url", "body_html_url")})[:400])
    text, how = "", ""
    if data.get("raw_text_url"):
        t, e = http_get(data["raw_text_url"], as_json=False)
        time.sleep(PACE_FR)
        if not e and t and t.strip():
            text, how = clean_fr(t), "raw_text"
    if not text and data.get("body_html_url"):
        t, e = http_get(data["body_html_url"], as_json=False)
        time.sleep(PACE_FR)
        if not e and t:
            text, how = clean_fr(t), "body_html"
    abstract = strip_html(data.get("abstract") or "")
    body = (abstract + "\n\n" if abstract else "") + text
    if not body.strip():
        return {"status": "no_text", "source": "federal_register_text", "note": "no abstract and no retrievable text"}
    return {"status": "ok", "source": "federal_register_text", "body": body[:MAX_CHARS_ORDER], "note": "%s%s | %d characters%s" % (how or "abstract only", " | abstract present" if abstract else "", len(body), " | TRUNCATED at %d" % MAX_CHARS_ORDER if len(body) > MAX_CHARS_ORDER else "")}


def safe_upsert(sb, rows):
    """one bad row must not kill the run: on a failed chunk, write the rows one by one and record a failing row as an error row"""
    try:
        sb.table("government_decision_text").upsert(rows, on_conflict="decision_id").execute()
        return 0
    except Exception as e:
        bad = 0
        for r in rows:
            try:
                sb.table("government_decision_text").upsert([r], on_conflict="decision_id").execute()
            except Exception as e2:
                bad += 1
                try:
                    sb.table("government_decision_text").upsert([{"decision_id": r["decision_id"], "status": "error", "note": ("write failed: " + str(e2))[:150], "fetched_at": r["fetched_at"]}], on_conflict="decision_id").execute()
                except Exception:
                    pass
        print("  (a chunk write failed: %s; rows written one by one, %d could not be written and are marked error)" % (str(e)[:90], bad), flush=True)
        return bad


def load_decisions(sb):
    out, off = [], 0
    while True:
        page = sb.table("government_decisions").select("id,decision_type,title,source_document_number,structured_data").order("id").range(off, off + 999).execute().data
        if not page:
            break
        out += page
        if len(page) < 1000:
            break
        off += 1000
    return out


def main(argv=None, sb=None, key=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--pilot", action="store_true", help="3 laws and 3 executive orders")
    ap.add_argument("--show-raw", action="store_true")
    ap.add_argument("--type", choices=["law", "eo", "all"], default="all")
    a = ap.parse_args(argv)
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
        key = os.environ["CONGRESS_API_KEY"]
    rows = [r for r in load_decisions(sb) if r["decision_type"] in ("enacted_law", "executive_order") and sd_of(r).get("relevance_verdict") == "relevant"]
    done = {r["decision_id"] for r in (sb.table("government_decision_text").select("decision_id,status").execute().data or []) if r["status"] in DONE}
    todo = [r for r in rows if r["id"] not in done]
    if a.type != "all":
        todo = [r for r in todo if r["decision_type"] == ("enacted_law" if a.type == "law" else "executive_order")]
    if a.pilot:
        todo = [r for r in todo if r["decision_type"] == "enacted_law"][:3] + [r for r in todo if r["decision_type"] == "executive_order"][:3]
    print("relevant decisions %d | already done %d | to fetch %d | %s" % (len(rows), len(rows) - len(todo) if not a.pilot and a.type == "all" else len(done), len(todo), "WRITING" if a.apply else "DRY RUN (the public APIs are called, nothing is written)"), flush=True)
    tally, chars, out = {"ok": 0, "no_text": 0, "error": 0}, [], []
    for r in todo:
        raw = [] if a.show_raw else None
        sd = sd_of(r)
        res = law_text(key, sd, raw) if r["decision_type"] == "enacted_law" else order_text(sd, r.get("source_document_number"), raw)
        tally[res["status"]] += 1
        if res["status"] == "ok":
            chars.append(len(res["body"]))
        print("  %-14s %-8s %6s chars  %-60s %s" % (r["decision_type"], res["status"], len(res.get("body", "")) or "-", (r.get("title") or "")[:60], ("[" + res.get("note", "") + "]")[:90]), flush=True)
        if a.show_raw:
            print("      RAW: " + " || ".join(raw)[:420])
            if res.get("body"):
                print("      TEXT: " + res["body"][:300].replace("\n", " "))
        if a.apply:
            out.append({"decision_id": r["id"], "source": res.get("source"), "text_chars": len(res.get("body", "")) or None, "body": res.get("body"), "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "status": res["status"], "note": res.get("note")})
            if len(out) >= 100:
                safe_upsert(sb, out)
                out = []
    if a.apply and out:
        safe_upsert(sb, out)
    print("\nok %d | no_text %d | error %d | median text length %s" % (tally["ok"], tally["no_text"], tally["error"], int(sorted(chars)[len(chars) // 2]) if chars else "n/a"))
    return tally


if __name__ == "__main__":
    main()
