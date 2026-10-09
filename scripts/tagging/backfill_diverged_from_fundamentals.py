"""
backfill_diverged_from_fundamentals.py

Real, one-time backfill pass (same shape as recompute_firm_state.py):
reviews every event already tagged "rewarded" or "punished" by
tag_reaction_character.py, and upgrades the tag to
"diverged_from_fundamentals" where the stock's reaction contradicts
what the company's underlying fundamentals (firm_state_label, from
event_pre_context, already a real, working quintile classification)
would suggest.

Real rule, agreed as the obvious reading of the tag's name:
  - "rewarded" (stock rose) while firm_state is "weakening" or
    "deteriorating" (fundamentals getting worse) => diverged
  - "punished" (stock fell) while firm_state is "strong" or "improving"
    (fundamentals getting better) => diverged
  - "stable" firm_state, or any firm_state_label aligned with the
    reaction's own direction, is left alone -- this tag is for a real
    contradiction, not just "fundamentals happened to be weak/strong".

Deliberately built as a SEPARATE backfill script rather than editing
tag_reaction_character.py's own core tagging loop directly -- that
function is actively used in production and this avoids risking a
regression in its proven rewarded/punished/muted logic. Re-running
tag_reaction_character.py later for NEW events will still just assign
rewarded/punished/muted as before; this script is the one that then
reviews those for the real divergence case.

Where an event has a firm_state_label for more than one entity (a
multi-entity event), uses the SAME entity tag_reaction_character.py
itself uses for its single reaction tag (confirmed: event_tags
structurally allows only one reaction per event, tied to the event's
FIRST-linked entity) -- not attempting to fix that separate, already-
documented limitation here.

Usage:
    python backfill_diverged_from_fundamentals.py --dry-run
    python backfill_diverged_from_fundamentals.py --live
"""
import os
import sys
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

CONTRADICTS = {
    "rewarded": {"weakening", "deteriorating"},
    "punished": {"strong", "improving"},
}


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


def get_tag_id(name):
    rows = supabase.table("tags").select("id").eq("name", name).execute().data
    if not rows:
        raise RuntimeError(f"Real tag '{name}' not found in tags table.")
    return rows[0]["id"]


def main():
    live = "--live" in sys.argv

    print("Fetching real tag IDs...")
    tag_ids = {name: get_tag_id(name) for name in
               ["rewarded", "punished", "diverged_from_fundamentals"]}
    reaction_tag_id_to_name = {tag_ids["rewarded"]: "rewarded", tag_ids["punished"]: "punished"}

    print("Fetching real event_tags rows currently tagged rewarded/punished...")
    tagged_rows = paginated("event_tags", "event_id,tag_id", "event_id",
                             [lambda q: q.in_("tag_id", [tag_ids["rewarded"], tag_ids["punished"]])])
    print(f"  {len(tagged_rows)} real rows found.")

    # REAL FIX (2026-10-09): a prior partial run had already upgraded some
    # events to diverged_from_fundamentals before crashing on an unrelated
    # transient error -- a plain re-run then tried to INSERT that same
    # (event_id, tag_id) pair again, hitting a real duplicate-key violation
    # (event_tags_pkey). Resume-safe fix: skip any event_id that already
    # has the diverged_from_fundamentals tag.
    already_diverged = {r["event_id"] for r in paginated(
        "event_tags", "event_id", "event_id",
        [lambda q: q.eq("tag_id", tag_ids["diverged_from_fundamentals"])])}
    before = len(tagged_rows)
    tagged_rows = [r for r in tagged_rows if r["event_id"] not in already_diverged]
    print(f"  {before - len(tagged_rows)} already upgraded in a prior run, skipping. "
          f"{len(tagged_rows)} real rows remaining.\n")

    print("Fetching real event_pre_context firm_state_label for every event/entity pair...")
    pc_rows = paginated("event_pre_context", "event_id,entity_id,firm_state_label", "event_id",
                         [lambda q: q.not_.is_("firm_state_label", "null")])
    # REAL, same choice as tag_reaction_character.py: use the first-linked
    # entity's firm_state per event (event_tags structurally has one
    # reaction per event, tied to that same first entity).
    firm_state_by_event = {}
    for r in pc_rows:
        if r["event_id"] not in firm_state_by_event:
            firm_state_by_event[r["event_id"]] = r["firm_state_label"]
    print(f"  {len(firm_state_by_event)} real events with a firm_state_label available.\n")

    to_upgrade = []
    for row in tagged_rows:
        reaction = reaction_tag_id_to_name.get(row["tag_id"])
        if not reaction:
            continue
        firm_state = firm_state_by_event.get(row["event_id"])
        if firm_state in CONTRADICTS.get(reaction, set()):
            to_upgrade.append({"event_id": row["event_id"], "old_tag_id": row["tag_id"],
                                "old_reaction": reaction, "firm_state": firm_state})

    print(f"{len(to_upgrade)} real events to upgrade to diverged_from_fundamentals.")
    dist = {}
    for r in to_upgrade:
        key = f"{r['old_reaction']} + {r['firm_state']}"
        dist[key] = dist.get(key, 0) + 1
    print(f"Real breakdown: {dist}\n")

    if not live:
        print("DRY RUN -- nothing written. Pass --live to write.")
        return

    written = 0
    for r in to_upgrade:
        supabase.table("event_tags").delete() \
            .eq("event_id", r["event_id"]).eq("tag_id", r["old_tag_id"]).execute()
        supabase.table("event_tags").insert({
            "event_id": r["event_id"], "tag_id": tag_ids["diverged_from_fundamentals"],
        }).execute()
        written += 1
        if written % 100 == 0:
            print(f"  ...{written}/{len(to_upgrade)} written")
    print(f"\nReal write complete: {written} events upgraded to diverged_from_fundamentals.")


if __name__ == "__main__":
    main()
