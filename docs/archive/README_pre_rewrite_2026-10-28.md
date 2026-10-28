# precedent-engine
Stock Research & Market Event Analysis Platform

A historical market research platform connecting company financials, news, real-world corporate events, macroeconomic conditions, and stock-price movements — built to investigate how markets have historically reacted to similar events, with calibrated, sample-size-aware confidence rather than guesswork.

Company → Financials → News → Events → Macro Conditions → Stock Price → Analysis

Core discipline: this platform is explicitly not trying to predict outcomes. It surfaces historical probabilities with visible sample sizes ("in N comparable cases, X% moved this direction") rather than forecasts. Nothing is treated as a real pattern until it clears a minimum sample-size threshold (n=30–50) — small-sample "patterns" are actively guarded against throughout the pipeline.


## Current State (see PROJECT_PLAN.md for the full breakdown)
- **499 securities tracked**, approaching full S&P 500 coverage
- **19,892 real, verified corporate events recorded**, spanning 1994–2026, across a 24-category event taxonomy (acquisitions, leadership changes, regulatory actions, capital raises, restructurings, spinoffs, and more) — every event traces back to its exact source SEC filing(s), nothing inferred or hallucinated
- **102,962 filing classifications reviewed or in review** (8,965 still in the backlog) — every bulk auto-confirmation policy in this pipeline is backed by a real, measured accuracy check before being trusted at scale, and every classification decision is logged with the AI's confidence and reasoning
- **3,365,653 rows of daily price data**, 497/499 securities, 1994–2026 coverage
- **81 macro/population series tracked, 57,510 real data releases** — rates, inflation, employment, GDP, oil, consumer sentiment, labor market health (jobless claims, JOLTS, wages), housing (new/existing home activity, mortgage rates, all 50 states' price indexes), and consumer financial health (savings rate, credit, retail sales, gas prices) — each series individually verified against the live FRED API before ingestion, not assumed
- **16,488 event_pre_context rows** carrying "status effect" context (yield curve inversion, labor market regime, housing regime) threaded onto company events at the moment they happened — not a snapshot, a persistent condition the event occurred within
- **424 global/geopolitical events tracked** (167 reviewed with severity + reviewer notes)
- **103 Track B news candidates confirmed** as real events (promotion into the main events table not yet built)

Every event in this database traces back to its exact source SEC filing(s) — nothing is inferred or hallucinated. Every bulk auto-confirmation policy in this pipeline is backed by a real, measured accuracy check before being trusted at scale.


## Architecture
Data Sources: SEC EDGAR XBRL (financials, primary events) · GDELT BigQuery (global events, company sentiment) · FRED API (macro, labor, housing, population) · Twelve Data (prices)

      ↓

Phase 1-2: Financial Foundation  →  financial_statements, financial_metrics, financial_condition_score

      ↓

Phase 3: Corporate Events        →  sec_8k_filings → filing_ai_classifications (AI + human review) → events

      ↓

Phase 4: Macro / News / Global Events  →  macro_data_releases (rates, inflation, employment, GDP, oil, sentiment, labor market, housing, consumer financial health) · company_sentiment_timeline (GDELT) · global_events (GDELT macro/geopolitical candidates) · news_ai_classifications (Track B)

      ↓

Phase 5: Price Reaction Engine   →  event_market_reactions_corrected (per-event abnormal returns vs. SPY) · financial_market_reactions (abnormal returns for every financial filing) · event_pre_context (status-effect threading: yield curve, labor market, housing regimes attached to the specific event they occurred within)

      ↓

Phase 6: Pattern Engine          →  pattern_significance_tests, same_entity_sequence_chain_position — cross-sectional comparison, n=30-50 threshold enforced

      ↓

Phase 7+: Dashboard / Live Feed  →  not yet built

See PROJECT_PLAN.md for phase-by-phase status and SCRIPTS.md for the real, verified interface of every script in the pipeline.


## Getting Started
Onboard a new company (full pipeline: register → financials → 8-K history → prices → classify → review → promote):

    python scripts/onboard_pipeline.py TICKER

This logs every step's result to onboarding_runs / onboarding_run_steps, so a run can be handed off and checked asynchronously. See SCRIPTS.md for the manual step-by-step version if you need finer control.

Check the review backlog:

    SELECT COUNT(*) FROM filing_ai_classifications WHERE human_verdict IS NULL;

Promote confirmed real events into the actual database:

    python scripts/classification/promote_events.py --live

The classification and tagging pipeline runs on a scheduled, cost-capped GitHub Action (`.github/workflows/nightly-classify.yml`) in addition to manual runs — see SCRIPTS.md for how the model version and per-run limits are configured.


## Recent Findings (updated 2026-10-08)

- **A 2026-09-24 mass auto-confirm had a duplicate-detection gap**: the
  process was built to catch materiality miscalls but never built to
  catch an AI explicitly reasoning "this is a duplicate of an existing
  event" while its verdict still said `real_event`. Found and corrected
  37 genuine errors across the full batch via direct reasoning-text
  search, confirmed clean via exhaustive re-check — this specific gap is
  now closed.
- **Model migration to Claude Haiku 5.5**: confirmed via Anthropic's own
  pricing page a flat 10x cost reduction across every tier vs. Haiku 4.5
  ($0.10/$0.50 vs $1/$5 per million tokens). All classification/tagging
  scripts now import a single shared `MODEL_VERSION` constant
  (`scripts/shared/model_config.py`) rather than hardcoding their own,
  after finding 9 scripts had silently drifted onto the old model.
  Also found and fixed a real crash risk from the switch: Haiku 5.5 can
  spend its whole token budget on (unsolicited) thinking and never emit
  a text response — every script now explicitly passes
  `thinking: {type: "disabled"}`.
- **`global_event_episodes` formally retired.** Four algorithmic
  iterations to group multi-day GDELT theme spikes into coherent
  "episodes" each fixed one case while breaking another; the real root
  cause (needs theme share of total coverage, not absolute count) was
  identified but never implemented. The simpler, already-proven
  alternative — hand-reviewed `global_events.severity` — is the real,
  intended path; the episode script is kept for reference only.
- **`reaction_character` tagging computes ONE reaction per event from the
  FIRST-linked entity only**, even for events linked to many companies.
  Sized at 49 of 15,928 tagged events (0.3%) — small in count but
  concentrated in large macro/systemic events where it matters most.
  **Until fixed, treat `systemic_shock`/`geopolitical`/`government_action`
  results from any model or significance test as unreliable.**
- **Table-naming trap**: `sec_filings` contains only 10-K/10-Q filings;
  `sec_8k_filings` contains the actual 8-K data. Names are swapped from
  their real contents.


## Non-Negotiable Discipline
- No number is trusted without re-verifying against the live database.
- No script interface is guessed — the real file is checked before writing against it.
- No bulk confirm/correct without reading a real sample first.
- Sample size and uncertainty are stated plainly, everywhere.
- Inconsistencies get dug into, not waved off.
- Company names, CIKs, and tickers are never fabricated — always pulled from SEC's own data.
- Every bulk auto-decision policy is backed by a measured accuracy check on real data before being trusted.
- A column's null-rate percentage alone never proves it's a usable signal — sample real rows before trusting any column as a feature.
- A table or column name is never trusted at face value — its real type (view vs. base table), real contents, and real behavior are checked directly before relying on it.
- A partial-column database write uses the operation that actually does a partial update (e.g. `update()`), never one with full-row-replace semantics (e.g. `upsert()`) unless every column is genuinely being supplied — confirmed the hard way when a batched `upsert()` attempt would have silently nulled out unrelated columns on success.
