"""
populate_storm_tier.py

Productionizes the validated storm/compounding finding (see THEORY.md) as real,
queryable columns on event_pre_context (storm_magnitude, storm_tier) instead of
being recomputed in-memory every time multi_feature_model.py runs. Reuses the
EXACT same logic as get_storm_lookup() there, just writes it to the database
instead of returning an in-memory dict.

For each (event, entity) pair with real 5-day ripple data, computes the sum of
|abnormal_return| for every OTHER event on the same entity within +/-40 days
(excluding known-bundled summary events on both sides via event_component_dates),
then buckets into isolated/small/medium/large -- the same 4 tiers validated in the
original investigation (6 independent tests, see THEORY.md).

Real limitation, same as the model's version: requires day_offset=5 ripple rows,
so any (event, entity) pair without ripple data gets no storm_tier row -- same
known ripple-data gap documented elsewhere (EA, ~876 pre-existing events, etc.).

Usage:
    python scripts/financial_pipeline/populate_storm_tier.py --dry-run
    python scripts/financial_pipeline/populate_storm_tier.py --live
"""
import os
import sys
from collections import defaultdict
from datetime import date
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def paginated(table, select, order_by, filters=None):
    # REAL FIX: .range() with no stable .order() first does not guarantee
    # consistent row ordering across separate paginated requests on a large
    # table -- confirmed directly (first --live run produced scattered
    # duplicate (event_id, entity_id) pairs across every chunk despite
    # event_ripple_timeline itself having zero true duplicates). Same bug
    # class as any unpaginated-query issue, just the .order() variant.
    # order_by is required and caller-specified since not every table has
    # an "id" column (e.g. event_component_dates does not).
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


def tier_for(magnitude):
    if magnitude == 0.0:
        return "isolated"
    if magnitude < 0.02:
        return "small"
    if magnitude < 0.05:
        return "medium"
    return "large"


def compute_storm_data():
    print("Fetching bundled-event exclusion list...")
    bundled_ids = {r["event_id"] for r in paginated("event_component_dates", "event_id", "event_id")}
    print(f"  {len(bundled_ids)} bundled events excluded.")

    print("Fetching real 5-day ripple rows...")
    ripple_rows = paginated("event_ripple_timeline", "event_id,entity_id,abnormal_return,day_offset", "id")
    day5_by_entity = defaultdict(list)
    for r in ripple_rows:
        if r["day_offset"] == 5 and r["event_id"] not in bundled_ids and r["abnormal_return"] is not None:
            day5_by_entity[r["entity_id"]].append((r["event_id"], r["abnormal_return"]))
    print(f"  {sum(len(v) for v in day5_by_entity.values())} real (event, entity) day-5 rows across "
          f"{len(day5_by_entity)} entities.")

    events_dates = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date", "id")}

    print("Computing storm magnitude/tier for each real (event, entity) pair...")
    out = []
    for entity_id, event_returns in day5_by_entity.items():
        for this_event_id, _ in event_returns:
            if this_event_id in bundled_ids:
                continue
            this_date_str = events_dates.get(this_event_id)
            if not this_date_str:
                continue
            this_date = date.fromisoformat(this_date_str)
            magnitude = 0.0
            for other_event_id, other_return in event_returns:
                if other_event_id == this_event_id:
                    continue
                other_date_str = events_dates.get(other_event_id)
                if not other_date_str:
                    continue
                other_date = date.fromisoformat(other_date_str)
                if abs((other_date - this_date).days) <= 40:
                    magnitude += abs(other_return)
            out.append({
                "event_id": this_event_id, "entity_id": entity_id,
                "storm_magnitude": round(magnitude, 6), "storm_tier": tier_for(magnitude),
            })

    # Safety net: dedupe on (event_id, entity_id) in case anything upstream
    # ever produces a repeat -- Postgres ON CONFLICT DO UPDATE cannot apply
    # two updates to the same key within one statement.
    seen = {}
    for r in out:
        seen[(r["event_id"], r["entity_id"])] = r
    deduped = list(seen.values())
    if len(deduped) != len(out):
        print(f"  NOTE: deduped {len(out) - len(deduped)} repeated (event_id, entity_id) pair(s).")
    return deduped


def main():
    dry_run = "--live" not in sys.argv
    rows = compute_storm_data()
    print(f"\n{len(rows)} real (event, entity) pairs to write.")

    dist = defaultdict(int)
    for r in rows:
        dist[r["storm_tier"]] += 1
    print("Real tier distribution:")
    for t in ("isolated", "small", "medium", "large"):
        print(f"  {t}: {dist[t]}")

    if dry_run:
        print("\nDRY RUN -- nothing written. Pass --live to write.")
        return

    print("\nWriting to event_pre_context (upsert on event_id, entity_id)...")
    written, failed = 0, 0
    for i in range(0, len(rows), 500):
        chunk = rows[i:i + 500]
        try:
            supabase.table("event_pre_context").upsert(
                chunk, on_conflict="event_id,entity_id"
            ).execute()
            written += len(chunk)
        except Exception as e:
            print(f"  FAILED chunk {i}-{i+len(chunk)}: {e}")
            failed += len(chunk)
    print(f"\nDone. Written: {written}, Failed: {failed}.")


if __name__ == "__main__":
    main()
