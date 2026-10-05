"""
walk_forward_consumer_confidence.py

Real, standalone test: does consumer confidence trend (UMCSENT, University of
Michigan Consumer Sentiment) predict reaction_character? Same disciplined pattern
as every other feature tested this session (sentiment, storm, chain_position) --
a standalone walk-forward test BEFORE touching multi_feature_model.py, not added
to the big model blind.

Real design, per the actual framing given: for each event, look at the confidence
reading for the event's own month vs. the PRIOR month -- this is the real trend
"going into" the event (matches the Dec-vs-Jan framing). Bucket into
rising/falling/stable using the same kind of real threshold already used for
gross_margin_trend (1-point move on the UMCSENT scale, which runs roughly 50-110,
so genuinely comparable in spirit to a 1% margin-change threshold elsewhere).

Real, honest scope note: UMCSENT is monthly and genuinely leading-indicator-like in
principle, but this test only checks correlation with existing reaction_character
tags -- it does not establish causation, and a monthly macro reading is a blunt
instrument next to any individual company event.

Usage:
    python walk_forward_consumer_confidence.py <cutoff_date: YYYY-MM-DD>
"""
import sys
from collections import defaultdict
from datetime import date
from supabase import create_client
import os

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MIN_N_FOR_READY = 30
TREND_THRESHOLD = 1.0  # UMCSENT points -- real scale runs roughly 50-110


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


def trend_bucket(delta):
    if delta > TREND_THRESHOLD:
        return "rising"
    if delta < -TREND_THRESHOLD:
        return "falling"
    return "stable"


def build_dataset():
    umcsent = paginated("macro_data_releases", "release_date,value", "release_date",
                         [lambda q: q.eq("series_id", "UMCSENT")])
    by_month = {}
    for r in umcsent:
        d = date.fromisoformat(str(r["release_date"])[:10])
        by_month[(d.year, d.month)] = r["value"]

    tag_ids = {t["name"]: t["id"] for t in supabase.table("tags").select("id,name")
               .in_("name", ["rewarded", "punished", "muted"]).execute().data}
    id_to_name = {v: k for k, v in tag_ids.items()}

    event_tags = paginated("event_tags", "event_id,tag_id", "event_id",
                            [lambda q: q.in_("tag_id", list(tag_ids.values()))])
    reaction_by_event = {r["event_id"]: id_to_name[r["tag_id"]] for r in event_tags}

    events = paginated("events", "id,event_date", "id",
                        [lambda q: q.gte("event_date", "2020-01-01")])

    rows = []
    for e in events:
        reaction = reaction_by_event.get(e["id"])
        if reaction is None:
            continue
        d = date.fromisoformat(str(e["event_date"])[:10])
        this_month = by_month.get((d.year, d.month))
        prior_year, prior_month = (d.year, d.month - 1) if d.month > 1 else (d.year - 1, 12)
        prior = by_month.get((prior_year, prior_month))
        if this_month is None or prior is None:
            continue
        delta = this_month - prior
        rows.append({
            "event_id": e["id"], "event_date": str(e["event_date"])[:10],
            "confidence": this_month, "delta": round(delta, 2),
            "bucket": trend_bucket(delta), "reaction": reaction,
        })
    return sorted(rows, key=lambda r: r["event_date"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python walk_forward_consumer_confidence.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    rows = build_dataset()
    print(f"Rows with both a real confidence trend AND a reaction tag: {len(rows)}\n")

    print("Real bucket distribution (all rows):")
    dist = defaultdict(int)
    for r in rows:
        dist[r["bucket"]] += 1
    for b in ("rising", "falling", "stable"):
        print(f"  {b}: {dist[b]}")
    print()

    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train: {len(train)}, Test: {len(test)}\n")
    if not train or not test:
        print("CANNOT RUN: one side of the split is empty. Try a different cutoff.")
        return

    # REAL FIX (2026-10-03): the old baseline used the TRAINING period's
    # majority class evaluated on the TRAINING set -- a double error, since
    # it's neither the real comparison point (the test set) nor a fair one
    # if the true label distribution drifts over time (confirmed it does,
    # directly, in the magnitude-model retraction the same day). Honest
    # baseline: the TEST period's own true majority class, on the TEST set.
    test_baseline = defaultdict(int)
    for r in test:
        test_baseline[r["reaction"]] += 1
    baseline_reaction = max(test_baseline, key=test_baseline.get)
    baseline_hit_rate = 100 * test_baseline[baseline_reaction] / len(test)
    print(f"--- HONEST BASELINE (test period's own true majority) ---\n"
          f"  Most common in TEST: {baseline_reaction} ({baseline_hit_rate:.1f}%)\n")

    train_by_bucket = defaultdict(lambda: defaultdict(int))
    for r in train:
        train_by_bucket[r["bucket"]][r["reaction"]] += 1

    learned = {}
    print("--- CONDITIONAL PROBABILITIES BY bucket (training only) ---")
    for bucket, reaction_counts in train_by_bucket.items():
        n = sum(reaction_counts.values())
        top = max(reaction_counts, key=reaction_counts.get)
        top_pct = 100 * reaction_counts[top] / n
        print(f"  {bucket} (train n={n}): most common = {top} ({top_pct:.1f}%)")
        learned[bucket] = top
    print()

    test_by_bucket = defaultdict(lambda: defaultdict(int))
    for r in test:
        test_by_bucket[r["bucket"]][r["reaction"]] += 1

    print("--- WALK-FORWARD TEST ---")
    any_ready = False
    for bucket, test_reaction_counts in test_by_bucket.items():
        test_n = sum(test_reaction_counts.values())
        predicted = learned.get(bucket)
        if predicted is None:
            print(f"  {bucket}: no training data for this bucket, skipping")
            continue
        hits = test_reaction_counts.get(predicted, 0)
        hit_rate = 100 * hits / test_n if test_n > 0 else 0
        ready = test_n >= MIN_N_FOR_READY
        if ready:
            any_ready = True
        print(f"  {bucket}: predicted={predicted}, test_n={test_n}, "
              f"hit_rate={hit_rate:.1f}% vs baseline={baseline_hit_rate:.1f}% -- "
              f"{'READY' if ready else 'not ready (n<' + str(MIN_N_FOR_READY) + ')'}")

    print()
    print("READY at individual level" if any_ready else "NOT READY -- sample too small")


if __name__ == "__main__":
    main()
