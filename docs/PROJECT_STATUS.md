# PROJECT STATUS (draft v0, 2026-10-26)

**What this file is.** The one place for the CURRENT state: what we have, what has been done (start to finish), what has been tested, what is left, what does not add up, and the calendar. History lives in CHANGELOG.md (entries cited as `CL <id>`), script interfaces in docs/SCRIPTS_REFERENCE.md (generated), how-to in docs/OPERATIONS.md, registrations in results/. Update this file at the end of every work session; never copy a live number here without its date.

**Source tags.** `[LIVE d]` = queried in the database on date d. `[CODE]` = read from the real source. `[DOC d: file]` = stated in a document dated d, NOT re-verified. `[PENDING]` = needs a query or a paste that has not happened yet. `[PROPOSED]` = my suggestion, not a decision.

---

## 1. What the project is

A historical market research platform that connects company financials, 8-K events, news, macro and government conditions, and stock-price reactions, to produce **calibrated historical probabilities with visible sample sizes**: explicitly not high-confidence prediction (Galen's frame: a "brain that needs memories"). Environment: GitHub repo stock-research1 (precedent-engine), Codespaces + Python, Supabase/Postgres. [DOC 2026-09-11: PROJECT_HANDOFF]

**Standing rules** (each learned from a documented mistake):
1. n of 30 to 50 before a tag or pattern counts; every finding shows its sample size.
2. Nothing auto-promotes from AI classification to the trusted layer; no bulk confirm or correction until the batch has been read.
3. Never guess or fabricate a UUID, CIK, ticker, or a script's interface: query it, or ask for the real file.
4. Abnormal returns against SPY are the base measure; every function that buckets and every function that saves a magnitude must use the SAME baseline (see section 7, item 1: the code appears to violate it; confirmation pending).
5. After any batch operation, verify with a real check; absence of an error proves nothing.
6. Pre-register tests before running them (results/TEMPLATE_PREREG.md; the pre-commit hook checks new ones); predictions carry an anchor label (DATA, LITERATURE or NONE) and a range; ranges with no anchor are wide.
7. The eight forward-test files are FROZEN until both verdicts are recorded (scripts/hooks/pre-commit blocks edits; `FROZEN_OK=1` only after the verdicts).
8. A seeded 30% of companies is SEALED for exploration (table explore_sealed_tickers); exploration creates no flag.
9. SQL given to Galen uses dollar-quoting (`$$text$$`); every long SQL goes through scripts/ops/lint_sql.py first; a multi-statement SQL run is one transaction.
10. Long jobs start with scripts/ops/bg.sh and are watched with scripts/ops/jobs.py; dependent steps chain with scripts/ops/wait_job.sh.
11. Be honest about uncertainty and sample size, including about our own findings; say so when something does not add up and dig.

---

## 2. Phase map and names (the same work has carried several names)

| work | PROJECT_PLAN (09-30) | README (10-08) | old SCRIPTS.md / notes | [PROPOSED] name from now on |
|---|---|---|---|---|
| raw data: prices, filings, financials | Phase 1 (~98%) | Phases 1-2 | onboarding pipeline | Phase 1 Data Foundation |
| financial analysis | Phase 2 (100%) | Phases 1-2 | financial_metrics gaps (closed 09-30 to 10-03) | Phase 2 Financial Analysis |
| 8-K events: classify, review, promote | Phase 3 (~85%) | Phase 3 | promote_events waves (10-03, 10-15) | Phase 3 Corporate Events |
| news, macro, government, global events | Phase 4 (~40%) | Phase 4 | FRED, GDELT, laws, EOs, FOMC, oil | Phase 4 External Conditions |
| price reaction engine | Phase 5 (~85%) | Phase 5 | reactions table, tags, pre-context ("Phase 5 complete" 10-09) | Phase 5 Reaction Engine |
| historical pattern evaluation harness (prediction contract D1-D4) | Phase 6 (~15%) | Phase 6 "Pattern Engine" | "Phase 6 kickoff" 10-13; D1, D2 built | Phase 6 Evaluation Harness |
| decomposition: market and sector, macro flags, own events, bands, day card, day map | (not in the plan) | (not in README) | "Phase 7 engine" (10-19 to 10-21) | the **Engine** (not a numbered phase) |
| synthesis: the day view with layered threads and a bottom-line panel; the five-factor attribution | (not in the plan; the design spec docs/phase6-factor-attribution-model.md calls it "Phase 6") | (not in README) | called "Phase 6" in the notes | Engine, day view (see section 6) |
| dashboard / website | Phase 7 (0%) | Phase 7+ | (not built) | Phase 7 Dashboard |
| autotrader ("the brain" in the plan) | Phase 8 (0%) | (not in README) | (not started) | Phase 8 Autotrader |

The plan's percentages date from 09-30 and are not updated for October. The rename is a PROPOSAL; the point is that "Phase 6" and "Phase 7" must each mean one thing.

---

## 3. What we have

### 3.1 Data: live vital signs
| item | value | source |
|---|---|---|
| events | **23,554**, event dates 1994-01-05 to 2026-09-11 (ingestion stopped there) | [LIVE 10-26] |
| events with a row in event_market_reactions_corrected | **15,897** (67.5%); the other 7,657 got reaction numbers from the live view as of 10-19 (22,513 of 23,348 view rows resolved) | [LIVE 10-26]; [CL 2026-10-19-01] |
| events with a reaction tag (rewarded / punished / muted / diverged) | **15,952** (67.7%); no event carries two reaction tags | [LIVE 10-26] |
| events with event_pre_context | **16,413** (69.7%) | [LIVE 10-26] |
| tickers | 498 plus SPY; **160 sealed** (explore_sealed_tickers); 275 explore-set tickers have events | [LIVE 10-26] |
| flag ledger | **112 flags**: 15 proven, 21 lead, 62 null, 2 retired, 12 untested | [LIVE 10-26] |
| untested flags (the 12) | cascade_effect; earnings_role_bands_forward_test; earnings_surprise_sign_operating_income_forward; flag_overlap_storm_testability; company_state_filing_dated; macro_other_series; fed_state; government_decisions_day_level; law_driven_charge_events_titles; law_named_charge_event_reaction; local_flags; news_sentiment_gdelt | [LIVE 10-26] |

**Every table with row counts and sizes:** `[PENDING]` (SQL query 1: table inventory). **Database size against the plan's host limit:** `[PENDING]` (the handoff said 801 MB against a 500 MB free cap and Anthropic credits exhausted on 09-11, with a plan to self-host; the notes since show work continued on Supabase, so this needs a current check).

**Numbers recorded in documents, not re-verified:** market_prices 3,365,653 rows [DOC 10-08: README]; sec_8k_filings 155,141 rows (138,608 .htm, 16,533 .txt), promoted_to_event unused [CL 2026-10-21-20]; ~150,539 filings classified [DOC 10-15: notes]; government_decisions 8,023 (6,422 enacted laws, 1,570 executive orders, 31 Fed rate changes) [DOC 10-16: notes]; government tagging v1: 3,035 relevant decisions, 2,992 usable, 12,149 tags [CL 2026-10-23-09]; CRS subjects for 2,176 laws [CL 2026-10-26-02]; event_ripple_timeline 653,815 rows [CL 2026-10-16-02]; company_sentiment_timeline complete for 141 months, 420-447 companies per month [CL 2026-10-21-15]; fomc_meetings 310 rows [results/fomc_calendar_validation.txt]; 81 macro series and 57,510 releases, 424 global events (167 reviewed) [DOC 10-08: README]; as-quoted price factors for 492 tickers, 479 valid from their first eligible close, 13 with recorded exclusions [CL 2026-10-26-06].

### 3.2 Code [LIVE 10-26, generated]
**266 files in 17 folders** (docs/SCRIPTS_REFERENCE.md lists every one with purpose, flags, and the tables it reads and writes): scripts/card 79, classification 30, models 29, ingestion 23, financial_pipeline 14, government_decisions 13, gdelt 12, macro 11, audits 10, sql 9, audit 8, onboarding 8, tagging 8, ops 6, ripple 4, review 1, shared 1.
Process tools: pre-commit hook (frozen files, new registrations), check_prereg.py, score_predictions.py, lint_sql.py, bg.sh, jobs.py, wait_job.sh, changelog_tools.py, build_scripts_reference.py, make_audit_pack.py, reaction_explorer.py, footing_simulation.py, audit_pattern_significance.py. Frozen: models/earnings_band_model.json, earnings_role_band_model.json, band_calibration.json; scripts/card/earnings_roles.py, earnings_role_band_test.py, day_card.py, earnings_surprise_test.py, earnings_forward_test.py. Git: first commit 2026-08-19; 463 commits at 10-26 (14 in August, 71 in September, 378 in October); safety tag `pre-cleanup-2026-10-26`.

### 3.3 Documents
| file | role | last commit | state |
|---|---|---|---|
| README.md | public summary | 2026-10-08 | **STALE**: 19,892 events; says to read SCRIPTS.md, which is now retired |
| PROJECT_PLAN.md | the eight-phase plan; Section 6 = the prediction contract and walk-forward harness (source of D1-D4) | 2026-09-30 | status table **STALE**; Section 6 is current |
| THEORY.md | findings log | 2026-10-05 | partly superseded (section 7, item 11) |
| CHANGELOG.md | dated history, newest first, stable IDs | 2026-10-26 | CURRENT (171 entries from the old SCRIPTS.md, verified line for line) |
| docs/OPERATIONS.md | pipeline order, gotchas (old Part 1 text of 09-29) | text of 2026-09-29 | may be stale; the generated reference wins |
| docs/SCRIPTS_REFERENCE.md | script interfaces | 2026-10-26 | CURRENT; regenerate, never edit |
| SCRIPTS.md | retirement stub with an old-label-to-ID table | 2026-10-26 | stub |
| docs/archive/SCRIPTS_monolith_2026-10-26.md | the original, untouched | 2026-10-26 | archive |
| docs/phase6-factor-attribution-model.md | five-factor design spec | 2026-09-17 | says "Not built"; the Engine built factors 1-3 (CL 2026-10-19-02) |
| docs/event-materiality-review.md | rubric for real events versus noise | 2026-09-29 | check against the notes of 10-22 |
| results/JANUARY_2027_RUNBOOK.md | the dated runbook (section 8) | 2026-10-26 | CURRENT |
| results/ANCHORS.md, results/TEMPLATE_PREREG.md | anchors and the registration template | 2026-10-26 | CURRENT |
| company_universe_tiers.html | tier file | last month | unknown |

### 3.4 The results folder [DOC: pack manifest 10-26]
79 text files kept; 46 run outputs (results/2026-10-19/*.out and .log) and 11 large CSVs skipped. Registrations: PREREG x8 (fomc day, drift, sector; government tag review; multi-event-day coverage; previously-announced walk-forward; as-quoted valid-from; round numbers) plus eo_trade_days_2025_2026.txt (a registration kept as a .txt), FROZEN x2 (role-band forward rule and addendum), DESIGN x1 (government tag validation), the runbook. Reading samples: the government tag review (10 part files, 250 decisions, plus manifest and attributes), classifier review sheets, 18 stock-day cards (JSON), 5 market day maps (JSON), FOMC calendar and validation, prediction_tally_2026-10-22.md (prediction_log.csv is an empty header).

---

## 4. What has been done, start to finish

Git history starts 2026-08-19; the days before the changelog's first entry are known only from the handoff and roadmap.

| date | what happened (entries) |
|---|---|
| to 09-11 | Phases 1-3 foundation: 489 securities onboarded, financials, raw 8-Ks, prices (Twelve Data limit about 8 requests a minute), AI classification pipeline (prompt v3), human review, reaction tagging; 180 tags mislabeled by a baseline mismatch and bulk-corrected; the ATM establishment-versus-completion finding; RLS and index fixes; handoff written. [DOC: HANDOFF 09-11, ROADMAP 09-18] |
| 09-11 | pattern_significance_tests populated (13 results) [CL 2026-09-11-01] |
| 09-22 to 09-29 | database audit, GDELT backfill, stale-URL sweep and price refresh, tagger fix; Track B news found active; auto-confirm threshold found documented wrong; dead-column scan [CL 2026-09-22-01 to 2026-09-29-06] |
| 09-30 | Phase 2 gaps closed (financial_metrics 842 to 78, bank revenue concept fix); sector-peer ripple and storm effect productionized; multi-entity reaction gap closed [CL 2026-09-30-01 to 11] |
| 10-02 to 10-03 | 367-ticker quarterly-revenue gap resolved; auto-confirm bands spot-checked (14 errors corrected); review backlog triaged (49,804 feared, 1,235 urgent); invalid-verdict bug; stale-URL sweep complete; promote_events created 3,139 events; duplicate-detection gap (67 corrected); nightly review cadence [CL 2026-10-02-01, 2026-10-03-01 to 24] |
| 10-08 | global_event_episodes retired; FRED sentiment, labor, housing series; consumer financial health index; 1,570 executive orders ingested [CL 2026-10-08-01 to 07] |
| 10-09 | 6,422 enacted laws; decision relevance classification; exposure threading; oil regime status; **Phase 5 complete** (diverged_from_fundamentals, company status); pre-Phase-6 audit [CL 2026-10-09-01 to 08] |
| 10-13 | **Phase 6 kickoff**: 4-way significance (6 of 13, later retracted), **D2 base rate**, Tier 4 tag-suggestion review cleared; theory tests (overreaction, size, context: null); plain-volatility range baseline [CL 2026-10-13-01 to 13] |
| 10-14 | magnitude lift found to be volatility; month-matched baseline (event premium small); volatility estimators; **range design frozen v1_6mo_recal**; first forward months; classifier rewrote rows (fixed); noise pool audited; prompt v6.x stopped [CL 2026-10-14-01 to 11] |
| 10-15 | premium replications; **promotion waves 1 and 2: events 19,892 to 23,554**; concurrent-process incident, 183 events removed [CL 2026-10-15-01 to 07] |
| 10-16 | out-of-time replication; event-time zoom-out (burst on days 0-1); macro-release lane; **flag ledger created**; ripple fill complete [CL 2026-10-16-01 to 06] |
| 10-19 to 10-20 | **event_market_reactions view repaired**; **the Engine**: chapter 1 (market and sector, R-squared 0.452), chapter 2 (macro flags: nothing earns a place), chapter 3 (own events: day width 1.6x proven; sign label a lead), band calibration; robust-scale and ex-jump tests (not adopted) [CL 2026-10-19-01 to 2026-10-20-06] |
| 10-21 | split and volume audits; earnings timing and role bands; group moves; **sentiment backfill complete (141 of 141 months)**; review queue; exhibit trial; guidance variance study [CL 2026-10-21-01 to 27] |
| 10-22 | re-classification test; consolidated notes 1-5: review backlog closed, ledger evidence backfilled, earnings forward tests frozen, T3a Fed change days and T3b executive-order days (null), prediction tally [CL 2026-10-22-01 to 08] |
| 10-23 | financial parser verified, free cash flow applied; year-to-date check; **FOMC calendar, FOMC day test (PASS), sector contrast (null), drift (replicated, then faded)**; government tagging v1 complete [CL 2026-10-23-01 to 11] |
| 10-26 | job visibility tooling; subject terms; **price foundation closed**; round-number tests (both null); anchors, template, hook; audit of the pattern-significance tests (0 of 13 survive); explorer; tags-versus-columns finding; this audit and the SCRIPTS.md retirement [CL 2026-10-26-01 to 18, and later entries] |

---

## 5. What has been tested

### 5.1 Ledger
**112 flags: 15 proven, 21 lead, 62 null, 2 retired, 12 untested** [LIVE 10-26]. The full list by status and family: `[PENDING]` (SQL query 2). Proven so far by the notes (not re-verified): event premium and burst on days 0-1; event types acquisition, leadership_change, strategic_partnership (burst) and capital_raise (no burst); event daily range coverage (shared multiplier 1.25); own-event day width 1.6x; earnings windows 2.72x / 2.47x; band edge calibration; FOMC announcement-day market move (1.140 / 1.112). [DOC: CL 2026-10-16-05, 2026-10-19-02, 2026-10-20-01, 2026-10-23-06]

### 5.2 Registered tests and verdicts
| test | registered | verdict | where |
|---|---|---|---|
| FOMC announcement day, market-wide | 10-23 | **PASS** (amplification 1.140 / 1.112; next day about 1.2) | PREREG_fomc_day_test; CL 2026-10-23-06 |
| FOMC sector contrast | 10-23 | NULL | PREREG_fomc_sector_test; CL 2026-10-23-07 |
| pre-FOMC drift | 10-23 | replicated 1994-2011 (about +0.449%), faded after | PREREG_fomc_drift_test; CL 2026-10-23-08 |
| multi-event-day coverage | 10-23 | could not run (under the 300-day minimum) | PREREG_multi_event_day_coverage |
| previously-announced walk-forward | 10-23 | **PASS** (k = 1.115) | PREREG_previously_announced_walkforward; CL 2026-10-23-04 |
| earnings surprise sign and role bands, forward | 10-22 | **FROZEN**; evaluate once after 2027-01-05 | FROZEN_role_band_forward_test; runbook step 7 |
| government tag review v1 | 10-23 | sample frozen; no verdicts yet (Galen's file untracked) | PREREG_government_tag_review_v1 |
| as-quoted levels valid-from | 10-26 | closed: 479 of 492 valid, 13 excluded | PREREG_asquoted_levels_valid_from; CL 2026-10-26-06 |
| round numbers: clustering; threshold move size | 10-26 | both **NULL** (clustering calibration failed; premium about 1%) | PREREG_round_number; CL 2026-10-26-09, -10 |
| T3a Fed change days; T3b executive-order days | 10-22 | did NOT pass (Fed Financials 1.065 / 1.038; executive-order days 0.967 / 0.977, 2025-26 orders 1.081) | results/prediction_tally_2026-10-22.md; CL 2026-10-22-07 |
| Phase 6 theory tests | 10-13 | direction, overreaction, size, context, time-to-threshold: null; magnitude lift was volatility; tag ranges no narrower than plain volatility | CL 2026-10-13-10 to 12 |

### 5.3 Corrections and retractions (so no one cites the old claim)
1. "6 of 13 tags significant" (and the earlier "2 of 13", "4 tags"): tested against an EVEN null; 0 of 13 survive against the overall reaction mix, even before multiple-testing adjustment [CL 2026-10-26-13, -15]. The old test calls 6.4 of 13 random groups significant.
2. "Events are calmer than random windows" (60.2% against 63.7%): compared tags with a column-style baseline; on the same measure 62.4% against 63.7% (1.3 points, about 1.6 SE) [CL 2026-10-26-17]. Withdrawn.
3. "Implied 55.7% for the sealed third": mixed two measures; withdrawn [CL 2026-10-26-17].
4. "D3 and D4 are not defined in any file": wrong; they are in PROJECT_PLAN.md Section 6 [CL 2026-10-26-18].
5. "Fatigue is answered by the compounding effect": withdrawn; fatigue is open.
6. "The labels measure the wrong horizon": withdrawn; they are a low-contrast filter for one horizon (about 1.4 points of the 20-day share is the whole event effect).
7. "No script writes event_market_reactions_corrected": wrong; tag_reaction_character.py writes it [CL 2026-10-19-01].

### 5.4 Prediction calibration
Oct 22 tally: 54 range predictions, **56% strictly inside** (target about 80%), 83% inside or within noise, 17% real misses; 7 probability calls [results/prediction_tally_2026-10-22.md]. Oct 26: the round-number priors missed by 5.6 and 17.6 SE (no anchor); the explorer's four calls were inside their wide ranges, one about 5 SE from its point. Ranges run too narrow where no anchor existed. `score_predictions.py` keeps the running tally for registrations made from the template.

---

## 6. What needs to be tested or done

**A. Gated by the frozen forward tests (after 2027-01-05):** runbook steps 0-15: backups, 8-K refresh, additive statements refresh, prices, caches, matrices, readiness, evaluate each forward test once, point-in-time repair of stored statement cells (only after both verdicts), card changes (multi-event note, previously-announced adjustment, FOMC lane), as-quoted refresh with the class C re-repair, backup cleanup, descriptive coverage analysis, anchor search session.

**B. Dated:** FOMC calendar refresh after the 2026-10-27/28 meeting; October sentiment top-up after 2026-10-31 (section 8).

**C. Evaluation harness (Phase 6, the plan's Section 6 contract):** D3 walk-forward split at tag level with a purge of overlapping 20-day windows, two dumb baselines (firm's unconditional drift; random events of the same broad type); D4 similarity-key hierarchy (event type, era, sector, firm state; surprise sign is unbuilt: needs analyst estimates); a matched baseline per tag; z-unit labels; the tag-window decision (section 7, item 1); the unprocessed events (item 2); fatigue test in magnitude terms; rerun the significance audit on corrected labels. Each registered from the template first.

**D. Engine (synthesis):** event sign labels from text meaning, relevance weights per thread, decay per event type, compounding rules (measure overlaps, never multiply), the hypothetical price and the gap analysis, bottom-line panel; the five-factor attribution factors 4 and 5 stay unbuilt until a registered test shows factors 1-3 add beyond own volatility. day_card.py, day_map.py and the decomposition exist (CL 2026-10-19-02, 2026-10-20-01).

**E. Registrations not yet written:** the forward tariff executive-order test (lead: 2025-26 day +1, t +3.98; 39 tariff days against 79 others); the pre-FOMC press-conference split (anchor ANCHORS#1, read the paper first); the government tag validation (verifier, counterfeit tags, calibration read) is PARKED behind the tariff test; Galen's own 30-decision read of the tag sample is not done.

**F. Data and universe:** 8-K predecessor-CIK gaps (DIS, LIN, CI, MDT, ETN, APA, VTRS, MRVL, BG, APO, PSKY); pre-2004 8-K coverage unreliable; survivorship scope (today's index members only); EA and AVB have no prices; HON level shift; as-quoted class B repair not built (8 tickers); stock_day_z ends 2026-07-31 and the script that builds it is unknown; mid and small cap pilot and delisted data (paid) are open.

**G. Housekeeping:** README, PROJECT_PLAN, THEORY refresh; retitle 5 or 6 changelog index titles; merge scripts/audits into scripts/audit and decide on scripts/card; untrack and git-ignore the three checkpoint files (find out who writes .populate_sectors_checkpoint first); replace the Project knowledge snapshot with this file; raise the Codespace idle timeout; run `git config core.hooksPath scripts/hooks` in any fresh clone; condense the notes.

---

## 7. Known inconsistencies and open questions

1. **Reaction tags versus columns (open, cause identified).** [CODE] `compute_abnormal_return` (sets the tag) bases its window on the first trading day on or after the event date, so it excludes the event day's own move; `compute_full_reaction` (writes the columns) bases on the PRIOR close, so it includes it. Standing rule 4 says they must agree; the Sept 11 fix bulk-corrected 180 tags but the code still differs. [LIVE 10-26] 1,636 of 10,703 explore-set events (15.3%) disagree; 36 have the wrong sign; of the 1,465 mismatches among muted, punished and rewarded tags, 71% are within 2 points of the threshold. The documents contradict each other (old SCRIPTS.md lines 349-351 versus the 10-19 note: "day 0 excluded"). `[PENDING]` confirmation by SQL (the day-0-excluded query). Decision needed: relabel to the prior-close convention (matches the columns and the ledger) or keep and rename the tags as post-event labels.
2. **The unprocessed third.** 7,657 events have no reaction row (they still resolve through the view), 7,602 no tag, 7,141 no pre-context [LIVE 10-26]. The recorded reasons (bundled 859, entity-less 320, thin price data 776) belong to the RIPPLE-timeline accounting of 10-16 [CL 2026-10-16-06], not to the reactions table, so no document explains the missing reaction rows; about 3,662 of them are the 10-15 promotion waves, which leaves about 3,995 older events (20% of the 19,892 that existed before the promotion) with no recorded reason.
3. **Phase naming** (section 2).
4. **Three status documents are stale** (README, PROJECT_PLAN, THEORY), and README points to the retired SCRIPTS.md.
5. **The same test counted three ways:** 2 of 13 (handoff, roadmap), 4 (changelog 09-11), 6 (10-13): all against even nulls; all superseded by 5.3 item 1.
6. **Folders:** scripts/audit and scripts/audits both exist; scripts/card holds 79 files (tests, frozen files, cards), but the hook names scripts/card paths, so it cannot move casually.
7. **Repo root:** three runtime checkpoint files are tracked; two GDELT scripts write them, the sectors one is unexplained.
8. **Changelog:** 15 entries have approximate dates (marked `~`); a few index titles are cosmetically wrong; the old notes held one duplicated paragraph (collapsed).
9. **Infrastructure plan versus reality:** the handoff planned to self-host Postgres and move to psycopg2; the notes show continued Supabase work and no migration. `[PENDING]` current database size and host.
10. **Prediction log:** results/prediction_log.csv is an empty header; the tally exists for 10-22 only.
11. **THEORY.md versus later results:** it lists the storm/compounding effect and sector-peer ripple as validated and COVID attribution as a first step; the Engine and ledger later found the event premium small and unstable, direction null, and the lift volatility. Reconcile before anyone cites it.
12. **Project knowledge** is a September snapshot without results/ or recent work.

---

## 8. Calendar

| date | what | source |
|---|---|---|
| 2026-10-27/28 | FOMC meeting; then run runbook 3c: build_fomc_calendar.py, read the validation, load_fomc_meetings.py --apply | runbook 3c |
| after 2026-10-31 (Mon 11-02) | October sentiment top-up: `backfill_gdelt_sentiment.py 2026-10 2026-10 --ignore-checkpoint` | runbook 8 |
| any time | anchor search session; first registration from the template (press-conference split or tariff test); live queries for the `[PENDING]` slots above | runbook 15 |
| 2027-01-04 | earliest the role-band forward test can read "matrices end" | runbook 5 |
| after 2027-01-05 | January runbook, run ONCE, steps 0-15; evaluate each forward test once; record verdicts on the ledger rows; THEN the point-in-time repair, the card changes (FROZEN_OK=1), the backup cleanup | runbook 0-15 |
| forward holdout | range product: events after 2026-07-31 scored at 1.18 x 1.25 x v64 against 80%; first readable verdict about 6 months after 2026-08-01 | [DOC 10-16: notes] |

---
*Draft v0. Slots marked `[PENDING]` fill from the three SQL queries (table inventory, ledger, day-0 test). Next revision: update this file at the end of the session and add a CHANGELOG entry.*