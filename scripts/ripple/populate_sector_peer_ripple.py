"""
populate_sector_peer_ripple.py

Productionizes the validated sector-peer ripple finding (issue #21, z=17.49 at
n=1,215 in the original small-scale test -- see test_sector_peer_ripple.py and
THEORY.md) into a real, queryable table instead of leaving it as a one-off test
result. Reuses the EXACT same real methodology as test_sector_peer_ripple.py's
compute_abnormal_return() -- prior-trading-day baseline, SPY benchmark, +/-5
trading days -- no new calculation invented.

Real, deliberate scope (per the original recommendation: "a scoped build, large-
reaction events only, not a full unscoped rebuild"): only computes peer rows for
TRIGGER events with |abnormal_return_5d| >= 0.05 (the same "large" threshold
already established by storm_tier) on their own directly-linked entity. Full,
unscoped build was estimated at ~21M rows (44x event_ripple_timeline's size);
this scoped version is ~3,134 trigger events x ~45 average real sector peers
each =~ 141K rows -- real, sized, and tractable.

For each qualifying trigger event, computes EVERY real company in the trigger
entity's sector (not a 10-company sample like the original test) as a peer,
skipping the trigger entity itself.

Usage:
    python populate_sector_peer_ripple.py --dry-run
    python populate_sector_peer_ripple.py --live [--limit N]
"""
import os
import sys
from datetime import timedelta, date
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DAYS_BEFORE = 5
DAYS_AFTER = 5
LARGE_THRESHOLD = 0.05

_PRICE_HISTORY_CACHE = {}


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


def get_full_price_history(security_id):
    if security_id in _PRICE_HISTORY_CACHE:
        return _PRICE_HISTORY_CACHE[security_id]
    rows = paginated("market_prices", "price_date,adjusted_close", "price_date",
                      [lambda q: q.eq("security_id", security_id)])
    _PRICE_HISTORY_CACHE[security_id] = rows
    return rows


def compute_abnormal_return(security_id, spy_id, event_date):
    start = (date.fromisoformat(event_date) - timedelta(days=DAYS_BEFORE + 10)).isoformat()
    end = (date.fromisoformat(event_date) + timedelta(days=DAYS_AFTER + 10)).isoformat()

    company_prices = [r for r in get_full_price_history(security_id) if start <= r["price_date"] <= end]
    spy_prices = [r for r in get_full_price_history(spy_id) if start <= r["price_date"] <= end]
    if len(company_prices) < 5 or len(spy_prices) < 5:
        return None

    idx = next((i for i, p in enumerate(company_prices) if p["price_date"] >= event_date), None)
    spy_idx = next((i for i, p in enumerate(spy_prices) if p["price_date"] >= event_date), None)
    if idx is None or spy_idx is None or idx == 0 or spy_idx == 0:
        return None

    day5_c_idx = min(idx + DAYS_AFTER, len(company_prices) - 1)
    day5_spy_idx = min(spy_idx + DAYS_AFTER, len(spy_prices) - 1)

    baseline_c = company_prices[idx - 1]["adjusted_close"]
    baseline_spy = spy_prices[spy_idx - 1]["adjusted_close"]
    day5_c = company_prices[day5_c_idx]["adjusted_close"]
    day5_spy = spy_prices[day5_spy_idx]["adjusted_close"]

    raw_return = (day5_c / baseline_c) - 1
    spy_return = (day5_spy / baseline_spy) - 1
    return raw_return - spy_return


def get_trigger_events():
    rows = paginated(
        "event_ripple_timeline", "event_id,entity_id,ticker,sector,abnormal_return", "id",
        [lambda q: q.eq("day_offset", 5).not_.is_("abnormal_return", "null")],
    )
    return [r for r in rows if r["sector"] and abs(r["abnormal_return"]) >= LARGE_THRESHOLD]


def get_done_keys():
    rows = paginated("sector_peer_ripple", "trigger_event_id,peer_entity_id", "id")
    return {(r["trigger_event_id"], r["peer_entity_id"]) for r in rows}


def main():
    dry_run = "--live" not in sys.argv
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    print(f"Fetching trigger events (|abnormal_return_5d| >= {LARGE_THRESHOLD})...")
    triggers = get_trigger_events()
    print(f"  {len(triggers)} real trigger events.")
    if limit:
        triggers = triggers[:limit]
        print(f"  Limited to {len(triggers)} for this run.")

    print("Fetching real securities by sector...")
    securities = paginated("securities", "id,entity_id,ticker,sector", "id")
    # REAL FIX: dedupe by entity_id before grouping -- a company with multiple
    # securities (e.g. NWS/NWSA dual-class shares, confirmed the real cause of
    # every "ON CONFLICT DO UPDATE cannot affect row a second time" failure in
    # the first --live run) would otherwise appear twice in the same sector's
    # peer list, producing two output rows with the identical
    # (trigger_event_id, peer_entity_id) key. Same bug class as this project's
    # well-documented NWS/NWSA dedup issue elsewhere, just a new instance of it.
    seen_entities = set()
    by_sector = {}
    for s in securities:
        if s["sector"] and s["entity_id"] not in seen_entities:
            seen_entities.add(s["entity_id"])
            by_sector.setdefault(s["sector"], []).append(s)

    spy_id = supabase.table("securities").select("id").eq("ticker", "SPY").execute().data[0]["id"]

    done = get_done_keys() if not dry_run else set()
    print(f"  {len(done)} (trigger, peer) pairs already done.")

    events_dates = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date", "id")}

    out = []
    skipped_no_date = skipped_no_price = 0
    for i, trig in enumerate(triggers):
        event_date = events_dates.get(trig["event_id"])
        if not event_date:
            skipped_no_date += 1
            continue
        peers = [s for s in by_sector.get(trig["sector"], []) if s["entity_id"] != trig["entity_id"]]
        for peer in peers:
            key = (trig["event_id"], peer["entity_id"])
            if key in done:
                continue
            ar = compute_abnormal_return(peer["id"], spy_id, event_date)
            if ar is None:
                skipped_no_price += 1
                continue
            out.append({
                "trigger_event_id": trig["event_id"], "trigger_entity_id": trig["entity_id"],
                "trigger_ticker": trig["ticker"], "sector": trig["sector"],
                "trigger_abnormal_return_5d": trig["abnormal_return"],
                "peer_entity_id": peer["entity_id"], "peer_security_id": peer["id"],
                "peer_ticker": peer["ticker"], "peer_abnormal_return_5d": round(ar, 6),
            })
        if (i + 1) % 200 == 0:
            print(f"  ...{i+1}/{len(triggers)} trigger events processed, {len(out)} peer rows built so far")

    print(f"\n{len(out)} real (trigger, peer) rows to write.")
    print(f"Skipped: {skipped_no_date} (no event date), {skipped_no_price} (insufficient peer price data).")

    if dry_run:
        print("\nDRY RUN -- nothing written. Pass --live to write.")
        return

    print("\nWriting to sector_peer_ripple (upsert on trigger_event_id, peer_entity_id)...")
    written, failed = 0, 0
    for i in range(0, len(out), 500):
        chunk = out[i:i + 500]
        try:
            supabase.table("sector_peer_ripple").upsert(
                chunk, on_conflict="trigger_event_id,peer_entity_id"
            ).execute()
            written += len(chunk)
        except Exception as e:
            print(f"  FAILED chunk {i}-{i+len(chunk)}: {e}")
            failed += len(chunk)
    print(f"\nDone. Written: {written}, Failed: {failed}.")


if __name__ == "__main__":
    main()
