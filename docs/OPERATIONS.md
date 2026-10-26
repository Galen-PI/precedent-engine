> **Curated text, last edited 2026-09-29, moved here from the old SCRIPTS.md Part 1 on 2026-10-26.** The verified, generated interface of every script is docs/SCRIPTS_REFERENCE.md; changes after 2026-09-29 are in CHANGELOG.md. Where this text and the generated reference disagree, the reference wins.

# Scripts Reference

Real, verified interfaces for every script in the pipeline, so a future session doesn't
have to rediscover this by pasting file contents again. Two parts: **Current Reference**
(what's true now — read this first) and **Session Changelog** (dated history of what was
found/fixed, kept for provenance).

---


## Company Onboarding Pipeline

Order matters — each step depends on the one before it.

**One-command version (recommended):**
```bash
python scripts/onboard_pipeline.py TICKER
```
Chains all 8 steps below, with a verification check and a logged record (into
`onboarding_runs` / `onboarding_run_steps`) after every step. If a check comes back wrong,
the run is marked `flagged` and the pipeline stops rather than continuing on bad data.

Check for unreviewed problems anytime:
```sql
SELECT r.ticker, r.started_at, r.status, s.step_name, s.status, s.detail
FROM onboarding_runs r JOIN onboarding_run_steps s ON s.run_id = r.id
WHERE r.reviewed = false AND r.status IN ('flagged', 'failed')
ORDER BY r.started_at DESC, s.started_at;
```

**Manual step-by-step version** (finer control, or onboarding many companies at once):

1. **Create entity + security rows**
```bash
   python scripts/bulk_onboard_step1_2.py --file some_ticker_list.txt
   python scripts/bulk_onboard_step1_2.py TICKER1 TICKER2 ...
```
   Uses SEC's official `company_tickers.json` for real names/CIKs. Safe to re-run — skips
   tickers already in `securities`.

2. **Map into the ingestion scripts' hardcoded dicts/lists**
```bash
   python scripts/bulk_add_company_mappings.py                    # all securities missing from CIK_TO_TICKER
   python scripts/bulk_add_company_mappings.py TICKER1 TICKER2 ...
```
   Pure local file editing (`ingest_sec_financials_multi.py`'s `CIK_TO_TICKER`/
   `FISCAL_YEAR_END` dicts and `import_8k_filings.py`'s `COMPANIES` list). No rate-limited
   API calls. Single company: `python scripts/add_company_mappings.py TICKER CIK ENTITY_ID SECURITY_ID`

3. **Ingest financials**
```bash
   python scripts/bulk_ingest_financials.py
   python scripts/bulk_ingest_financials.py TICKER1 ...
```
   Reuses `ingest_sec_financials_multi.py` directly (imported, not reimplemented). Hits
   SEC's own API (generous limits). Checks real DB state first — safe to interrupt/re-run.
   Single company (CIK only): `python scripts/ingest_sec_financials_multi.py CIK`

4. **Import raw 8-K filings**
```bash
   python scripts/bulk_import_8k.py
   python scripts/bulk_import_8k.py TICKER1 ...
```
   Reuses `import_8k_filings.py`'s real functions. Checks real DB state (zero
   `sec_8k_filings` rows = needs it). Manual/single: `python scripts/import_8k_filings.py
   TICKER1 TICKER2 ...` — no args re-processes the ENTIRE hardcoded `COMPANIES` list, slow,
   usually not what you want.

5. **Ingest prices — do not bulk naively.** Twelve Data's real observed limit is ~8
   requests/minute; more parallelism just produces more 429s.
```bash
   python scripts/bulk_ingest_prices.py
   python scripts/bulk_ingest_prices.py TICKER1 ...
```
   Paces itself at ~8s/request, auto-retries on 429 with backoff, checks real DB state
   first. Expect ~16s/ticker; ~400 tickers takes ~100-110 minutes.
   Manual/single (two-call pattern, avoids a truncation bug on very long single-window
   requests):
```bash
   python scripts/ingest_market_prices.py TICKER 1994-01-01 2011-12-31
   python scripts/ingest_market_prices.py TICKER 2012-01-01 <today>
```
   **No incremental updater existed until 2026-09-28** — neither script above refreshes an
   already-loaded ticker forward from its last stored date. See
   `scripts/ingestion/refresh_market_prices.py` under "Stale-URL Sweep & Price Refresh"
   below for that job.

6. **Classify 8-K filings (AI-assisted, staging only)**
```bash
   python scripts/classify_8k_filings_batch_v2.py TICKER [TICKER2 ...] [--yes]
   python scripts/classify_8k_filings_batch_v2.py ALL
```
   Concurrent SEC fetching, multi-ticker batch support, chunked multi-batch Anthropic
   submission, pre-flight cost estimate with y/N confirmation (`--yes` skips it). Writes
   ONLY to `filing_ai_classifications` (staging) — never promotes directly. `PROMPT_VERSION`
   tracked per-row. **2026-09-28 fix**: `fetch_filing_text()` now streams the download and
   caps at 2MB raw bytes instead of holding full multi-MB filings in memory — was causing
   OOM kills on sweep-style runs holding thousands of filings at once (3-4 copies per
   worker × 3 workers). Callers only ever use the first 15-30K characters anyway.

   Real result to expect: most `flag_reason = 'novel_real_event_no_template_match'` is
   inherent to brand-new companies with zero event history — every company's first
   confirmed real event is "novel" by definition. This is the check-and-balance working
   correctly.

   **Reviewing the backlog** — measure real agreement rate on a sample first, don't
   eyeball it:
```sql
   SELECT ai_confidence >= 0.9 AS high_confidence,
          (ai_matched_known_template IS NOT NULL) AS matched_template,
          ai_verdict, human_verdict, COUNT(*) AS n,
          ROUND(100.0 * COUNT(*) FILTER (WHERE human_agreed_with_ai) / COUNT(*), 1) AS agree_pct
   FROM filing_ai_classifications
   WHERE human_verdict IS NOT NULL
   GROUP BY 1, 2, 3, 4 ORDER BY high_confidence DESC, matched_template DESC, n DESC;
```
   As of 2026-09, two buckets measured ~99-100% agreement across thousands of rows and are
   safe to bulk auto-confirm without individual review:
   - `ai_verdict = 'likely_noise' AND ai_confidence >= 0.9` (regardless of template match)
   - `ai_verdict = 'real_event' AND ai_confidence >= 0.9 AND ai_matched_known_template IS NULL`

   **Correction, 2026-09-29: the real code (`compute_flag()`) only flags below 0.75, not
   0.90 -- the >=0.9 threshold above was never what's actually running in production.**
   A real spot-check of the true unvalidated 0.75-0.90 band found a real ~8% disagreement
   rate (n=25), meaningfully higher than the ~1% measured for >=0.90. Treat >=0.9 as the
   only genuinely validated safe-to-bulk-confirm bar; the 0.75-0.90 band (4,060 rows as
   of 2026-09-29) needs either a real, larger validation pass or individual review.

   Everything else needs real individual attention. `flag_reason = 'random_audit_sample'`
   is a genuine 10% random QA sample, safe to spot-check — but it's drawn after other
   filters, so it's not representative of the whole pool. See `event-materiality-review.md`
   (linked from `working-practices.md`) for the actual confirm/reject test to apply when
   reading each row — it's a judgment test, not a checklist, and has real documented
   exceptions in both directions.

7. **Promote confirmed real_events into `events` rows**
```bash
   python scripts/promote_events.py                              # dry run
   python scripts/promote_events.py --live                        # writes
   python scripts/promote_events.py --live --ticker TICKER        # scoped to one company
   python scripts/promote_events.py --live --limit 50              # cap, for testing
   python scripts/promote_events.py --exclude-types capital_raise,corporate_action --live
   python scripts/promote_events.py --only-title-match "REGEX" --live   # added 2026-09-28
```
   Groups confirmed `real_event` rows by `(filing_date, accession_number)` — collapses
   dual-ticker filings (NWS/NWSA file identical 8-Ks under both tickers, same accession
   number) into one event instead of duplicates. Two-stage duplicate check: (1) heuristic —
   same entity, `event_date` within ±14 days of an existing event; (2) a real LLM
   verification call on every heuristic match before trusting it — the heuristic alone had
   a measured ~33% false-positive rate at sample scale. `--exclude-types` skips entire
   `ai_suggested_event_type` categories (used to hold back `capital_raise`/`corporate_action`
   pending a closer look at which are routine vs. deal-tied financing).
   `--only-title-match` filters by a regex against the title (used for narrow slices like
   "all the stock splits" or "financing tied to a named deal").

   Tracks promotion via `event_source_filings` (ticker, filing_date, accession_number →
   event_id) — always safe to re-run, already-promoted filings auto-skip. **Proven safe
   across three real interruption types** (Ctrl+C, network drop, full machine restart) —
   verified via integrity checks after each, zero corruption found. Wrap a long pass in an
   auto-restart loop:
```bash
   until python scripts/promote_events.py --live; do
       echo "Crashed -- restarting in 10 seconds..."
       sleep 10
   done
```
   Known slow/silent point: for tickers with dense existing history (XOM, GE, PG, AEP, CCL),
   the "Loading existing events for duplicate-checking" phase can take a while with zero
   visible progress — normal, not a hang. Verify real progress via
   `SELECT COUNT(*) FROM event_source_filings;` in a separate query.

   **After any promotion pass touching `capital_raise`-adjacent events**, check for routine
   events that slipped through (standalone buybacks/dividends/notes with no named deal) —
   see the removal pattern in the 2026-09-28 changelog entry below. This has happened twice
   now (Baxter's buyback, Adobe's senior notes) and needs a human read, not a rule.

## Deterministic (non-AI) tag computation

**`compute_chain_position.py`** — computes `chain_position_opening/middle/closing`, a
purely deterministic fact about event ORDER within a `same_entity_sequence` chain.
```bash
python scripts/compute_chain_position.py              # all companies
python scripts/compute_chain_position.py TICKER        # one company
python scripts/compute_chain_position.py --dry-run     # print, don't write
```

**`resolve_sentiment_confounds.py`** — computes `sentiment_confirms_confound`/
`sentiment_reveals_distinct_driver` from real `company_sentiment_timeline` data vs. a
same-sector peer baseline. Dynamically discovers which sectors currently have enough real
peer coverage (default: 2+ other same-sector companies with sentiment data). Never lower
`--min-peers` below 2 without a real reason — a 1-peer "baseline" measures noise, not
genuine divergence (tested true for Energy specifically). Structurally limited to events
after 2015-02-17 (real sentiment coverage start) — most of its skip rate on older events
is this boundary, not a bug.
```bash
python scripts/resolve_sentiment_confounds.py           # dry run
python scripts/resolve_sentiment_confounds.py --live    # writes
```

## AI-suggested tags (staging only, human confirmation required)

**`suggest_event_tags_batch.py`** — Batch API version of `suggest_event_tags.py`. Writes
ONLY to `event_tag_suggestions` — nothing auto-applies to `event_tags`.
```bash
python scripts/suggest_event_tags_batch.py              # all untagged/unsuggested events
python scripts/suggest_event_tags_batch.py TICKER
python scripts/suggest_event_tags_batch.py --yes          # skip confirmation, chained runs
```
Excludes 5 tags from the AI's options (`chain_position_*`, `sentiment_*`) — computed by
the two deterministic scripts above instead. Calibration: `same_entity_sequence` needs a
stricter auto-flag threshold (0.87, not the general 0.75) — can produce a genuine miss at
confidence as high as 0.85.

## `tag_reaction_character.py` — computes rewarded/punished/muted from real price data

```bash
python scripts/tagging/tag_reaction_character.py                 # all untagged events
python scripts/tagging/tag_reaction_character.py TICKER
python scripts/tagging/tag_reaction_character.py TICKER --window 5    # override 20-day default
python scripts/tagging/tag_reaction_character.py --dry-run
python scripts/tagging/tag_reaction_character.py --find-dates TICKER "keyword"   # for bundled events
python scripts/tagging/tag_reaction_character.py --tag-one <event_id> <YYYY-MM-DD>
python scripts/tagging/tag_reaction_character.py --backfill-magnitudes
```
Deterministic (not AI judgment) — writes directly to `event_tags`, no staging table.
Computes real 0d/1d/5d/20d abnormal returns and upserts into `event_market_reactions_corrected`
(on every tag/retag).

**Crashes reliably around ~20,000 requests** (HTTP/2 `last_stream_id` cap) with no built-in
recovery — wrap in a restart loop, same pattern as `promote_events.py`:
```bash
until python -u scripts/tagging/tag_reaction_character.py >> tag_reaction_full.log 2>&1; do
    echo "Crashed -- restarting in 5 seconds..." >> tag_reaction_full.log
    sleep 5
done
```

**2026-09-28 fix**: previously accepted any window ≥2 prices as valid, silently producing
a "20-day" reaction from as few as 8 real days when recent price data was incomplete —
biased short-window events toward `muted`. Now requires the real full `window_days + 1`
prices for both company and SPY, or skips (to be picked up on a later run once prices
catch up).

**Known bug, NOT yet fixed as of 2026-09-29**: computes exactly ONE reaction per event,
from the FIRST-linked entity only (`ticker = e["tickers"][0]`) — even when an event links
many companies. Confirmed example: the COVID-19 panic event links 17 companies, all get the
SAME tag from whichever company happened first. Sized on 2026-09-29:
**49 of 15,928 currently-tagged events (0.3%) are multi-entity** and exposed to this —
small in count, but concentrated in exactly the large macro/systemic events where getting
it right matters most (confirmed to have inflated `systemic_shock`'s apparent predictive
strength in earlier model testing). `event_entity_relationships.relationship_type`
(primary/affected/actor/competitor) already exists and could disambiguate — unused by this
script or any downstream model. **Real fix needed before trusting any
`systemic_shock`/`geopolitical`/`government_action` model result.**

## GDELT / Global Events Pipeline

**`discover_global_events_combined.py`** — resume-safe, checkpoints per-month.
```bash
python scripts/discover_global_events_combined.py 2015-02 2026-09 --dry-run-only
python scripts/discover_global_events_combined.py 2015-02 2026-09 --live
```

**`fetch_global_daily_totals.py`** — total (unfiltered) daily GDELT article volume, needed
so episode/spike detection can measure a theme's SHARE of coverage rather than raw count
(raw count conflates real events with the corpus's own secular growth over 11 years).
```bash
python scripts/fetch_global_daily_totals.py 2015-02 2026-09 --dry-run-only
python scripts/fetch_global_daily_totals.py 2015-02 2026-09 --live
```

**`backfill_gdelt_sentiment.py`** — has NO `--live` flag; writes for real BY DEFAULT.
```bash
python scripts/backfill_gdelt_sentiment.py 2015-02 2026-09                     # writes for real
python scripts/backfill_gdelt_sentiment.py 2015-02 2026-09 --dry-run-only      # print cost, write nothing
python scripts/backfill_gdelt_sentiment.py 2015-02 2026-09 --ignore-checkpoint # re-run completed months
```
**Coverage as of 2026-09-29: 445 distinct entities in `company_sentiment_timeline`**
(verified live — corrects an earlier session's 184/497 figure, which is stale).

**`build_event_episodes.py`** — **UNRESOLVED as of 2026-09-22, status not re-checked
since.** Meant to group consecutive days of elevated theme coverage into one episode. Four
iterations each broke a case the previous one fixed (see Changelog for detail). Root cause
identified (needs theme SHARE of total coverage, not absolute count) but not implemented.
`global_event_episodes` table is empty. Simpler proven alternative already exists:
`global_events.severity`/`reviewer_note`, populated for 11 confirmed multi-day events by
hand — worth considering instead of finishing the algorithmic approach.

## Sector / Data Quality

**`populate_sectors_gics.py`** — the real, correct sector-backfill. `populate_sectors.py`
(SIC-code-based) is an abandoned first attempt — **do not use**, produced confirmed
misclassifications (NOC labeled Health Care, Garmin wrong). Uses real S&P 500 GICS data
transcribed from the authoritative constituent list.
```bash
python scripts/populate_sectors_gics.py --dry-run
python scripts/populate_sectors_gics.py --live
```

## Stale-URL Sweep & Price Refresh (added 2026-09-28/29)

**`sweep_stale_url_noise.py`** — re-classifies old `likely_noise` verdicts whose
`primary_document_url` predates the URL-building fix (points at cover-page-only text
instead of the complete-submission `.txt` with exhibits). Writes ONLY to
`stale_url_sweep_results`, never touches `filing_ai_classifications` directly.
```bash
python scripts/classification/sweep_stale_url_noise.py --limit 2500 --yes
```
Real measured rate: ~1% of old-noise stale-URL verdicts hide a genuine deal/restructuring/
investigation that only appears in the exhibit text. Every flip needs individual human
read — see `event-materiality-review.md`. After review, mark `review_status =
'confirmed'`/`'rejected'` in the sweep table, then run `writeback_confirmed_sweep_flips.py`
to push confirmed rows into `filing_ai_classifications`.

**`draft_missing_event_text.py`** — drafts title/description for confirmed `real_event`
rows that have neither (model sometimes returns a verdict with no text on a first pass).
`--only TICKER:DATE,...` targets specific rows; `--skip TICKER:DATE,...` on `--apply`
excludes rows you've decided not to write. Accepts an optional `focus` hint (existing
`ai_reasoning` text) — needed when a filing discusses multiple things and the model's first
attempt picks the wrong one (fixed ADSK 2012-08-23 this way, which first drafted the
quarterly earnings instead of the $50-60M restructuring in the same filing).

**`refresh_market_prices.py`** — the incremental price updater that never existed before.
For each ticker, fetches from a few days before its last stored date to today, and checks
the OVERLAP against what's stored before appending — because prices are fetched with
`adjust=all`, so a dividend/split with an ex-date after the last fetch restates the whole
adjusted series. Tickers whose overlap doesn't match (`restated`) are flagged and NOT
appended — they need a full-history refetch instead (`ingest_market_prices.py`, both date
windows) to get back on one consistent adjustment basis.
```bash
python scripts/ingestion/refresh_market_prices.py --tickers AAPL MSFT
python scripts/ingestion/refresh_market_prices.py --all --apply --max-requests 500
```
**Real finding 2026-09-28**: no scheduled job refreshes prices at all — `market_prices` had
silently drifted ~1 month stale (some tickers 5-6 weeks) with no error, no alert. SPY
(the benchmark for every abnormal return in this project) was itself `restated` and needed
a full refetch before any downstream tagging/ripple work on recent events could be trusted.
~10-11% of tickers restate on any given check (measured on the A-C alphabetical slice).

## Known Gotchas

- Downloaded files land on your local machine, not the Codespace — use a heredoc directly
  in the terminal for getting a large list in.
- `event_market_reactions` is a read-only VIEW, always recomputes live from
  `events.event_date` — wrong for bundled/enriched events (stored `event_date` is often the
  bundle's summary date). Corrected values live in `event_market_reactions_corrected`
  (real table); the view COALESCEs over that first.
- `compute_abnormal_return` and `compute_full_reaction` must use the SAME baseline
  methodology (prior trading day's close, not event day's own close) — diverged once,
  caused 180 mislabeled `reaction_character` tags project-wide before being caught.
- Twelve Data 429s get worse with more parallel terminals — they share one per-minute cap.
  Same for SEC/Anthropic at scale. `FETCH_CONCURRENCY` lowered 10→3 after real 429 storms.
- `entities.ticker` is sparsely populated — the authoritative ticker is `securities.ticker`
  (joined via `securities.entity_id`), always populated.
- NWS/NWSA (News Corp dual-class) file identical 8-Ks under both tickers, same accession
  number — dedupe by `(filing_date, accession_number)`, not by ticker.
- `sec_filings` and `sec_8k_filings` are misleadingly named — `sec_filings` has ONLY
  10-K/10-Q data (zero 8-Ks); the real 8-K data lives in `sec_8k_filings`.
- **"Always-same-value" dead tracking columns** — a null-rate or constant-value alone never
  proves a pipeline is broken; check for a real working alternate mechanism first. Confirmed
  examples: `sec_8k_filings.promoted_to_event` (FALSE for all 154,607 rows — real
  promotion pipeline works, verify via `event_source_filings` instead),
  `event_pre_context.surprise_vs_consensus` (always NULL), `financial_condition_score
  .fcf_margin_change` (always NULL, though ingredients exist for 4,489 rows — cheap
  unbackfilled improvement), `event_pre_context.size_bucket` (97% populated but every
  populated value is identical — this universe has no smaller-cap companies to bucket
  differently).
- `financial_market_reactions` (VIEW) computes real abnormal returns (0/1/5/20-day vs SPY)
  for ~every quarterly/annual filing — 35,826 rows, 496/497 securities, 98.6-99.4%
  populated. Sitting completely unused by any model/test as of 2026-09-22 — likely the
  strongest available foundation for predicting market reaction to financial results,
  independent of the `events`/`reaction_character` system entirely. **Status not
  re-checked since — worth confirming whether this is still true before assuming it.**
- Any script holding thousands of full filing texts or price series in memory at once is a
  real OOM risk on this Codespace (7.8GB total) — stream/truncate at fetch time, don't rely
  on a downstream slice. Bit both `tag_reaction_character.py`'s (indirect, via price
  windows — not yet confirmed as a memory issue) and `sweep_stale_url_noise.py`'s fetch
  step (confirmed, fixed 2026-09-28).
- **`financial_statements.free_cash_flow` backfill claim is stale.** The 2026-09-22 note
  ("4,489 rows have both ingredients but the subtraction was never computed") is no longer
  true — verified live 2026-09-29: only 36 rows remain unbackfilled. Either fixed and
  never marked resolved, or the denominator shifted since — not re-investigated further,
  just corrected here so it isn't repeated as current.
- **`populate_financial_metrics.py`'s own printed summary line is unreliable — verify the
  real count directly, don't trust it.** Found 2026-09-29: two large, fully-onboarded
  companies (MA: 93 statement rows, ADBE: 82) had ZERO financial_metrics rows despite
  complete real revenue history back to 2007 — the script has no CLI args and no
  ticker-based skip logic (`fetch_financial_statements()` is an unconditional, paginated
  `select("*")`), so this was very likely just "script last ran before these companies'
  statements existed," not a per-company bug. Re-ran it live (safe: chunked per-security
  upsert on `(security_id, period_type, period_end)`, isolated failure handling). The
  script's own final printout said "Total metrics: 36001" (matching total statement
  count exactly, implying 100% coverage) — **this was wrong.** Direct verification showed
  the real total was 35,819, not 36,001 — the script's summary logic has a real bug of
  its own, separate from the coverage gap it partly fixed. Real outcome: metrics coverage
  34,662 -> 35,819 (+1,157). ADBE fully recovered (82/82). MA nearly complete (90/93, 3
  still missing). 182 rows remain uncovered project-wide — not yet root-caused; some is
  plausibly the `growth()` helper correctly returning NULL for each company's first
  tracked period (no prior period to compare against), but 182 across ~499 companies is
  lower than that alone would predict, so this isn't confirmed as the full explanation.

---

