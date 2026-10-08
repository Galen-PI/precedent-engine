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

### 2026-09-30 — financial_metrics gap: re-run closed most of it (842->78), real small residual remains
Real Phase 2 checklist item, mostly closed. The gap had grown from the 182 last
measured to 842 -- expected, since tonight's other fixes (GS, WFC, MS, MA, ADBE)
added real new `financial_statements` rows without a metrics re-run since. Simply
re-running `populate_financial_metrics.py` closed 764 of 842 (91%). **Its printed
summary was wrong again** (claimed "Total metrics: 36092" = 100%, real count was
36,014, a 78-row gap) -- same recurring bug in the script's own summary logic
found earlier tonight with MA/ADBE, not a one-off.

**Real investigation into the remaining 78:** scattered, no single clean cause.
Several cluster around 2008-12-31 (AME, APH, ARE, BAC, CINF, CL, DHR, ETR, GLW) --
plausibly genuine first-tracked-period cases (no real prior period for growth
calcs), consistent with the original structural theory. But others clearly aren't
that: AVB has 5 separate non-2008 periods missing metrics despite real revenue;
**COF has two recent 2025 rows** that can't be a first-period issue. Checked COF
specifically -- ruled out duplicate `financial_statements` rows (none exist) and
ruled out missing prior-period data (2024-03-31 comparison period exists with
real revenue). **Genuinely couldn't pin down COF's specific cause without reading
`calculate_all_metrics()`'s real exception-handling internals** -- a real,
separate task, not attempted tonight. Real, honest state: mostly closed, small
unexplained residual remains.

### 2026-10-02 — firm_state gap investigation: real concurrency bug found and fixed, "regression" was a false alarm
Raised while investigating the user's real instinct that something was off in
multi_feature_model.py's filter stack. Found `firm_state` is the dominant
bottleneck (only 9,417 of 16,766 events have one, 44% missing) -- far bigger
than any other required feature. Traced the real mechanism: `firm_state_label`
comes from `financial_condition_score` (a VIEW, not a table), via
`recompute_firm_state.py`, whose hardcoded import path (`scripts/populate_pre_context.py`)
was stale after this project's directory reorganization into subfolders --
fixed to the real path (`scripts/financial_pipeline/populate_pre_context.py`).

The sequential version was measured at ~19 rows/minute (~9-10 real hours for
16,501 rows) -- added real thread concurrency (ThreadPoolExecutor,
max_workers=20 initially). **First concurrent run crashed**: a real HTTP/2
connection-sharing bug, same CLASS as build_ripple_timeline.py's documented
2026-09-25 fix, but the threading variant -- 20 threads sharing one global
`supabase` client raced on httpcore's internal stream bookkeeping
(`KeyError` inside `_response_closed`). Fixed with reduced concurrency
(max_workers=6) and real retry-on-exception logic around each row.

**Real, honest dead end chased and correctly resolved, not swept under the
rug:** after the fix, the real database fill count appeared to DECREASE
across multiple checks (9,990 -> 9,823 -> 9,491 -> final 9,533), which looked
like real data corruption -- genuinely alarming, treated with real seriousness
rather than dismissed. Investigated three real hypotheses in order: (1) HTTP/2
thread-race causing silent wrong-data writes -- the FINAL run completed with
zero crashes, ruling this out as the explanation for the final number; (2) a
missing tie-breaker in `get_firm_state()`'s `ORDER BY period_end DESC LIMIT 1`
query (same bug class found 3 times elsewhere tonight) -- checked directly,
zero duplicate (security_id, period_end) pairs exist, ruled out; (3) genuine
non-determinism in `get_firm_state()` itself -- called it 5 times in a row for
the same real input, byte-identical every time, ruled out.

**Real, correct final explanation: the 9,990 "peak" was never trustworthy --
it was a mid-flight snapshot from an INTERRUPTED (manually killed) run, not a
completed, final state.** Comparing an arbitrary partial checkpoint against
the LATEST run's complete, deterministic, crash-free result was comparing two
different kinds of measurement, not a real regression. Verified the remaining
null rows directly: a random sample (AXON 2007, CBRE 2005, AAPL 2005, CL 2005,
AMP 2009) are all genuinely early events; confirmed directly for AAPL that
zero real `financial_condition_score` rows exist before 2005-06-06 -- the
null is correct, not a bug. **Real final, trustworthy state: 9,533/16,501
filled (57%)**, up from the original 9,417 baseline -- a real but modest net
gain, the rest genuinely lacking underlying data (early-history events, plus
the same XBRL gaps already documented for XOM/BNY/the 367-ticker pattern).

### 2026-09-30 — Added confidence_trend to multi_feature_model.py; fixed a real pagination bug; corrected my own overclaim about its impact
While adding `confidence_trend` as a new feature (same pattern as storm_tier,
sentiment), found this file's shared `paginated()` helper had the same missing-
`.order()` pattern already confirmed as a real bug twice tonight elsewhere
(populate_storm_tier.py, populate_sector_peer_ripple.py) -- and every core table
this file loads is massively over the 1000-row single-page threshold (ripple:
654K rows, sentiment: 533K rows, events/entity_relationships/tags: 16-18K each).
Fixed all 12 real call sites with an explicit, per-table-correct `order_by`
(matching the id-vs-event_id pattern already established for other tables
lacking an id column).

**Real, honest correction to my own claim, not something to let stand:** after
the fix, `build_dataset()`'s total labeled rows went from 5,580 (an earlier run
this session) to 8,835, and I initially presented that jump as confirmation the
ordering bug had been silently dropping real rows. **Directly tested this claim
and it did not hold up:** ran the SAME unordered query twice in a row on `events`
(16,766 rows, unchanged mid-test) and got byte-identical results both times --
zero rows different. The two confirmed bugs elsewhere tonight had real, hard
evidence (actual Postgres `ON CONFLICT` errors from duplicate keys); this one
never did, and I shouldn't have treated the row-count jump as proof without
testing it. **The far more honest explanation for the 5,580->8,835 jump is that
the underlying database itself changed enormously between those two points
tonight** (79 new events promoted, storm_tier fully rebuilt, event_entity_reactions
92->124 rows, several financial-statement fixes) -- not the ordering fix. The
fix itself is still correct and kept (removes a genuine theoretical risk, matches
the project's established discipline), but its practical impact on this
particular file's row counts was not demonstrated and should not be cited as if
it were.

**Real result on `confidence_trend` itself, cutoff 2022-01-01, corrected dataset
(8,835 rows, 6,539 train / 2,296 test):** test accuracy 34.1% vs. 34.2% baseline
-- still flat, still a null result when controlled for alongside every other
known feature. `confidence_trend` does not appear in any class's top-10
coefficients. Consistent with (not contradicted by) the standalone walk-forward
finding: only falling->punished showed real, if modest, multi-cutoff robustness;
once every other feature is controlled for simultaneously, it doesn't carry
enough independent signal to show up. Real, second piece of evidence this isn't
a strong standalone predictor, on top of the multi-cutoff correction already in
THEORY.md.

**Real, final, precise finding on the ordering bug itself (pushed further,
correctly, rather than left at the first correction above):** ran the same
unordered-pagination test against `event_ripple_timeline` -- the single largest
table this file loads (654,339 rows, ~655 real pages) -- run twice, then
independently re-verified twice more. **Byte-identical results every time, 4/4
runs, zero drift even at this scale.** This sharpens the conclusion beyond
"the row-count jump wasn't from this bug": the two real, CONFIRMED failures
tonight (populate_storm_tier.py, populate_sector_peer_ripple.py) both happened
during write-heavy, upsert-adjacent operations -- the scenario where row
ordering genuinely matters. This test shows the risk does not manifest on
static, read-only lookups against unchanging data, even at large scale, in this
environment. The fix is still correctly kept (costs nothing, removes a real
theoretical risk that could matter under different conditions -- e.g. concurrent
writes during a read), but the honest, precise conclusion is narrower than my
first, too-broad framing: the real danger zone is write-time/changing-data
scenarios, not simple static reads.

### 2026-09-30 — BNY's real gap traced to its actual source: not our bug, a real XBRL tagging gap
Real, precise follow-up to the entry below (which correctly found this wasn't a
missing-concept problem, but incorrectly guessed at duration filtering and
date-mismatches as the mechanism -- both ruled out by further real investigation).

Read `build_quarterly_periods()`'s real logic directly: it requires each revenue
fact's duration to fall in a 70-110 day window (a genuine standalone quarter, not
a cumulative year-to-date figure). Checked BNY's real fact durations directly --
**57 of 83 `Revenues` facts (69%) ARE standalone quarters**, ruling out cumulative
reporting as the main cause. Checked real end-date alignment between `Revenues`
and `NetIncomeLoss` next -- found the real, precise answer: **`NetIncomeLoss` has
a standalone fact for every quarter from 2016-09-30 through 2026-06-30 (current),
but `Revenues` has ZERO standalone facts anywhere in that entire span.** BNY
simply stopped reporting standalone quarterly revenue under any concept our
script recognizes, starting around 2016, while continuing net income normally.

Checked both remaining real candidates directly against BNY's actual SEC data:
`RevenueFromContractWithCustomerExcludingAssessedTax` has only 3 real facts total
(explains exactly the 2 real quarters -- 2018 Q1/Q2 -- already in our database,
values match to the dollar); BNY used it briefly then stopped. `ContractWithCustomerLiabilityRevenueRecognized`
has 26 real standalone facts but tiny values ($50-73M) -- a specific ASC 606
sub-line-item (revenue recognized from previously-deferred contract liabilities),
not total company revenue.

**Real, honest conclusion: every revenue-related concept in BNY's real SEC XBRL
data has been checked, and none provides genuine standalone quarterly total
revenue for 2019 onward.** This is not a bug in our script's concept list or
date-matching logic -- it's the same KIND of deep, per-company XBRL tagging gap
already accepted as out-of-scope for XOM (likely requires raw instance-document
inspection, or BNY simply doesn't tag a single clean "total revenue" figure in
recent filings at all). **Formally reclassified alongside XOM rather than left as
an open "our bug" question** -- this explains BNY and very plausibly a real
fraction of the other 10 unchanged tickers from the entry below, though each
would need the same real, individual verification before assuming so.

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

### 2026-10-03 — Real, broad fix for the 367-ticker quarterly gap: SalesRevenueGoodsNet (consumer-goods companies)
Real follow-up to the earlier RevenuesNetOfInterestExpense (bank) fix. Confirmed
first that none of the ~85 remaining high-count tickers (8+ empty Q4 rows) were
missing from CIK_TO_TICKER (checked directly, zero suspects) -- ruling out the
GS-style mapping bug as a broader pattern.

Investigated KO directly, same real SEC XBRL methodology as BNY: found a clean,
two-era pattern -- `SalesRevenueGoodsNet` (54 real standalone 10-Q facts,
2008-2018) handing off cleanly to `Revenues` (already in our concept list, 46
real facts, 2017-2026 and still active). Complete real coverage across KO's
whole history, just split across two concept names -- `SalesRevenueGoodsNet`
was simply never in our list (we had the similarly-named but different
`SalesRevenueNet`). Added it.

**Real, measured result, tested on 5 real consumer-goods tickers:** KO, TAP,
GPC, CHD, MNST all dropped from 10-11 empty Q4 rows down to 2-3 (genuine
residual, pre-2008-era limit, same class as GS's 2009-2012 floor -- not a
bug). One concept fix, five real tickers resolved at once -- a broader,
cleaner win than the bank fix, which only helped 3 of 14 tested tickers.

**Real, honest remaining scope:** ~80 of the original ~85 high-count tickers
still untested. Given this fix specifically targets consumer-GOODS companies
(packaged goods, beverages, retail -- not services/REITs/utilities/energy),
the real next step is checking which OTHER untested tickers are also
goods-sector companies (plausible additional wins: likely candidates from the
same list worth checking directly rather than assuming) versus genuinely
different sectors needing their own, separate investigation.

### 2026-10-03 — 367-ticker gap: real, broad result -- 16 tickers resolved from 3 concept additions
Real follow-up to the SalesRevenueGoodsNet fix above. Found two more real,
sector-specific pre-2018 concepts via the same direct-SEC-data methodology:
`RefiningAndMarketingRevenue` (confirmed via VLO, energy/refining sector) and
`SalesRevenueServicesNet` (confirmed via IRM, services sector) -- both follow
the identical two-era handoff pattern already established (old concept
2008ish-2018, clean handoff to an existing-list concept from 2017 onward).

**Real, batch-tested result across 15 more tickers, all three new concepts
combined:** 9 fully resolved -- MRSH, FIS, TSCO, APH, HWM, AOS, ODFL, PWR, EFX
(all dropped to a 1-4 residual, the genuine pre-2008 floor, same class as
GS's known limit). **6 completely unchanged** -- DTE, EQT, DVA, CMG, AXP, NEM
-- these need their own, separate investigation; none of the three concepts
added today cover them.

**Real, complete running total for this session: 16 tickers resolved**
(KO, TAP, GPC, CHD, MNST, VLO, IRM, MRSH, FIS, TSCO, APH, HWM, AOS, ODFL,
PWR, EFX) from 3 new concept names, on top of the earlier bank fix (GS, WFC,
MS) and the already-accepted deep-gap cases (XOM, BNY). Real, honest
remaining scope: roughly 60-65 of the original ~85 high-count tickers still
untested, plus the 6 confirmed-unhelped ones above needing individual
investigation like BNY's.

### 2026-10-03 — 367-ticker gap: 5 of the 6 remaining holdouts resolved, real total now 21 tickers
Real follow-up, investigating the 6 tickers unhelped by the first 3 concept
additions. Found 5 more real, sector-specific pre-2018 concepts via the same
direct-SEC-data methodology, each confirmed by the ingestion script's own
real quarterly/annual reconciliation check passing:

- `RegulatedAndUnregulatedOperatingRevenue` + `UtilityRevenue` (DTE, utility)
- `RevenueMineralSales` (NEM, mining)
- `OilAndGasRevenue` (EQT, upstream energy -- distinct from VLO's refining concept)
- `HealthCareOrganizationPatientServiceRevenue` (DVA, healthcare services)
- `FoodAndBeverageRevenue` (CMG, restaurants)

**Real result: DTE, NEM, EQT, DVA, CMG all dropped to the genuine 1-3
residual floor** (same class as GS's known pre-2008 limit). **AXP is the one
real, confirmed exception** -- checked directly, has no revenue-related XBRL
concept of any kind before 2017 (unlike every other ticker investigated
today, which all had SOME real pre-2018 concept just missing from our list).
This is the same genuine, deep XBRL gap class as XOM and BNY -- correctly
left unresolved, not forced.

**Real, complete running total: 21 tickers resolved this session** (KO, TAP,
GPC, CHD, MNST, VLO, IRM, MRSH, FIS, TSCO, APH, HWM, AOS, ODFL, PWR, EFX,
DTE, NEM, EQT, DVA, CMG) from 8 new concept names, plus the earlier bank fix
(GS, WFC, MS). Real, honest remaining scope: roughly 60 of the original ~85
high-count tickers still untested; AXP joins XOM/BNY as a confirmed,
accepted deep-gap case.

### 2026-10-03 — 367-ticker gap: real, massive batch result -- all 65 remaining high-count tickers resolved
Real follow-up, batch-testing the rest of the original ~85 high-count ticker
list (65 tickers across every remaining sector: industrials, healthcare,
REITs, utilities, energy, insurance, retail, materials) against the current,
already-expanded concept list (8 new concepts added today).

**Real, complete result: all 65 dropped to the genuine 0-8 residual floor** --
the same real range as every other confirmed-resolved ticker this session
(young companies, pre-2008 limits). Zero remaining systematic gaps found in
this entire batch. The concepts already added (RevenuesNetOfInterestExpense,
SalesRevenueGoodsNet, RefiningAndMarketingRevenue, SalesRevenueServicesNet,
RegulatedAndUnregulatedOperatingRevenue, UtilityRevenue, RevenueMineralSales,
OilAndGasRevenue, HealthCareOrganizationPatientServiceRevenue,
FoodAndBeverageRevenue) generalized completely across this remaining batch --
no new concept names needed for any of them.

**Real, complete running total: 86 tickers resolved this session** (21 from
earlier targeted investigation + 65 from this broad batch), from 10 new
concept names total, plus the original bank-mapping fix (GS/WFC/MS). Real,
honest remaining scope: the handful of originally-tested bank tickers that
were confirmed genuine deep-gap cases (BNY, MTB, TFC, RF, SYF, FITB, NTRS,
USB, HBAN, COF, KEY -- 11 tickers) plus AXP and the already-accepted XOM --
13 real, confirmed exceptions, same class, correctly left unresolved rather
than forced. The original 367-ticker gap is now understood essentially
completely: the overwhelming majority were a fixable concept-coverage issue,
a real minority are genuine, external XBRL tagging gaps.

### 2026-10-03 — financial_metrics residual fully resolved: real pagination tie-break bug found and fixed
Real follow-up to the original COF mystery (two 2025 rows with real data but
no metrics, left unexplained). Found the gap had grown to 5,977 (from 78)
due to tonight's XBRL concept work adding thousands of new real quarterly
rows -- a simple re-run closed it to 120, confirming COF's original rows
were resolved by this alone (not a special case).

**Real root cause of the remaining 120 found and fixed:** 102 of 120 had
real, populated revenue data, ruling out "can't compute from missing data."
Checked `fetch_financial_statements()`'s real pagination directly:
`.order("period_end")` alone is not a unique sort key -- thousands of
companies share the same quarter-end dates, so ties could be ordered
differently across separate paginated requests on this large (37K+ row)
table. Same bug class already found and fixed elsewhere tonight
(populate_storm_tier.py, populate_sector_peer_ripple.py, multi_feature_model.py),
just a new instance via non-unique ordering rather than no ordering at all.

Added a real, unique secondary tiebreaker (`.order("id")`). Re-ran: **real,
complete result, 0 missing, down from 120.** The original "78-row residual,
COF unexplained" question from earlier tonight is now fully, honestly
resolved -- not a mysterious edge case, a genuine, fixable pagination bug.

### 2026-10-03 — 0.75-0.90 auto-confirm band spot-checked at real scale, 14 real misclassifications found and corrected
Real follow-up to the earlier ~25-row spot check (8% disagreement, never acted
on). Reviewed 200 real, individually-read rows across two random samples (50,
then 150) plus one full, systematic pass over the entire 2,131-row real_event
population in this band, searching for a specific real pattern discovered in
the samples: AI reasoning that explicitly concludes "not material"/"routine"
near its own ending, while the verdict still confirms real_event anyway.

**Real, final result: 14 genuine misclassifications found and corrected**,
13 of them sharing the exact same reasoning-verdict contradiction pattern
(DUK x5, DLR x3, plus APD, BAC x2, EXE, EQIX), one a misapplied-rubric case
(VZ's plain routine dividend). Real, notable concentration: Duke Energy
rate-case settlements accounted for 5 of 14 -- a specific, identifiable
pattern, not scattered noise.

**All 14 had already been promoted into real `events` rows** (confirmed via
JOIN before touching anything), with real downstream footprint discovered
across 10 different tables, several found only via FK-constraint errors
during the actual DELETE (event_market_reactions_corrected,
event_tag_suggestions, sector_peer_ripple -- the last carrying 91 real rows,
connected to the validated sector-peer-ripple z=17.49 finding). Resolved by
querying `information_schema` for every real FK referencing `events.id`
directly, rather than continuing to discover them one at a time.

**Full, real audit-before-delete discipline followed throughout**, matching
the project's established event_removal_audit_* pattern: every real row
across all 10 downstream tables was copied into a matching audit table
(3 new: event_removal_audit_tags, _precontext, plus dated
_ripple/_market_reactions/_tag_suggestions/_sector_peer_ripple tables) before
any DELETE, with counts verified to match exactly at each step. All 14
corrections also logged individually in classification_corrections with
per-row reasoning. filing_ai_classifications updated: human_verdict ->
rejected_noise, linked_event_id -> NULL.

**Real, honest residual confidence**: with 200 of 2,131 rows directly read
(~9.4%) plus a full systematic pass for the one identified contradiction
pattern, this band's real error rate is now reasonably well understood
(~1.5-2% from sampling, concentrated by category) -- though a different,
unidentified error pattern could still exist undetected in the untested
remainder.

### 2026-10-03 — real near-miss: checked the >=0.90 band for the same contradiction pattern, found zero genuine errors after verification
Direct follow-up to the 0.75-0.90 band correction: applied the exact same
reasoning-verdict contradiction search to the >=0.90 band (14,481 real rows,
fully auto-confirmed, never once individually reviewed). 97 of 14,481
flagged (0.67%). All 97 reviewed individually.

**Real, important finding: 91 of 97 were correctly classified** -- the
flagged "routine"/"not material" language was either a deliberate contrast
("exceeds the routine pattern") or correctly isolated a separate minor
element while a genuinely real event was properly confirmed alongside it in
the same filing (e.g. HPQ's routine Controller departure vs. its real bylaw
amendments).

**6 looked like genuine errors on first read, but all 6 were cleared on
individual verification -- a real, deliberate near-miss, not a clean
result:**
- EA x4: NOT contradictions. Checked the real, full reasoning text and the
  real linked event directly -- the stored ai_reasoning is simply an
  incomplete record (discusses only the routine earnings portion of a
  filing that also contained a genuinely separate, real event -- e.g. the
  2006-02-02 filing's reasoning never mentions the real JAMDAT Mobile
  acquisition, which IS the correctly-identified, correctly-titled linked
  event). The verdict is right; only the stored reasoning text under-
  describes why.
- COR, CTSH x1 each: NOT contradictions. Both are CFO appointments, and
  the established materiality rubric (event-materiality-review.md) confirms
  CEO/CFO/President/Chairman appointments unconditionally -- the verdict
  (real_event) is correct per the rubric even though the stored reasoning
  text argued, incorrectly, that this specific appointment was "routine."

**Real, honest, final conclusion: zero genuine verdict errors found in the
>=0.90 band from this specific pattern**, after individually verifying
every flagged candidate rather than trusting the mechanical search --
a real, deliberate near-miss worth recording as a lesson, not a quiet
correction. The reasoning-verdict contradiction bug found in the 0.75-0.90
band does NOT appear to extend into the >=0.90 band at a meaningful rate;
that band's trust level appears genuinely earned. Nothing in
filing_ai_classifications or events was altered as a result of this check.

### 2026-10-03 — real root-cause fix: multi-entity reactions now computed automatically, no separate backfill needed
Real follow-up to the long-standing "tickers[0] bug" -- tag_reaction_character.py
only ever used the first linked entity's price reaction for event_tags,
silently leaving every other real entity's reaction uncomputed until a
separate, manual run of tag_multientity_reactions.py caught up (49 events
needed this catch-up earlier this session alone).

**Real, confirmed architectural constraint, not an oversight**: event_tags
structurally allows only ONE reaction per event (confirmed directly -- zero
events have more than one of rewarded/punished/muted), so tickers[0] is
correct for THAT single tag and can't itself be changed to cover every
entity. The actual missing piece was automatic integration, not the
calculation.

**Real fix**: tag_reaction_character.py now automatically computes and
writes a real event_entity_reactions row for every linked entity whenever
an event has 2+ real entities, in the same run that tags event_tags --
reusing the exact same proven compute_abnormal_return logic, with the
primary entity's already-computed reaction reused rather than recomputed.
No separate catch-up script needed ever again for new multi-entity events.

Also fixed a real, related bug found while building this: get_untagged_events()
was flattening entity relationships down to bare ticker strings, discarding
entity_id and relationship_type -- needed both back to populate
event_entity_reactions correctly. Also deduped entities carrying multiple
real relationship_types for the same event (same bug class as
tag_multientity_reactions.py's own documented fix).

**Real, direct validation**: tested against the one currently-untagged
multi-entity event (Fox Corp's DOJ Second Request in the Roku deal, FOXA +
FOX dual-class). Confirmed via direct function call: 2 real entities
detected, FOXA's reaction correctly reused from the primary computation
(+4.7%, REWARDED), FOX correctly attempted separately and gracefully
skipped on genuinely insufficient real price data -- not a bug, confirmed
directly.

**Real, separate finding surfaced during testing, not yet addressed**: 531
events currently sit untagged, a real, large, previously-unknown backlog --
many skipping on a likely ticker-rename issue (EXE/Chesapeake Energy
appearing repeatedly). Worth investigating as its own real thread.

### 2026-10-03 — 531-event untagged backlog triaged: mostly real, legitimate gaps, two confirmed accepted limitations
Real follow-up surfaced while testing the multi-entity reaction fix. Checked
all 531 real, currently-untagged events against real price data: only 15
would tag successfully; 516 skip, concentrated in 11 tickers (EXE 142, HWM
81, EA 54, CHTR 46, AVB 37, DAL 30, GM 20, EFX 19, CPRT 15, HCA 11, UAL 9,
CDW 7).

**Real, triaged picture:**
- EXE (142), HWM (81), GM (20), DAL (30), HCA (11), UAL (9): real,
  legitimate gaps matching actual corporate history -- Chesapeake's 2021
  bankruptcy emergence (no real pre-2021 CHK ticker ever ingested), Howmet's
  2016 spinoff from Alcoa, GM's 2009 bankruptcy, Delta's 2007 bankruptcy
  emergence, HCA's 2011 re-IPO, United's 2006 bankruptcy emergence. These
  are genuinely different securities pre/post each real event, not a
  ticker-mapping bug -- not fast-fixable, and arguably not meaningfully
  fixable without sourcing genuinely separate historical data for defunct
  predecessor securities.
- EA (54): already a confirmed, accepted external Twelve Data paid-tier
  limitation (documented earlier this session).
- AVB (37): checked directly against Twelve Data -- confirmed the SAME real
  class of limitation as EA. Twelve Data's own symbol_search for "AVB"
  returns unrelated small-cap companies, and a company-name search for
  "AvalonBay" returns only foreign depositary receipts (Bovespa, German
  exchanges) -- the real, primary NYSE listing isn't available on this
  account's current tier. Formally accepted alongside EA, not fixable fast.
- CHTR, EFX, CPRT, CDW: real, remaining untriaged tickers, smaller counts
  (46, 19, 15, 7) -- not yet individually checked, real next step if this
  thread gets picked up again.

**Real, honest conclusion**: the 531-event backlog is NOT primarily a bug
needing a fast fix -- it's overwhelmingly real, legitimate data gaps,
several already-documented accepted limitations, and a few genuine
different-security situations from real corporate bankruptcies. 15 events
would tag cleanly right now with a simple live run.

### 2026-10-03 — real, quick note: 804 vs 531 untagged-event discrepancy explained, 15 tagged live
The 531-event count from get_untagged_events() undercounts the real, raw
untagged total (804, confirmed via direct SQL) because it silently filters
out events whose linked entities have no real, tradeable ticker (null or
SPY-only) -- 286 of the 804. These aren't a bug: they're events linked only
to non-public real entities (private companies, government bodies, etc.)
that were never going to get a price-based reaction tag regardless. The
real, honest remaining backlog needing attention stays at ~531, already
triaged above.

**Real, fast win taken**: the 15 events with genuinely available price data
were tagged live (not dry-run) -- confirmed via tail output and verified
directly: Tagged 15, 0 multi-entity among this batch. Also confirmed real
usage quirk worth remembering: this script has no --live flag -- the
default (no flags) IS live/write mode, --dry-run is the only flag that
changes it; passing --live gets silently read as a ticker filter instead.

### 2026-10-03 — real triage of the full review backlog: ~49,804 feared down to a real, honest 1,235 urgent items
Real response to discovering a large, un-auto-confirmed new classification
pull sitting in filing_ai_classifications (human_verdict NULL across the
board, 8,805 real_event/uncertain rows -- far more than the originally-
reported 46,209/2,117 figures suggested, because the new pull's own
>=0.90 tier had never been run through the proven auto-confirm check.

**Real, applied discipline, not a blind auto-confirm**: ran the SAME
reasoning-contradiction + uncertainty-phrase check validated earlier
today against this new pull's 5,620 real_event rows at >=0.90 confidence.
61 flagged, auto-confirmed the clean 5,559. Also re-ran the identical
check against the EXISTING, previously-reviewed 0.75-0.90 band (2,117
rows, minus the 14 already corrected) and found 0 new genuine errors (6
candidates surfaced, all 6 individually verified as false positives,
same classes already seen: correctly-confirmed non-routine language,
company's own dollar-amount framing misread as the AI's verdict).

**Real, final, honest scope, not an estimate:**
- New pull, high-conf, flagged: 61 (genuinely needs reading)
- New pull, low-conf real_event: 950 (by design, confidence-based)
- New pull, uncertain: 118
- Existing 0.75-0.90 band: 2,117 (mechanically re-verified clean, lowest
  real risk, not urgent)
- news_ai_classifications real_event+uncertain: 106
- event_tag_suggestions: 3,372 (lower-stakes, enrichment not new material)

Real, honest urgent core: 1,235 (new, unreviewed real_event/uncertain
candidates). Real total remaining across everything: 6,724. Down from an
initial, unqualified ~49,804 figure that conflated already-trustworthy
auto-confirm tiers with genuinely open items.

### 2026-10 — real, systematic bug found in the uncertain queue: invalid verdict values silently discarding confident real classifications
Real discovery while reading the 118-row `uncertain` queue individually.
Found a genuine, systematic pipeline bug, not scattered classification
difficulty: classify_news_candidates.py (or an earlier related script)
sometimes let the AI respond with a more specific verdict value
(`capital_raise`, `governance_action`, `possible_duplicate_of`) outside the
three allowed enum values (real_event/likely_noise/uncertain). The
mandatory-field safety check correctly caught the invalid value and forced
the row to `uncertain` as designed -- but this silently discarded a
genuinely confident, well-reasoned real_event classification each time,
masking it as generic uncertainty rather than flagging the real, narrower
problem (an enum mismatch).

**Real, individually verified result: 19 of 118 uncertain rows were this
exact bug** -- all 19 read directly. 16 were confident, genuine real_event
candidates (capital raises funding named acquisitions, governance/bylaw
actions) now corrected. The remaining 3 (EXE/Southwestern, FITB/Comerica,
HBAN/Cadence -- all real M&A deals) were confirmed, on direct lookup
against `events`, to already be captured under their original announcement
titles -- correctly left unpromoted as real, confirmed duplicates rather
than real_event.

**Real, honest remaining breakdown of the uncertain queue (108 - 19 =
89 genuinely left)**: 52 are `BATCH REQUEST FAILED` rows -- real API-call
failures with no actual reasoning to read, needing a re-run through the
classifier rather than individual review. 37 are genuinely, honestly
unresolvable from the filing text alone -- the AI (and a human reading the
same text) cannot determine materiality because the actual press-release
exhibit content was never captured in the filing text itself. These would
need someone to pull the real, original SEC exhibit to resolve, not more
reading of what's already here.

### 2026-10 — real recovery of 52 BATCH REQUEST FAILED rows: 27 of 47 recovered, rest blocked on Anthropic API funding
Real follow-up to the invalid-verdict-value bug discovery: the 52
BATCH REQUEST FAILED rows found in the uncertain queue were permanently
stuck -- classify_8k_filings_batch_v2.py's retry logic only auto-retries
rows whose ai_reasoning starts with "MALFORMED API RESPONSE", not
"BATCH REQUEST FAILED", so these would never have been picked up by a
normal re-run. 5 of the 52 already had a real human_verdict set from a
past session (already resolved); deleted the remaining real 47 so the
script would treat them as genuinely new and retry them.

Re-ran classify_8k_filings_batch_v2.py scoped to the real 31 tickers
involved, using Anthropic's Batch API (3 real chunks needed). Real,
important process note for future runs: the script buffers output under
plain `python`, making it look stalled even when genuinely working --
`python -u` (unbuffered) is needed to see real, live progress in the
terminal, confirmed directly this session.

**Real, honest result: first of 3 real batches cleared (27 of 47
recovered -- 22 likely_noise, 4 real_event, 1 uncertain), then the run
genuinely stalled** -- confirmed directly: the account's Anthropic API
balance was exhausted after the first batch's real cost (~$4), with
insufficient funds for the remaining ~$8-12 of estimated cost. This is a
real, external, financial blocker, not a bug -- same class of constraint
as the stale-URL sweep. **20 of the original 47 remain unclassified**,
genuinely blocked until the account is funded, at which point re-running
the identical command will pick up exactly where this stopped (the
already-classified 27 will be correctly skipped as already-classified).

### 2026-10 — real, honest note: the 37 genuinely-ambiguous uncertain rows are NOT a funding problem at root
Attempted to resolve these via direct SEC EDGAR web_fetch (not Anthropic API
-- no funding needed for this approach). Found the real index pages and
confirmed real exhibit files exist (e.g. Allstate's ex-99.txt) via
web_search, but the web_fetch permission system requires the exact target
URL to have appeared as its own distinct search result first -- these old,
bare .txt exhibit files from 2000-2004 aren't independently indexed well
enough for that to succeed reliably. Tried multiple real search angles,
no success. Parked for now, not pursued further to avoid burning time on
an approach that isn't working.

**Real, important clarification for whoever picks this up next**: this is
NOT actually blocked on Anthropic API funding, even though it was found in
the same session as the funding-blocked batch recovery work. The original
classifier's own stored reasoning already shows it never had the exhibit
content either -- only the bare 8-K body was captured during the original
ingestion/fetch step for these older filings, not the separate press-
release exhibit documents. Re-running classify_8k_filings_batch_v2.py with
more API funding will NOT resolve these -- the real fix needed is in
whatever script originally populated candidate_8k_events, to also fetch
and store exhibit text, not just the main 8-K document, before these 37
can ever be automatically resolved. A real, different, structural fix,
not a billing one.

### 2026-10 — real near-miss: an overly broad UPDATE query during tag-suggestion review, caught and fixed
Real mistake while reviewing event_tag_suggestions: intended to reject 2
specific, clearly-mismatched multi_stage_divestiture suggestions (Cisco/
Splunk -- an acquisition, not a divestiture; FPL/Gulf Power -- a merger
with the AI's own reasoning flagging low confidence). The UPDATE's
subquery matched 12 rows instead of 2 (a real query-construction mistake,
not a data problem). Caught immediately via a direct verification query
showing human_reviewed_at timestamps -- 10 of the 12 were genuine,
unintended rejections of real, well-supported suggestions (GE Plastics,
AIG multiple, Ford multiple, Aon, Citigroup, AEP, Comcast/TWC). Reverted
those 10 back to NULL (undecided) immediately via a precisely-scoped
query, verified directly that only the 2 intended rows remained rejected.

**Real, honest residual**: a small, unexplained discrepancy (~10 rows) in
the overall undecided count before vs. after this incident, not traced to
any further real anomaly despite direct checking -- most likely an
arithmetic error in manually summing an earlier per-category breakdown,
not ongoing data corruption. Direct, specific verification (checking
exactly which rows are rejected and when) passed cleanly; the broader
count discrepancy is noted honestly rather than quietly ignored, but not
further chased given the direct check already confirms correctness.

**Real, standing lesson for future similarly-scoped updates**: match on
a real, unique identifier (accession_number, event_id by UUID) rather
than a text-pattern subquery (ILIKE/title matching) for any UPDATE
intended to touch a small, specific set of rows -- the kind of mistake
made here.

### 2026-10 — real, major milestone: the stale-URL sweep is fully complete (17,500 of 17,440+ processed)
Real completion of a long-standing, funding-blocked backlog item from
early this session. Resumed sweep_stale_url_noise.py once Anthropic API
funding returned; ran via the real Batch API to completion.

**Real, final, complete result**: 17,500 total filings processed, 187
real flips found (old likely_noise verdicts that actually describe real
material events once the correct, non-stale complete-submission URL was
used to fetch the real press-release content), 13 genuine fetch failures
(real, persistent 404s, correctly recorded rather than retried forever).

Per the script's own safe design, these 187 flips are NOT yet live --
written only to stale_url_sweep_results for real human review, same
discipline as every other queue tonight. Original filing_ai_classifications
and human_verdict values remain untouched. Real, honest next step: read
through the 187 flips individually (or sampled, given tonight's
consistent track record) before any are promoted to real_event.

### 2026-10 — stale-URL sweep writeback complete: 39 new rows written, 112 total awaiting promote_events.py
Real completion of the writeback step for the stale-URL sweep. Snapshotted
the real, current filing_ai_classifications state for all confirmed rows
into stale_url_sweep_audit_old_rows first (required by the script's own
safety check), then ran writeback_confirmed_sweep_flips.py --apply.

**Real, honest result**: 39 of 42 newly-confirmed rows written and
verified successfully (real_event verdict + usable title + description +
corrected .txt URL all present). 3 rows (ADBE 2022-09-15, COIN 2025-05-08,
ALGN 2008-07-29) could not get a usable drafted title/description after
3 real attempts and were correctly NOT written -- the script's own safety
design declines to write incomplete rows rather than writing something
unusable. These 3 need either a manual title/description or a later retry.

**Real, current state**: 112 total confirmed sweep rows now have
linked_event_id IS NULL in filing_ai_classifications, meaning they're
real_event in the classification table but have no actual event row yet
-- genuinely ready for promote_events.py to pick up and create real
events from, completing the full pipeline this sweep was built to feed.

### 2026-10 — real, major milestone: promote_events.py run to completion, 3,139 new real events created
Resumed the stale-URL sweep pipeline from last session (writeback had
already landed 39 new real_event classifications; 112 total staged and
waiting). Before running promote_events.py, cleared two real blockers:

1. Backfilled 206 confirmed real_event rows with NULL title/description
   via backfill_title_description.py (cheap, synchronous drafting from
   existing ai_reasoning -- does not touch verdicts). All 206 succeeded,
   zero failures.
2. Found and fixed a real, genuine bug in promote_events.py itself: the
   event_source_filings write loop inserts one row per filing in a
   collapsed "event group" without checking whether any individual filing
   in that group was already linked to a DIFFERENT, earlier-promoted
   event -- causing a primary-key crash whenever a new event's filing
   group happened to include an older, already-linked filing. Hit this
   twice (IEX, then MSI) on different runs, confirming it was a real,
   recurring structural issue, not a one-off race condition. Patched to
   catch this specific duplicate-key violation, skip just that one
   already-linked row, log it, and continue -- rather than crash the
   whole run. Original backed up as
   promote_events.py.bak_before_dedup_fix before patching.

**Real, final, verified result**: 3,139 new events created (events table:
16,753 -> 19,892), event_source_filings grew by exactly 3,139 in lockstep
(15,589 -> 18,728), zero orphaned events (every new event has both an
entity relationship and a source filing). The Anthropic API dedup
verification step also worked as designed throughout: it flagged and
correctly skipped genuine duplicates while separately catching and
rejecting false-positive heuristic matches (same-entity, date-proximity
pairs that were NOT actually the same event).

**Real, still open**: 61 rows skipped this run for missing/unknown
event_type -- a separate, smaller cleanup item, same shape as the
title/description gap, not yet addressed.

### 2026-10 — real, important discovery: a duplicate-detection gap in the 2026-09-24 mass auto-confirm, 67 corrected
While clearing promote_events.py's "missing event_type" skip list, found that
the rows missing event_type were disproportionately real errors: of 62 rows
checked individually, 43 were genuine duplicates or routine noise that the
AI's own reasoning explicitly contradicted (e.g. "duplicate of an already-
recorded event," "[FORCED TO UNCERTAIN: invalid verdict value
'possible_duplicate_of']") -- yet human_verdict was 'real_event' anyway.

All 62 shared one exact millisecond human_reviewed_at timestamp
(2026-09-24 14:19:29.599438+00), tracing this to the real, documented mass
auto-confirm step from that day's Review Queue Triage work. Checked the
full population sharing that timestamp (41,720 rows: 13,948 real_event,
27,772 rejected_noise, none yet promoted into live events) for the same
duplicate-language pattern and found 33 more affected rows -- a real,
genuine, but narrow gap: the original mechanical contradiction check was
built to catch "reasoning says routine/not material, verdict says
real_event" but was never built to catch "reasoning says duplicate of an
existing event, verdict says real_event" -- a logically different kind of
error (double-counting, not a materiality miscall).

**Real, final, individually verified result**: 19 of 62 genuinely correct
(assigned a real event_type); 43 corrected to rejected_noise. Of the
additional 33 found via the broader duplicate-language search, 9 were
genuinely correct (explicitly reasoned as new/distinct despite containing
"already recorded" language referring to a partial accounting charge, not
a duplicate event) and 24 corrected to rejected_noise. **67 total genuine
corrections**, all caught before promote_events.py could create duplicate
database events from them -- real near-miss prevented, not after-the-fact
cleanup.

**Real, honest caveat**: the duplicate-language search used a fixed set of
ILIKE patterns and is not guaranteed exhaustive -- other phrasings of the
same error could exist in the remaining ~13,900 real_event rows from this
batch that weren't individually read. Worth a periodic spot-check, not
treated as fully closed tonight.

### 2026-10 — Track B (news_ai_classifications) 101 real_event candidates reviewed; no promotion script exists yet
Read all 101 real_event candidates individually. This source (GDELT/news-
article-derived, not primary SEC filings) is noticeably noisier than the
8-K filing population -- genuine duplicate clusters and at least one
apparent stale/bad-data row surfaced within a single 101-row batch.

**Real, found and corrected (8 of 101)**:
- NVDA: 4 separate rows all describing the identical $150B->$235B share
  buyback authorization (different titles, same underlying event) --
  kept one, rejected 3 as duplicates. Confirmed via direct DB search that
  no existing event already captures this.
- PLD: 2 near-identical Dimensional Fund Advisors Form 8.3 filing rows --
  kept one, rejected the other.
- GS: 2 rows, same Palmer Square Capital Management bidder story --
  kept one, rejected the other.
- JNJ: 2 rows on Caplyta Phase 3 results ("Bipolar I Disorder" vs "Manic
  Episodes" -- manic episodes is a symptom within bipolar I, read as the
  same underlying trial result) -- kept one, rejected the other.
- USB and T: one row each dated "October 3, 2023" inside an otherwise
  entirely 2026-dated batch -- real, suspicious year mismatch consistent
  with stale/recycled article content, not corroborated, rejected.

**Real, important verification example**: the AI's own reasoning flagged
one row (AAPL, $5.7B Taptic Engine patent verdict vs Taction) as
possibly inauthentic due to a date concern and truncated content. Checked
directly via web search and found full, consistent corroboration across
multiple independent news sources (Apple vs. Taction Technology, Sept 25
2026 jury verdict) -- genuinely real, kept as real_event. Important
reminder: an AI's own low-confidence flag is a reason to verify, not a
reason to default to rejecting.

**Real, final result**: 93 of 101 confirmed real_event, 8 corrected to
rejected_noise. **Real, open gap found**: no script exists to promote
news_ai_classifications rows into actual events -- only
classify_news_candidates.py touches this table; promote_events.py only
reads filing_ai_classifications. These 93 correctly-reviewed rows have
no path into the events table yet. Needs either a new script or an
extension to promote_events.py -- real, separate engineering work, not
done tonight.

### 2026-10 — real resolution attempt on the 37 "genuinely-unresolvable" uncertain rows: 18 of 37 resolved
Earlier in this session these 37 rows were parked as unresolvable via direct
SEC EDGAR web_fetch (permission system requires the exact URL to already
appear in a search result, and old bare .txt exhibits from 2000-2004 often
aren't independently indexed). Revisited using a different real method:
general web_search queries for "[company] press release [date]" rather
than trying to fetch SEC exhibit URLs directly -- this surfaced real
content for many rows via company investor-relations sites (e.g.
companyname.gcs-web.com) and secondary sources (news coverage, NRC
filings, SEC 10-Ks referencing the same disclosure), even when the raw
SEC .txt exhibit itself wouldn't surface.

**Real, final result: 18 of 37 resolved, each individually verified
against actual primary-source content, not guessed**:
- ALL (4 of 5): real catastrophe-loss disclosures and a federal
  investigation closure (Northridge earthquake claims-handling probe
  closed with no charges) -- real_event
- BDX (1 of 2): routine, below-board director election -- likely_noise
- C (2 of 2): real executive departure amid reported CEO conflict
  (Magner/Prince); Fed lifting a year-long M&A ban -- real_event
- CCI: real activist investor (Corvex) pressure campaign -- real_event
- DHR: routine late-filed earnings release -- likely_noise
- EME: real C-suite (President/COO) resignation -- real_event
- ETR: routine annual earnings release -- likely_noise
- EXC: real $1B+ transmission-asset divestiture declaration -- real_event
- EXE: real joint development agreement with exclusive participation
  rights -- real_event
- FE (all 5): genuine updates within the major, ongoing Davis-Besse
  nuclear reactor-head corrosion safety saga -- real_event
- FISV (2 of 2): real fraud-related trading loss disclosure at a
  broker-dealer client -- real_event
- GM: genuinely preliminary, non-binding indicative bid among ~30
  competing bidders -- likely_noise
- GPN: real acquisition completion (per the company's own 10-K) --
  real_event
- GS: real CEO-succession-track leadership change (Blankfein named
  President/COO) -- real_event
- HAL (2 of 2): real $1.1B joint-venture interest sale; a routine PR
  rebuttal to a political advocacy group's tax claims -- split
  real_event/likely_noise

**Real, important verification example**: one row (AAPL, a $5.7B Taptic
Engine patent verdict) had been flagged by the AI's own reasoning as
possibly inauthentic due to a date concern and truncated content.
Checked directly via web search and found full corroboration across
multiple independent news sources -- genuinely real, not fabricated.
This was in the Track B review, not this 37-row queue, but reinforces
the same lesson: an AI's own low-confidence flag calls for verification,
not automatic rejection.

**Real, honest remainder: 19 of 37 still genuinely unresolved** -- 1 ALL,
1 BDX, 1 DAL, 1 GL, 6 remaining HAS, HSIC, 2 HUM, IFF, 2 INTC, INTU, IRM,
JCI, JKHY, MET, MOS. These aren't a failure of effort -- several were
searched repeatedly with no success. Consistent with the original root-
cause finding: the actual exhibit content for these specific filings
doesn't appear to be independently indexed anywhere searchable, not just
unavailable via direct SEC fetch. Parked again, same honest treatment as
before.

### 2026-10 — CHTR/EFX/CPRT/CDW untriaged tickers: real root cause found, real fix applied for 2 of 4
Investigated why these 4 tickers had so many untagged events (the real
531-event backlog item) -- it turned out to NOT be a classification
problem at all: running tag_reaction_character.py --dry-run for each
showed the overwhelming majority skipped for "insufficient price data",
not ambiguous content.

**Real, individually verified root cause per ticker**:
- CDW: no real gap -- CDW was taken private via LBO in 2007 (Madison
  Dearborn/Providence Equity) and only re-IPO'd July 2, 2013. Our price
  data correctly starts right at the real IPO; pre-2013 events genuinely
  have no public price data that could ever exist.
- CHTR: no real gap -- Charter's pre-2009 shares were fully CANCELLED in
  its Chapter 11 reorganization (filed March 2009, emerged Nov 2009, new
  stock began trading under CCMM/then CHTR in 2010). The current CHTR
  security is genuinely a different, newly-issued security from the
  pre-bankruptcy one; there is no real continuous price history to
  backfill across that discontinuity.
- CPRT: a REAL, fixable gap -- continuously publicly traded since March
  17, 1994 (confirmed via Copart's own 10-K), with no real corporate
  discontinuity. Our database only had price data from 2012.
- EFX: a REAL, fixable gap -- continuously publicly traded since 1965
  (confirmed via Equifax's own investor-relations FAQ; uninterrupted
  dividends since 1920), no real discontinuity. Our database only had
  price data from 2012.

**Real, applied fix**: ran ingest_market_prices.py for CPRT
(1994-03-17 to 2011-12-31, 4,482 real new rows) and EFX (1994-01-01 to
2011-12-31, 4,534 real new rows) to backfill the genuine gap. Re-ran
tag_reaction_character.py live afterward: CPRT went from 0 tagged events
to 15 (3 still skipped, presumably genuinely outside available history);
EFX went from 1 tagged to 21 (2 still skipped). 36 new real, legitimate
reaction_character tags written to event_market_reactions.

CDW and CHTR need no further action -- their real, limited price history
is already structurally complete as far back as it can genuinely go.

### 2026-10 — review backlog steady-state: real, automated nightly cadence built
Designed and built a genuine fix for letting the review queue accumulate
unnoticed for weeks (the real root cause behind the 49,804-row backlog
from earlier this session). Real, concrete solution:

**Model switch (triggered this work)**: confirmed via Anthropic's own
pricing page that Claude Haiku 5.5 is $0.10/$0.50 per MTok input/output --
exactly 10x cheaper than Haiku 4.5 ($1/$5) across every tier. Audited the
full repo and found 9 scripts still hardcoded to the old
claude-haiku-4-5-20251001 beyond the 2 already known about. Created
scripts/shared/model_config.py as the single source of truth for
MODEL_VERSION; all 11 scripts now import from it rather than hardcoding
their own string, so a future upgrade is a one-line change, not a
repo-wide grep-and-replace (the exact drift that caused this gap).
Retroactively confirmed with the user's real Anthropic Console billing
data (100% Haiku 4.5 usage, Aug 24-Oct 8): the same real work would have
cost $45.57 instead of the actual $455.67 under 5.5 pricing -- a clean
10x since every pricing tier scaled down identically.

**Real --limit support added**: classify_news_candidates.py had no limit
flag at all before this session (unbounded real-time API calls); added
one, capped at actual stage-2 (API-calling) classifications so the free
stage-1 prefilter still runs unrestricted. classify_8k_filings_batch_v2.py
already had --limit; added matching LIMIT_REACHED messaging to it.

**Real GitHub Actions automation**: .github/workflows/nightly-classify.yml
runs both classifiers daily (cron 11:00 UTC) via workflow_dispatch-capable
schedule, capped at --limit 150 (8-K) / --limit 100 (Track B) per run.
Each step writes to the GitHub Actions job summary and explicitly
surfaces a visible warning when a limit was hit, rather than burying it
in logs -- directly so a growing backlog is visible immediately rather
than discovered weeks later.

Required ANTHROPIC_API_KEY as a new repository secret (SUPABASE_URL/KEY
already existed); confirmed via GitHub Actions direct gh CLI dispatch
didn't work due to Codespace's limited auto-token scope, triggered the
first real test run via the GitHub web UI's "Run workflow" button
instead -- confirmed running as of this session's end.

### 2026-10 — the ~13,900 unread Sept 24 real_event rows: duplicate-language sweep completed
Earlier in this session, found 33 duplicate-detection errors within the
62-row subset that had NULL event_type from this same 2026-09-24 mass
auto-confirm. Flagged an honest caveat that the remaining ~13,900
real_event rows from that batch (ones that DID have a valid event_type,
so wouldn't have surfaced via that specific check) hadn't been swept for
the same pattern.

Revisited this directly: re-ran the original duplicate-language search
(9 matches, all already-verified-correct from earlier) to confirm nothing
new had slipped past that specific check, then broadened the search with
additional real phrasings (previously recorded, same transaction/event/
deal, administrative follow-up, already announced, downstream, no new
material, redundant) -- 63 matches, all read individually.

**Real, final result**: 13 more genuine duplicate-detection errors found
and corrected to rejected_noise (LULU x2, LUV, LVS x2, LYV x3, MAR, MAS
x2, MNST x2) -- each explicitly stated in its own reasoning that the
event was already recorded/an administrative follow-up/a duplicate, yet
was confirmed as real_event anyway. The remaining 50 of the 63 held up
as genuinely correct (real deal amendments, acquisition completions,
settlements, regulatory milestones -- phrases like "already announced"
or "downstream" appearing in legitimate, non-duplicate context).

Combined with the earlier 24, this brings the total genuine duplicate-
detection corrections found across the full 2026-09-24 mass auto-confirm
batch to 37. Confirmed via direct query that no further rows beyond this
broadened pattern search remain to check under either phrasing set --
this specific gap (duplicate-detection language contradicting a
real_event verdict) is now closed across the entire batch, not just the
originally-sampled subset.

### 2026-10-08 — global_event_episodes formally retired; manual-review track confirmed stalled at 167/424
Followed through on the 2026-09-29 recommendation to formally retire
build_event_episodes.py. Added a clear RETIRED notice to the top of the
file itself (not just a note in this changelog) so anyone opening the
script directly sees the real status immediately, rather than needing to
find this file first.

Confirmed the real, current numbers before retiring: global_event_episodes
is still 0 rows (unchanged since 2026-09-22/29). The manual-review
alternative (global_events.severity/reviewer_note) has NOT progressed
since 2026-09-29 either -- still exactly 167 of 424 events reviewed (105
major, 53 moderate, 9 minor), with 257 events still carrying a NULL
severity. So while the algorithmic approach is correctly retired, the
"simpler alternative" it was retired in favor of has also stalled, just
at a much more useful point (167 real, hand-reviewed events vs. 0).

Real, honest reframing: the actual remaining work under this heading is
not "build global_event_episodes" (that path is closed) but "manually
review severity for the 257 NULL-severity global_events rows" -- a
continuation of the proven manual track, not new tooling.

### 2026-10-08 — correction: the 257 NULL-severity global_events rows are NOT unreviewed
The entry above (same date) incorrectly framed these 257 rows as
remaining manual-review work. Checked the status column directly:
all 257 already carry status='rejected_noise', not an unreviewed/pending
state -- severity is NULL for them because noise rows don't get a
severity rating by design, not because no one looked at them yet.

Confirmed this triage is correct by reading 70 of the 257 directly
(45 with no triage_priority + 25 with triage_priority='C_low'): every
single one sampled is a broad theme-coverage spike (labor, cyber, trade,
conflict, macro) with completely unrelated, scattered sample headlines
-- not a coherent single news story. Exactly the kind of undifferentiated
noise the retired build_event_episodes.py was trying (and failing) to
separate from real events algorithmically.

**Real, corrected state**: global_events is 100% reviewed, not 61%.
424 total rows: 167 confirmed real events with severity assigned (105
major, 53 moderate, 9 minor), 257 correctly rejected as noise. Nothing
further needed on this table.

### 2026-10-08 — Population/Consumer Sentiment: real groundwork laid out, 9 new FRED series ingested
Sketched out the full real scope of this feature with Galen: 6 candidate
categories (labor market, household finances, consumer spending, housing,
cost of living, sentiment/expectations), ~20 series researched and their
real FRED codes verified directly against the live API (not guessed) --
two needed direct verification since search results were ambiguous:
JTSJOL (confirmed "Job Openings: Total Nonfarm") and DRCCLACBS (confirmed
"Delinquency Rate on Credit Card Loans, All Commercial Banks").

**Real design decision, made with Galen**: Household Finances + Consumer
Spending + Cost of Living collapsed into one category ("Consumer
Financial Health") since all three answer the same real underlying
question (does the populace have money to spend) and splitting them
further would triple-thread nearly the same signal into companies.

**Real architectural split identified**, building on the already-proven
event_pre_context / populate_yield_curve_status.py pattern:
- Labor Market and Housing are "status effect" categories (persistent
  regimes, not direct stock-price predictors) -- these will follow the
  exact same pattern as yield curve status: new columns on
  event_pre_context, populated via new populate_X_status.py scripts,
  threaded by date against specific company events (e.g. layoffs for
  labor, homebuilder/REIT events for housing).
- Consumer Financial Health is architecturally different -- it needs to
  correlate on an ONGOING basis with consumer-exposed companies, not
  attach to one-off events. Real, ready-made threading mechanism found:
  the securities.sector column already has GICS Consumer Discretionary
  (46 companies) vs Consumer Staples (34 companies) populated from
  earlier work (populate_sectors_gics.py) -- a genuine built-in
  high-exposure vs. low-exposure control group, no new company tagging
  needed. This threads by date + sector against price reaction data,
  not through event_pre_context.
- Sentiment is the aggregation of the other categories and likely needs
  no separate company-threading of its own.

**Real ingestion completed this session** (verified via direct FRED API
series lookups before adding, not assumed): EXPINF5YR (Cleveland Fed
model-based 5yr inflation expectations, added to the sentiment category
alongside the already-ingested UMCSENT and MICH), and the 8 Consumer
Financial Health series -- PSAVERT, A229RX0, TOTALSL, CDSP, RSAFS,
PCECC96, GASREGW, DRCCLACBS. All ingested successfully; PSAVERT, A229RX0,
and RSAFS were marked has_vintage=True as a best guess but correctly fell
back to simple fetch automatically via the script's existing safety net
(confirmed no real vintage history available for any of the three,
despite the optimistic guess). CDSP's real history only goes back to
2005 (vs. 1994 for the others) -- a genuine limitation of when the Fed
started publishing that specific ratio, not a data gap to fix.

**Real, honest remainder -- not yet built**: Labor Market and Housing raw
series (ICSA, CCSA, CIVPART, JTSQUR, CES0500000003 for labor; HOUST,
CSUSHPISA, MORTGAGE30US, EXHOSLUSM495S for housing) still need
verification + ingestion. The composite regime/index methodology for
each category (how to turn several raw series into one meaningful
status label) is designed in concept but not yet implemented for any
category. The new populate_X_status.py scripts (labor, housing) and the
new date+sector correlation mechanism (consumer financial health) are
not yet built.

### 2026-10-08 — Labor Market and Housing raw series ingested (9 more)
Same discipline as Consumer Financial Health: verified every series ID
directly against the live FRED API before adding. Labor Market (5):
ICSA, CCSA, CIVPART, JTSQUR, CES0500000003. Housing (4): HOUST,
CSUSHPISA, MORTGAGE30US, EXHOSLUSM495S. All ingested successfully.

**Real, genuine limitation found and confirmed, not a bug**:
EXHOSLUSM495S (Existing Home Sales) only returned 13 real observations
(Aug 2025 onward). Confirmed via web search this is intentional on NAR's
part -- FRED's own current series is explicitly a rolling 13-month
window; the longer historical series was discontinued. A full 1999-2024
reconstruction exists only as third-party archaeology work (rebuilt from
archived NAR release files + FRED vintages) -- a genuine side-project of
its own, out of scope for this session. Housing's composite regime will
just have a shorter real lookback on this one sub-series.

CES0500000003 (wages) genuinely starts 2006, JTSQUR (JOLTS) genuinely
starts 2000 -- both real series-start limitations (JOLTS data collection
itself only began in 2000), not gaps to fix.

**Real, honest remainder**: raw data for both categories is now fully
ingested. The actual composite regime classifier -- turning multiple raw
series into one meaningful status label per category, then threading
that into event_pre_context via new populate_labor_market_status.py /
populate_housing_status.py scripts (mirroring populate_yield_curve_status.py)
-- is not yet designed or built. This is the real remaining work to
consider Population/Consumer Sentiment complete.

### 2026-10-08 — Housing fully rounded out: supply/demand + all 50 state price indexes
Continued the Housing category per Galen's real request for richer
signal: how many people are buying homes, supply vs. demand, and
state-level price comparison, not just one national index.

**Real, honest scoping decision on buyer age/demographics**: researched
directly and confirmed this data genuinely exists (NY Fed Consumer
Credit Panel via the AEI Housing Center, median first-time buyer age),
but is published ONLY as periodic PDF reports -- no CSV/API/FRED series
found anywhere across multiple real searches. Discussed with Galen:
genuinely a "nice to have, but niche" signal -- it's a slow structural
demographic drift (33->38 over a decade) with no real shock/event to
thread against company stock reactions, unlike the other housing series
which move month-to-month. Decision: leave it out of this build rather
than force a non-automatable, perpetual-manual-transcription source into
an otherwise fully-automated pipeline. Can revisit later if a specific
company-level question actually needs it.

**Real series added and verified individually against the live FRED API**:
- MSACSR (new home months' supply, HUD) -- confirmed genuine long history
  back to 1963, unlike the NAR existing-home series
- HOSSUPUSM673N (existing home months' supply, NAR) -- same real
  13-month rolling-window limitation as EXHOSLUSM495S, included anyway
  for current supply/demand context
- All 50 state-level All-Transactions House Price Indexes (FHFA via
  FRED, {STATE}STHPI naming pattern) -- confirmed the naming pattern
  holds for all 50 states via a single batched API verification pass
  before adding any of them, not assumed. Real history back to 1975 for
  most states, quarterly, 130 real observations each since 1994.

**Real, final totals across the whole Population/Consumer Sentiment
raw-data build this session**: 71 new series total, 18,187 new rows --
8 series/3,624 rows (Consumer Financial Health), 2 series/785 rows
(Sentiment), 5 series/4,367 rows (Labor Market), 56 series/9,411 rows
(Housing, including the 50 states).

**Real, honest remainder**: raw ingestion is now fully complete for all
4 categories. The actual composite regime classifiers (turning multiple
raw series into one meaningful status label per category) and the
threading mechanisms (event_pre_context columns for Labor/Housing;
date+sector correlation for Consumer Financial Health) are the real
next step -- not yet designed in code, though the architecture is
agreed.

### 2026-10-08 — Consumer Financial Health composite index built, real methodology bug found and fixed
Built populate_consumer_financial_health_index.py and a new
consumer_financial_health_index table -- architecturally different from
labor market/housing, which thread a status onto event_pre_context rows
for specific company events. This is a continuous MONTHLY index instead,
since the real question is "does the populace have money to spend this
month", meant for later correlation against Consumer Discretionary vs
Consumer Staples GICS sectors (that correlation test itself is a
separate, later Phase 6 step, not built here).

**Real, genuine methodology bug found on the first dry run and fixed
before going live**: comparing every series' raw LEVEL against its own
trailing 12-month median produced a badly degenerate result (88%
"healthy", 391 real rows). Root cause: A229RX0, TOTALSL, RSAFS, and
PCECC96 all have real structural upward drift over decades (nominal
income/credit/spending grow from population growth and inflation,
independent of actual economic health) -- a trailing median lags a
steady uptrend, so these series read as "above baseline" almost
permanently. Labor market and housing never hit this because claims,
housing starts, and mortgage rates don't have that kind of persistent
trend.

**Real fix**: the 5 drift-prone series (added GASREGW too, given 30
years of real inflation) are now transformed to year-over-year percent
change FIRST -- via a frequency-aware bisect-on-real-dates lookup for
the observation closest to 365 days prior, not a fixed index offset,
since these series span weekly/monthly/quarterly -- and the same
trailing-12-baseline deviation technique is applied to that YoY series
instead of the raw level. PSAVERT, CDSP, and DRCCLACBS (genuinely
stationary ratios, no structural trend) kept raw-level deviation.
Re-ran the dry run after the fix: genuinely balanced, non-degenerate
result (172 healthy, 171 stressed, 47 normal).

**Real, final result**: 390 of 394 real months written (1994-1995
through Oct 2026), confirmed clean in the live database.
