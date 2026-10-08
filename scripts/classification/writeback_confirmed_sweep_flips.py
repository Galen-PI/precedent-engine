"""
writeback_confirmed_sweep_flips.py

Writes human-confirmed sweep flips (stale_url_sweep_results.review_status='confirmed')
into filing_ai_classifications so promote_events.py can pick them up.
Dry run unless --apply is passed.

Safety:
  - stops unless stale_url_sweep_audit_old_rows holds a snapshot of EVERY row it would
    change, showing the old verdict the sweep saw
  - skips and reports any row whose current ai_verdict differs from what the sweep saw
    (changed since), and any row already written back (safe to re-run)
  - UPDATEs specific columns only; never inserts or deletes
  - rows with no title/description/event type get their text drafted by a synchronous
    (non-batch) model call; the human confirmation stands, the model only drafts text

Usage: python writeback_confirmed_sweep_flips.py [--apply]
"""
import os, sys, time
from datetime import datetime, timezone
import requests
from classify_8k_filings_batch_v2 import (
    supabase, fetch_filing_text, get_recent_event_titles, build_batch_request,
    parse_classification_result, MODEL_VERSION, PROMPT_VERSION,
)

HEAD = {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"}
AUDIT = "stale_url_sweep_audit_old_rows"
APPLY = "--apply" in sys.argv


def key(r):
    return (r["ticker"], str(r["filing_date"])[:10], r["accession_number"])


def by_key(table, cols, accs):
    out = {}
    for i in range(0, len(accs), 100):
        page = supabase.table(table).select(cols) \
            .in_("accession_number", accs[i:i + 100]).execute().data
        for r in page:
            out[key(r)] = r
    return out


def draft_text(s, item_codes):
    cid = f"{s['ticker']}__{str(s['filing_date'])[:10]}__{s['accession_number']}"
    text = fetch_filing_text(s["fixed_url"])
    recent = get_recent_event_titles(s["ticker"])
    req = build_batch_request(cid, s["ticker"], str(s["filing_date"])[:10],
                              item_codes, text, recent)
    for attempt in range(1, 4):
        r = requests.post("https://api.anthropic.com/v1/messages", headers=HEAD,
                          json=req["params"], timeout=180)
        if r.status_code != 200:
            print(f"    attempt {attempt}: HTTP {r.status_code}")
            time.sleep(5)
            continue
        _msg = r.json()
        _text_blocks = [b["text"] for b in _msg["content"] if b.get("type") == "text"]
        if not _text_blocks:
            raise ValueError(f"No text block found: block types were {[b.get('type') for b in _msg['content']]}")
        parsed = parse_classification_result(_text_blocks[0])
        ok = (parsed.get("verdict") == "real_event" and parsed.get("suggested_title")
              and parsed.get("suggested_description") and parsed.get("suggested_event_type"))
        print(f"    attempt {attempt}: verdict={parsed.get('verdict')}, "
              f"title={'yes' if parsed.get('suggested_title') else 'no'}, "
              f"description={'yes' if parsed.get('suggested_description') else 'no'}")
        if ok:
            return parsed
    return None


def main():
    confirmed = supabase.table("stale_url_sweep_results").select("*") \
        .eq("review_status", "confirmed").execute().data
    print(f"{len(confirmed)} confirmed sweep rows.")
    if not confirmed:
        return
    accs = sorted({r["accession_number"] for r in confirmed})

    try:
        audit = by_key(AUDIT, "ticker,filing_date,accession_number,ai_verdict", accs)
    except Exception as e:
        sys.exit(f"STOP: cannot read {AUDIT} -- create the snapshot first. ({e})")
    current = by_key("filing_ai_classifications",
                     "ticker,filing_date,accession_number,item_codes,ai_verdict,human_verdict", accs)

    missing = [key(s) for s in confirmed if key(s) not in audit]
    if missing:
        sys.exit(f"STOP: {len(missing)} confirmed rows are not in {AUDIT}, e.g. {missing[:3]}. "
                 "Snapshot them (INSERT INTO ... SELECT) before applying.")
    bad = [key(s) for s in confirmed if audit[key(s)]["ai_verdict"] != s["old_ai_verdict"]]
    if bad:
        sys.exit(f"STOP: snapshot does not show the old verdict for {len(bad)} rows, e.g. {bad[:3]}. "
                 "It may have been taken after a write.")

    plan, skipped = [], []
    for s in confirmed:
        cur = current.get(key(s))
        if cur is None:
            skipped.append((key(s), "no filing_ai_classifications row"))
        elif cur["human_verdict"] == "real_event" and cur["ai_verdict"] == "real_event":
            skipped.append((key(s), "already written back"))
        elif cur["ai_verdict"] != s["old_ai_verdict"]:
            skipped.append((key(s), f"ai_verdict is now {cur['ai_verdict']!r}, sweep saw {s['old_ai_verdict']!r}"))
        else:
            complete = bool(s.get("new_title") and s.get("new_description") and s.get("new_event_type"))
            plan.append((s, cur, complete))

    print(f"\n{len(plan)} to write, {len(skipped)} skipped.")
    for s, cur, complete in plan:
        hv = cur["human_verdict"]
        rev = f"  (reverses human {hv})" if hv and hv != "real_event" else ""
        note = "" if complete else "  [text to be drafted]"
        print(f"  {s['ticker']:<5}{str(s['filing_date'])[:10]}  {(s.get('new_title') or '(no title yet)')[:64]}{rev}{note}")
    for kk, why in skipped:
        print(f"  SKIP {kk[0]} {kk[1]}: {why}")

    need = sum(1 for _, _, c in plan if not c)
    if not APPLY:
        print(f"\nDRY RUN -- nothing written. --apply writes {len(plan)} rows and makes {need} "
              f"small model calls (~${need * 0.01:.2f}).")
        return

    now_iso = datetime.now(timezone.utc).isoformat()
    written, unresolved = [], []
    for s, cur, complete in plan:
        if complete:
            conf, reasoning = s["new_confidence"], s["new_reasoning"]
            title, desc, etype = s["new_title"], s["new_description"], s["new_event_type"]
        else:
            print(f"Drafting text for {s['ticker']} {str(s['filing_date'])[:10]}...")
            parsed = draft_text(s, cur["item_codes"])
            if parsed is None:
                unresolved.append((s["ticker"], str(s["filing_date"])[:10]))
                continue
            conf, reasoning = parsed["confidence"], parsed["reasoning"]
            title, desc, etype = (parsed["suggested_title"], parsed["suggested_description"],
                                  parsed["suggested_event_type"])
        supabase.table("filing_ai_classifications").update({
            "ai_verdict": "real_event", "ai_confidence": conf, "ai_reasoning": reasoning,
            "ai_suggested_title": title, "ai_suggested_description": desc,
            "ai_suggested_event_type": etype, "ai_matched_known_template": None,
            "primary_document_url": s["fixed_url"],
            "human_verdict": "real_event", "human_reviewed_at": now_iso,
            "model_version": MODEL_VERSION, "prompt_version": PROMPT_VERSION,
        }).eq("ticker", s["ticker"]).eq("filing_date", s["filing_date"]) \
          .eq("accession_number", s["accession_number"]).execute()
        written.append(key(s))

    after = by_key("filing_ai_classifications",
                   "ticker,filing_date,accession_number,human_verdict,ai_suggested_title,"
                   "ai_suggested_description,primary_document_url", accs)
    verified = sum(1 for k in written if after.get(k)
                   and after[k]["human_verdict"] == "real_event"
                   and after[k]["ai_suggested_title"] and after[k]["ai_suggested_description"]
                   and str(after[k]["primary_document_url"]).endswith(".txt"))
    print(f"\nWrote {len(written)} rows; {verified} verified (real_event, title, description, .txt URL).")
    for t, d in unresolved:
        print(f"  NOT written (no usable title/description after 3 tries): {t} {d}")


if __name__ == "__main__":
    main()
