"""
walk_forward_chain_position.py

Standalone walk-forward test: does an event's position within a same_entity_sequence
chain predict reaction_character (rewarded/punished/muted)?

Real motivation (2026-09-29): the existing chain_position_opening/middle/closing tags
(compute_chain_position.py) throw away two things -- chain LENGTH (a 3-event chain over
2 weeks vs a 15-event saga over years) and position as a FRACTION (2-of-10 vs 8-of-10,
both "middle", plausibly very different market reactions -- anticipation vs fatigue).
This builds a richer feature instead: chain_length bucketed (short=2, medium=3-4,
long=5+) crossed with position-as-fraction bucketed (early/middle/late third).

Real, honest scale note: only 39 entities have ANY same_entity_sequence chain (409 total
events), of which 393 also carry a reaction_character tag. This is a genuinely small,
low-power test -- not a reason to skip it, but read the results with that in mind.

Standalone test only -- NOT wired into multi_feature_model.py. That's a deliberate next
step only if this shows something real.

Usage:
    python walk_forward_chain_position.py <cutoff_date: YYYY-MM-DD>
"""
import sys
from datetime import date
from collections import defaultdict
from supabase import create_client
import os

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MIN_N_FOR_READY = 30


def paginated(table, select, filters=None):
    rows, offset = [], 0
    while True:
        q = supabase.table(table).select(select)
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


def chain_length_bucket(n):
    if n == 2:
        return "short"
    if n <= 4:
        return "medium"
    return "long"


def position_bucket(frac):
    if frac < 1/3:
        return "early"
    if frac < 2/3:
        return "middle"
    return "late"


def build_dataset():
    tag_names = {t["id"]: t["name"] for t in supabase.table("tags").select("id,name")
                 .in_("name", ["same_entity_sequence", "rewarded", "punished", "muted"]).execute().data}
    name_to_id = {v: k for k, v in tag_names.items()}

    seq_event_ids = {r["event_id"] for r in paginated(
        "event_tags", "event_id", [lambda q: q.eq("tag_id", name_to_id["same_entity_sequence"])])}
    print(f"{len(seq_event_ids)} real events carry the same_entity_sequence tag.")

    reaction_by_event = {}
    for name in ("rewarded", "punished", "muted"):
        for r in paginated("event_tags", "event_id",
                            [lambda q, tid=name_to_id[name]: q.eq("tag_id", tid)]):
            reaction_by_event[r["event_id"]] = name

    events = {e["id"]: e["event_date"][:10] for e in paginated("events", "id,event_date")
              if e["id"] in seq_event_ids}

    entity_map = defaultdict(list)
    for r in paginated("event_entity_relationships", "event_id,entity_id"):
        if r["event_id"] in seq_event_ids:
            entity_map[r["entity_id"]].append(r["event_id"])

    rows = []
    for entity_id, event_ids in entity_map.items():
        chain = sorted([(events[eid], eid) for eid in event_ids if eid in events])
        n = len(chain)
        if n < 2:
            continue
        for i, (event_date, event_id) in enumerate(chain):
            reaction = reaction_by_event.get(event_id)
            if reaction is None:
                continue
            frac = i / (n - 1)
            bucket = f"{chain_length_bucket(n)}_{position_bucket(frac)}"
            rows.append({"event_id": event_id, "event_date": event_date,
                         "chain_len": n, "position_frac": round(frac, 2),
                         "bucket": bucket, "reaction": reaction})
    return sorted(rows, key=lambda r: r["event_date"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python walk_forward_chain_position.py <cutoff_date: YYYY-MM-DD>")
        sys.exit(1)
    cutoff = sys.argv[1]

    rows = build_dataset()
    print(f"Rows with both a real chain position AND a reaction tag: {len(rows)}\n")

    print("Real bucket distribution (all rows):")
    dist = defaultdict(int)
    for r in rows:
        dist[r["bucket"]] += 1
    for b in sorted(dist):
        print(f"  {b}: {dist[b]}")
    print()

    train = [r for r in rows if r["event_date"] < cutoff]
    test = [r for r in rows if r["event_date"] >= cutoff]
    print(f"Train: {len(train)}, Test: {len(test)}\n")
    if not train or not test:
        print("CANNOT RUN: one side of the split is empty. Try a different cutoff.")
        return

    train_baseline = defaultdict(int)
    for r in train:
        train_baseline[r["reaction"]] += 1
    baseline_reaction = max(train_baseline, key=train_baseline.get)
    baseline_hit_rate = 100 * train_baseline[baseline_reaction] / len(train)
    print(f"--- DUMB BASELINE ---\n  Most common: {baseline_reaction} ({baseline_hit_rate:.1f}%)\n")

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
    print("READY at individual level" if any_ready else "NOT READY at individual level -- sample too small, expected given only ~400 chain events exist")


if __name__ == "__main__":
    main()
