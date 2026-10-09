"""
check_decision_exposure_fixed_window.py

Real, fixed-window exposure check for executive orders and enacted laws
-- deliberately DIFFERENT from populate_government_decision_exposure.py
(FOMC's variable-length "until the next decision" model), per the real
design discussion with Galen 2026-10-09: with 7,992 non-FOMC decisions
instead of 31, a shared "until the next decision" timeline would shrink
most windows to 0-1 days (laws/EOs land close together), which can't
capture any real signal. Most individual laws/EOs also aren't
genuinely regime-setting the way a rate decision is -- a short, fixed
window (the SAME 7-day template already proven in
check_event_exposure.py for global events) fits them better.

Writes into the SAME existing government_decision_exposure table FOMC
already uses (it stores event_window_days per row, so it already
supports mixed window lengths) -- distinguishable from FOMC's rows via
the real event_window_days value (7 here, variable there) and
traceable back to decision_type via the government_decision_id join.

Real, deliberate scope: only decisions already marked
relevance_verdict = 'relevant' by classify_decision_relevance.py are
processed -- running exposure checks against the ~5,000 not_relevant
rows (commemorative bills, etc.) would be real wasted compute with no
real signal to find.

Reuses check_event_exposure.py's proven bulk-loading technique directly
(same real N+1 crash it fixed applies here at even larger scale) --
fetch companies and ALL of company_sentiment_timeline once, then do
every decision's baseline/window tone computation as pure in-memory
lookups. Same real baseline (30 days trailing), same 7-day window, same
z-score formula, same batched-upsert-per-decision write pattern.

Usage:
    python check_decision_exposure_fixed_window.py --dry-run
    python check_decision_exposure_fixed_window.py --live
"""
import os
import sys
from datetime import date, timedelta
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

EVENT_WINDOW_DAYS = 7
BASELINE_WINDOW_DAYS = 30
MIN_DAYS_FOR_BASELINE = 10


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


def get_all_companies():
    rows = paginated("securities", "entity_id,ticker,sector", "entity_id",
                      [lambda q: q.neq("ticker", "SPY")])
    seen, deduped = set(), []
    for r in rows:
        if r["entity_id"] not in seen:
            seen.add(r["entity_id"])
            deduped.append(r)
    return deduped


def get_all_sentiment_in_range(min_date, max_date):
    by_entity = defaultdict(list)
    rows = paginated("company_sentiment_timeline", "entity_id,date,avg_tone", "entity_id",
                      [lambda q: q.gte("date", min_date).lte("date", max_date)])
    for r in rows:
        if r["avg_tone"] is not None:
            by_entity[r["entity_id"]].append((r["date"], r["avg_tone"]))
    return by_entity


def tone_stats_in_window(entity_tones, start, end):
    tones = [t for d, t in entity_tones if start <= d <= end]
    if not tones:
        return None, None, 0
    mean = sum(tones) / len(tones)
    variance = sum((t - mean) ** 2 for t in tones) / len(tones)
    return mean, variance ** 0.5, len(tones)


def get_already_processed_decision_ids():
    # REAL FIX (2026-10-09): event_window_days is NOT the calendar window
    # length -- same real field semantics as the original
    # check_event_exposure.py template this was copied from -- it's the
    # COUNT of real sentiment data points found in the window, which
    # varies per decision. Filtering on it as if it equaled the constant
    # 7 would only catch decisions that happened to have exactly 7 real
    # data points, not "already processed with this fixed-window script"
    # -- caught via a direct DB check after the first live run (151,963
    # written, confirmed correct via a join to decision_type, but only
    # 19,518 had event_window_days==7). The write itself was fine; only
    # this resume-detection filter was wrong, so fixing it now before any
    # future re-run could rely on it. No real government_decision_id
    # collision risk between this and FOMC's rows -- the caller's own
    # decisions list is already filtered to non-FOMC, so simply checking
    # ANY existing government_decision_id in the exposure table is safe.
    rows = paginated("government_decision_exposure", "government_decision_id", "government_decision_id")
    return {r["government_decision_id"] for r in rows if r["government_decision_id"]}


def check_decision(decision, live, companies, sentiment_by_entity):
    dec_date = date.fromisoformat(str(decision["decision_date"])[:10])
    window_start = dec_date
    window_end = dec_date + timedelta(days=EVENT_WINDOW_DAYS)
    baseline_end = dec_date - timedelta(days=1)
    baseline_start = dec_date - timedelta(days=BASELINE_WINDOW_DAYS)

    results = []
    for c in companies:
        entity_id = c["entity_id"]
        entity_tones = sentiment_by_entity.get(entity_id, [])
        baseline_tone, baseline_stdev, baseline_n = tone_stats_in_window(
            entity_tones, baseline_start.isoformat(), baseline_end.isoformat())
        if baseline_tone is None or baseline_n < MIN_DAYS_FOR_BASELINE:
            continue
        window_tone, _, window_n = tone_stats_in_window(
            entity_tones, window_start.isoformat(), window_end.isoformat())
        if window_tone is None:
            continue

        deviation = window_tone - baseline_tone
        z_score = deviation / baseline_stdev if baseline_stdev > 0 else None
        results.append({
            "entity_id": entity_id, "ticker": c["ticker"], "sector": c.get("sector"),
            "baseline_avg_tone": baseline_tone, "event_window_avg_tone": window_tone,
            "tone_deviation": deviation, "tone_z_score": z_score,
            "baseline_days": baseline_n, "event_window_days": window_n,
        })

    if live and results:
        rows_to_write = [{
            "government_decision_id": decision["id"],
            "entity_id": r["entity_id"], "ticker": r["ticker"], "sector": r["sector"],
            "baseline_avg_tone": r["baseline_avg_tone"],
            "event_window_avg_tone": r["event_window_avg_tone"],
            "tone_deviation": r["tone_deviation"], "tone_z_score": r["tone_z_score"],
            "baseline_days": r["baseline_days"], "event_window_days": r["event_window_days"],
        } for r in results]
        supabase.table("government_decision_exposure").upsert(
            rows_to_write, on_conflict="government_decision_id,entity_id"
        ).execute()

    return len(results)


def main():
    live = "--live" in sys.argv

    print("Fetching real, relevant non-FOMC government decisions...")
    decisions = paginated(
        "government_decisions", "id,decision_date,title,structured_data", "decision_date",
        [lambda q: q.neq("decision_type", "interest_rate")],
    )
    decisions = [d for d in decisions if d["structured_data"].get("relevance_verdict") == "relevant"]
    print(f"  {len(decisions)} real relevant decisions found.\n")

    already_done = get_already_processed_decision_ids() if live else set()
    if already_done:
        before = len(decisions)
        decisions = [d for d in decisions if d["id"] not in already_done]
        print(f"Resuming: {before - len(decisions)} decision(s) already have real fixed-window exposure rows, skipping.\n")

    if not decisions:
        print("Nothing to process.")
        return

    companies = get_all_companies()
    dates = [date.fromisoformat(str(d["decision_date"])[:10]) for d in decisions]
    min_date = (min(dates) - timedelta(days=BASELINE_WINDOW_DAYS)).isoformat()
    max_date = (max(dates) + timedelta(days=EVENT_WINDOW_DAYS)).isoformat()
    print(f"Bulk-loading real sentiment data for {len(companies)} companies, {min_date} to {max_date}...")
    sentiment_by_entity = get_all_sentiment_in_range(min_date, max_date)
    print(f"Loaded {sum(len(v) for v in sentiment_by_entity.values())} real sentiment rows across "
          f"{len(sentiment_by_entity)} companies with any coverage.\n")

    print(f"Checking exposure for {len(decisions)} decision(s){' (LIVE writes)' if live else ' (dry run)'}...")
    total_rows = 0
    for i, decision in enumerate(decisions):
        n = check_decision(decision, live, companies, sentiment_by_entity)
        total_rows += n
        if (i + 1) % 200 == 0:
            print(f"  ...{i + 1}/{len(decisions)} decisions processed, {total_rows} real exposure rows so far")

    print(f"\nReal check complete: {len(decisions)} decisions processed, {total_rows} real exposure rows "
          f"{'written' if live else 'would be written (dry run)'}.")


if __name__ == "__main__":
    main()
