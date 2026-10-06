"""
populate_government_decision_exposure.py

Real, DIFFERENT methodology from check_event_exposure.py's global-events
template, by deliberate design (Galen's real framing): a government
decision isn't a one-off shock that spikes and fades -- it's a persistent
condition ("buff/debuff") applied continuously until the NEXT decision
replaces it. So the exposure window here is NOT a fixed 7 days -- it's the
real, variable-length period from this decision's date until the next real
decision's date (or today, for whichever decision is currently live).

Reuses check_event_exposure.py's PROVEN bulk-loading technique (that
script's own docstring documents a real N+1 crash it fixed -- 150,000+
individual requests) to avoid repeating that mistake: fetch the real
company list and ALL of company_sentiment_timeline once, then do every
real baseline/window computation as pure in-memory lookups.

Real, same baseline logic as the proven template: 30 real trailing days
before the decision. Real, genuinely different exposure window: variable-
length, decision_date through (next_decision_date - 1) or today.

Usage:
    python populate_government_decision_exposure.py --dry-run
    python populate_government_decision_exposure.py --live
"""
import os
import sys
from datetime import date, timedelta
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASELINE_WINDOW_DAYS = 30
MIN_DAYS_FOR_BASELINE = 10


def get_all_companies():
    # REAL FIX (2026-10-03): dedupe by entity_id before use -- a company
    # with multiple securities (e.g. NWS/NWSA dual-class shares) would
    # otherwise appear twice, producing two rows with the identical
    # (government_decision_id, entity_id) key. Same real bug, same real
    # fix already proven in populate_sector_peer_ripple.py.
    rows = []
    offset = 0
    while True:
        page = supabase.table("securities").select("entity_id,ticker,sector") \
            .neq("ticker", "SPY").order("entity_id") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    seen = set()
    deduped = []
    for r in rows:
        if r["entity_id"] not in seen:
            seen.add(r["entity_id"])
            deduped.append(r)
    return deduped


def get_all_sentiment_in_range(min_date, max_date):
    by_entity = defaultdict(list)
    offset = 0
    while True:
        page = supabase.table("company_sentiment_timeline") \
            .select("entity_id,date,avg_tone") \
            .gte("date", min_date).lte("date", max_date).order("id") \
            .range(offset, offset + 999).execute().data
        if not page:
            break
        for r in page:
            if r["avg_tone"] is not None:
                by_entity[r["entity_id"]].append((r["date"], r["avg_tone"]))
        if len(page) < 1000:
            break
        offset += 1000
    return by_entity


def tone_stats_in_window(entity_tones, start, end):
    tones = [t for d, t in entity_tones if start <= d <= end]
    if not tones:
        return None, None, 0
    mean = sum(tones) / len(tones)
    variance = sum((t - mean) ** 2 for t in tones) / len(tones)
    stdev = variance ** 0.5
    return mean, stdev, len(tones)


def main():
    live = "--live" in sys.argv
    today = date.today().isoformat()

    print("Fetching real government decisions, sorted by date...")
    decisions = sorted(
        supabase.table("government_decisions").select("id,decision_date").execute().data,
        key=lambda r: r["decision_date"],
    )
    print(f"  {len(decisions)} real decisions found.\n")

    # Real, variable-length exposure window per decision: this decision's
    # date through the day before the NEXT decision (or today, for the
    # most recent/still-live one).
    for i, dec in enumerate(decisions):
        dec["window_end"] = (
            date.fromisoformat(decisions[i + 1]["decision_date"]) - timedelta(days=1)
        ).isoformat() if i + 1 < len(decisions) else today

    min_date = (date.fromisoformat(decisions[0]["decision_date"]) - timedelta(days=BASELINE_WINDOW_DAYS)).isoformat()
    max_date = today
    print(f"Bulk-fetching real sentiment data once, {min_date} to {max_date}...")
    sentiment_by_entity = get_all_sentiment_in_range(min_date, max_date)
    print(f"  Real sentiment history for {len(sentiment_by_entity)} entities.\n")

    companies = get_all_companies()
    print(f"Real companies to test per decision: {len(companies)}\n")

    rows = []
    for dec in decisions:
        dec_date = date.fromisoformat(dec["decision_date"])
        baseline_start = (dec_date - timedelta(days=BASELINE_WINDOW_DAYS)).isoformat()
        baseline_end = (dec_date - timedelta(days=1)).isoformat()
        window_start = dec["decision_date"]
        window_end = dec["window_end"]

        n_exposed = 0
        for c in companies:
            entity_tones = sentiment_by_entity.get(c["entity_id"], [])
            base_mean, base_stdev, base_n = tone_stats_in_window(entity_tones, baseline_start, baseline_end)
            if base_n < MIN_DAYS_FOR_BASELINE:
                continue
            window_mean, _, window_n = tone_stats_in_window(entity_tones, window_start, window_end)
            if window_n == 0:
                continue
            deviation = window_mean - base_mean
            z = deviation / base_stdev if base_stdev and base_stdev > 0 else None
            rows.append({
                "government_decision_id": dec["id"],
                "entity_id": c["entity_id"],
                "ticker": c["ticker"],
                "sector": c["sector"],
                "baseline_avg_tone": round(base_mean, 4),
                "event_window_avg_tone": round(window_mean, 4),
                "tone_deviation": round(deviation, 4),
                "tone_z_score": round(z, 4) if z is not None else None,
                "baseline_days": base_n,
                "event_window_days": window_n,
            })
            n_exposed += 1
        print(f"  {dec['decision_date']} (live {window_start} to {window_end}): {n_exposed} real companies with data")

    print(f"\n{len(rows)} real (decision, company) exposure rows prepared.")
    if not live:
        print("\nDRY RUN -- nothing written. Pass --live to write.")
        return

    written = 0
    for i in range(0, len(rows), 500):
        chunk = rows[i:i + 500]
        supabase.table("government_decision_exposure").upsert(
            chunk, on_conflict="government_decision_id,entity_id"
        ).execute()
        written += len(chunk)
    print(f"\nReal write complete: {written} rows upserted.")


if __name__ == "__main__":
    main()
