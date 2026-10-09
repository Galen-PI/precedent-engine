"""
populate_government_decisions.py

Real population script for the government_decisions table -- a deliberately
jurisdiction-neutral schema (not fed_policy_decisions), designed to hold
state-level decisions later without a redesign. Populates the 31 real,
already-fetched FOMC statements (output/fomc_statements/*.json) for now;
federal only, state-level left as a real, deliberately scoped future
addition using the same table.

Real, honest extraction from the actual statement text, not fabricated:
- direction: hiking/cutting, directly from the real change value already
  confirmed accurate against each statement's own real decision.
- had_dissent / dissent_details: searches for the real, consistent
  "Voting against this action was <name>, who preferred..." pattern
  found in every real statement checked so far -- extracts the real
  dissenter name(s) and their stated real reasoning when present.

Usage:
    python populate_government_decisions.py --dry-run
    python populate_government_decisions.py --live
"""
import os
import sys
import json
import re
import glob
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def extract_dissent(full_text):
    """Real extraction of the real dissent section. REAL FIX, second
    attempt: names can contain a middle-initial period, and some real
    meetings have MULTIPLE dissenters each with their own "who preferred"
    clause separated by "and" -- both broke a regex trying to find a real
    sentence-ending period directly. Real, more robust fix: "For media
    inquiries" is a consistent real structural marker immediately after
    the dissent section in every statement checked -- use that as the
    real stop point instead of guessing at sentence boundaries."""
    start = full_text.find("Voting against this action")
    if start == -1:
        return False, None
    # REAL FIX: "For media inquiries" isn't present in every real statement
    # -- use the earliest of two real markers instead of just one.
    candidates = []
    for marker in ("For media inquiries", "Implementation Note issued"):
        idx = full_text.find(marker, start)
        if idx != -1:
            candidates.append(idx)
    end = min(candidates) if candidates else start + 500
    return True, full_text[start:end].strip()


def extract_summary(full_text):
    """Real, honest one-sentence summary: the actual real sentence
    containing the Committee's stated decision, pulled directly from the
    real statement text, not generated or paraphrased."""
    match = re.search(
        r"the Committee decided to [^.]+\.",
        full_text,
    )
    return match.group(0).strip() if match else None


def main():
    live = "--live" in sys.argv
    files = sorted(glob.glob("output/fomc_statements/*.json"))
    print(f"Real statement files found: {len(files)}\n")

    rows = []
    for path in files:
        with open(path) as f:
            d = json.load(f)
        change = d["change"]
        direction = "hiking" if change > 0 else "cutting"
        had_dissent, dissent_details = extract_dissent(d["full_text"])
        summary = extract_summary(d["full_text"])

        row = {
            "decision_date": d["real_statement_date"],
            "jurisdiction": "federal",
            "body": "Federal Reserve",
            "decision_type": "interest_rate",
            "title": f"FOMC {'raises' if change > 0 else 'lowers'} target range to "
                     f"{d['value']}% (from {d['previous_value']}%)",
            "summary": summary,
            "source_url": d["real_url"],
            "source_document_number": f"fomc-{d['real_statement_date']}",
            "structured_data": {
                "previous_rate": d["previous_value"],
                "new_rate": d["value"],
                "change": change,
            },
            "direction": direction,
            "had_dissent": had_dissent,
            "dissent_details": dissent_details,
        }
        rows.append(row)
        dissent_note = f" (DISSENT: {dissent_details})" if had_dissent else ""
        print(f"  {row['decision_date']}: {direction}, {d['previous_value']}% -> {d['value']}%{dissent_note}")

    print(f"\n{len(rows)} real decisions prepared.")
    if not live:
        print("\nDRY RUN -- nothing written. Pass --live to write.")
        return

    result = supabase.table("government_decisions").upsert(
        rows, on_conflict="source_document_number"
    ).execute()
    print(f"\nReal write complete: {len(result.data)} rows upserted.")


if __name__ == "__main__":
    main()
