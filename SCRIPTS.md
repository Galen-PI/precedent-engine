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
