"""
draft_missing_event_text.py

Fills missing title / description / event_type on human-confirmed real_event rows that
promote_events.py skipped. The row list comes from the promote dry-run output, so it
targets exactly what was skipped. The human confirmation stands; the model only drafts
factual text from the filing and does NOT judge materiality or duplicates
(promote_events.py's own duplicate check still runs afterward).

Two steps so what you read is what gets written:
  python draft_missing_event_text.py            # draft, print, save output/drafted_event_text.json
  python draft_missing_event_text.py --apply    # write ONLY those saved drafts, no model calls
--apply fills NULL/invalid fields only; never overwrites existing text or touches verdicts.
Option: --from <dry-run file>   (default output/promote_dryrun2.txt)
"""
import ast, json, os, re, sys, time
import requests
from classify_8k_filings_batch_v2 import supabase, fetch_filing_text, MODEL_VERSION
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ingestion"))
from import_8k_filings import COMPANIES

HEAD = {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"}
DRAFTS = "output/drafted_event_text.json"
TEXT_CHARS = 30000
PROMPT_TYPES = ["acquisition", "capital_raise", "corporate_action", "governance_action",
                "ipo_spinoff", "leadership_change", "restructuring", "strategic_partnership",
                "financial_result", "legal_settlement", "accounting_investigation",
                "cybersecurity_incident", "regulatory"]
SYSTEM = ("You write factual database entries for SEC 8-K filings that a human reviewer has "
          "already confirmed as material events. Use only facts stated in the filing text. "
          "Do not judge materiality and do not worry about duplicates. If the text does not "
          "contain enough to write a factual entry, return null for title and description.")


def correct_url(cik, acc):
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{acc}.txt"


def call_model(user):
    for attempt in range(4):
        try:
            r = requests.post("https://api.anthropic.com/v1/messages", headers=HEAD, timeout=120,
                              json={"model": MODEL_VERSION, "max_tokens": 800, "system": SYSTEM,
                                    "messages": [{"role": "user", "content": user}]})
        except requests.RequestException:
            time.sleep(3)
            continue
        if r.status_code == 200:
            return r.json()["content"][0]["text"]
        if r.status_code in (429, 500, 502, 503, 529):
            time.sleep(5 * (attempt + 1))
            continue
        print(f"    HTTP {r.status_code}: {r.text[:150]}")
        return None
    return None


def parse(raw):
    i, j = raw.find("{"), raw.rfind("}")
    if i == -1 or j == -1:
        return None
    try:
        return json.loads(raw[i:j + 1])
    except json.JSONDecodeError:
        pass
    a, b = raw.find("["), raw.rfind("]")
    if a != -1 and b != -1:
        try:
            items = json.loads(raw[a:b + 1])
            if isinstance(items, list) and items and isinstance(items[0], dict):
                if len(items) > 1:
                    print(f"    note: model returned {len(items)} items, using the first")
                return items[0]
        except json.JSONDecodeError:
            pass
    return None


def find_targets(src):
    text = open(src).read()
    groups = set()
    for m in re.finditer(r"\[SKIP - missing title/description\] (\[[^\]]*\]) (\d{4}-\d{2}-\d{2})", text):
        groups.add((tuple(ast.literal_eval(m.group(1))), m.group(2)))
    for m in re.finditer(r"\[SKIP - unknown event_type '([^']*)'\] (\[[^\]]*\]) (\d{4}-\d{2}-\d{2})", text):
        groups.add((tuple(ast.literal_eval(m.group(2))), m.group(3)))
    return sorted(groups)


def draft_one(row, cik, allowed, focus=None):
    try:
        text = fetch_filing_text(correct_url(cik, row["accession_number"]))
    except Exception as e:
        return None, f"fetch failed: {e}"
    user = (f"TICKER: {row['ticker']}\nFILING DATE: {row['filing_date']}\n"
            f"ITEM CODES: {row['item_codes']}\nFILING TEXT: {text[:TEXT_CHARS]}\n\n"
            "Respond with ONLY valid JSON, no markdown:\n"
            '{"title": "<factual, concise, with names and figures>",\n'
            ' "description": "<2-3 factual sentences>",\n'
            f' "event_type": "<one of: {", ".join(allowed)}>",\n'
            ' "basis": "<the specific sentence or figures in the filing that support this>"}')
    if focus:
        user += ("\n\nThe human reviewer confirmed this filing as a material event. Their reading: "
                 + str(focus)[:1500] + "\nDescribe THAT event (not routine earnings results).")
    raw = call_model(user)
    if raw is None:
        return None, "model call failed"
    d = parse(raw)
    if not d:
        print(f"    unparseable, raw start: {raw[:300]!r}")
        raw2 = call_model(user + "\n\nYour previous reply could not be parsed. Reply with ONLY the JSON object, starting with { and ending with }.")
        d = parse(raw2) if raw2 else None
        if not d:
            return None, "unparseable response after retry"
    title, desc, etype = ((d.get(k) or "").strip() for k in ("title", "description", "event_type"))
    if not title or not desc:
        return None, "model returned no usable title/description"
    if etype not in allowed:
        return None, f"event_type {etype!r} not in allowed list"
    return {"ticker": row["ticker"], "filing_date": str(row["filing_date"])[:10],
            "accession_number": row["accession_number"], "title": title,
            "description": desc, "event_type": etype, "basis": (d.get("basis") or "").strip()}, None


def pairs(flag):
    if flag not in sys.argv:
        return set()
    out = set()
    for tok in sys.argv[sys.argv.index(flag) + 1].split(","):
        t, d = tok.split(":")
        out.add((t.strip().upper(), d.strip()))
    return out


def main():
    valid_types = {r["name"] for r in supabase.table("event_types").select("name").execute().data}
    allowed = [t for t in PROMPT_TYPES if t in valid_types]

    if "--apply" in sys.argv:
        drafts = json.load(open(DRAFTS))
        wrote = skipped = 0
        skip = pairs("--skip")
        for d in drafts:
            if (d["ticker"], d["filing_date"]) in skip:
                skipped += 1
                print(f"  SKIP (--skip) {d['ticker']} {d['filing_date']}")
                continue
            cur = supabase.table("filing_ai_classifications").select(
                "human_verdict,ai_suggested_title,ai_suggested_description,ai_suggested_event_type"
            ).eq("ticker", d["ticker"]).eq("filing_date", d["filing_date"]) \
             .eq("accession_number", d["accession_number"]).execute().data
            if not cur or cur[0]["human_verdict"] != "real_event":
                skipped += 1
                print(f"  SKIP {d['ticker']} {d['filing_date']}: row missing or not human-confirmed")
                continue
            c, patch = cur[0], {}
            if not c["ai_suggested_title"]:
                patch["ai_suggested_title"] = d["title"]
            if not c["ai_suggested_description"]:
                patch["ai_suggested_description"] = d["description"]
            if c["ai_suggested_event_type"] not in valid_types:
                patch["ai_suggested_event_type"] = d["event_type"]
            if patch:
                supabase.table("filing_ai_classifications").update(patch) \
                    .eq("ticker", d["ticker"]).eq("filing_date", d["filing_date"]) \
                    .eq("accession_number", d["accession_number"]).execute()
                wrote += 1
            else:
                skipped += 1
        print(f"Applied: {wrote} rows updated, {skipped} skipped.")
        return

    src = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else "output/promote_dryrun2.txt"
    cik_by_ticker = {c["ticker"]: c["cik"] for c in COMPANIES}
    groups = find_targets(src)
    print(f"{len(groups)} skipped groups found in {src}.")

    drafts, failures = [], []
    only = pairs("--only")
    for tickers, date in groups:
        if only and not any((t, date) in only for t in tickers):
            continue
        rows = supabase.table("filing_ai_classifications").select(
            "ticker,filing_date,accession_number,item_codes,ai_suggested_title,"
            "ai_suggested_description,ai_suggested_event_type"
        ).in_("ticker", list(tickers)).eq("filing_date", date).eq("human_verdict", "real_event").execute().data
        for row in rows:
            needs = (not row["ai_suggested_title"] or not row["ai_suggested_description"]
                     or row["ai_suggested_event_type"] not in valid_types)
            if not needs:
                continue
            cik = cik_by_ticker.get(row["ticker"])
            if cik is None:
                failures.append((row["ticker"], date, "no CIK on file"))
                continue
            d, err = draft_one(row, cik, allowed)
            if d is None:
                failures.append((row["ticker"], date, err))
                print(f"FAILED {row['ticker']} {date}: {err}")
            else:
                drafts.append(d)
                print(f"\n{d['ticker']} {d['filing_date']} [{d['event_type']}]\n  TITLE: {d['title']}\n"
                      f"  DESC:  {d['description']}\n  BASIS: {d['basis'][:300]}")
            time.sleep(0.3)

    os.makedirs("output", exist_ok=True)
    if only and os.path.exists(DRAFTS):
        prior = json.load(open(DRAFTS))
        keys = {(d["ticker"], d["filing_date"], d["accession_number"]) for d in drafts}
        drafts = [p for p in prior if (p["ticker"], p["filing_date"], p["accession_number"]) not in keys] + drafts
    json.dump(drafts, open(DRAFTS, "w"), indent=1)
    print(f"\n{len(drafts)} drafted, {len(failures)} failed. Saved to {DRAFTS}. Nothing written to the database.")
    for t, d, e in failures:
        print(f"  failed: {t} {d}: {e}")
    print("Read the drafts, then run with --apply.")


if __name__ == "__main__":
    main()
