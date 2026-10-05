"""
time_to_threshold_confidence_test.py

Real, different reframing of the multi-horizon confidence question, after
two prior attempts hit real, different problems (fixed threshold confounds
window length with signal; percentile threshold stops measuring the same
thing the original validated finding used, so it can't reproduce it as a
sanity check). Neither was "wrong" exactly -- the classification-at-a-
snapshot framing itself was the problem.

Real reframing: instead of asking "at exactly day N, is this event
punished," ask "for events that DO eventually cross the real, meaningful
-3% bar at some point, how many days does it take to get there -- and does
falling confidence make that happen FASTER or SLOWER?" This tests the
user's real original intuition (does the reaction develop quickly then
fade, or build slowly) directly, using the SAME real, externally meaningful
-3% threshold at every comparison -- no different threshold per horizon
needed, so the mechanical confound from both prior attempts cannot occur
here by construction.

Real population: same as the validated confidence_trend test (events from
2020 onward with a real reaction_character tag). Real data source:
event_ripple_timeline's daily coverage, day_offset 1-39 (confirmed real max).

Usage:
    python time_to_threshold_confidence_test.py
"""
import os
from datetime import date
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

PUNISHED_THRESHOLD = -0.03
REWARDED_THRESHOLD = 0.03
CONFIDENCE_TREND_THRESHOLD = 1.0


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


def get_confidence_by_month():
    rows = paginated("macro_data_releases", "release_date,value", "id",
                      [lambda q: q.eq("series_id", "UMCSENT")])
    by_month = {}
    for r in rows:
        d = date.fromisoformat(str(r["release_date"])[:10])
        by_month[(d.year, d.month)] = r["value"]
    return by_month


def get_real_policy_decisions():
    """Real, structured Fed policy decisions -- every real rate CHANGE
    (not every observation), with its real direction. Used to determine
    the real, most recent policy stance (hiking/cutting) as of any event
    date, rather than parsing statement text qualitatively."""
    rows = paginated("macro_data_releases", "release_date,change_from_previous", "id",
                      [lambda q: q.eq("series_id", "DFEDTARU").neq("change_from_previous", 0)])
    return sorted(
        [(date.fromisoformat(str(r["release_date"])[:10]), r["change_from_previous"]) for r in rows],
        key=lambda x: x[0],
    )


def get_policy_stance(event_date_str, decisions):
    """Real policy stance as of event_date: the direction of the most
    recent real rate change before this date. 'none_yet' if this event
    predates the first real decision in our data (2015-12-16)."""
    d = date.fromisoformat(event_date_str)
    most_recent = None
    for dec_date, change in decisions:
        if dec_date >= d:
            break
        most_recent = change
    if most_recent is None:
        return "none_yet"
    return "hiking" if most_recent > 0 else "cutting"


def get_confidence_trend(event_date_str, by_month):
    d = date.fromisoformat(event_date_str)
    this_month = by_month.get((d.year, d.month))
    prior_year, prior_month = (d.year, d.month - 1) if d.month > 1 else (d.year - 1, 12)
    prior = by_month.get((prior_year, prior_month))
    if this_month is None or prior is None:
        return None
    delta = this_month - prior
    if delta > CONFIDENCE_TREND_THRESHOLD:
        return "rising"
    if delta < -CONFIDENCE_TREND_THRESHOLD:
        return "falling"
    return "stable"


def get_real_population(start_date="2020-01-01", end_date=None):
    """Same real population as walk_forward_consumer_confidence.py: events
    from 2020+ with a real reaction_character tag. Real date range is now
    configurable, to test robustness across different real sub-periods."""
    tag_ids = {t["name"]: t["id"] for t in supabase.table("tags").select("id,name")
               .in_("name", ["rewarded", "punished", "muted"]).execute().data}
    event_tags = paginated("event_tags", "event_id,tag_id", "event_id",
                            [lambda q: q.in_("tag_id", list(tag_ids.values()))])
    tagged_event_ids = {r["event_id"] for r in event_tags}

    entity_reactions = paginated("event_entity_reactions", "event_id,entity_id", "id")
    entity_map = defaultdict(list)
    for r in entity_reactions:
        entity_map[r["event_id"]].append(r["entity_id"])

    eer = paginated("event_entity_relationships", "event_id,entity_id", "id")
    for r in eer:
        if r["entity_id"] not in entity_map.get(r["event_id"], []):
            entity_map.setdefault(r["event_id"], []).append(r["entity_id"])

    filters = [lambda q: q.gte("event_date", start_date)]
    if end_date:
        filters.append(lambda q: q.lt("event_date", end_date))
    events = {e["id"]: e["event_date"][:10] for e in paginated(
        "events", "id,event_date", "id", filters)}

    pop = []
    for event_id in tagged_event_ids:
        event_date = events.get(event_id)
        if not event_date:
            continue
        for entity_id in entity_map.get(event_id, [None]):
            pop.append({"event_id": event_id, "entity_id": entity_id, "event_date": event_date})
    return pop


def main():
    import sys
    start_date = sys.argv[1] if len(sys.argv) > 1 else "2020-01-01"
    end_date = sys.argv[2] if len(sys.argv) > 2 else None
    print(f"Real date range: {start_date} to {end_date or 'present'}")
    print("Fetching real confidence data and the real, fixed population...")
    confidence_by_month = get_confidence_by_month()
    population = get_real_population(start_date, end_date)
    print(f"Real population: {len(population)} rows\n")

    print("Fetching real full daily ripple time series (day_offset 1-39)...")
    ripple_rows = paginated(
        "event_ripple_timeline", "event_id,entity_id,day_offset,abnormal_return", "id",
        [lambda q: q.lte("day_offset", 39).gte("day_offset", 1).not_.is_("abnormal_return", "null")],
    )
    print(f"  {len(ripple_rows)} real daily rows loaded.\n")

    series = defaultdict(dict)
    for r in ripple_rows:
        series[(r["event_id"], r["entity_id"])][r["day_offset"]] = r["abnormal_return"]

    print("Fetching real Fed policy decisions (for the real policy-stance cross)...")
    policy_decisions = get_real_policy_decisions()
    print(f"  {len(policy_decisions)} real rate changes loaded.")
    print()

    results_punished = defaultdict(list)
    never_punished = defaultdict(int)
    results_rewarded = defaultdict(list)
    never_rewarded = defaultdict(int)
    # REAL EXTENSION (2026-10-03): also bucket by (confidence_trend x real
    # policy stance) -- testing whether the same raw confidence_trend
    # reading means something different depending on whether the Fed is
    # actively hiking vs cutting at the time, per the real hypothesis that
    # missing macro context explains why the pooled result isn't time-stable.
    results_punished_crossed = defaultdict(list)
    never_punished_crossed = defaultdict(int)
    for p in population:
        key = (p["event_id"], p["entity_id"])
        day_series = series.get(key)
        if not day_series:
            continue
        ct = get_confidence_trend(p["event_date"], confidence_by_month)
        if ct is None:
            continue
        stance = get_policy_stance(p["event_date"], policy_decisions)

        first_punish = None
        first_reward = None
        for day in sorted(day_series.keys()):
            val = day_series[day]
            if first_punish is None and val <= PUNISHED_THRESHOLD:
                first_punish = day
            if first_reward is None and val >= REWARDED_THRESHOLD:
                first_reward = day
            if first_punish is not None and first_reward is not None:
                break

        if first_punish is not None:
            results_punished[ct].append(first_punish)
            results_punished_crossed[(ct, stance)].append(first_punish)
        else:
            never_punished[ct] += 1
            never_punished_crossed[(ct, stance)] += 1
        if first_reward is not None:
            results_rewarded[ct].append(first_reward)
        else:
            never_rewarded[ct] += 1

    def report(label, results, never_crossed):
        print("=" * 70)
        print(f"REAL RESULT: days until first crossing {label}, by confidence_trend bucket")
        print("=" * 70)
        for bucket in ("falling", "rising", "stable"):
            days = results.get(bucket, [])
            nc = never_crossed.get(bucket, 0)
            if not days:
                print(f"  {bucket}: no real events crossed the bar at all (n={nc} never crossed)")
                continue
            days_sorted = sorted(days)
            median = days_sorted[len(days_sorted) // 2]
            mean = sum(days_sorted) / len(days_sorted)
            total = len(days) + nc
            rate = 100 * len(days) / total if total else 0
            print(f"  {bucket}: n={len(days)} crossed (median {median} days, mean {mean:.1f} days, "
                  f"real crossing rate {rate:.1f}%), {nc} never crossed within 39 days")
        print()

    report("the -3% PUNISHED bar", results_punished, never_punished)
    report("the +3% REWARDED bar", results_rewarded, never_rewarded)

    print("=" * 70)
    print("REAL RESULT: punishment speed, confidence_trend CROSSED WITH real Fed policy stance")
    print("=" * 70)
    for ct_bucket in ("falling", "rising", "stable"):
        for stance in ("hiking", "cutting", "none_yet"):
            days = results_punished_crossed.get((ct_bucket, stance), [])
            nc = never_punished_crossed.get((ct_bucket, stance), 0)
            total = len(days) + nc
            if total < 30:
                continue
            days_sorted = sorted(days)
            median = days_sorted[len(days_sorted) // 2] if days else None
            rate = 100 * len(days) / total if total else 0
            print(f"  {ct_bucket} + {stance}: n={total} (median {median} days, "
                  f"real crossing rate {rate:.1f}%)")


if __name__ == "__main__":
    main()
