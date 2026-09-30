# Scripts Reference

Real, verified interfaces for every script in the pipeline, so a future session doesn't
have to rediscover this by pasting file contents again. Two parts: **Current Reference**
(what's true now — read this first) and **Session Changelog** (dated history of what was
found/fixed, kept for provenance).

---

# PART 1: CURRENT REFERENCE

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

# PART 2: SESSION CHANGELOG

Dated history of what was found and fixed. Current Reference above already incorporates
all of this — read this section only for provenance/context, not to find out what's true
now.

### 2026-09-11
`pattern_significance_tests` populated — 13 chi-square results, 4 tags statistically
significant at the time (`same_entity_sequence`, `high_confidence_causal_link`,
`multi_stage_divestiture`, `confounded_regulatory_action`). Predates the 09-22 multi-entity
tagging bug discovery — worth re-running `test_pattern_significance.py` once that's fixed,
to check whether any of the four partly depended on the same mislabeling mechanism that
inflated `systemic_shock`.

### 2026-09-22 — Database Audit, GDELT Backfill, Reaction-Tagging Fixes
- Found and fixed: `get_untagged_events()` unpaginated query silently capped at 1,000 rows,
  reporting ~70 events needing tags instead of the real ~11,500+.
- Found (not fixed until 09-29's window guard): the per-event, first-entity-only reaction
  tagging bug (see Current Reference above).
- `populate_sectors_gics.py` built and run — resolved 419/421 NULL sectors; last case
  (VMRK) needed manual entry after discovering the AvalonBay/EQR merger.
- AVB/EQR/VMRK: confirmed a real 2026-08-17 merger of equals explains both tickers'
  disappearance from `market_prices` — not a Twelve Data limitation as previously assumed.
  EA's absence remained genuinely unexplained at the time (no merger applies) --
  see the 2026-09-30 entry above: real cause is a Twelve Data paid-tier restriction.
- `multi_feature_model.py`: fixed an N+1 query bug in `get_sentiment_bucket()` (thousands
  of sequential round-trips → one bulk fetch). Added `--exclude-bundled`; found it barely
  moved test accuracy (32.8%→32.9%), so date-bundling contamination doesn't explain that
  model's null result.
- `discover_global_events_combined.py`: patched for per-month checkpointing (a crash
  previously meant zero rows written for the whole run, not partial credit).
- `build_event_episodes.py`: four iterations, each breaking a case the last one fixed (v1
  closed real episodes too early; v2 fixed that but produced multi-year false episodes; v3
  regressed; v4 fixed the test case but still produced multi-year episodes elsewhere).
  Root cause identified, not implemented.
- GDELT sentiment: found `TRACKED_COMPANIES` hardcoded to only ~184 of ~497 securities.
  Extension drafted (`tracked_companies_extension.py`), not yet merged as of this date.
  **Superseded 2026-09-29: coverage is now 445, so this was merged/expanded since.**

### Earlier (undated in source) — PROJECT_PLAN.md findings, folded in above
Multi-entity tag bug's COVID-19/2008-crisis examples; `sec_filings`/`sec_8k_filings` naming
swap; dead-column pattern; `financial_market_reactions` discovery — all incorporated into
Current Reference and Known Gotchas above.

### 2026-09-30 — Financial-sector quarterly gap: real partial win, real deeper bug found and NOT fixed
Real follow-up after rolling the RevenuesNetOfInterestExpense fix out to 13 more
likely bank tickers (BNY, MTB, TFC, SYF, RF, NTRS, FITB, MS, USB, HBAN, WFC, KEY,
COF), all already correctly present in `CIK_TO_TICKER` (checked first, none needed
a GS-style mapping fix).

**Real, honest result: only 3 of 14 tickers touched today actually improved.**
GS 17->4, WFC 7->2, MS 11->0 (fully resolved). **The other 11 are completely
unchanged** (BNY 19, MTB 17, TFC 16, RF 14, SYF 14, FITB 12, NTRS 12, USB 9,
HBAN 7, COF 6, KEY 5) -- the concept addition only helps companies that actually
report under `RevenuesNetOfInterestExpense`; it doesn't generalize to every bank.

**Real, deeper bug found while investigating BNY specifically, NOT fixed today:**
fetched BNY's real SEC XBRL data directly. It has abundant real data under
concepts the script ALREADY recognizes -- 83 real 10-Q `Revenues` facts, 200+ real
`NetIncomeLoss` facts. Yet BNY's ingestion still reports "missing Q1/Q2/Q3" for
nearly its entire 19-year history. **This is not a missing-concept problem at
all** -- something in the script's real quarter-assignment/period-matching logic
fails to pair these genuinely-present facts into Q1/Q2/Q3 periods for this
company. Working theory, not confirmed: BNY may report cumulative year-to-date
figures in its 10-Qs (common practice for some filers) rather than standalone
quarterly figures, which a date-matching algorithm built around standalone
periods would silently reject. **This needs real, dedicated time reading the full
`build_quarterly_periods()` logic (hundreds of lines) to properly diagnose --
deliberately not attempted rushed tonight.** Likely explains most/all of the
remaining 11 unchanged tickers, and plausibly a real fraction of the wider
367-ticker pattern beyond just banks.

**Real, honest summary of tonight's XOM/quarterly-gap thread:** XOM itself
formally accepted as out-of-scope (confirmed real, deep, hard). Found a real,
working partial fix (3 tickers) for part of the broader 367-ticker pattern. Found
and clearly scoped a second, deeper, unfixed bug affecting most of the rest.
Genuine progress, genuinely incomplete -- not oversold as "solved."

### 2026-09-30 — Real fix found for the financial-sector quarterly gap: RevenuesNetOfInterestExpense
Real follow-up to the XOM/Q4-gap investigation above. Confirmed the working theory:
fetched Goldman Sachs' real SEC XBRL company-facts data directly and found
`RevenuesNetOfInterestExpense` -- a standard concept many banks use instead of the
regular "Revenues" concept -- with 130 real, well-populated quarterly facts, values
matching GS's real reported scale (e.g. $15.184B Q3 2025). Added it to
`CONCEPTS["revenue"]` in `ingest_sec_financials_multi.py` (not a per-ticker
composite hack -- this is a real, standard concept, so any ticker using it benefits
automatically). Also found and fixed a real, separate gap while testing: **GS was
entirely missing from `CIK_TO_TICKER`/`FISCAL_YEAR_END`** (added both, CIK
0000886982, confirmed real fiscal year-end Dec 31 from the actual filing dates).

**Real, measured result on GS specifically:** quarterly periods went from ~0 real
rows (just empty Q4 placeholders) to 59 real quarterly periods, genuine revenue/
net_income back through 2022-2023, matching GS's real reported figures. Empty Q4
rows dropped from 17 to 4 (2009-2012 specifically -- the concept doesn't extend
that far back for GS, a real, honest remaining limit, not a bug).

**Not yet done -- real next step:** this was tested and confirmed on ONE ticker
(GS) of the 367 affected. Re-running `ingest_sec_financials_multi.py` for the
other affected tickers (many likely also missing from `CIK_TO_TICKER` the same way
GS was) is the real remaining work -- expect this new concept alone won't fix
every ticker (different banks may use yet other concept names), so real, honest
measurement of the before/after gap size per ticker is needed, not an assumption
that this one fix closes the whole 367-ticker pattern.

### 2026-09-30 — financial_market_reactions "unification" was already resolved, before tonight
Final Phase 5 checklist item, checked: `event_market_reactions`/`financial_market_reactions`
"unification" -- turned out to already be fully resolved, and already documented as
such, inside `PROJECT_PLAN.md`'s own addendum ("Correction (verified this session):
Anchor-Date Unification Is Already Resolved"). That addendum's own verification
query (comparing `abnormal_return_20d` across every `financial_result` event in both
tables) found exact agreement except one fully-explained case (AMD Q3 2024, a normal
one-day filing-timing offset). **No new work needed -- the checklist item was closed
before this session started; PROJECT_PLAN.md's summary table (line 138, "still
pending") just contradicted its own addendum below it.** Real lesson: check a
document's own later corrections before assuming its summary table is current, even
within the same file.

### 2026-09-30 — The ~876-event ripple gap fully explained: not a bug, F/GE/AEP specifically
Real Phase 5 checklist item, closed: F, GE, and AEP were specifically flagged as
"unexplained" ripple-data gaps (unlike EA or pre-listing-date events, all three have
full price history from 1994, so those usual explanations didn't apply). **Checked
directly rather than assumed: 100% of the 167 missing events for these three tickers
(50 AEP, 60 F, 57 GE) are bundled/summary events**, confirmed via a direct join
against `event_component_dates`. Not a bug -- `build_ripple_timeline.py` has
deliberately excluded bundled events by default since the 2026-09-24 fix (see that
script's own docstring). F, GE, and AEP simply have unusually rich, multi-year
narrative event histories (already documented elsewhere in this project -- GE's
"richest single history," F's "largest single haul"), so they naturally have more
bundled summary events than typical tickers, which is what made the pattern stand
out as suspicious. **Formally retired as a real mystery -- working as designed.**

### 2026-09-30 — Sector-peer ripple finding productionized: new sector_peer_ripple table
Phase 5 checklist item: the validated sector-peer ripple finding (issue #21, z=17.49
at the original small-scale test, n=1,215 -- see test_sector_peer_ripple.py and
THEORY.md) previously existed only as a one-off validation script result, never
productionized. Real, deliberate scope, per the original recommendation ("scoped
build, large-reaction events only, not a full unscoped rebuild" -- unscoped would
have been ~21M rows, 44x event_ripple_timeline's size): built a new
`sector_peer_ripple` table and `scripts/ripple/populate_sector_peer_ripple.py`,
reusing test_sector_peer_ripple.py's EXACT methodology (prior-trading-day baseline,
SPY benchmark, +/-5 trading days). Scoped to trigger events with |abnormal_return_5d|
>= 0.05 (the same threshold already established by storm_tier's "large" bucket).
2,527 of 2,539 real trigger events covered, 124,638 real (trigger, peer) rows.

**Real bug found and fixed during the first --live run, same class as the
populate_storm_tier.py pagination bug found earlier tonight but a DIFFERENT root
cause:** 21 chunks failed with the same `ON CONFLICT DO UPDATE cannot affect row a
second time` error (10,500 rows). This time `paginated()` already had the `.order()`
fix from the earlier lesson -- the real cause was different: NWS/NWSA (News Corp's
dual-class shares, the SAME well-documented dedup issue that's bitten this project
multiple times before) has one entity_id mapped to TWO securities. The script
iterated over `securities` directly when building each sector's peer list, so this
one company appeared twice in the Communication Services sector's peer set,
producing duplicate (trigger_event_id, peer_entity_id) keys scattered across ~21
different chunks by chance. Fixed by deduping securities by entity_id before
grouping by sector. Confirmed zero duplicate keys remain after the fix, re-ran
safely on top of the 114,194 already-written rows (upsert-safe, no data loss from
the first partial run).

### 2026-09-30 — EA's price-data absence explained (real, external, not a pipeline bug)
EA's complete absence from `market_prices` had been flagged as "genuinely
unexplained" repeatedly across this project (2026-09-22's audit explicitly ruled
out the earlier "Twelve Data limitation" assumption for AVB/EQR, and left EA as the
one real, open exception). **Real cause, confirmed directly by the project owner:**
EA's price data specifically requires a paid tier/add-on on Twelve Data beyond the
current plan -- a genuine data-provider access restriction, not a pipeline bug, not
a ticker-mapping issue, not a coverage gap to keep chasing. **Formally closed as a
known, accepted limitation** rather than an open mystery -- would require upgrading
the Twelve Data plan to resolve, a real cost/business decision, not an engineering
task.

### 2026-09-30 — Multi-entity reaction tagging gap closed (real fix backfilled, not a permanent code fix)
Phase 5 checklist item, real gap found and closed: `event_entity_reactions` (built
2026-09-24 by `tag_multientity_reactions.py`, the correct per-(event,entity) reaction
fix for `tag_reaction_character.py`'s known single-company bug -- see that script's
own docstring) only covered 33 events as of 2026-09-29. Measured 49 events actually
affected by the underlying bug in `event_tags` -- 16 new multi-entity events had
appeared since the original fix, with no corresponding entry.

**Real, important finding: `tag_multientity_reactions.py` is fully general-purpose,
not hardcoded to the original 33** -- it queries `event_entity_relationships` fresh
every run and requires no changes to pick up new multi-entity events. Simply re-ran
it. Verified: 49/49 events now covered, 124 total rows (up from 92), confirmed via
direct query, not the script's own printed summary.

**Real, still-open gap, not fixed today:** the underlying root cause in
`tag_reaction_character.py` (`ticker = e["tickers"][0]`) is UNCHANGED --
`event_entity_reactions` is a parallel, correct table that has to be manually
re-run to catch up, not an automatic fix. Every future multi-entity event will
keep getting the wrong single tag in `event_tags` until `tag_multientity_reactions.py`
is re-run again. **Real recommendation: run `tag_multientity_reactions.py` as a
standard paired step immediately after every `tag_reaction_character.py` run**,
not a thing to remember separately -- or, as a more permanent fix, merge the
per-entity logic directly into `tag_reaction_character.py`'s own main loop so this
gap can't silently reopen again. Neither has been done yet.

### 2026-09-30 — Storm/compounding finding productionized: real event_pre_context columns
Phase 5 checklist item: the validated storm finding (THEORY.md) previously only lived
as an in-memory computation inside multi_feature_model.py's get_storm_lookup(),
recomputed from scratch on every model run. Added real `storm_magnitude` (numeric) and
`storm_tier` (text) columns to `event_pre_context` and built
`scripts/financial_pipeline/populate_storm_tier.py`, reusing the exact same logic.
15,050 real (event, entity) pairs written: isolated 6,647, large 3,838, medium 2,336,
small 2,229.

**Real bug found and fixed during this build, worth remembering:** a `paginated()`
helper with `.range()` but no `.order()` first does NOT guarantee stable row ordering
across separate paginated requests on a large table -- confirmed directly, the first
--live attempt produced scattered duplicate (event_id, entity_id) keys across every
single 500-row chunk (`ON CONFLICT DO UPDATE command cannot affect row a second time`),
despite `event_ripple_timeline` itself having zero true duplicate rows (verified via a
direct GROUP BY / HAVING COUNT(*) > 1 check before assuming the bug was upstream).
Fixed by requiring an explicit `order_by` argument on every paginated call -- not every
table has an `id` column (`event_component_dates` doesn't), so a hardcoded `.order("id")`
isn't safe to assume either. Same bug CLASS as the well-known unpaginated-query-silently-
capped-at-1000-rows issue, just the ordering variant -- worth checking for in any new
pagination helper, not just the row-count version.

### 2026-09-29 — Global Events: manual review track quietly scaled, algorithmic track still stalled
`build_event_episodes.py`'s output table (`global_event_episodes`) confirmed still 0
rows -- exactly as documented 2026-09-22 (four failed iterations, root cause identified,
not implemented). No change there.

**But the simpler, already-proven alternative the old notes recommended "instead of
continuing" the algorithmic effort has real, substantial progress never documented:**
`global_events.severity` now populated for 167 events (up from the "11 confirmed"
figure in the stale notes -- a real ~15x increase), with genuine variance (105 major,
53 moderate, 9 minor -- not degenerate). This looks like the recommended simpler
approach was actually followed at real scale, just never written down. 424 total
`global_events` rows exist, latest dated 2026-09-14.

**Real recommendation:** formally retire `build_event_episodes.py` as the intended
path (or explicitly re-scope it) given the manual-review track already works and has
real traction -- continuing to carry it as "unresolved, in progress" undersells what's
actually been accomplished a different way.

### 2026-09-29 — Phase 4 Track B (news) is active, not "paused" as documented
`PROJECT_PLAN.md`'s architecture section describes `news_articles` as an "early-stage
live feed, paused." **This is stale.** Verified live: 407 total articles, latest
timestamped TODAY (2026-09-29). Real daily cadence confirmed (mostly 28-30
articles/day over the last two weeks, one real gap 2026-08-31 to 2026-09-16) --
driven by an external daily automation outside this codebase, not a manual/occasional
run. Genuinely active, just low-volume relative to the 8-K pipeline. Funnel: 407
articles -> 60 AI-classified -> 22 candidate events -> 6 confirmed into real `events`.

### 2026-09-29 — Auto-confirm threshold is documented wrong; real spot-check at the real threshold
The bulk auto-confirm policy documented earlier in this file (Part 1, step 6) says
"ai_confidence >= 0.9" for both safe-to-bulk-confirm buckets. **This is wrong relative
to the actual code.** `classify_8k_filings_batch_v2.py`'s real `compute_flag()` flags a
row for human review only when confidence < 0.75 (not < 0.9) -- meaning the real
population being bulk auto-confirmed in production reaches all the way down to 0.75
confidence, not 0.90. The documented "~99-100% agreement, measured on thousands of
sampled rows" was very likely only ever measured on the >=0.90 subset -- **the real
0.75-0.90 band (4,060 rows: 4,050 likely_noise + 10 real_event) has never been
validated at all.**

Pulled a real random sample of 25 from the unvalidated 0.75-0.90 likely_noise band and
read each one individually against the AI's own stated reasoning (same standard as
`event-materiality-review.md`). 23/25 correct. **2 real disagreements (8% in this
small sample, vs. the ~1% documented for the >=0.90 band):**
- **APD 2018-05-17** (EVP departure, $2.58M severance, 0.78 confidence) -- dismissed
  as noise purely because the departing exec wasn't literally CEO/CFO/Chairman. Per
  our own rubric (and a real confirmed precedent from tonight's sweep review, a Chief
  Ethics and Compliance Officer departure), the real test is Item 5.02(b) named-
  executive-officer status, not C-suite title specifically. Looks like a genuine miss.
- **PSA 2023-02-21** (0.85 confidence) -- filing text was truncated to boilerplate
  cover-page only; the AI's own item-code description reads internally confused. This
  was a low-information guess dressed up with 0.85 confidence, not a well-supported
  call -- should have been flagged `low_confidence`, not passed through.

**Real implication:** the safe-to-bulk-confirm claim should be scoped to confidence
>=0.90 specifically, not the full 0.75+ range the code actually auto-passes. The
0.75-0.90 band (4,060 rows) needs either a proper validation pass (a larger real
sample, not just 25) or should be routed to individual review going forward.

### 2026-09-29 — Derived financial chain verified, one real fix, one false alarm resolved
Checked the full Phase 2 derived chain fresh (financial_statements -> financial_metrics
-> financial_health_snapshot -> fundamental_signals -> financial_condition_summary),
not just the two endpoints. `financial_health_snapshot` and `fundamental_signals` are
real database VIEWS (not tables -- no Python script writes to them, confirmed by a
real grep coming back empty before checking table_type).

Real finding, initially looked like a bug, wasn't: only 27,528 of 35,819
`financial_metrics` rows (76.9%) flow through to `fundamental_signals` -- a real
8,291-row gap, concentrated at a consistent ~19-21 rows per company across MANY
different tickers (DE, TAP, JCI, GS, YUM, TSN, GPC, CIEN, BBY, ADI, AES, AEP, AFL,
AIG, ADBE), not a handful like the earlier MA/ADBE metrics bug. Pulled the real view
definition (`pg_get_viewdef`) rather than guess: `fundamental_signals` has an
explicit, deliberate `WHERE period_type = 'quarterly'` filter, using `LAG()` window
functions to compare each quarter to the immediately PRECEDING quarter (not prior
year) for trend detection. Annual periods are correctly, intentionally excluded --
mixing an annual total into a quarter-over-quarter LAG sequence would be a nonsensical
comparison. **Not a bug, not a coverage gap -- the ~77% figure is the correct ceiling,
not something to chase toward 100%.** `revenue_momentum` and `gross_margin_trend` both
checked for real variance (not another `size_bucket`) -- both genuinely well-distributed
across 3 real categories each, confirmed working.

### 2026-09-29 — Dead-column scan (Phase 1 checklist item)
`PROJECT_PLAN.md` recommended a dedicated scan for other "always-same-value" dead
tracking columns after finding two by accident (`size_bucket`, `promoted_to_event`) --
never actually done until now. Built `scripts/audit/scan_dead_columns.sql`: a real
PL/pgSQL scan across 44 real pipeline tables (audit/scratch snapshot tables excluded),
flagging any column where non-null values collapse to a single distinct value (n>10).

Real result: 16 flagged. 9 genuinely benign (single data source/currency/model-version
in use so far -- e.g. `securities.currency` always `USD`, expected for an all-US-listed
universe). 2 already known. 1 confirms (doesn't newly reveal) the known
`surprise_vs_consensus` gap. 2 are `stale_url_sweep_results`' own intentional filter
criteria. 1 small-sample/likely-benign (`news_ai_classifications`, n=60, matches Track
B's known early/paused status). **1 new, real, minor finding:**
`financial_statements.statement_type` is stuck at `"income_cash_flow"` for all 36,001
rows -- followed up directly rather than assumed: the real balance-sheet columns
(`total_assets`, `total_liabilities`, `total_equity`, `cash_and_equivalents`) ARE
present in the schema and well-populated (94-97% coverage), so this is a stale/
misleading label, not a coverage gap -- initially worried this meant balance-sheet
data was never ingested at all; direct query ruled that out.

### 2026-09-29 — Phase 2 spot-check: financial_metrics coverage gap
Checked Phase 2 (financial analysis) fresh rather than trust `PROJECT_PLAN.md`'s stale
100%-complete claim from the ~13-company era. Found 498/499 securities have
`financial_statements` coverage (genuinely near-complete), but 1,339 of 36,001 statement
rows had no corresponding `financial_metrics` row, concentrated in specific tickers rather
than scattered — AVB, VMRK, EA (all three already flagged elsewhere tonight for other
onboarding issues) plus, unexpectedly, MA and ADBE (0/93 and 0/82 respectively, despite
complete statement history, no known prior issues). Re-ran `populate_financial_metrics.py`
live — see Known Gotchas for the real before/after numbers and the script's own
unreliable summary line, caught by verifying directly rather than trusting its printout.
Also corrected a separate stale claim (`free_cash_flow` backfill, see Known Gotchas).

### 2026-09-28/29 — Stale-URL Sweep, Price Refresh, Tagger Fix
- Root-caused and measured the stale-`primary_document_url` issue (~1% of old-noise
  verdicts hide a real event in exhibit text not visible from the cover page alone). Built
  `sweep_stale_url_noise.py`, `draft_missing_event_text.py`, `writeback_confirmed_sweep_flips.py`.
- Swept and reviewed 5,000 filings across 3 chunks; 45 flips confirmed real, 7 rejected as
  routine; ~4,000 events promoted total (including a separate backlog of already-confirmed-
  but-textless rows found via `promote_events.py`'s own skip list). 35 routine events
  removed after sampling found ~a third of `governance_action`-type promotions were routine
  poison-pill/majority-voting housekeeping, not real news.
- Fixed a real OOM bug in `fetch_filing_text()` (see Current Reference) — sweep runs were
  being killed by the Codespace's memory limit, not crashing on their own.
- Discovered `market_prices` had no incremental updater at all and had drifted stale by
  several weeks with zero alerting. Built `refresh_market_prices.py` with an overlap-check
  against dividend/split restatement. SPY itself needed a full refetch.
- Fixed `tag_reaction_character.py`'s short-window bug (see Current Reference) and ran it
  to completion: 15,928 events tagged total.
- Wrote `event-materiality-review.md` (linked from `working-practices.md`) — the actual
  confirm/reject test for filing review, developed from ~150 individually-read filings
  across two sessions, with explicit documented exceptions rather than a rigid checklist.

---

# STILL OPEN / UNVERIFIED

- `tag_reaction_character.py`'s multi-entity bug — 49 events currently affected, real fix
  (use `event_entity_relationships.relationship_type` to disambiguate) not yet built.
- `build_event_episodes.py` — unresolved, status not re-checked since 2026-09-22.
- ~~EA's price-data gap~~ -- RESOLVED 2026-09-30: Twelve Data paid-tier restriction, not a pipeline bug.
- `financial_market_reactions` (unused modeling target) — status not re-checked since
  2026-09-22; worth confirming it's still true that nothing uses it.
- CNC 2021-06-25 (Centene/Magellan financing) — a human-confirmed real_event with no
  title/description; the model resists drafting text for it even with a focus hint (3
  failed attempts). Needs either a different prompting approach or a hand-written entry.
- ~876 pre-existing events with no ripple-timeline data that aren't explained by known
  causes (bundled-event exclusion, or a company's price history starting after the event) —
  ~~F, GE, AEP specifically flagged as unexplained~~ -- RESOLVED 2026-09-30: 100% bundled/summary events, working as designed, not a bug.
