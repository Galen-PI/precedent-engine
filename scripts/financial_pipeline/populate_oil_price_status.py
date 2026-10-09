"""
populate_oil_price_status.py

Real "status effect" pattern, same shape as populate_labor_market_status.py
and populate_housing_status.py, but for a single series (DCOILWTICO,
WTI crude oil daily spot price) -- deliberately framed differently from
those two. Labor market and housing have a real, defensible "healthier
vs. weaker" direction; oil price does not -- a spike helps energy
producers and hurts airlines/consumers, a crash does the reverse. So
this is a real VOLATILITY/SHOCK regime (spike/crash/normal), not a
directional health score -- the magnitude of deviation matters, not a
signed "good/bad" direction.

Same real methodology as labor/housing: deviation from the trailing
12-observation baseline, normalized by the series' own real
median_abs_change_for_series (already computed during ingestion).

REAL METHODOLOGY CORRECTION: the first version used the same +-0.5
threshold as labor/housing. This was badly wrong for oil specifically --
a direct check confirmed 85.2% of ALL real trading days (not just
events) exceed |0.5| deviation, because oil's real day-to-day
volatility is far higher than labor/housing's monthly-cadence series.
+-0.5 made "spike" the default state, not a genuine signal.

Real fix: computed the actual real deviation distribution across all
8,209 real trading days and picked a threshold near the real 20th/80th
percentile (-2.70 / +3.13) instead of reusing an unexamined constant --
+-3.0 gives a genuinely meaningful split (roughly 20% spike, 20% crash,
60% normal) reflecting where oil's real day-to-day moves actually
become unusual for THIS series, not an assumption carried over from a
different one.

Bucket: deviation > +3.0 (in units of typical moves) => "spike",
        deviation < -3.0 => "crash",
        else "normal".

Usage:
    python populate_oil_price_status.py --dry-run
    python populate_oil_price_status.py --live
"""
import os
import sys
import bisect
from statistics import median
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SERIES_ID = "DCOILWTICO"
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


def deviation_as_of(dates, values, mac, event_date):
    idx = bisect.bisect_right(dates, event_date) - 1
    if idx < TRAILING_WINDOW:
        return None
    current = values[idx]
    baseline = median(values[idx - TRAILING_WINDOW:idx])
    if not mac or mac == 0:
        return None
    return (current - baseline) / mac


def classify(score):
    if score > 3.0:
        return "spike"
    if score < -3.0:
        return "crash"
    return "normal"


def main():
    live = "--live" in sys.argv

    print(f"Fetching real {SERIES_ID} data...")
    dates, values, mac = load_series(SERIES_ID)
    print(f"  {len(dates)} real observations, median_abs_change={mac}\n")

    print("Fetching real event_pre_context rows...")
    pc_rows = paginated("event_pre_context", "id,event_id,oil_price_status", "id")
    events = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date", "id")}

    already_done = sum(1 for r in pc_rows if r["oil_price_status"] is not None)
    pc_rows = [r for r in pc_rows if r["oil_price_status"] is None]
    print(f"  {already_done} real rows already filled (skipping), {len(pc_rows)} real rows remaining.\n")

    rows = []
    skipped_no_date = 0
    skipped_no_data = 0
    for pc in pc_rows:
        event_date = events.get(pc["event_id"])
        if not event_date:
            skipped_no_date += 1
            continue

        dev = deviation_as_of(dates, values, mac, event_date)
        if dev is None:
            skipped_no_data += 1
            continue

        status = classify(dev)
        rows.append({
            "id": pc["id"],
            "oil_price_deviation": round(dev, 4),
            "oil_price_status": status,
        })

    print(f"{len(rows)} real rows to update, {skipped_no_date} skipped (no event date), "
          f"{skipped_no_data} skipped (no oil price data available that early).")
    dist = {}
    for r in rows:
        dist[r["oil_price_status"]] = dist.get(r["oil_price_status"], 0) + 1
    print(f"Real status distribution: {dist}\n")

    if not live:
        print("DRY RUN -- nothing written. Pass --live to write.")
        return

    written = 0
    for r in rows:
        supabase.table("event_pre_context").update({
            "oil_price_deviation": r["oil_price_deviation"],
            "oil_price_status": r["oil_price_status"],
        }).eq("id", r["id"]).execute()
        written += 1
        if written % 200 == 0:
            print(f"  ...{written}/{len(rows)} written")
    print(f"\nReal write complete: {written} rows updated.")


if __name__ == "__main__":
    main()
