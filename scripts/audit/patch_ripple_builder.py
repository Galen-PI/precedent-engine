"""patch_ripple_builder.py (2026-10-28): fixes three defects in build_ripple_timeline.py, each guarded by an exact-match assertion.
1. bundle skip list = the view ripple_skip_events (events with 2+ component rows, plus every 'exclude' reason), not every id in event_component_dates
2. ONE deterministic security per (event, entity): the reaction row's ticker if it belongs to the entity, else the share class with the earliest price
3. a written record of every skipped pair (results/ripple_skips_<date>.csv) and a unique paging order for events
Usage: python3 scripts/audit/patch_ripple_builder.py <path to build_ripple_timeline.py>"""
import sys

path = sys.argv[1]
t = open(path, encoding="utf-8").read()

def sub(old, new, label):
    global t
    n = t.count(old)
    assert n == 1, "%s: expected exactly 1 match, found %d; nothing was written" % (label, n)
    t = t.replace(old, new)
    print("ok  ", label)

sub("import os\nimport sys\nimport time\n", "import csv\nimport os\nimport sys\nimport time\n", "import csv")

sub('''        page = supabase.table("event_component_dates").select("event_id") \\
            .range(offset, offset + page_size - 1).execute().data''',
'''        # REAL FIX (2026-10-28): the skip list is the view ripple_skip_events (events with 2 or more
        # component rows, plus every event with an 'exclude' reason in event_exclusions), not every id in
        # event_component_dates: 280 real single-date events carried one stray component row.
        page = supabase.table("ripple_skip_events").select("event_id").order("event_id") \\
            .range(offset, offset + page_size - 1).execute().data''', "skip list from the view")

sub('''.order("event_date").limit(limit * 2 if exclude_bundled else limit).execute().data''',
    '''.order("event_date").order("id").limit(limit * 2 if exclude_bundled else limit).execute().data''', "unique order (limit branch)")

sub('''                .order("event_date") \\
                .range(offset, offset + page_size - 1).execute().data''',
'''                .order("event_date").order("id") \\
                .range(offset, offset + page_size - 1).execute().data''', "unique order (paged branch)")

HELPERS = '''# REAL FIX (2026-10-28): ONE deterministic security per (event, entity), and a written record of every skip.
# The old get_ticker_and_sector() took the first security of an entity, unordered. For an entity with two share
# classes (NWS / NWSA, FOX / FOXA) that picked whichever came back first, so every News Corp event before NWS had
# prices (mid-2023) found no prices and was skipped silently. The primary security is now the ticker of the event's
# reaction row (event_market_reactions_corrected) when it belongs to the entity, else the share class with the
# earliest price (ties: alphabetical).
_REACTION_TICKER: dict[str, str] = {}
_ENTITY_SECURITIES_CACHE: dict[str, list[dict]] = {}
SKIPPED: list[dict] = []


def _load_reaction_tickers() -> None:
    if _REACTION_TICKER:
        return
    offset = 0
    page_size = 1000
    while True:
        page = supabase.table("event_market_reactions_corrected").select("event_id,ticker") \\
            .order("event_id").range(offset, offset + page_size - 1).execute().data
        if not page:
            break
        for row in page:
            _REACTION_TICKER[row["event_id"]] = row["ticker"]
        if len(page) < page_size:
            break
        offset += page_size
    print(f"  Loaded {len(_REACTION_TICKER)} reaction-row tickers (the primary security per event).")


def _entity_securities(entity_id: str) -> list[dict]:
    if entity_id not in _ENTITY_SECURITIES_CACHE:
        _ENTITY_SECURITIES_CACHE[entity_id] = supabase.table("securities").select("ticker,sector") \\
            .eq("entity_id", entity_id).order("ticker").execute().data
    return _ENTITY_SECURITIES_CACHE[entity_id]


def pick_security(event: dict, entity_id: str) -> tuple[str | None, str | None]:
    rows = _entity_securities(entity_id)
    if not rows:
        return (None, None)
    if len(rows) > 1:
        preferred = _REACTION_TICKER.get(event["id"])
        for row in rows:
            if row["ticker"] == preferred:
                return (row["ticker"], row.get("sector"))

        def first_price(row):
            hist = get_full_price_history(row["ticker"])
            return hist[0]["price_date"] if hist else "9999-12-31"

        rows = sorted(rows, key=lambda row: (first_price(row), row["ticker"]))
    return (rows[0]["ticker"], rows[0].get("sector"))


def _record_skip(event: dict, entity_id: str, ticker: str | None, reason: str) -> None:
    SKIPPED.append({"event_id": event["id"], "event_date": str(event["event_date"])[:10],
                    "entity_id": entity_id, "ticker": ticker or "", "reason": reason})


def _write_skips() -> None:
    if not SKIPPED:
        print("No skipped event-entity pairs to record.")
        return
    os.makedirs("results", exist_ok=True)
    path = f"results/ripple_skips_{date.today().isoformat()}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["event_id", "event_date", "entity_id", "ticker", "reason"])
        w.writeheader()
        w.writerows(SKIPPED)
    by_reason: dict[str, int] = {}
    for s in SKIPPED:
        by_reason[s["reason"]] = by_reason.get(s["reason"], 0) + 1
    print(f"Wrote {len(SKIPPED)} skipped pairs to {path}: {by_reason}")


'''
sub("def build_for_event(event: dict, entity_id: str, live: bool) -> int:", HELPERS + "def build_for_event(event: dict, entity_id: str, live: bool) -> int:", "helpers")

sub('''    ticker, sector = get_ticker_and_sector(entity_id)
    if not ticker or ticker == "SPY":
        return 0''',
'''    ticker, sector = pick_security(event, entity_id)
    if not ticker or ticker == "SPY":
        _record_skip(event, entity_id, ticker, "no security for the entity, or SPY")
        return 0''', "primary security + skip record 1")

sub('''    if len(company_prices) < 5 or len(spy_prices) < 5:
        return 0''',
'''    if len(company_prices) < 5 or len(spy_prices) < 5:
        _record_skip(event, entity_id, ticker, "fewer than 5 prices in the window (company or SPY)")
        return 0''', "skip record 2")

sub('''    if idx is None or spy_idx is None or idx == 0 or spy_idx == 0:
        return 0''',
'''    if idx is None or spy_idx is None or idx == 0 or spy_idx == 0:
        _record_skip(event, entity_id, ticker, "no prior close in the window (event before the first price, or after the last)")
        return 0''', "skip record 3")

sub('''    event_ids = [e["id"] for e in events]
    entity_map = get_event_entities(event_ids)''',
'''    _load_reaction_tickers()
    event_ids = [e["id"] for e in events]
    entity_map = get_event_entities(event_ids)''', "load reaction tickers")

sub("def main():\n    args = sys.argv[1:]", "def _main_inner():\n    args = sys.argv[1:]", "rename main")

sub('''if __name__ == "__main__":
    main()''',
'''def main():
    _main_inner()
    _write_skips()


if __name__ == "__main__":
    main()''', "main wrapper")

open(path, "w", encoding="utf-8").write(t)
print("patched:", path)