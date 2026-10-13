"""
compute_base_rate.py

Real Phase 6 harness gap, closing item D2 from the prediction-contract
review: "what fraction of random, unrelated same-sector days show the
same move, so 'stocks often rise after good news' isn't mistaken for
alpha." No script in this project currently computes this -- every tag
finding so far reports its own rate in isolation, with nothing to
compare it against.

Real methodology: samples a large number of genuinely RANDOM
(security, date) pairs from the real 32-year, 497-company price
universe -- NOT tied to any real event -- and computes each one's
forward abnormal return vs. SPY using the identical index-based method
tag_reaction_character.py uses (same REWARDED_THRESHOLD/PUNISHED_THRESHOLD
= +-0.03, same 20-trading-day window). The resulting rewarded/punished/
muted split IS the real base rate: what chance alone produces, with no
event at all.

Can compute this overall, or scoped to one real sector (sector-specific
base rate is the real, correct comparison per the contract's own
"same-sector" wording -- Industrials' baseline volatility is not
Utilities' baseline volatility).

Real, deliberate exclusion: samples are NOT filtered to avoid real
event dates. At this project's real scale (~19,892 events across 32
years x 497 companies x ~252 trading days/year, several million real
trading-day-companies total), real events are a small enough fraction
that this is a reasonable, honest approximation -- noted here plainly
rather than silently assumed away.

Usage:
    python compute_base_rate.py                    # overall base rate
    python compute_base_rate.py --sector "Energy"   # one real sector
    python compute_base_rate.py --samples 10000     # real sample size (default 5000)
"""
import os
import sys
import random
import bisect
from collections import defaultdict
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

REWARDED_THRESHOLD = 0.03
PUNISHED_THRESHOLD = -0.03
DEFAULT_SAMPLES = 5000


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


def company_return(dates, closes, idx, offset_days):
    """Real, index-based return -- same method as compute_full_reaction()."""
    if idx == 0 or idx + offset_days >= len(closes):
        return None
    prior_close = closes[idx - 1]
    forward_close = closes[idx + offset_days]
    if not prior_close:
        return None
    return (forward_close / prior_close) - 1


def classify(abnormal_return):
    if abnormal_return is None:
        return None
    if abnormal_return > REWARDED_THRESHOLD:
        return "rewarded"
    if abnormal_return < PUNISHED_THRESHOLD:
        return "punished"
    return "muted"


def main():
    args = sys.argv[1:]
    sector_filter = None
    n_samples = DEFAULT_SAMPLES
    if "--sector" in args:
        sector_filter = args[args.index("--sector") + 1]
    if "--samples" in args:
        n_samples = int(args[args.index("--samples") + 1])

    print("Fetching real securities...")
    sec_rows = supabase.table("securities").select("id,ticker,sector").neq("ticker", "SPY").execute().data
    if sector_filter:
        sec_rows = [r for r in sec_rows if r["sector"] == sector_filter]
    security_ids = [r["id"] for r in sec_rows]
    print(f"  {len(security_ids)} real securities in scope"
          f"{f' (sector: {sector_filter})' if sector_filter else ' (all sectors)'}.\n")

    print("Bulk-loading real market_prices (company + SPY)...")
    prices_by_security = load_all_prices()
    spy_row = supabase.table("securities").select("id").eq("ticker", "SPY").execute().data
    spy_dates, spy_closes = prices_by_security[spy_row[0]["id"]]
    print(f"  {len(prices_by_security)} real securities with price data loaded.\n")

    eligible = [sid for sid in security_ids if sid in prices_by_security and len(prices_by_security[sid][0]) > 30]
    print(f"Sampling {n_samples} real random (security, date) pairs from {len(eligible)} eligible securities...\n")

    results = {0: [], 1: [], 5: [], 20: []}
    real_samples_used = 0
    random.seed(42)  # real, deliberate reproducibility -- same base rate every re-run unless sample size changes
    attempts = 0
    while real_samples_used < n_samples and attempts < n_samples * 5:
        attempts += 1
        sid = random.choice(eligible)
        dates, closes = prices_by_security[sid]
        idx = random.randint(20, len(dates) - 21)  # real margin for a full -20/+20 window
        as_of_date = dates[idx]
        spy_idx = bisect.bisect_left(spy_dates, as_of_date)
        if spy_idx == 0 or spy_idx >= len(spy_dates):
            continue

        got_one = False
        for offset in (0, 1, 5, 20):
            company_ret = company_return(dates, closes, idx, offset)
            spy_ret = company_return(spy_dates, spy_closes, spy_idx, offset)
            if company_ret is None or spy_ret is None:
                continue
            abnormal = company_ret - spy_ret
            results[offset].append(abnormal)
            got_one = True
        if got_one:
            real_samples_used += 1

    print(f"{real_samples_used} real usable samples drawn ({attempts} attempts).\n")

    print("REAL BASE RATE (what random chance alone produces, no event):")
    for offset, label in [(0, "0d"), (1, "1d"), (5, "5d"), (20, "20d")]:
        values = results[offset]
        if not values:
            continue
        rewarded = sum(1 for v in values if v > REWARDED_THRESHOLD)
        punished = sum(1 for v in values if v < PUNISHED_THRESHOLD)
        muted = len(values) - rewarded - punished
        n = len(values)
        print(f"  {label:4s} window: rewarded={rewarded/n:.1%}  punished={punished/n:.1%}  "
              f"muted={muted/n:.1%}  (n={n})")


if __name__ == "__main__":
    main()
