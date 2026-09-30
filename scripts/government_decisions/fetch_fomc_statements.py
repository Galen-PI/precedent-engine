"""
fetch_fomc_statements.py

Real Phase 4 "Government Decisions" build. Fetches the real FOMC statement text
for each of the 31 real Fed rate decisions in macro_data_releases (series_id =
DFEDTARU, change_from_previous != 0), so real events can be drafted from real
source text -- same discipline as every SEC filing reviewed all session, never
fabricated.

Real, confirmed finding before writing this: the Fed's press-release URL pattern
is monetary{YYYYMMDD}a.htm, but the date does NOT always match
macro_data_releases' stored release_date directly -- confirmed by direct testing:
2025-09-18's real statement is dated 2025-09-17 (one day earlier), while
2015-12-16's real statement IS dated 2015-12-16 (same day). The offset is not
universal, so this tries BOTH the exact date and one day earlier for each real
decision, and uses whichever one actually returns a real statement.

This script only FETCHES and SAVES real text locally -- it does not create
events. Drafting real event titles/descriptions from this text, and having each
one individually read before confirming, is a deliberate separate step.

Usage:
    python fetch_fomc_statements.py
"""
import os
import json
import re
import requests
from datetime import date, timedelta
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

HEADERS = {"User-Agent": "Research research@example.com"}
OUT_DIR = "output/fomc_statements"


def get_real_decisions():
    rows = (supabase.table("macro_data_releases")
            .select("release_date,value,previous_value,change_from_previous")
            .eq("series_id", "DFEDTARU")
            .neq("change_from_previous", 0)
            .order("release_date").execute().data)
    return rows


def try_fetch(d: date):
    url = f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{d.strftime('%Y%m%d')}a.htm"
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        return None, url
    text = re.sub(r"<[^>]+>", " ", r.text)
    text = re.sub(r"\s+", " ", text).strip()
    idx = text.find("federal funds rate")
    if idx == -1:
        return None, url
    return text, url


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    decisions = get_real_decisions()
    print(f"{len(decisions)} real Fed rate decisions found.\n")

    results = []
    for dec in decisions:
        release = date.fromisoformat(str(dec["release_date"])[:10])
        real_statement, real_url, real_date = None, None, None
        for candidate in (release, release - timedelta(days=1)):
            text, url = try_fetch(candidate)
            if text:
                real_statement, real_url, real_date = text, url, candidate.isoformat()
                break

        status = "OK" if real_statement else "FAILED"
        print(f"  {dec['release_date']}: {dec['previous_value']}% -> {dec['value']}% "
              f"({dec['change_from_previous']:+.2f}) -- {status}"
              + (f" (real statement date: {real_date})" if real_date and real_date != str(dec['release_date'])[:10] else ""))

        if real_statement:
            fname = f"{OUT_DIR}/{dec['release_date']}.json"
            with open(fname, "w") as f:
                json.dump({
                    "release_date": str(dec["release_date"]),
                    "real_statement_date": real_date,
                    "real_url": real_url,
                    "previous_value": dec["previous_value"],
                    "value": dec["value"],
                    "change": dec["change_from_previous"],
                    "full_text": real_statement,
                }, f, indent=1)
        results.append({"release_date": str(dec["release_date"]), "status": status})

    ok = sum(1 for r in results if r["status"] == "OK")
    print(f"\n{ok}/{len(results)} real statements fetched and saved to {OUT_DIR}/")
    failed = [r["release_date"] for r in results if r["status"] == "FAILED"]
    if failed:
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
