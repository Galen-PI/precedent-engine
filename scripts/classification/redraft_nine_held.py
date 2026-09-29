"""
redraft_nine_held.py

Redrafts CCL 2026-04-20, CNC 2021-06-25, DUK 2021-05-20 -- three of the nine
originally-held-back drafts whose text lost the material event (routine
annual-meeting wording, a notes offering with no deal named, a routine-sounding
press-release response) even though a human already confirmed human_verdict=real_event
on the underlying filing_ai_classifications row.

Source is filing_ai_classifications directly (NOT the stale_url_sweep_results table --
these three never went through that sweep). The focus hint passed to draft_one() is
each row's own existing ai_reasoning, which is what the human actually read when
confirming real_event (this matters for CNC, where ai_verdict itself was likely_noise
but a human overrode it -- the reasoning still correctly identifies the Magellan Health
acquisition financing).

Draft only unless --apply; draft writes nothing to the DB.
"""
import json, os, sys
from datetime import datetime, timezone
from classify_8k_filings_batch_v2 import supabase, MODEL_VERSION, PROMPT_VERSION
from draft_missing_event_text import draft_one, PROMPT_TYPES, COMPANIES

TARGETS = [("CCL", "2026-04-20"), ("CNC", "2021-06-25"), ("DUK", "2021-05-20")]
DRAFTS = "output/nine_held_drafts.json"


def current_row(t, d):
    r = supabase.table("filing_ai_classifications").select(
        "ticker,filing_date,accession_number,item_codes,ai_verdict,human_verdict,"
        "ai_reasoning,ai_confidence,primary_document_url") \
        .eq("ticker", t).eq("filing_date", d).execute().data
    return r[0] if r else None


def draft():
    valid = {r["name"] for r in supabase.table("event_types").select("name").execute().data}
    allowed = [t for t in PROMPT_TYPES if t in valid]
    cik_by_ticker = {c["ticker"]: c["cik"] for c in COMPANIES}
    out = []
    for t, d in TARGETS:
        cur = current_row(t, d)
        if not cur or cur["human_verdict"] != "real_event":
            print(f"{t} {d}: missing row or not human-confirmed real_event, skipping")
            continue
        row = {"ticker": t, "filing_date": d, "accession_number": cur["accession_number"],
               "item_codes": cur["item_codes"]}
        dr, err = draft_one(row, cik_by_ticker[t], allowed, focus=cur.get("ai_reasoning"))
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
    for dr in drafts:
        cur = current_row(dr["ticker"], dr["filing_date"])
        if not cur:
            print(f"{dr['ticker']} {dr['filing_date']}: row disappeared, skipping")
            continue
        supabase.table("filing_ai_classifications").update({
            "ai_verdict": "real_event", "ai_suggested_title": dr["title"],
            "ai_suggested_description": dr["description"], "ai_suggested_event_type": dr["event_type"],
            "human_verdict": "real_event", "human_reviewed_at": now_iso,
            "model_version": MODEL_VERSION, "prompt_version": PROMPT_VERSION,
        }).eq("ticker", cur["ticker"]).eq("filing_date", cur["filing_date"]) \
          .eq("accession_number", cur["accession_number"]).execute()
        print(f"{dr['ticker']} {dr['filing_date']}: written")
    print(f"Wrote {len(drafts)} rows.")


if __name__ == "__main__":
    apply() if "--apply" in sys.argv else draft()
