# NAMING (2026-10-26)

One standard so that a name tells you what a thing is, where it belongs, and when it was made. Existing names are NOT renamed for tidiness: a rename happens only when a name collides with another, or misleads, and every rename is recorded in CHANGELOG.md as old name to new name.

## 1. Principles (they apply to everything: phases, files, tables, scripts, labels, IDs)
1. **A name says what the thing IS, not how it was made or how good it is.** `event_market_reactions`, not `new_reactions_v2_final`. Words like new, old, final, fixed, tmp, better never appear in a name that is meant to last.
2. **A name is stable.** Once a name is used in a document, a table, a script or an ID, it is never reused for something else. To change the meaning, make a new name and record the old to new mapping.
3. **One thing, one name.** If two names exist for the same thing, this file lists the alias and says which wins.
4. **A name is no narrower than what it contains.** If a phase or a folder holds more than its name says, the name is wrong, not the content.
5. **Kind goes first, date or generation goes last.** `PREREG_round_number_2026-10-26.md`: the prefix names the kind of document, the suffix is the date (made, as of, or valid from) or a generation (`v1`, `v2`). Dates are always ISO (YYYY-MM-DD), never "last month".
6. **A status is a check that can be run, not a percentage someone estimated.** Every phase below says "done when" in terms of a query or a script that returns pass or fail.
7. **Generated things say so** (first line "GENERATED ... do not edit") and are only ever rewritten by their generator.
8. **Work outside the numbered phases is a TRACK, never a new phase.** Tracks are letters under their phase (6A, 6B). There is no "Phase 7 engine": that work is tracks 6D and 6E.
9. **A folder is named for the job or domain its files do** (lowercase, underscores), and two folders may never name the same job (`audit` and `audits` was a violation; they are merged).
10. **A label names its measurement.** A label's definition is stored next to its name and states the window, the baseline and the benchmark (see section 5).

## 2. The eight phases
The numbers and names come from PROJECT_PLAN.md. Each phase answers ONE question, and is done when its check passes (the checks are targets to build; until a check exists the phase is marked "unmeasured", not given a percentage).

| # | name | the question it answers | done when (check) | tracks |
|---|---|---|---|---|
| 1 | Data Foundation | Is the raw data correct and complete? | every security has prices, filings and financials, or a written exclusion; as-quoted levels have a valid-from row or an exclusion | 1A prices (stored and as-quoted), 1B filings (8-K), 1C financial statements, 1D onboarding |
| 2 | Financial Analysis | Given correct raw data, what do the financials say? | financial_metrics exists for every company with statements, or the null register explains the gap | 2A metrics, 2B condition score, 2C null register |
| 3 | Corporate Events | What happened, and can we prove it? | every candidate 8-K is classified; every classification is human-reviewed or covered by a written policy; every real event is promoted | 3A classification, 3B review, 3C promotion, 3D materiality rubric |
| 4 | News Ingestion **[name too narrow, see below]** | What was the world telling the market? | each source is current to its stated date with a documented update path | 4A macro (FRED), 4B news and sentiment (GDELT, Marketaux), 4C government decisions (laws, orders, tags, subjects), 4D Federal Reserve (FOMC calendar and state), 4E global events |
| 5 | Price Reaction Engine | How did the market respond, net of what the whole market did? | **every event has a reaction row, one reaction label that agrees with it, a pre-context row and a ripple timeline, or a documented exclusion reason** | 5A reactions, 5B reaction labels, 5C pre-context, 5D ripple timeline |
| 6 | Historical Pattern Engine | Does this actually recur, or does it only look like it does? | every pattern claim meets the prediction contract (universe, horizon, benchmark, base rate, similarity keys, magnitude with interval, out-of-sample window) | 6A evaluation harness (D1-D4), 6B flag ledger and event premium, 6C ranges and bands, 6D decomposition (chapters 1-3), 6E day card and day view |
| 7 | Dashboard / Website | Can a person see and use it? | not started | (none yet) |
| 8 | Autotrader | Can the system act on its own analysis, safely? | not started; gated on phase 6 | (none yet) |

**Principle 4 applied:** Phase 4 holds macro, government, global-event and sentiment work, not just news, so its name fails. Proposed: "Phase 4: External Conditions (news, macro, government, global events)". Every other phase name passes.

**Old names to current names**
| old | now |
|---|---|
| "Phase 7 engine" (SCRIPTS.md, 10-19 to 10-21) | 6D decomposition and 6E day card |
| "Phase 6" as the synthesis / "brain" (notes, 10-13 to 10-26) | 6E day view (with 6D) |
| "Phase 6 harness" D1-D4 | 6A evaluation harness |
| "Pattern Engine" (README) | Historical Pattern Engine (phase 6) |
| "the brain" (plan) | Phase 8 Autotrader; the whole platform is "a brain that needs memories" |

## 3. Documents and folders
| kind | form | example |
|---|---|---|
| status, history, how-to | ALL_CAPS.md, one job each | PROJECT_STATUS.md, CHANGELOG.md, OPERATIONS.md |
| generated reference | ALL_CAPS.md with "GENERATED" on line 1 | SCRIPTS_REFERENCE.md |
| registration | PREREG_<topic>_<date>.md; frozen rule FROZEN_<topic>_<date>.md; design DESIGN_<topic>_<date>.md | PREREG_round_number_2026-10-26.md |
| run output | results/<date>/<script>.out | results/2026-10-19/band_coverage.out |
| archive | docs/archive/<name>_<date>.md, never edited | SCRIPTS_monolith_2026-10-26.md |

One home per kind of information: live numbers in the database; history in CHANGELOG.md; the current state and the docket in PROJECT_STATUS.md; script interfaces in SCRIPTS_REFERENCE.md; how to run pipelines in OPERATIONS.md; tests and their rules in results/. SCRIPTS.md is retired (a stub).

## 4. Scripts, tables, flags, IDs
| thing | form | example |
|---|---|---|
| script | `<verb>_<object>.py`; a test ends in `_test`; run once, reproducible | build_ripple_timeline.py, fomc_drift_test.py |
| folder under scripts/ | the job or domain | card, ingestion, audit (not audits) |
| backup before a change | `<table>_backup_YYYYMMDD` (the revert path) | financial_metrics_backup_20261023 |
| frozen comparison copy | `<table>_snapshot_YYYYMMDD` | filing_ai_classifications_snapshot_20261014 |
| scratch table (new rule) | `scratch_<topic>_YYYYMMDD`, with its drop date written in the changelog | scratch_events_ratio_20261026 |
| ledger flag_key | `<object>_<what is tested>_<scope or window>` | event_premium_20d, fomc_announcement_day_market_move |
| changelog entry ID | date-sequence | 2026-10-26-12 |
| a registration's predictions | id, type, point, range, level, anchor (PRED-TABLE) | see results/TEMPLATE_PREREG.md |

## 5. Labels
A label's definition lives next to its name. The reaction label (rewarded, punished, muted, and the derived diverged_from_fundamentals) is defined as: **window** 20 trading days from the prior close through day +20; **baseline** the prior trading day's close (the event day's own move IS included); **benchmark** SPY; **thresholds** plus or minus 3%; diverged is a derived upgrade of rewarded or punished when firm state points the other way. The label is computed from the saved abnormal_return_20d and from nothing else, so a label and its column can never disagree. (As of 2026-10-26 they disagree for 15.3% of events: PROJECT_STATUS.md section 7, item 1.)