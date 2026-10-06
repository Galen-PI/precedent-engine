"""
populate_yield_curve_status.py

Real, first instance of the "status effect" pattern applied deliberately
outside government_decisions, per the real design principle Galen raised:
a persistent macro condition (inverted vs. normal yield curve), not a
one-off snapshot -- same real shape as regime and firm_state, just a new
signal.

Real spread: 10-year minus 2-year Treasury yield (DGS10 - DGS2), the
standard, most widely-cited real inversion metric. Confirmed directly:
8,194 real days of overlapping data since 1994, 12.6% genuinely inverted
-- real, non-trivial variance, not a degenerate feature.

For each real (event, entity) pair in event_pre_context, looks up the
real, most recent spread value on or before the event's date and stores
both the raw spread and a simple inverted/normal status.

Usage:
    python populate_yield_curve_status.py --dry-run
    python populate_yield_curve_status.py --live
"""
import os
import sys
from datetime import date
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


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


def main():
    live = "--live" in sys.argv

    print("Fetching real DGS10 and DGS2 data once...")
    d10_rows = paginated("macro_data_releases", "release_date,value", "id",
                          [lambda q: q.eq("series_id", "DGS10")])
    d2_rows = paginated("macro_data_releases", "release_date,value", "id",
                         [lambda q: q.eq("series_id", "DGS2")])
    d10_by_date = {str(r["release_date"])[:10]: r["value"] for r in d10_rows}
    d2_by_date = {str(r["release_date"])[:10]: r["value"] for r in d2_rows}

    real_dates = sorted(set(d10_by_date) & set(d2_by_date))
    spreads = [(d, d10_by_date[d] - d2_by_date[d]) for d in real_dates]
    print(f"  {len(spreads)} real overlapping days computed.\n")

    print("Fetching real event_pre_context rows...")
    pc_rows = paginated("event_pre_context", "id,event_id,entity_id,yield_curve_status", "id")
    events = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date", "id")}
    # REAL FIX (2026-10-03): no resume logic meant every re-run after a
    # crash started over from row 1, silently discarding real prior
    # progress and making the "filled" count a useless way to track a
    # given run -- confirmed directly (CPU time climbing, DB count frozen
    # for several real minutes, because it was re-walking already-filled
    # rows before reaching new ones). Real fix: skip rows that already
    # have a real yield_curve_status set.
    already_done = sum(1 for r in pc_rows if r["yield_curve_status"] is not None)
    pc_rows = [r for r in pc_rows if r["yield_curve_status"] is None]
    print(f"  {already_done} real rows already filled (skipping), {len(pc_rows)} real rows remaining.\n")

    import bisect
    spread_dates = [d for d, _ in spreads]
    spread_values = [v for _, v in spreads]

    rows = []
    skipped = 0
    for pc in pc_rows:
        event_date = events.get(pc["event_id"])
        if not event_date:
            skipped += 1
            continue
        idx = bisect.bisect_right(spread_dates, event_date) - 1
        if idx < 0:
            skipped += 1
            continue
        spread = spread_values[idx]
        status = "inverted" if spread < 0 else "normal"
        rows.append({"id": pc["id"], "yield_curve_spread": round(spread, 4), "yield_curve_status": status})

    print(f"{len(rows)} real rows to update, {skipped} skipped (no real date match).")
    dist = {}
    for r in rows:
        dist[r["yield_curve_status"]] = dist.get(r["yield_curve_status"], 0) + 1
    print(f"Real status distribution: {dist}\n")

    if not live:
        print("DRY RUN -- nothing written. Pass --live to write.")
        return

    written = 0
    for i, r in enumerate(rows):
        supabase.table("event_pre_context").update({
            "yield_curve_spread": r["yield_curve_spread"],
            "yield_curve_status": r["yield_curve_status"],
        }).eq("id", r["id"]).execute()
        written += 1
        if written % 200 == 0:
            print(f"  ...{written}/{len(rows)} written")
    print(f"\nReal write complete: {written} rows updated.")


if __name__ == "__main__":
    main()
