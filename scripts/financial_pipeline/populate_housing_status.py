"""
populate_housing_status.py

Real "status effect" pattern, same shape as populate_labor_market_status.py:
combines 3 real national series into one composite housing-market health
score (the state-level price indexes are deliberately NOT folded into
this national composite -- they answer a different, regional question
that needs a company-to-state mapping, a separate real task; they're
left as raw data in macro_data_releases for that future work):

  HOUST          Housing starts (monthly)              -- rising = good (construction activity)
  MSACSR         New home months' supply (monthly)      -- rising = bad (unsold inventory piling up vs. demand)
  MORTGAGE30US   30-year mortgage rate (weekly)          -- rising = bad (cools borrowing/demand)

Same real methodology as labor market: each series' deviation from its
own trailing 12-observation baseline, normalized by its own real
median_abs_change_for_series, with MSACSR/MORTGAGE30US sign-flipped so
all 3 point the same direction (positive = healthy/hot, negative = weak/cold).

Bucket: score > +0.5 => "hot", score < -0.5 => "cold", else "normal".
Same real, simple, interpretable threshold choice as labor market -- not
formally calibrated, consistent with this project's established
preference for simple, defensible rules.

Usage:
    python populate_housing_status.py --dry-run
    python populate_housing_status.py --live
"""
import os
import sys
import bisect
from statistics import median
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SERIES_DIRECTION = {
    "HOUST": 1,
    "MSACSR": -1,
    "MORTGAGE30US": -1,
}

TRAILING_WINDOW = 12


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


def load_series(series_id):
    rows = paginated("macro_data_releases", "release_date,value,median_abs_change_for_series", "release_date",
                      [lambda q: q.eq("series_id", series_id)])
    rows = sorted(rows, key=lambda r: r["release_date"])
    dates = [str(r["release_date"])[:10] for r in rows]
    values = [float(r["value"]) for r in rows]
    mac = float(rows[0]["median_abs_change_for_series"]) if rows else None
    return dates, values, mac


def deviation_as_of(dates, values, mac, direction, event_date):
    idx = bisect.bisect_right(dates, event_date) - 1
    if idx < TRAILING_WINDOW:
        return None
    current = values[idx]
    baseline = median(values[idx - TRAILING_WINDOW:idx])
    if not mac or mac == 0:
        return None
    return direction * (current - baseline) / mac


def classify(score):
    if score > 0.5:
        return "hot"
    if score < -0.5:
        return "cold"
    return "normal"


def main():
    live = "--live" in sys.argv

    print("Fetching real series data for all 3 housing-market indicators...")
    series_data = {}
    for series_id, direction in SERIES_DIRECTION.items():
        dates, values, mac = load_series(series_id)
        series_data[series_id] = (dates, values, mac, direction)
        print(f"  {series_id}: {len(dates)} real observations, "
              f"median_abs_change={mac}")

    print("\nFetching real event_pre_context rows...")
    pc_rows = paginated("event_pre_context", "id,event_id,housing_market_status", "id")
    events = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date", "id")}

    already_done = sum(1 for r in pc_rows if r["housing_market_status"] is not None)
    pc_rows = [r for r in pc_rows if r["housing_market_status"] is None]
    print(f"  {already_done} real rows already filled (skipping), {len(pc_rows)} real rows remaining.\n")

    rows = []
    skipped_no_date = 0
    skipped_no_series = 0
    for pc in pc_rows:
        event_date = events.get(pc["event_id"])
        if not event_date:
            skipped_no_date += 1
            continue

        deviations = []
        for series_id, (dates, values, mac, direction) in series_data.items():
            dev = deviation_as_of(dates, values, mac, direction, event_date)
            if dev is not None:
                deviations.append(dev)

        if not deviations:
            skipped_no_series += 1
            continue

        composite = sum(deviations) / len(deviations)
        status = classify(composite)
        rows.append({
            "id": pc["id"],
            "housing_market_composite_score": round(composite, 4),
            "housing_market_status": status,
        })

    print(f"{len(rows)} real rows to update, {skipped_no_date} skipped (no event date), "
          f"{skipped_no_series} skipped (no series data available that early).")
    dist = {}
    for r in rows:
        dist[r["housing_market_status"]] = dist.get(r["housing_market_status"], 0) + 1
    print(f"Real status distribution: {dist}\n")

    if not live:
        print("DRY RUN -- nothing written. Pass --live to write.")
        return

    # REVERTED (2026-10-08): batched upsert() is NOT a safe substitute for
    # per-row update() here -- upsert() replaces the WHOLE row, not just
    # the listed columns, and a real production error confirmed this:
    # Supabase returned a failing-row dump showing every other column
    # (event_id, entity_id, firm_state_label, etc.) set to NULL except
    # the 3 fields in the payload. The batch happened to fail atomically
    # on a pre-existing orphaned row (NULL event_id, a genuine prior data
    # issue, not caused by this script) before anything was written, so
    # no real corruption occurred -- confirmed directly via SQL -- but a
    # batch that didn't hit a NOT-NULL violation would have silently
    # wiped out every other column on those rows. Back to safe,
    # isolated per-row update() -- slower, but correct.
    written = 0
    for r in rows:
        supabase.table("event_pre_context").update({
            "housing_market_composite_score": r["housing_market_composite_score"],
            "housing_market_status": r["housing_market_status"],
        }).eq("id", r["id"]).execute()
        written += 1
        if written % 200 == 0:
            print(f"  ...{written}/{len(rows)} written")
    print(f"\nReal write complete: {written} rows updated.")


if __name__ == "__main__":
    main()
