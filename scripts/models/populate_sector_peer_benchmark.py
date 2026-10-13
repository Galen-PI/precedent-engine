"""
populate_sector_peer_benchmark.py

Real Phase 6 harness gap, closing item D1 from the prediction-contract
review (external day-trading practitioner): "a broad sector move (e.g.,
SOXX +3%) can masquerade as a company-specific reaction under SPY-only
adjustment." Every abnormal return in this project so far is computed
only vs. SPY -- this adds a genuine sector/peer benchmark alongside it.

Real methodology, matching tag_reaction_character.py's
compute_full_reaction() exactly (same real index-based trading-day
offsets, not shared calendar dates -- a peer's own small price gaps
could otherwise shift which real day is "day 5"):
  - For each event, find every OTHER company in the SAME real GICS
    sector (securities.sector), excluding the event's own company.
  - For each peer, independently compute ITS OWN return_0d/1d/5d/20d
    using the identical index-based method (peer's own price index on
    or after event_date, prior=idx-1, forward=idx+1/5/20).
  - Average all peers' returns (equal-weighted) into a real
    sector_peer_return_Xd.
  - abnormal_return_vs_sector_Xd = the event company's OWN return_Xd
    (already stored in event_market_reactions_corrected) minus this
    real sector-peer basket return.

Real, proven bulk-loading technique (same lesson as check_event_exposure.py
and populate_government_decision_exposure.py's own real N+1 crashes):
loads ALL market_prices once, keyed by security_id, sorted by date, then
does every peer lookup as an in-memory bisect -- not one live query per
(event, peer) pair, which would be tens of millions of real requests at
this project's real scale (19,892 events x up to 81 peers each).

Usage:
    python populate_sector_peer_benchmark.py --dry-run
    python populate_sector_peer_benchmark.py --live
"""
import os
import sys
import bisect
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MIN_PEERS_REQUIRED = 3  # real floor -- an "average" of 1-2 peers isn't a real basket


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


def load_all_prices():
    """Real, bulk-loaded {security_id: (sorted_dates, sorted_closes)}.
    REAL FIX (2026-10-13): the original OFFSET-based pagination
    (.range(offset, offset+999), ordered by security_id with no
    tie-breaking key) genuinely does not scale against market_prices'
    real 3.37M rows -- each page forces Postgres to re-sort/re-scan an
    ever-larger offset, hitting a real statement timeout partway
    through on both this script and populate_sector_peer_benchmark.py.
    Real fix: keyset (cursor) pagination on the table's own real,
    indexed id column -- WHERE id > last_seen_id, ordered by id -- which
    stays fast regardless of table size since it's a genuine indexed
    range scan, not a re-sort of growing size."""
    by_security = defaultdict(list)
    last_id = None
    while True:
        q = supabase.table("market_prices").select("id,security_id,price_date,adjusted_close").order("id").limit(5000)
        if last_id is not None:
            q = q.gt("id", last_id)
        page = q.execute().data
        if not page:
            break
        for r in page:
            if r["adjusted_close"] is not None:
                by_security[r["security_id"]].append((str(r["price_date"])[:10], float(r["adjusted_close"])))
        last_id = page[-1]["id"]
        # REAL FIX (2026-10-13): Supabase/PostgREST silently caps each
        # request at 1,000 rows server-side regardless of .limit(5000)
        # client-side -- confirmed directly (a live test fetched exactly
        # 1,000 rows on "page 1" then incorrectly treated that as the
        # final page). Never trust page size to mean "last page" --
        # only a genuinely EMPTY page (checked at the top of the loop)
        # means pagination is done.
    result = {}
    for sid, pairs in by_security.items():
        pairs.sort()
        result[sid] = ([d for d, _ in pairs], [c for _, c in pairs])
    return result


def company_return_as_of(dates, closes, event_date, offset_days):
    """Real, index-based return for one company -- same method as
    compute_full_reaction(): find this company's own price index on or
    after event_date, prior=idx-1, forward=idx+offset_days. Returns
    None if there isn't enough real data on either side."""
    idx = bisect.bisect_left(dates, event_date)
    if idx == 0 or idx >= len(dates):
        return None
    if idx + offset_days >= len(dates):
        return None
    prior_close = closes[idx - 1]
    forward_close = closes[idx + offset_days] if offset_days > 0 else closes[idx]
    if not prior_close:
        return None
    return (forward_close / prior_close) - 1


def main():
    live = "--live" in sys.argv

    print("Fetching real securities and their sectors...")
    sec_rows = supabase.table("securities").select("id,ticker,sector").neq("ticker", "SPY").execute().data
    ticker_to_sector = {r["ticker"]: r["sector"] for r in sec_rows}
    sector_to_security_ids = defaultdict(list)
    ticker_to_security_id = {}
    for r in sec_rows:
        ticker_to_security_id[r["ticker"]] = r["id"]
        if r["sector"]:
            sector_to_security_ids[r["sector"]].append(r["id"])
    print(f"  {len(sec_rows)} real securities, {len(sector_to_security_ids)} real sectors.\n")

    print("Bulk-loading real market_prices for every security (this is the expensive real step)...")
    prices_by_security = load_all_prices()
    print(f"  {len(prices_by_security)} real securities with price data loaded.\n")

    print("Fetching real event_market_reactions_corrected rows needing a sector benchmark...")
    emr_rows = paginated("event_market_reactions_corrected",
                          "event_id,ticker,event_date,return_0d,return_1d,return_5d,return_20d,sector_peer_n",
                          "event_id")
    to_process = [r for r in emr_rows if r["sector_peer_n"] is None]
    print(f"  {len(emr_rows)} real rows total, {len(to_process)} need a sector benchmark.\n")

    rows_to_write = []
    skipped_no_sector = 0
    skipped_too_few_peers = 0
    for r in to_process:
        ticker = r["ticker"]
        sector = ticker_to_sector.get(ticker)
        if not sector:
            skipped_no_sector += 1
            continue

        peer_ids = [sid for sid in sector_to_security_ids[sector] if sid != ticker_to_security_id.get(ticker)]
        event_date = str(r["event_date"])[:10]

        peer_returns = {0: [], 1: [], 5: [], 20: []}
        for peer_id in peer_ids:
            if peer_id not in prices_by_security:
                continue
            dates, closes = prices_by_security[peer_id]
            for offset in (0, 1, 5, 20):
                ret = company_return_as_of(dates, closes, event_date, offset)
                if ret is not None:
                    peer_returns[offset].append(ret)

        if len(peer_returns[0]) < MIN_PEERS_REQUIRED:
            skipped_too_few_peers += 1
            continue

        def avg(lst):
            return sum(lst) / len(lst) if lst else None

        sector_0d = avg(peer_returns[0])
        sector_1d = avg(peer_returns[1])
        sector_5d = avg(peer_returns[5])
        sector_20d = avg(peer_returns[20])

        row = {"event_id": r["event_id"], "sector_peer_n": len(peer_returns[0])}
        if sector_0d is not None:
            row["sector_peer_return_0d"] = round(sector_0d, 6)
            row["abnormal_return_vs_sector_0d"] = round(r["return_0d"] - sector_0d, 6) if r["return_0d"] is not None else None
        if sector_1d is not None:
            row["sector_peer_return_1d"] = round(sector_1d, 6)
            row["abnormal_return_vs_sector_1d"] = round(r["return_1d"] - sector_1d, 6) if r["return_1d"] is not None else None
        if sector_5d is not None:
            row["sector_peer_return_5d"] = round(sector_5d, 6)
            row["abnormal_return_vs_sector_5d"] = round(r["return_5d"] - sector_5d, 6) if r["return_5d"] is not None else None
        if sector_20d is not None:
            row["sector_peer_return_20d"] = round(sector_20d, 6)
            row["abnormal_return_vs_sector_20d"] = round(r["return_20d"] - sector_20d, 6) if r["return_20d"] is not None else None

        rows_to_write.append(row)

    print(f"{len(rows_to_write)} real rows to write, {skipped_no_sector} skipped (no sector), "
          f"{skipped_too_few_peers} skipped (fewer than {MIN_PEERS_REQUIRED} real peers with data that early).\n")

    if not live:
        print("DRY RUN -- nothing written. Pass --live to write.")
        if rows_to_write:
            print("Sample row:", rows_to_write[0])
        return

    # REAL FIX (2026-10-13): one-row-at-a-time writes hit the same
    # reproducible HTTP/2 connection-recycling limit (last_stream_id:19999)
    # that's crashed multiple scripts this project -- confirmed live on
    # this exact run (6,615 of 15,816 written before the crash). Real
    # fix, same proven pattern as populate_company_status.py: a genuine
    # server-side bulk UPDATE via a Postgres function
    # (bulk_update_sector_benchmark, UPDATE ... FROM jsonb_to_recordset),
    # called through supabase.rpc() in large chunks -- a true PARTIAL
    # update (only the real sector-benchmark columns touched), not
    # upsert()'s risky full-row-replace. Also adds real resume-safety:
    # skip event_ids that already have a non-null sector_peer_n, so a
    # re-run after any future crash picks up exactly where it left off.
    already_done = {r["event_id"] for r in paginated(
        "event_market_reactions_corrected", "event_id", "event_id",
        [lambda q: q.not_.is_("sector_peer_n", "null")])}
    before_resume = len(rows_to_write)
    rows_to_write = [r for r in rows_to_write if r["event_id"] not in already_done]
    print(f"  {before_resume - len(rows_to_write)} already written in a prior run, skipping. "
          f"{len(rows_to_write)} real rows remaining.\n")

    BATCH = 2000
    written = 0
    for i in range(0, len(rows_to_write), BATCH):
        chunk = rows_to_write[i:i + BATCH]
        result = supabase.rpc("bulk_update_sector_benchmark", {"updates": chunk}).execute()
        written += result.data if isinstance(result.data, int) else len(chunk)
        print(f"  ...{written}/{len(rows_to_write)} written")
    print(f"\nReal write complete: {written} rows updated.")


if __name__ == "__main__":
    main()
