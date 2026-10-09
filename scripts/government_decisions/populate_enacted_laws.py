"""
populate_enacted_laws.py

Real population script for Congressional enacted public laws into the
same, jurisdiction-neutral government_decisions table used for FOMC
decisions and executive orders -- same real schema, different
body/decision_type, so this slots into the existing threading
infrastructure (populate_government_decision_exposure.py) with no
changes needed there.

Real data source: the official Congress.gov API (api.congress.gov/v3),
Library of Congress, confirmed directly via live test calls before
building. Requires a real, free API key (CONGRESS_API_KEY env var,
registered at api.congress.gov) -- unlike the Federal Register API,
this one is not keyless.

Two real real API calls per law, by design:
  1. /law/{congress}/pub -- list endpoint, cheap, gives the bare bill
     identifier (type/number) and the enactment date/law number.
  2. /bill/{congress}/{type}/{number} -- detail endpoint, needed because
     the list endpoint does NOT include policyArea -- the Congressional
     Research Service's own real subject-area tag, the real basis for
     relevance filtering later.

Real scope: congresses 103 through 119 (1994-present, matching this
project's own earliest tracked company date), confirmed via a live
count check before building -- 6,422 real public laws total across
that span.

RELEVANCE SCOPING (same real, deliberate two-step as executive orders,
Galen 2026-10-08): this script (step 1) ingests the raw set with no
filtering beyond "became a public law" -- policyArea IS available here
(unlike EOs), but deciding which policy areas actually touch companies/
health/economic regulation vs. something irrelevant is still a separate
real judgment call, not built here. structured_data.relevance_reviewed
stays false until that step runs.

Usage:
    python populate_enacted_laws.py --dry-run [--congress N]
    python populate_enacted_laws.py --live [--congress N]
"""
import os
import sys
import time
import json
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
CONGRESS_API_KEY = os.environ["CONGRESS_API_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://api.congress.gov/v3"
EARLIEST_CONGRESS = 103
LATEST_CONGRESS = 119
REQUEST_DELAY = 0.2  # real, conservative pacing -- well under the 5,000/hr limit


def fetch_with_retry(url, params, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 429:
            wait = 5 * (attempt + 1)
            print(f"    Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Real fetch failed for {url} after {max_retries} retries.")


def fetch_laws_for_congress(congress):
    laws = []
    offset = 0
    limit = 250
    while True:
        data = fetch_with_retry(f"{BASE_URL}/law/{congress}/pub", {
            "api_key": CONGRESS_API_KEY, "format": "json",
            "limit": limit, "offset": offset,
        })
        page = data.get("bills", [])
        laws.extend(page)
        time.sleep(REQUEST_DELAY)
        if len(page) < limit:
            break
        offset += limit
    return laws


def fetch_bill_detail(congress, bill_type, number):
    data = fetch_with_retry(f"{BASE_URL}/bill/{congress}/{bill_type.lower()}/{number}", {
        "api_key": CONGRESS_API_KEY, "format": "json",
    })
    time.sleep(REQUEST_DELAY)
    return data.get("bill", {})


def main():
    live = "--live" in sys.argv
    only_congress = None
    if "--congress" in sys.argv:
        only_congress = int(sys.argv[sys.argv.index("--congress") + 1])

    congresses = [only_congress] if only_congress else list(range(EARLIEST_CONGRESS, LATEST_CONGRESS + 1))

    print("Fetching real, already-written law document numbers...")
    existing = []
    offset = 0
    while True:
        page = supabase.table("government_decisions").select("source_document_number") \
            .eq("decision_type", "enacted_law").range(offset, offset + 999).execute().data
        if not page:
            break
        existing.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    existing_doc_numbers = {r["source_document_number"] for r in existing}
    print(f"  {len(existing_doc_numbers)} real laws already ingested.\n")

    total_written = 0
    for congress in congresses:
        print(f"=== Congress {congress} ===")
        laws = fetch_laws_for_congress(congress)
        print(f"  {len(laws)} real public laws found.")

        rows = []
        for law in laws:
            law_number = law["laws"][0]["number"]
            doc_id = f"law-{law_number}"
            if doc_id in existing_doc_numbers:
                continue

            detail = fetch_bill_detail(congress, law["type"], law["number"])
            policy_area = (detail.get("policyArea") or {}).get("name")
            subjects = detail.get("subjects", {})

            row = {
                "decision_date": law["latestAction"]["actionDate"],
                "jurisdiction": "federal",
                "body": "Congress",
                "decision_type": "enacted_law",
                "title": law["title"],
                "summary": None,
                "source_url": law["url"].replace("?format=json", ""),
                "source_document_number": doc_id,
                "structured_data": {
                    "law_number": law_number,
                    "congress": congress,
                    "bill_type": law["type"],
                    "bill_number": law["number"],
                    "policy_area": policy_area,
                    "relevance_reviewed": False,
                },
                "direction": None,
                "had_dissent": None,
                "dissent_details": None,
            }
            rows.append(row)
            print(f"    {law_number}: {policy_area or '(no policy area)'} -- {law['title'][:70]}")

        print(f"  {len(rows)} new real rows prepared for Congress {congress}.")
        if live and rows:
            CHUNK = 200
            for i in range(0, len(rows), CHUNK):
                chunk = rows[i:i + CHUNK]
                result = supabase.table("government_decisions").upsert(
                    chunk, on_conflict="source_document_number"
                ).execute()
                total_written += len(result.data)
            print(f"  Written for Congress {congress}.\n")
        else:
            print()

    if not live:
        print("DRY RUN -- nothing written. Pass --live to write.")
    else:
        print(f"\nReal write complete: {total_written} total rows upserted across all congresses.")


if __name__ == "__main__":
    main()
