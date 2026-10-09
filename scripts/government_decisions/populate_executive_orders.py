"""
populate_executive_orders.py

Real population script for federal executive orders into the same,
jurisdiction-neutral government_decisions table used for FOMC decisions
(populate_government_decisions.py) -- same real schema, different
decision_type/body, so this slots into the existing threading
infrastructure (populate_government_decision_exposure.py) with no
changes needed there.

Real data source: the Federal Register's own free, keyless, official
API (federalregister.gov/api/v1/documents.json), confirmed directly via
a live test call before building this. Covers Presidential Documents
back to 1994 -- matching this project's own earliest tracked company
date exactly.

RELEVANCE SCOPING (real, deliberate, two-step per Galen 2026-10-08):
This script (step 1) ingests the RAW, complete set of executive orders
with no filtering -- EOs have no clean "policy area" field the way
Congressional bills do via Congressional Research Service tags, so
filtering by relevance (does this actually touch companies, health, or
economic regulation, as opposed to something like a commemorative
proclamation) requires real judgment on title/content, not a keyword
rule. That judgment is step 2, a separate classification script -- not
built here. structured_data.relevance_reviewed stays false until that
step runs, so step 2 can find exactly what still needs review.

direction / had_dissent / dissent_details don't apply to executive
orders (no rate direction, no dissent mechanism) -- left NULL.

Usage:
    python populate_executive_orders.py --dry-run
    python populate_executive_orders.py --live [--since YYYY-MM-DD]
"""
import os
import sys
import json
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

FR_BASE_URL = "https://www.federalregister.gov/api/v1/documents.json"
EARLIEST_DATE = "1994-01-01"  # matches this project's earliest tracked company data


def fetch_all_executive_orders(since_date):
    """Real, paginated fetch of every executive order since since_date,
    using the Federal Register's own cursor-based pagination
    (next_page_url) rather than guessing at page numbers."""
    params = {
        "conditions[type][]": "PRESDOCU",
        "conditions[presidential_document_type]": "executive_order",
        "conditions[publication_date][gte]": since_date,
        "per_page": 1000,
        "order": "oldest",
        "fields[]": ["executive_order_number", "title", "publication_date",
                      "signing_date", "abstract", "agencies", "html_url",
                      "document_number"],
    }
    all_results = []
    url = FR_BASE_URL
    page_params = params
    while True:
        resp = requests.get(url, params=page_params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        all_results.extend(data["results"])
        print(f"  ...fetched {len(all_results)} of {data['count']} real EOs")
        next_url = data.get("next_page_url")
        if not next_url:
            break
        url = next_url
        page_params = None  # next_page_url already has all real params encoded
    return all_results


def main():
    live = "--live" in sys.argv
    since_date = EARLIEST_DATE
    if "--since" in sys.argv:
        since_date = sys.argv[sys.argv.index("--since") + 1]

    print(f"Fetching real executive orders since {since_date}...")
    eos = fetch_all_executive_orders(since_date)
    print(f"\n{len(eos)} real executive orders fetched.\n")

    rows = []
    for eo in eos:
        agency_names = [a.get("name") or a.get("raw_name") for a in (eo.get("agencies") or []) if a]
        row = {
            "decision_date": eo["signing_date"] or eo["publication_date"],
            "jurisdiction": "federal",
            "body": "Executive Branch",
            "decision_type": "executive_order",
            "title": eo["title"],
            "summary": eo.get("abstract"),
            "source_url": eo["html_url"],
            "source_document_number": eo["document_number"],
            "structured_data": {
                "executive_order_number": eo.get("executive_order_number"),
                "document_number": eo.get("document_number"),
                "publication_date": eo.get("publication_date"),
                "signing_date": eo.get("signing_date"),
                "agencies": agency_names,
                "relevance_reviewed": False,  # real step 2 (not built here) flips this
            },
            "direction": None,
            "had_dissent": None,
            "dissent_details": None,
        }
        rows.append(row)

    print(f"{len(rows)} real rows prepared.")
    if not live:
        print("\nDRY RUN -- nothing written. Pass --live to write.")
        print("Sample:", json.dumps(rows[0], indent=2) if rows else "(none)")
        return

    CHUNK = 500
    written = 0
    for i in range(0, len(rows), CHUNK):
        chunk = rows[i:i + CHUNK]
        result = supabase.table("government_decisions").upsert(
            chunk, on_conflict="source_document_number"
        ).execute()
        written += len(result.data)
        print(f"  ...{written}/{len(rows)} written")
    print(f"\nReal write complete: {written} rows upserted.")


if __name__ == "__main__":
    main()
