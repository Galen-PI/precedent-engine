"""
multi_horizon_confidence_test.py

REAL FIX (2026-10-03, same day as first built): the first version of this
script accidentally changed TWO things at once -- the time horizon AND the
underlying population/methodology (switched to event_ripple_timeline's raw
entity-level rows instead of the original confidence_trend test's real
population). That produced numbers that don't match the already-validated
falling->punished finding at all (showed muted everywhere), which was the
real tell something was wrong, not a genuine reversal. Real fix: use the
EXACT SAME population as walk_forward_consumer_confidence.py (only events
with an existing real reaction_character tag), and for each one, swap in its
real abnormal_return AT A DIFFERENT HORIZON from event_ripple_timeline --
isolating horizon as the only real variable, holding everything else fixed.

Real, data-driven percentile thresholds per horizon (top/bottom 30% ->
rewarded/punished, middle 40% -> muted) since a fixed +/-3% cutoff calibrated
for 20-day returns doesn't fit shorter horizons' naturally smaller moves.

Honest baseline throughout: the TEST period's own true majority, not
training's.

Usage:
    python multi_horizon_confidence_test.py <cutoff_date: YYYY-MM-DD>
"""
import sys
import os
from datetime import date
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MIN_N_FOR_READY = 30
HORIZONS = [1, 3, 5, 10, 20, 30]
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


def get_real_population():
    """REAL FIX: same population as walk_forward_consumer_confidence.py's
    build_dataset() -- only (event_id, entity_id) pairs with an existing
    real reaction_character tag, same entity-resolution logic."""
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
        if r["event_id"] not in entity_map:
            entity_map[r["event_id"]] = []
        if r["entity_id"] not in entity_map[r["event_id"]]:
            entity_map[r["event_id"]].append(r["entity_id"])

    # REAL FIX: the original confidence_trend test only used events from
    # 2020 onward (n=4,139) -- missed this the first time, which is why the
    # population stayed ~15,000 instead of matching.
    events = {e["id"]: e["event_date"][:10] for e in paginated(
        "events", "id,event_date", "id", [lambda q: q.gte("event_date", "2020-01-01")])}

    pop = []
    for event_id in tagged_event_ids:
        event_date = events.get(event_id)
        if not event_date:
            continue
        entities = entity_map.get(event_id, [None])
        for entity_id in entities:
            pop.append({"event_id": event_id, "entity_id": entity_id, "event_date": event_date})
    return pop


# REAL FIX, SECOND ATTEMPT (2026-10-03): the fixed +/-3% threshold was
# ALSO wrong -- it confounds window length with real signal, since a fixed
# bar is mechanically easier to cross with more cumulative time (confirmed
# directly: the honest baseline's own "muted" rate shrank smoothly from
# 71.6% at day 1 to 42.6% at day 10 for the WHOLE population, independent
# of confidence_trend -- pure return-compounding, not a real finding).
# Real fix: percentile-based thresholds on the SIGNED return, computed
# independently per horizon from the real, UNCONDITIONAL population (not
# conditioned on confidence_trend bucket, so real signal isn't normalized
# away) -- top 30% most positive -> rewarded, bottom 30% most negative ->
# punished, middle 40% -> muted. This makes horizons genuinely comparable
# without the fixed-threshold confound, while preserving the real,
# intended sign-based meaning of reaction_character.
def real_thresholds_for_horizon(signed_values):
    s = sorted(signed_values)
    n = len(s)
    punished_cut = s[int(n * 0.30)]
    rewarded_cut = s[int(n * 0.70)]
    return punished_cut, rewarded_cut


def classify(ar, punished_cut, rewarded_cut):
    if ar <= punished_cut:
        return "punished"
    if ar >= rewarded_cut:
        return "rewarded"
    return "muted"


def main():
    if len(sys.argv) < 2:
        print("Usage: python multi_horizon_confidence_test.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    print("Fetching real confidence data and the real, fixed population...")
    confidence_by_month = get_confidence_by_month()
    population = get_real_population()
    print(f"Real population (same as the validated confidence_trend test): {len(population)} rows\n")

    print(f"{'='*80}\nTesting confidence_trend at {len(HORIZONS)} real horizons, SAME population throughout: {HORIZONS}\n{'='*80}\n")

    for horizon in HORIZONS:
        print(f"--- HORIZON: day_offset={horizon} ---")
        ripple_rows = paginated(
            "event_ripple_timeline", "event_id,entity_id,abnormal_return", "id",
            [lambda q: q.eq("day_offset", horizon).not_.is_("abnormal_return", "null")],
        )
        ripple_lookup = {(r["event_id"], r["entity_id"]): r["abnormal_return"] for r in ripple_rows}

        real_values = []
        matched = []
        for p in population:
            ar = ripple_lookup.get((p["event_id"], p["entity_id"]))
            if ar is None:
                continue
            ct = get_confidence_trend(p["event_date"], confidence_by_month)
            if ct is None:
                continue
            real_values.append(ar)
            matched.append({"event_date": p["event_date"], "bucket": ct, "abnormal_return": ar})

        if len(real_values) < 100:
            print(f"  Too few real matched rows ({len(real_values)}), skipping.\n")
            continue

        punished_cut, rewarded_cut = real_thresholds_for_horizon(real_values)
        for r in matched:
            r["reaction"] = classify(r["abnormal_return"], punished_cut, rewarded_cut)

        train = [r for r in matched if r["event_date"] < cutoff]
        test = [r for r in matched if r["event_date"] >= cutoff]
        if not train or not test:
            print(f"  Empty train or test split, skipping.\n")
            continue

        test_baseline = defaultdict(int)
        for r in test:
            test_baseline[r["reaction"]] += 1
        baseline_reaction = max(test_baseline, key=test_baseline.get)
        baseline_rate = 100 * test_baseline[baseline_reaction] / len(test)

        train_by_bucket = defaultdict(lambda: defaultdict(int))
        for r in train:
            train_by_bucket[r["bucket"]][r["reaction"]] += 1
        learned = {b: max(c, key=c.get) for b, c in train_by_bucket.items()}

        test_by_bucket = defaultdict(lambda: defaultdict(int))
        for r in test:
            test_by_bucket[r["bucket"]][r["reaction"]] += 1

        print(f"  Real matched rows: {len(matched)} | Train n={len(train)}, Test n={len(test)}, "
              f"honest baseline={baseline_reaction} ({baseline_rate:.1f}%)")
        for bucket in ("falling", "rising", "stable"):
            counts = test_by_bucket.get(bucket)
            if not counts:
                continue
            test_n = sum(counts.values())
            predicted = learned.get(bucket)
            if predicted is None:
                continue
            hit_rate = 100 * counts.get(predicted, 0) / test_n
            ready = test_n >= MIN_N_FOR_READY
            print(f"    {bucket}: predicted={predicted}, test_n={test_n}, "
                  f"hit_rate={hit_rate:.1f}% vs honest baseline {baseline_rate:.1f}% "
                  f"({hit_rate - baseline_rate:+.1f}pp) -- {'READY' if ready else 'not ready'}")
        print()


if __name__ == "__main__":
    main()
