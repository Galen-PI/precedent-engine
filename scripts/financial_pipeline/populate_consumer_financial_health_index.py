"""
populate_consumer_financial_health_index.py

Real composite monthly index combining 8 series into one "consumer
financial health" score -- architecturally different from
populate_labor_market_status.py / populate_housing_status.py, which
thread a status onto specific company EVENTS via event_pre_context. This
one builds a continuous MONTHLY index (its own table,
consumer_financial_health_index) instead, because the real question it
answers isn't "what was the regime when this one event happened" but
"does the populace have money to spend this month" -- meant for ongoing
correlation against consumer-exposed companies (Consumer Discretionary
vs Consumer Staples GICS sectors), ONE MONTH AT A TIME, not threaded to
individual events. That correlation test itself is a separate, later
Phase 6 analysis step, not built here.

REAL METHODOLOGY CORRECTION (2026-10-08): the first version compared
every series' raw LEVEL against its own trailing 12-observation median.
This produced a genuinely broken, degenerate result (88% "healthy") for
one real reason: several of these series have real structural upward
drift over decades (nominal income, credit, retail sales all trend up
from population growth and inflation, independent of whether the
economy is actually healthy) -- a trailing-12-month median lags behind
a steady uptrend, so these series read as "above baseline" almost
permanently, masking any real signal. Labor market and housing didn't
have this problem because claims, housing starts, and mortgage rates
don't have that kind of persistent structural trend.

Real fix: series with structural drift are transformed to YEAR-OVER-YEAR
PERCENT CHANGE first (comparing each value to the real observation
closest to 365 days prior, found via bisect on actual dates --
frequency-aware, not a fixed index offset, since these series span
weekly/monthly/quarterly), and the SAME trailing-12-baseline deviation
technique is then applied to that YoY series instead of the raw level.
This asks "is growth accelerating/decelerating relative to its own
recent normal", not "is the level above average" -- the right real
question for a series that's supposed to keep growing.

  PSAVERT     Personal savings rate         +1  raw level  (stationary ratio)
  A229RX0     Real disposable income/capita +1  YoY %      (structural drift)
  TOTALSL     Consumer credit outstanding   +1  YoY %      (structural drift)
  CDSP        Consumer debt service ratio   -1  raw level  (stationary ratio)
  RSAFS       Retail sales                  +1  YoY %      (structural drift)
  PCECC96     Real PCE                      +1  YoY %      (structural drift)
  GASREGW     Gas price                     -1  YoY %      (decades of inflation drift)
  DRCCLACBS   Credit card delinquency rate  -1  raw level  (stationary ratio)

Bucket: score > +0.5 => "healthy", score < -0.5 => "stressed", else "normal".

Usage:
    python populate_consumer_financial_health_index.py --dry-run
    python populate_consumer_financial_health_index.py --live
"""
import os
import sys
import bisect
from datetime import date, timedelta
from statistics import median
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SERIES_DIRECTION = {
    "PSAVERT": 1,
    "A229RX0": 1,
    "TOTALSL": 1,
    "CDSP": -1,
    "RSAFS": 1,
    "PCECC96": 1,
    "GASREGW": -1,
    "DRCCLACBS": -1,
}

USE_YOY = {"A229RX0", "TOTALSL", "RSAFS", "PCECC96", "GASREGW"}

TRAILING_WINDOW = 12
EARLIEST_MONTH = date(1994, 1, 1)


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


def to_yoy(dates_str, values):
    """Real, frequency-aware YoY transform: for each real observation,
    find the real prior observation closest to 365 days earlier (via
    bisect on actual dates, not a fixed index offset -- these series
    span weekly/monthly/quarterly), and compute percent change from it.
    Skips points with no real prior-year observation available."""
    date_objs = [date.fromisoformat(d) for d in dates_str]
    yoy_dates, yoy_values = [], []
    for i, d in enumerate(date_objs):
        target = d - timedelta(days=365)
        j = bisect.bisect_left(date_objs, target)
        # pick whichever of j-1/j is real, closest to target
        candidates = [k for k in (j - 1, j) if 0 <= k < i]
        if not candidates:
            continue
        j = min(candidates, key=lambda k: abs((date_objs[k] - target).days))
        prior_value = values[j]
        if prior_value == 0:
            continue
        pct_change = (values[i] - prior_value) / abs(prior_value) * 100
        yoy_dates.append(dates_str[i])
        yoy_values.append(pct_change)
    return yoy_dates, yoy_values


def compute_mac(values):
    if len(values) < 2:
        return None
    diffs = [abs(values[i] - values[i - 1]) for i in range(1, len(values))]
    return median(diffs)


def load_series(series_id):
    rows = paginated("macro_data_releases", "release_date,value", "release_date",
                      [lambda q: q.eq("series_id", series_id)])
    rows = sorted(rows, key=lambda r: r["release_date"])
    dates = [str(r["release_date"])[:10] for r in rows]
    values = [float(r["value"]) for r in rows]

    if series_id in USE_YOY:
        dates, values = to_yoy(dates, values)

    mac = compute_mac(values)
    return dates, values, mac


def deviation_as_of(dates, values, mac, direction, as_of_date):
    idx = bisect.bisect_right(dates, as_of_date) - 1
    if idx < TRAILING_WINDOW:
        return None
    current = values[idx]
    baseline = median(values[idx - TRAILING_WINDOW:idx])
    if not mac or mac == 0:
        return None
    return direction * (current - baseline) / mac


def classify(score):
    if score > 0.5:
        return "healthy"
    if score < -0.5:
        return "stressed"
    return "normal"


def month_range(start, end):
    months = []
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        months.append(date(y, m, 1))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return months


def main():
    live = "--live" in sys.argv

    print("Fetching real series data for all 8 Consumer Financial Health indicators...")
    series_data = {}
    for series_id, direction in SERIES_DIRECTION.items():
        dates, values, mac = load_series(series_id)
        mode = "YoY %" if series_id in USE_YOY else "raw level"
        series_data[series_id] = (dates, values, mac, direction)
        print(f"  {series_id} ({mode}): {len(dates)} real usable observations, "
              f"median_abs_change={mac}")

    print("\nFetching real, already-written index dates...")
    existing = paginated("consumer_financial_health_index", "index_date", "index_date")
    existing_dates = {str(r["index_date"])[:10] for r in existing}
    print(f"  {len(existing_dates)} real months already filled.\n")

    today = date.today()
    months = month_range(EARLIEST_MONTH, today)
    months = [m for m in months if m.isoformat() not in existing_dates]
    print(f"{len(months)} real months to compute.\n")

    rows = []
    for month in months:
        as_of = month.isoformat()
        deviations = {}
        for series_id, (dates, values, mac, direction) in series_data.items():
            dev = deviation_as_of(dates, values, mac, direction, as_of)
            deviations[series_id] = dev

        usable = [v for v in deviations.values() if v is not None]
        if not usable:
            continue
        composite = sum(usable) / len(usable)
        status = classify(composite)

        row = {
            "index_date": as_of,
            "composite_score": round(composite, 4),
            "status": status,
        }
        for series_id in SERIES_DIRECTION:
            col = series_id.lower() + "_deviation"
            v = deviations[series_id]
            row[col] = round(v, 4) if v is not None else None
        rows.append(row)

    print(f"{len(rows)} real rows to write.")
    dist = {}
    for r in rows:
        dist[r["status"]] = dist.get(r["status"], 0) + 1
    print(f"Real status distribution: {dist}\n")

    if not live:
        print("DRY RUN -- nothing written. Pass --live to write.")
        return

    written = 0
    for r in rows:
        supabase.table("consumer_financial_health_index").insert(r).execute()
        written += 1
        if written % 50 == 0:
            print(f"  ...{written}/{len(rows)} written")
    print(f"\nReal write complete: {written} rows written.")


if __name__ == "__main__":
    main()
