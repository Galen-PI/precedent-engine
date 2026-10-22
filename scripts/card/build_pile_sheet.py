#!/usr/bin/env python3
"""
build_pile_sheet.py -- READ-ONLY (database read; SEC exhibits through add_exhibit_excerpts, cached). Writes results/pile313_sheet.csv.
THE PILE: filings with human_verdict = real_event, NO suggested event type (so no suggested title or description either), not linked to any event (expected 313 on 2026-10-22). Provenance unknown: none appears in candidate_review_log, classification_corrections, bulk_confirm_20261015,
recoverable_rejected_noise, review_flip_audit_20261015 or audit_flagged_20261014; 87% were AI likely_noise calls, 83% have no review timestamp, 35 carry human_agreed_with_ai = true on an AI noise call. QUESTION: are they real events (legacy human confirmations the classifier later called noise) or corrupted verdicts?
A seeded random 20 is read by CONTENT against the rubric (price move not shown). In the importer 'event' = it IS a real event (the human verdict is right), 'not an event' = the verdict is wrong; tier PILE313.
DECISION RULES (fixed before reading): at least 16 of 20 real -> the pile is mostly real human-found events: draft title, description and type for the pile into a STAGING csv (nothing written to the database), accept it, then a guarded update fills the fields only where they are NULL and the verdict is real_event, then promote_events.py;
10 or fewer real -> the verdicts are suspect: flag them in notes, do NOT promote, and consider resetting them with an audit table; 11-15 -> park the pile (not worth reading 313 rows).
Usage:   python3 -u scripts/card/build_pile_sheet.py [n, default 20]
"""
import os, sys, csv, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import unrecorded_candidates as uc
import add_exhibit_excerpts as ae

RESULTS = os.path.join(os.path.abspath(os.path.join(HERE, "..", "..")), "results")
SEED = 20261025
EXPECTED = 313
COL = "reviewer_decision (event / not an event / need more)"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    sb = ew.get_sb()
    cols = "accession_number,ticker,filing_date,item_codes,primary_document_url,ai_verdict,ai_confidence,ai_reasoning,human_agreed_with_ai,human_reviewed_at"
    cand = list(uc.paged(lambda: sb.table("filing_ai_classifications").select(cols).eq("human_verdict", "real_event").is_("ai_suggested_event_type", "null").order("accession_number")))
    linked = {r["accession_number"] for r in uc.paged(lambda: sb.table("event_source_filings").select("accession_number").order("accession_number"))}
    pile = [r for r in cand if r["accession_number"] not in linked]
    print("pile (real_event verdict, no suggested type, not linked to any event): %d (expected %d: %s)" % (len(pile), EXPECTED, "MATCH" if len(pile) == EXPECTED else "MISMATCH, the data moved"))
    smp = random.Random(SEED).sample(pile, min(n, len(pile)))
    ua_ok = "@" in ae.UA and not any(w in ae.UA for w in ("example.com", "YOUR_REAL", "your"))
    out, nex = [], 0
    for r in smp:
        url = r.get("primary_document_url") or ""
        p = ae.parse_url(url)
        cached = p is not None and os.path.exists(os.path.join(ae.CACHE, p[1] + ".json"))
        if p is not None and not cached and not ua_ok:
            sys.exit("Set SEC_USER_AGENT to a real contact first.")
        res = ae.excerpt_for(url) if p is not None else {"type": "", "excerpt": "", "status": "no accession in URL"}
        ex = ("[%s] %s" % (res["type"], res["excerpt"][:1200])) if res.get("excerpt") else "(%s)" % res.get("status", "no exhibit")
        nex += int(bool(res.get("excerpt")))
        d = str(r["filing_date"])[:10]
        out.append({"tier": "PILE313", "date": d, "ticker": r["ticker"], "evidence": "pile of 313 (agreed_flag=%s, reviewed=%s): items %s filed %s %s" % (r.get("human_agreed_with_ai"), str(r.get("human_reviewed_at"))[:10], r["item_codes"], d, url),
                    "classifier_verdict": r["ai_verdict"], "classifier_confidence": r["ai_confidence"], "classifier_reasoning": (r["ai_reasoning"] or "")[:300], "exhibit_excerpt": ex, COL: "", "notes": ""})
    path = os.path.join(RESULTS, "pile313_sheet.csv")
    os.makedirs(RESULTS, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print("sample %d (seed %d) | with an exhibit excerpt %d | wrote %s" % (len(out), SEED, nex, path))


if __name__ == "__main__":
    main()
