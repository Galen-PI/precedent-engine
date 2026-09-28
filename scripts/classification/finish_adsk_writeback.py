"""
finish_adsk_writeback.py

One-off: ADSK 2012-08-23 and 2017-11-28 were confirmed as real events in the sweep, but
the classifier returned no title/description, so writeback_confirmed_sweep_flips.py could
not write them. Drafts text with draft_missing_event_text.draft_one (draft only: prints
and saves output/adsk_drafts.json). --apply writes ONLY those saved drafts to
filing_ai_classifications, the same columns the write-back script sets. Old rows are
already in stale_url_sweep_audit_old_rows; the script stops if they are not.
"""
import json, os, sys
from datetime import datetime, timezone
from classify_8k_filings_batch_v2 import supabase, MODEL_VERSION, PROMPT_VERSION
from draft_missing_event_text import draft_one, PROMPT_TYPES, COMPANIES

TARGETS = [("ADSK", "2012-08-23"), ("ADSK", "2017-11-28")]
DRAFTS = "output/adsk_drafts.json"


def sweep_row(t, d):
    r = supabase.table("stale_url_sweep_results").select("*") \
        .eq("ticker", t).eq("filing_date", d).eq("review_status", "confirmed").execute().data
    return r[0] if r else None


def current_row(s):
    r = supabase.table("filing_ai_classifications").select(
        "ticker,filing_date,accession_number,item_codes,ai_verdict,human_verdict") \
        .eq("ticker", s["ticker"]).eq("filing_date", s["filing_date"]) \
        .eq("accession_number", s["accession_number"]).execute().data
    return r[0] if r else None


def in_audit(s):
    r = supabase.table("stale_url_sweep_audit_old_rows").select("accession_number") \
        .eq("ticker", s["ticker"]).eq("filing_date", s["filing_date"]) \
        .eq("accession_number", s["accession_number"]).execute().data
    return bool(r)


def draft():
    valid = {r["name"] for r in supabase.table("event_types").select("name").execute().data}
    allowed = [t for t in PROMPT_TYPES if t in valid]
    cik_by_ticker = {c["ticker"]: c["cik"] for c in COMPANIES}
    out = []
    for t, d in TARGETS:
        s = sweep_row(t, d)
        if not s:
            print(f"{t} {d}: no confirmed sweep row, skipping")
            continue
        cur = current_row(s)
        if cur is None:
            print(f"{t} {d}: no filing_ai_classifications row, skipping")
            continue
        if cur["human_verdict"] == "real_event" and cur["ai_verdict"] == "real_event":
            print(f"{t} {d}: already written back, skipping")
            continue
        if not in_audit(s):
            sys.exit(f"STOP: {t} {d} is not in stale_url_sweep_audit_old_rows")
        row = {"ticker": t, "filing_date": str(s["filing_date"])[:10],
               "accession_number": s["accession_number"], "item_codes": cur["item_codes"]}
        dr, err = draft_one(row, cik_by_ticker[t], allowed)
        if dr is None:
            print(f"FAILED {t} {d}: {err}")
            continue
        out.append(dr)
        print(f"\n{t} {d} [{dr['event_type']}]\n  TITLE: {dr['title']}\n  DESC:  {dr['description']}\n  BASIS: {dr['basis'][:300]}")
    os.makedirs("output", exist_ok=True)
    json.dump(out, open(DRAFTS, "w"), indent=1)
    print(f"\n{len(out)} drafted. Saved to {DRAFTS}. Nothing written to the database.")


def apply():
    drafts = json.load(open(DRAFTS))
    now_iso = datetime.now(timezone.utc).isoformat()
    done = []
    for dr in drafts:
        s = sweep_row(dr["ticker"], dr["filing_date"])
        cur = current_row(s) if s else None
        if not s or cur is None or not in_audit(s):
            print(f"SKIP {dr['ticker']} {dr['filing_date']}: missing row or snapshot")
            continue
        supabase.table("filing_ai_classifications").update({
            "ai_verdict": "real_event", "ai_confidence": s["new_confidence"],
            "ai_reasoning": s["new_reasoning"], "ai_suggested_title": dr["title"],
            "ai_suggested_description": dr["description"],
            "ai_suggested_event_type": dr["event_type"], "ai_matched_known_template": None,
            "primary_document_url": s["fixed_url"], "human_verdict": "real_event",
            "human_reviewed_at": now_iso, "model_version": MODEL_VERSION,
            "prompt_version": PROMPT_VERSION,
        }).eq("ticker", s["ticker"]).eq("filing_date", s["filing_date"]) \
          .eq("accession_number", s["accession_number"]).execute()
        done.append((s["ticker"], str(s["filing_date"])[:10], s["accession_number"]))
    for t, d, acc in done:
        r = supabase.table("filing_ai_classifications").select(
            "human_verdict,ai_suggested_title,ai_suggested_description,primary_document_url") \
            .eq("ticker", t).eq("filing_date", d).eq("accession_number", acc).execute().data[0]
        ok = (r["human_verdict"] == "real_event" and r["ai_suggested_title"]
              and r["ai_suggested_description"] and str(r["primary_document_url"]).endswith(".txt"))
        print(f"{t} {d}: {'verified' if ok else 'CHECK THIS ROW'}")
    print(f"Wrote {len(done)} rows.")


if __name__ == "__main__":
    apply() if "--apply" in sys.argv else draft()
