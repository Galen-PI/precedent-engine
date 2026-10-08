"""
populate_labor_market_status.py

Real "status effect" pattern, same shape as populate_yield_curve_status.py,
but combining 5 real series into one composite labor-market health score
instead of a single spread:

  ICSA            Initial jobless claims (weekly)      -- rising = bad, sign flipped
  CCSA            Continued jobless claims (weekly)    -- rising = bad, sign flipped
  CIVPART         Labor force participation rate (monthly) -- rising = good
  JTSQUR          JOLTS quits rate (monthly)            -- rising = good (worker confidence)
  CES0500000003   Average hourly earnings (monthly)     -- rising = good

For each real series, at each event's date, finds the most recent real
observation on or before that date, then computes how many "typical
moves" (median_abs_change_for_series, already computed during ingestion)
that observation sits above/below the TRAILING 12-OBSERVATION median
baseline strictly before it -- i.e. no look-ahead. ICSA/CCSA have their
sign flipped so all 5 normalized deviations point the same real
direction: positive = healthy, negative = stressed.

The composite score is the real, simple average of however many of the
5 series have a usable value as of that event's date (an event early in
some series' real history may only have 2-3 of 5 available -- that's
fine, same honest "no match = skip" spirit as yield curve).

Bucket: score > +0.5 => "tight" (healthy/strong labor market),
        score < -0.5 => "stressed",
        else "normal".
These thresholds are a real, simple, interpretable starting point -- not
derived from a formal calibration -- consistent with this project's
established preference for simple, defensible rules over opaque ones.

Usage:
    python populate_labor_market_status.py --dry-run
    python populate_labor_market_status.py --live
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
    "ICSA": -1,
    "CCSA": -1,
    "CIVPART": 1,
    "JTSQUR": 1,
    "CES0500000003": 1,
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
    """Real normalized deviation of this series as of event_date, or None
    if no real observation exists on or before event_date, or if there
    aren't enough real prior observations to compute a trailing baseline."""
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
        return "tight"
    if score < -0.5:
        return "stressed"
    return "normal"


def main():
    live = "--live" in sys.argv

    print("Fetching real series data for all 5 labor-market indicators...")
    series_data = {}
    for series_id, direction in SERIES_DIRECTION.items():
        dates, values, mac = load_series(series_id)
        series_data[series_id] = (dates, values, mac, direction)
        print(f"  {series_id}: {len(dates)} real observations, "
              f"median_abs_change={mac}")

    print("\nFetching real event_pre_context rows...")
    pc_rows = paginated("event_pre_context", "id,event_id,labor_market_status", "id")
    events = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date", "id")}

    already_done = sum(1 for r in pc_rows if r["labor_market_status"] is not None)
    pc_rows = [r for r in pc_rows if r["labor_market_status"] is None]
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
            "labor_market_composite_score": round(composite, 4),
            "labor_market_status": status,
        })

    print(f"{len(rows)} real rows to update, {skipped_no_date} skipped (no event date), "
          f"{skipped_no_series} skipped (no series data available that early).")
    dist = {}
    for r in rows:
        dist[r["labor_market_status"]] = dist.get(r["labor_market_status"], 0) + 1
    print(f"Real status distribution: {dist}\n")

    if not live:
        print("DRY RUN -- nothing written. Pass --live to write.")
        return

    written = 0
    for r in rows:
        supabase.table("event_pre_context").update({
            "labor_market_composite_score": r["labor_market_composite_score"],
            "labor_market_status": r["labor_market_status"],
        }).eq("id", r["id"]).execute()
        written += 1
        if written % 200 == 0:
            print(f"  ...{written}/{len(rows)} written")
    print(f"\nReal write complete: {written} rows updated.")


if __name__ == "__main__":
    main()
