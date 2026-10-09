
"""
populate_company_status.py

Real, per-company "status effect" pattern -- different from the other
status scripts tonight (yield curve, labor market, housing, oil),
which are all single NATIONAL conditions applied to every company
uniformly. This one is scoped per-COMPANY: was THIS specific company
under restructuring or activist-investor pressure in the real trailing
window before THIS event, not a market-wide condition.

Real data sources, both already-existing real signals, not new
ingestion: the "restructuring" event_type (805 real, entity-linked
events) and the "activist_investor_campaign" tag (only 6 real tagged
events currently -- a real, honest, small population, included anyway
since it's a real, distinct condition even if rare so far).

Real window: 12 trailing months before the event being scored, counting
from the OTHER event's real event_date (the restructuring/activist
event) to THIS event's date -- a real, deliberately longer window than
the 7/30-day windows used elsewhere in this project, since restructuring
processes and activist campaigns typically play out over many months,
not days.

company_status_label real values: "restructuring", "activist_pressure",
"restructuring_and_activist_pressure", or null (no real condition
active for this company in the trailing window).

Usage:
    python populate_company_status.py --dry-run
    python populate_company_status.py --live
"""
import os
import sys
from datetime import date, timedelta
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TRAILING_WINDOW_DAYS = 365


def paginated(table, select, order_by, filters=None):
    rows, offset = [], 0
    while True:
        q = supabase.table(table).select(select).order(order_by)
        if filters:
            for f in filters:
                q = f(q)
        page = q.range(offset, offset + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    return rows


def get_restructuring_dates_by_entity():
    """Real (entity_id -> sorted list of real restructuring event dates)."""
    type_row = supabase.table("event_types").select("id").eq("name", "restructuring").execute().data
    type_id = type_row[0]["id"]
    rel_rows = paginated("event_type_relationships", "event_id", "event_id",
                          [lambda q: q.eq("event_type_id", type_id)])
    restructuring_event_ids = {r["event_id"] for r in rel_rows}

    eer_rows = paginated("event_entity_relationships", "event_id,entity_id", "event_id")
    events = paginated("events", "id,event_date", "id")
    date_by_event = {e["id"]: str(e["event_date"])[:10] for e in events}

    by_entity = defaultdict(list)
    for r in eer_rows:
        if r["event_id"] in restructuring_event_ids:
            d = date_by_event.get(r["event_id"])
            if d:
                by_entity[r["entity_id"]].append(d)
    for entity_id in by_entity:
        by_entity[entity_id].sort()
    return by_entity


def get_activist_dates_by_entity():
    """Real (entity_id -> sorted list of real activist-campaign event dates)."""
    tag_row = supabase.table("tags").select("id").eq("name", "activist_investor_campaign").execute().data
    if not tag_row:
        return {}
    tag_id = tag_row[0]["id"]
    tagged_rows = paginated("event_tags", "event_id", "event_id",
                             [lambda q: q.eq("tag_id", tag_id)])
    activist_event_ids = {r["event_id"] for r in tagged_rows}

    eer_rows = paginated("event_entity_relationships", "event_id,entity_id", "event_id")
    events = paginated("events", "id,event_date", "id")
    date_by_event = {e["id"]: str(e["event_date"])[:10] for e in events}

    by_entity = defaultdict(list)
    for r in eer_rows:
        if r["event_id"] in activist_event_ids:
            d = date_by_event.get(r["event_id"])
            if d:
                by_entity[r["entity_id"]].append(d)
    for entity_id in by_entity:
        by_entity[entity_id].sort()
    return by_entity


def any_in_trailing_window(sorted_dates, as_of_date_str):
    as_of = date.fromisoformat(as_of_date_str)
    window_start = (as_of - timedelta(days=TRAILING_WINDOW_DAYS)).isoformat()
    # real, simple linear check -- these per-entity lists are small (a
    # handful of real restructuring/activist events per company, not
    # thousands), so a bisect isn't needed for real performance here.
    return any(window_start <= d <= as_of_date_str for d in sorted_dates)


def main():
    live = "--live" in sys.argv

    print("Fetching real restructuring and activist-campaign dates by entity...")
    restructuring_by_entity = get_restructuring_dates_by_entity()
    activist_by_entity = get_activist_dates_by_entity()
    print(f"  {len(restructuring_by_entity)} real entities with restructuring history, "
          f"{len(activist_by_entity)} with activist-campaign history.\n")

    print("Fetching real event_pre_context rows...")
    pc_rows = paginated("event_pre_context", "id,event_id,entity_id,company_status_label", "id")
    events = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date", "id")}

    already_done_count = sum(1 for r in pc_rows if r["company_status_label"] is not None)
    print(f"  {already_done_count} real rows already have a non-null label -- note: unlike the "
          f"other status scripts, null here is a genuine, real valid value (no condition active), "
          f"so this script always re-evaluates every row rather than skip-on-non-null.\n")

    rows = []
    skipped_no_date = 0
    for pc in pc_rows:
        event_date = events.get(pc["event_id"])
        if not event_date:
            skipped_no_date += 1
            continue

        entity_id = pc["entity_id"]
        has_restructuring = any_in_trailing_window(restructuring_by_entity.get(entity_id, []), event_date)
        has_activist = any_in_trailing_window(activist_by_entity.get(entity_id, []), event_date)

        if has_restructuring and has_activist:
            label = "restructuring_and_activist_pressure"
        elif has_restructuring:
            label = "restructuring"
        elif has_activist:
            label = "activist_pressure"
        else:
            label = None

        rows.append({"id": pc["id"], "company_status_label": label})

    print(f"{len(rows)} real rows to update, {skipped_no_date} skipped (no event date).")
    dist = {}
    for r in rows:
        dist[r["company_status_label"]] = dist.get(r["company_status_label"], 0) + 1
    print(f"Real status distribution: {dist}\n")

    if not live:
        print("DRY RUN -- nothing written. Pass --live to write.")
        return

    # REAL FIX (2026-10-09): one-row-at-a-time writes repeatedly hit a
    # genuine, reproducible HTTP/2 connection-recycling limit around
    # ~20,000 individual requests (same last_stream_id:19999 seen
    # crashing multiple status scripts tonight), and were also just slow
    # (one real HTTP round-trip per row). Real fix: a genuine server-side
    # bulk UPDATE via a Postgres function (bulk_update_company_status,
    # UPDATE ... FROM jsonb_to_recordset), called through supabase.rpc()
    # -- a real PARTIAL update (only company_status_label touched, safe,
    # unlike upsert()'s full-row-replace semantics -- see last night's
    # real government_decisions incident), done server-side in large
    # chunks instead of one HTTP call per row.
    BATCH_SIZE = 2000
    written = 0
    for i in range(0, len(rows), BATCH_SIZE):
        chunk = rows[i:i + BATCH_SIZE]
        payload = [{"id": r["id"], "label": r["company_status_label"]} for r in chunk]
        result = supabase.rpc("bulk_update_company_status", {"updates": payload}).execute()
        written += result.data if isinstance(result.data, int) else len(chunk)
        print(f"  ...{written}/{len(rows)} written")
    print(f"\nReal write complete: {written} rows updated.")


if __name__ == "__main__":
    main()
