#!/usr/bin/env python3
"""
import_review_decisions.py -- loads a reviewer's decisions from the review-queue CSV into the NEW table review_queue_decisions (it never touches candidate_review_log, classification_corrections or any other review table).
Reads results/human_review_queue_with_excerpts.csv (or the path given), takes the rows whose reviewer_decision column is filled, and checks every one BEFORE writing anything:
  decision must be one of: event, not an event (or not_an_event), need more (or need_more); the filing's accession number must be found in its URL; the same (accession, miss date) may appear only once.
DRY RUN by default (prints what would be written); add --write to upsert (on_conflict accession_number,miss_date, so a re-import updates a decision instead of duplicating it).
Usage:   python3 -u scripts/card/import_review_decisions.py --reviewer "Galen" [path] [--write]
"""
import os, sys, re, csv, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from add_exhibit_excerpts import parse_url

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT = os.path.join(ROOT, "results", "human_review_queue_with_excerpts.csv")
VALID = {"event": "event", "not an event": "not_an_event", "not_an_event": "not_an_event", "need more": "need_more", "need_more": "need_more"}
QUEUE_VERSION = "review_queue_2026-10-21"


def get_sb():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def build(path, reviewer):
    rows, errors, seen = [], [], set()
    for n, r in enumerate(csv.DictReader(open(path)), 2):
        raw = (r.get("reviewer_decision (event / not an event / need more)") or r.get("reviewer_decision") or "").strip().lower()
        if not raw:
            continue
        dec = VALID.get(raw)
        urls = re.findall(r"https?://[^\s;|]+", r.get("evidence", ""))
        p = parse_url(urls[0]) if urls else None
        if dec is None:
            errors.append("line %d (%s %s): decision '%s' is not one of event / not an event / need more" % (n, r["ticker"], r["date"], raw)); continue
        if p is None:
            errors.append("line %d (%s %s): no accession number found in the evidence URL" % (n, r["ticker"], r["date"])); continue
        key = (p[2], r["date"])
        if key in seen:
            errors.append("line %d (%s %s): duplicate decision for the same filing and date" % (n, r["ticker"], r["date"])); continue
        seen.add(key)
        conf = r.get("classifier_confidence", "").split("|")[0].strip()
        rows.append({"accession_number": p[2], "ticker": r["ticker"], "miss_date": r["date"], "tier": r["tier"], "classifier_verdict": (r.get("classifier_verdict") or "").split("|")[0].strip() or None,
                     "classifier_confidence": float(conf) if re.fullmatch(r"[0-9.]+", conf) else None, "decision": dec, "notes": (r.get("notes") or "").strip() or None, "reviewer": reviewer, "queue_version": QUEUE_VERSION})
    return rows, errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=DEFAULT)
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    rows, errors = build(a.path, a.reviewer)
    from collections import Counter
    print("decisions found: %d | %s" % (len(rows), ", ".join("%s %d" % kv for kv in Counter(r["decision"] for r in rows).most_common())))
    for e in errors:
        print("  PROBLEM " + e)
    if errors:
        sys.exit("%d problem(s): nothing written. Fix the CSV and rerun." % len(errors))
    for r in rows[:5]:
        print("  %s %-6s %s -> %s%s" % (r["miss_date"], r["ticker"], r["accession_number"], r["decision"], " (" + r["notes"][:40] + ")" if r["notes"] else ""))
    if not a.write:
        print("dry run: nothing written (add --write to upsert into review_queue_decisions)")
        return
    sb = get_sb()
    for i in range(0, len(rows), 200):
        sb.table("review_queue_decisions").upsert(rows[i:i + 200], on_conflict="accession_number,miss_date").execute()
    print("upserted %d decisions into review_queue_decisions" % len(rows))


if __name__ == "__main__":
    main()
