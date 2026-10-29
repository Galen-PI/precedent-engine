# precedent-engine

Stock Research & Market Event Analysis Platform

A historical market research platform that connects company financials, corporate events, news, macroeconomic and government conditions, and stock-price reactions, to investigate how markets have historically responded to events.

Company → Financials → Events → External Conditions → Price Reaction → Pattern → (forward tests)

**The stance.** This platform is not trying to predict outcomes. It reports historical probabilities with visible sample sizes ("in N comparable cases, X% moved this way"), and it holds itself to the same standard it applies to the data: every finding states its sample, its uncertainty and what would overturn it, including findings about its own earlier work.

---

## Where it stands (as of 2026-10-29)

*Every number in this table was measured on 2026-10-29: the database figures by the query saved as scripts/sql/readme_snapshot.sql, the repository figures (scripts, commits, changelog entries) by counting files and commits. Re-check before relying on one: the table is regenerated at each milestone, not edited by hand.*

| area | what exists |
|---|---|
| **Universe** | 499 securities (today's index members only, a survivorship limit), 497 with prices; 160 sealed for out-of-sample exploration |
| **Events** | **23,554** events, 1994-01-05 to 2026-09-11, in a 24-type taxonomy; **22,385 (95.0%)** are linked to a source SEC filing |
| **Filings** | 155,141 8-K filings and 49,892 10-K/10-Q filings; 150,539 AI classifications, **95,485 (63.4%)** with a human verdict, the rest governed by written policy |
| **Prices** | 3,371,150 daily rows, 1994-01-03 to 2026-10-13 |
| **Financials** | 28,533 quarterly and 8,473 annual statements (2006-12-31 to 2026-08-31), 37,006 metric rows; point-in-time only from about 2010 |
| **External conditions** | 57,510 macro releases and 250,055 long-history macro rows; 310 FOMC meetings; 1,334,852 company-sentiment rows; 424 global events; 8,024 government decisions (3,035 with text); 2,176 laws with stage dates; 1,204 news articles |
| **Reactions** | **22,486** events with a measured 20-day reaction against SPY; 23,309 pre-context rows; 954,685 ripple-timeline rows (21,915 events) |
| **Labels** | rewarded 5,918, punished 6,082, muted 8,144, diverged 2,380 (the diverged label is under revision; see limits) |
| **Accounting** | every one of the 23,554 events is either measured or has a recorded reason (1,068 unmeasured, all explained); 1,527 are excluded from analysis, none are under review, 639 carry a note |
| **Findings** | 112 flags in the ledger: **15 proven, 21 lead, 62 null, 2 retired, 12 untested** |
| **System** | Supabase Postgres: 163 tables and 34 views, 3.2 GB; 263 Python scripts in 17 folders; 498 commits since 2026-08-19; 200 dated changelog entries |

## The eight phases

Each phase answers one question and is done when a query says so (definitions and checks: docs/NAMING.md; current state: docs/PROJECT_STATUS.md).

| # | phase | the question |
|---|---|---|
| 1 | Data Foundation | Is the raw data correct and complete? |
| 2 | Financial Analysis | Given correct raw data, what do the financials say? |
| 3 | Corporate Events | What happened, and can we prove it? |
| 4 | External Conditions | What was the world telling the market? (macro, news, sentiment, government, the Fed, global events) |
| 5 | Price Reaction Engine | How did the market respond, net of what the whole market did? (passes its five-component gate as of 2026-10-29; no event awaits a review decision) |
| 6 | Historical Pattern Engine | Does this actually recur, or only look like it does? (a cleanup gate comes first) |
| 7 | Dashboard / Website | Can a person see and use it? (not started) |
| 8 | Autotrader | Can the system act on its own analysis, safely? (not started; gated on phase 6) |

## What has held and what has not

By the flag ledger on 2026-10-28 (112 flags: 15 proven, 21 lead, 62 null, 12 untested, 2 retired; the readings and numbers are in THEORY.md). None has yet been re-run on the cleaned analysis set.

- **Held, about the size of moves (not their direction):** event days run about 1.3 to 1.6 times a normal day, earnings days about 2.5 to 2.7 times, and scheduled FOMC announcements lift the whole market about 1.1 to 1.14 times; bands built from those widths calibrate to about 90% out of sample; Energy stocks move more on oil-shock days (same day only). Capital-raise filings show no burst.
- **Held, weakly (direction):** the labeler's good-or-bad reading of an event's text gets the sign of the two-day move right about 58% of the time against about 54% by chance, and it explains almost none of the squared miss.
- **Did not hold:** price-side direction signals (overreaction reversal, the sign of the earnings surprise at about 53%, news tone), the apparent magnitude lift (it was plain volatility), law stages and executive-order signing days, Federal Reserve change days, and round-number effects as registered. The first-reported tag-level significance ("6 of 13") was tested against the wrong null and is retracted (docs/PROJECT_STATUS.md).

## Known limits

Measured on 2026-10-28 and 2026-10-29 and stated in full in docs/PROJECT_STATUS.md section 3.5:

1. **1,169 events (5.0%) have no source-filing link.** For 813 of them the filings are recorded in a different table (`event_component_dates`): 575 multi-filing summaries, and 238 curated events of which 236 duplicate an event the pipeline had already promoted from the same 8-K. All but three of the 813 are excluded from analysis (two were read and kept as single occurrences; one has a 95-day filing gap). The other 356 have no filing recorded anywhere (mostly events without a reaction row).
2. **Price series carry a few artifacts at corporate actions** (spin-offs, special dividends). Seven events carry a price-step exclusion (JCI's unadjusted 2007 separation was added on 2026-10-29), and two violent but real moves (HIG, LVS) were read and kept; detection below a 60% one-day step is still to be built.
3. **Quarterly financial data are point-in-time only from about 2010.** Firm-state labels before then, or computed by the quarter-end rule, carry look-ahead; the `diverged` label is unstable (about 65% of its members survive honest inputs) and is not used as a feature until redefined.
4. **The effective sample is smaller than the row count:** about 70% of reaction rows were independent within their company when measured on 2026-10-28, before 508 events left the analysis set on 2026-10-29 (it will be re-measured at gate G7), and dependence across companies on the same date is not yet measured.
5. **709 events have no price history** (events of predecessor tickers, and securities without prices) and are permanently excluded.

## How the work is done

- Tests are **pre-registered** before they run, with predictions that carry a range and an anchor; every call is scored afterwards.
- The **forward tests are frozen** until their verdicts are recorded (the next reading is after 2027-01-05); a git hook enforces it.
- **30% of companies are sealed** from exploration; exploration creates no flag.
- Every change is a dated entry in CHANGELOG.md; every status is a check that can be run; every bulk operation has a backup and a read of the cases before it is applied.

## Where things live

| to find | look in |
|---|---|
| the first file for a new session | docs/START_NEW_DAY.md |
| the current state, tests, to-do and inconsistencies | docs/PROJECT_STATUS.md |
| names, the eight phases and their "done when" checks | docs/NAMING.md |
| the design and the prediction contract | PROJECT_PLAN.md |
| the findings log, anchored to the flag ledger | THEORY.md |
| history, newest first | CHANGELOG.md |
| how to run the pipelines | docs/OPERATIONS.md |
| every script's interface (generated) | docs/SCRIPTS_REFERENCE.md |
| where every results file came from (generated) | docs/RESULTS_MAP.md |
| registrations, tests, samples | results/ |
| scheduled jobs | .github/workflows (nightly-classify.yml, marketaux_daily.yml) |

Built with Python, Supabase (Postgres), the Anthropic API (classification), SEC EDGAR, Twelve Data (prices), FRED, GDELT and Marketaux. Credentials live in environment variables (SUPABASE_URL, SUPABASE_KEY, and the API keys), never in the repository.

---

## Retired (as of 2026-10-28)

What this README used to say, and where it went. The unedited original is docs/archive/README_pre_rewrite_2026-10-28.md.

| it said | why retired | now |
|---|---|---|
| "Current State" counts of 2026-10-08 (19,892 events; 102,962 classifications; 16,488 pre-context rows) | superseded: events grew to 23,554, classifications to 150,539, pre-context to 23,309 | the snapshot table above |
| "Every event traces back to its exact source SEC filing" | false for 1,215 events (5.2%) when retired, 1,169 on 2026-10-29 | the known limits above |
| "103 Track B news candidates confirmed" | not verified; the news tables hold about 1,200 articles | docs/PROJECT_STATUS.md |
| "Recent Findings (2026-10-08)" | stale; several were corrected later | docs/PROJECT_STATUS.md section 5.3 and CHANGELOG.md |
| "Getting Started" and the command list | a manual, not a snapshot; paths have moved (onboarding is now scripts/onboarding/onboard_pipeline.py) | docs/OPERATIONS.md |
| "Non-Negotiable Discipline" list | grew to 15 standing rules | docs/PROJECT_STATUS.md section 1 |
| "read SCRIPTS.md" | SCRIPTS.md was retired into the changelog and the generated reference | CHANGELOG.md, docs/SCRIPTS_REFERENCE.md |
| "Phase 4: News Ingestion" | too narrow for what it holds | Phase 4: External Conditions |
| global_event_episodes | retired in October (the table is empty) | global_events severity and reviewer notes |
