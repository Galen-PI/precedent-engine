# PROJECT STATUS (v1.3, 2026-10-29)

**What this file is.** The one place for the CURRENT state: what we have, what has been done (start to finish), what has been tested, what is left, what does not add up, and the calendar. History lives in CHANGELOG.md (entries cited as `CL <id>`), script interfaces in docs/SCRIPTS_REFERENCE.md (generated), how-to in docs/OPERATIONS.md, names and phase definitions in docs/NAMING.md, registrations in results/. Update this file at the end of every work session; never copy a live number here without its date.

**Source tags.** `[LIVE d]` = queried in the database on date d. `[CODE]` = read from the real source. `[DOC d: file]` = stated in a document dated d, NOT re-verified. `[PENDING]` = needs a query or a paste that has not happened yet. `[PROPOSED]` = a suggestion, not a decision.

---

## 1. What the project is

A historical market research platform that connects company financials, 8-K events, news, macro and government conditions, and stock-price reactions, to produce **calibrated historical probabilities with visible sample sizes**: explicitly not high-confidence prediction (Galen's frame: a "brain that needs memories"). Environment: GitHub repo stock-research1 (precedent-engine), Codespaces + Python, Supabase/Postgres. [DOC 2026-09-11: PROJECT_HANDOFF]

**Standing rules** (each learned from a documented mistake):
1. n of 30 to 50 before a tag or pattern counts; every finding shows its sample size AND its independent-cluster count (rule 12).
2. Nothing auto-promotes from AI classification to the trusted layer; no bulk confirm or correction until the batch has been read.
3. Never guess or fabricate a UUID, CIK, ticker, or a script's interface: query it, or ask for the real file.
4. Abnormal returns against SPY are the base measure; the label and the saved column use the SAME baseline (prior close, event-day move included). Resolved 2026-10-26: the tagger was fixed and every explore-set label now agrees with its column (0 mismatches on 2026-10-28). [CL 2026-10-26 entries; LIVE 10-28]
5. After any batch operation, verify with a real check; absence of an error proves nothing.
6. Pre-register tests before running them (results/TEMPLATE_PREREG.md; the pre-commit hook checks new ones); predictions carry an anchor label (DATA, LITERATURE or NONE) and a range.
7. The eight forward-test files are FROZEN until both verdicts are recorded (scripts/hooks/pre-commit; `FROZEN_OK=1` only after the verdicts).
8. A seeded 30% of companies is SEALED for exploration (table explore_sealed_tickers); exploration creates no flag.
9. SQL given to Galen uses dollar-quoting (`$$text$$`); every long SQL goes through scripts/ops/lint_sql.py first; the SQL editor shows at most 100 rows (exactly 100 means truncated).
10. Long jobs start with scripts/ops/bg.sh and are watched with scripts/ops/jobs.py (a killed or failed job stays under ATTENTION until `--ack NAME`); a Codespace stops about 30 minutes after the last terminal INPUT and kills its background jobs (log output does not count); one HTTP/2 connection allows 10,000 requests, so long database jobs run as restart wrappers.
11. Be honest about uncertainty and sample size, including about our own findings; say so when something does not add up and dig; every numeric call is recorded before it is checked and scored after.
12. **Effective sample size (adopted 2026-10-28).** Every Phase 6 result reports rows AND independent clusters (a company's events within 28 calendar days chain into one cluster); the n-of-30-to-50 rule applies to clusters. On 2026-10-28, 69.8% of analysis rows were independent clusters, a lower bound, within companies only; dependence across companies on the same date is not yet measured. [LIVE 10-28]
13. **Tests read the analysis set (adopted 2026-10-28).** Statistics use the view event_analysis_set (reaction row present, no `exclude` reason in event_exclusions; flags for sealed, under_review, has_note), never the raw reaction table; rows under review are read before use.
14. **Firm state is point-in-time only from about 2010.** The quarterly data are point-in-time from 2010-2011 on; earlier periods exist only as comparatives in later filings. Any firm-state key states its availability rule. The `diverged_from_fundamentals` tag is NOT a feature until its definition is settled (section 3.5).
15. **Corrections are visible.** Retired or moved material goes to CHANGELOG.md at its true date (docs/archive keeps the unedited original); documents keep only the current state.

---

## 2. Phase map

Phase names, questions and "done when" checks are defined in docs/NAMING.md (the source of truth). **Phase 4 is renamed "External Conditions" (decided 2026-10-28; news is one track beside macro, sentiment, government decisions, the Federal Reserve and global events).** Status is a check that can be run, not a percentage:

| phase | gate check | state 2026-10-28 |
|---|---|---|
| 1 Data Foundation | `[PENDING]` (G8) | unmeasured; known gaps: EA and AVB have no prices; 8-K predecessor-CIK gaps; pre-2004 8-K coverage unreliable; **ingestion is paused since 2026-10-22 by decision (history-first plan): the nightly classification schedule is disabled, 8-Ks after 2026-09-18 and prices after 2026-10-13 are not loaded, only the daily news job runs; the price refresh is a manual script** [LIVE 10-29] |
| 2 Financial Analysis | `[PENDING]` (G8) | unmeasured; quarterly data point-in-time only from about 2010 (section 3.5) |
| 3 Corporate Events | `[PENDING]` (G8) | unmeasured; 1,169 events (5.0%) have no source-filing link, 813 of them recorded in event_component_dates (section 3.5) |
| 4 External Conditions | `[PENDING]` (G8) | unmeasured; FOMC calendar loaded through the 2026-10-28 meeting (310 rows; one spurious 2003-09-15 row, section 7) [LIVE 10-28] |
| 5 Price Reaction Engine | the five-component gate, scripts/sql/phase5_gate.sql (G1) | **5 of 5 components PASS** [LIVE 10-29, on the final data]; no event awaits a review decision after G5; 21,915 events have a ripple timeline (954,685 rows) |
| 6 Historical Pattern Engine | the prediction contract (PROJECT_PLAN Section 6, D1 to D4) | **Gate A (section 6) comes first**; D1 and D2 built; D3 and D4 not built |
| 7 Dashboard / Website | not started | not started |
| 8 Autotrader | not started; gated on phase 6 | not started |

Old names to current names are in NAMING.md section 2 ("Phase 7 engine" is tracks 6D and 6E).

---

## 3. What we have

### 3.1 Data: live vital signs
| item | value | source |
|---|---|---|
| events | **23,554**, event dates 1994-01-05 to 2026-09-11 (ingestion stopped there) | [LIVE 10-26] |
| events with a reaction row (event_market_reactions_corrected) | **22,470** (95.4%) | [LIVE 10-28] |
| events with a reaction tag | **22,525**: 55 of them have no reaction row (recorded as `reaction_row_not_computable`) | [LIVE 10-28] |
| events without a reaction row | **1,084**, every one with a recorded reason: no price history 709, no listed company 286, no entity link 34, tag without a computable row 55 | [LIVE 10-28] |
| event_pre_context | **23,309** rows for 23,312 pairs (3 pairs appear twice with two relationship types); 0 pairs uncovered | [LIVE 10-28] |
| event_firm_state_pit | 23,348 rows (rule pit_v1; 39 extra rows because some entities own two securities: join on security_id) | [LIVE 10-28] |
| event_entity_reactions | 124 rows for the 49 multi-entity events | [LIVE 10-28] |
| event_exclusions | 1,527 `exclude` (no_price_history 709, bundle_duplicates_sibling_event 271, duplicate_of_promoted_event 236, rollup_no_source 235, date_gap_over_year 69, price_step_in_window 7); 0 `review`; 639 `note` (no_listed_company 286, no_source_curated 278, reaction_row_not_computable 37, no_entity_link 34, price_step_in_window 2, date_corrected_review 2); 2,166 rows | [LIVE 10-29] |
| event_analysis_set (view) | **21,670 rows** [LIVE 10-29]; the split into sealed, under review and with a note was 7,409 / 270 / 323 of 22,162 on 10-28 and is `[PENDING]` a re-measure | [LIVE 10-29] |
| explore set (non-sealed reaction-tagged) | 14,960 events: rewarded 3,921, punished 3,965, muted 5,444, diverged 1,630; label versus saved column: 0 mismatches | [LIVE 10-28] |
| tickers | 498 plus SPY; **160 sealed** (explore_sealed_tickers) | [LIVE 10-26] |
| flag ledger | **112 flags**: 15 proven, 21 lead, 62 null, 2 retired, 12 untested | [LIVE 10-26] |
| database | 151 tables and 32 views, about 3.0 GB (hand sum of the 20 largest, plus or minus 10%); about 61 tables are audit, backup, snapshot or scratch tables by name (about 190 MB) | [LIVE 10-26 inventory] |

**Tables created or changed 2026-10-28** (all additive; no tag was changed after the tagger finished): event_firm_state_pit, event_exclusions, event_analysis_set (view), scratch_diverged_new_20261028, scratch_diverged_v2_20261028, event_tags_backup_20261028 (full copy after the tagger finished), event_entity_reactions_backup_20261026 (122 rows). Scratch tables need a drop date recorded in the changelog. `[PENDING]` a fresh table inventory.

**Added 2026-10-28 evening** (CHANGELOG 2026-10-28-07 and -08): the view ripple_skip_events (1,291 events the ripple builder skips: 2 or more component rows, plus every `exclude` reason); backups fomc_meetings_backup_20261028 (310 rows) and event_ripple_timeline_backup_20261028 (8 events, 349 rows), BOTH to be dropped after 2026-11-28; 8 new event_exclusions review rows; ripple timeline 21,913 events and 954,599 rows (was 21,599 and 940,758); fomc_meetings 310 rows with the 2026-10-28 meeting confirmed; results/ripple_skips_2026-10-28.csv (323 skipped pairs: 286 no security for the entity, 37 no prior close, each with its reason; the 37 are unread). Database 3,160 MB, 157 tables and 33 views at the snapshot, 159 and 34 after the two backups and the view [LIVE 10-28].

**Added and changed 2026-10-29** (CHANGELOG 2026-10-29): backups flag_ledger_backup_20261029 (112 rows), event_exclusions_backup_20261029 (1,993 rows) and event_exclusions_backup_20261029b (2,184 rows), and the staging table event_source_links_added_20261029, which holds the 279 PLANNED source links, NOT links that were added (46 were linked; the other 233 collided with a filing that is already another event's source and became duplicate exclusions): all four to be dropped after 2026-11-28. event_source_filings gained 46 rows (its PRIMARY KEY is (ticker, filing_date, accession_number): one event per filing). event_exclusions: 271 bundles excluded as bundle_duplicates_sibling_event, 236 curated duplicates as duplicate_of_promoted_event, 2 narrative rollups and JCI (a price artifact); 45 stale no_source_curated notes removed; the review backlog is 0. event_tags: 17 reaction labels deleted and 16 rewritten by the tagger (13 of 13 plain labels reproduced exactly; four unsupported diverged labels gone, diverged 2,384 to 2,380; the Exelon event has none); event_market_reactions_corrected gained 16 rows (22,486); event_ripple_timeline gained 86 rows for P&G and Valero (21,915 events, 954,685 rows); the view ripple_skip_events now lists only events with an `exclude` reason (1,527). Database 3,163 MB, 163 tables and 34 views.

**Numbers recorded in documents, not re-verified:** market_prices 3,365,653 rows [DOC 10-08: README]; sec_8k_filings 155,141 rows [CL 2026-10-21-20]; about 150,539 filings classified [DOC 10-15]; government_decisions 8,023; government tagging v1: 3,035 relevant decisions, 12,149 tags [CL 2026-10-23-09]; event_ripple_timeline 653,815 rows at 10-16 [CL 2026-10-16-02]; company_sentiment_timeline complete for 141 months [CL 2026-10-21-15]; fomc_meetings 310 rows [results/fomc_calendar_validation.txt]; as-quoted price factors for 492 tickers, 479 valid, 13 excluded [CL 2026-10-26-06].

### 3.2 Code
**266 files in 17 folders** at 2026-10-26 (docs/SCRIPTS_REFERENCE.md lists every one; regenerate it, it does not yet include the files added since): scripts/card 79, classification 30, models 29, ingestion 23, financial_pipeline 14, government_decisions 13, gdelt 12, macro 11, audits 10 (merged into audit on 10-26), sql 9, audit 8, onboarding 8, tagging 8, ops 6, ripple 4, review 1, shared 1. [LIVE 10-26, generated]
Added since: scripts/audit/changelog_tools.py (split, add, check, retitle, checkpoint), build_scripts_reference.py, patch_tagger_baseline.py, check_tagger_convention.py (the regression check: recomputes a random sample of labels from prices; passes at 100 of 100 on 10-28), make_audit_pack.py, build_results_map.py, import_plan_addenda.py, patch_jobs_ack.py, repair_entity_reactions.py (tested on stand-in tables, NEVER run against the database); scripts/ops/jobs.py patched (commit 2c2b529). Frozen: models/earnings_band_model.json, earnings_role_band_model.json, band_calibration.json; scripts/card/earnings_roles.py, earnings_role_band_test.py, day_card.py, earnings_surprise_test.py, earnings_forward_test.py.

### 3.3 Documents
| file | role | state |
|---|---|---|
| README.md | public summary | **STALE** (2026-10-08): to be rewritten as a true snapshot, not a manual (decided 2026-10-28); original archived |
| PROJECT_PLAN.md | the eight-phase plan | **STALE** (2026-09-30): to be rewritten as the current plan with no status; its seven addenda are in CHANGELOG at their true dates; original archived |
| THEORY.md | findings log | **MISLEADING at the top** (lists the storm effect as validated; the ledger says lead): to be rewritten anchored to the ledger with a Retired section; original archived |
| CHANGELOG.md | dated history, newest first, stable IDs | CURRENT (oldest entry now 2026-09-08) |
| docs/NAMING.md | names, phases, "done when" checks | CURRENT; Phase 4 rename adopted |
| docs/OPERATIONS.md | pipeline order, gotchas | partly stale (text of 2026-09-29: tagger notes, script paths such as scripts/onboarding/onboard_pipeline.py) |
| docs/SCRIPTS_REFERENCE.md | script interfaces | generated; regenerate |
| docs/RESULTS_MAP.md | where every results file came from | generated 10-28 (130 files; 57 not named in any changelog entry) |
| docs/START_NEW_DAY.md | first file to read; the latest checkpoint | CURRENT |
| docs/archive/ | unedited originals: SCRIPTS monolith, session journal, README, PROJECT_PLAN, THEORY (pre-rewrite 2026-10-28) | committed |

### 3.4 The results folder
130 files [LIVE 10-28: docs/RESULTS_MAP.md]. Registrations: PREREG x8 (fomc day, drift, sector; government tag review; multi-event-day coverage; previously-announced walk-forward; as-quoted valid-from; round numbers), FROZEN x2, DESIGN x1, the runbook. Reading samples, 18 stock-day cards, 5 market day maps, FOMC calendar and validation, the prediction tally of 10-22.

### 3.5 Known limits of the data (measured 2026-10-28; none yet changes a ledger verdict)
1. **Events without a source-filing link: 1,169 (5.0%).** [LIVE 10-29] 813 have their filings recorded in a different table, event_component_dates (a real accession number each, all found in sec_8k_filings): 575 multi-filing summaries (excluded, except P&G's and Valero's, which were read and kept) and 238 curated events (236 duplicate an event the pipeline had already promoted from the same 8-K and are excluded; J&J's rollup is excluded; Prologis-Duke Realty, with a 95-day filing gap, remains a note). 46 other curated events were linked to their filings on 10-29. The other 356 have no filing recorded anywhere, mostly events without a reaction row. The events table has no origin column.
2. **Price series.** A scan of one-day changes beyond 1.6x or below 0.4x found 17 days (non-sealed): over-adjusted upward steps (KLAC 2014-11-26 x2.368; HPQ 2015-11-02 x1.747), unadjusted raw drops at spin-offs and special dividends (MO 2008, ROK 2001, KDP 2018; JCI 2007 not placed), a Sunday row (CVS 2009-07-26), early-data oddities (HUBB and TSCO 1994) and moves that may be real. Nine reaction rows have a window containing one (6 excluded, 3 under review). **The scan is blind below 60%**: smaller artifacts are unmeasured (G4). Extremes: of 14,962 non-sealed rows, 64 beyond 50%, 15 beyond 80%, 4 beyond 150%; adjusted and raw returns are identical in all 64; most are real crisis rebounds.
3. **709 events have no price history** (617 predate the first price of the company's CURRENT ticker: predecessor tickers such as EXE, DAL, HWM, GM, HCA, CHTR, CPAY, EG; 92 belong to securities with no prices at all). Permanent exclusions.
4. **Quarterly financials are point-in-time only from about 2010.** filed_date is retroactive for periods ending 2006-2009 (median lag 1,517, 787, 403 and 387 days for 2006, 2007, 2008, 2009; 50.8% over 100 days in 2009; 2010 mixed at 20.9%; from 2011 the median is 31 to 37 days and under 6% over 100). 514 quarterly rows were filed 8 to 19 days after period end (unchecked). A capped availability date (LEAST of filed_date and period_end + 90 days) is the proposed repair.
5. **Firm-state labels drifted.** The stored labels (computed 2026-09-01 to 09-28) differ from today's scores for 34% of a 194-row sample (about 27 to 41%): 65 of 66 are the same company-quarter scoring differently; 98.5% of the differing rows have the free-cash-flow term today against 36% of unchanged rows, consistent with the 2026-10-23 cash-flow fill (a correlation). The composite score is a per-row mean of up to four quarter-over-quarter changes, each counted only between -5 and +5. 3,404 new listed-company rows have no firm state (financials start about 2009).
6. **The `diverged` tag is unstable.** Of the 1,636 existing non-sealed diverged tags: 84.5% survive today's scores with the old quarter-end rule (staleness costs about 15 points); 64.9% survive the point-in-time rule (look-ahead costs about 20 more); 53 untagged events would become diverged. A v2 rule would remove 838 tags and add 2,067 (1,127 old events, 940 new), a 52% larger set of which only 42.7% was diverged before. 42% of the new-event proposals used a quarter that ended fewer than 45 days earlier. The pattern-significance audit found no signal in any tag. NO tag was written.
7. **Independence.** 69.8% of 14,753 analysis rows (non-sealed, exclusions removed) are independent clusters within their company; 574 rows share the previous row's date. Cross-company dependence on the same date is unmeasured.
8. **Multi-entity events** (49, all with entity rows) include dual-class share pairs (FOX and FOXA trade at a nearly constant ratio, so their returns agree to four decimals): near-duplicates, not independent cases.

---

## 4. What has been done, start to finish

Git history starts 2026-08-19; the days before the changelog's first entry are known only from the handoff and roadmap.

| date | what happened (entries) |
|---|---|
| to 09-11 | Phases 1-3 foundation: 489 securities onboarded, financials, raw 8-Ks, prices, AI classification pipeline, human review, reaction tagging; 180 tags mislabeled by a baseline mismatch and bulk-corrected; handoff written. [DOC] |
| 09-11 to 09-30 | pattern_significance_tests; database audit, GDELT backfill, stale-URL sweep and price refresh; Phase 2 gaps closed; sector-peer ripple and storm effect; multi-entity reaction gap closed [CL 2026-09-11-01 to 2026-09-30-11] |
| 10-02 to 10-09 | 367-ticker revenue gap; auto-confirm bands spot-checked; promote_events created 3,139 events; global_event_episodes retired; FRED series, 1,570 executive orders, 6,422 laws; **Phase 5 complete** by the old definition [CL 2026-10-02-01 to 2026-10-09-08] |
| 10-13 to 10-16 | **Phase 6 kickoff**: significance (6 of 13, later retracted), D2 base rate, theory tests null; range design frozen; promotion waves (events 19,892 to 23,554); out-of-time replication; macro-release lane; **flag ledger created**; ripple fill complete [CL 2026-10-13-01 to 2026-10-16-06] |
| 10-19 to 10-23 | event_market_reactions view repaired; **the Engine** (chapters 1-3, band calibration); sentiment backfill complete; earnings role bands; consolidated notes; FOMC calendar and day test (PASS); government tagging v1 [CL 2026-10-19-01 to 2026-10-23-11] |
| 10-26 | job tooling; price foundation closed; round-number tests (null); anchors, template, hook; significance audit (0 of 13 survive); **tagger convention bug found and fixed** (15.3% of labels disagreed with their columns); **reaction labels relabeled** (2,435 changes, 70 cases read, 0 mismatches after); SCRIPTS.md retired into CHANGELOG, NAMING and checkpoint protocol [CL 2026-10-26-01 to later] |
| 10-28 | **live tagger finished** (7,279 events: 6,570 tagged, 709 skipped; 5 restarts); **pre-context finished** (6,821 new rows); jobs.py patched; seven plan addenda moved into CHANGELOG at their true dates; firm-state drift measured; **data-quality audit** (section 3.5); point-in-time table, exclusions table, analysis-set view; Phase 5 gate written; no tag changed [CL 2026-10-28 checkpoints] |

---

## 5. What has been tested

### 5.1 Ledger
**112 flags: 15 proven, 21 lead, 62 null, 2 retired, 12 untested** [LIVE 10-26]. Untested: cascade_effect; earnings_role_bands_forward_test; earnings_surprise_sign_operating_income_forward; flag_overlap_storm_testability; company_state_filing_dated; macro_other_series; fed_state; government_decisions_day_level; law_driven_charge_events_titles; law_named_charge_event_reaction; local_flags; news_sentiment_gdelt. Proven (by the notes, not re-verified): event premium and burst on days 0-1; event types acquisition, leadership_change, strategic_partnership (burst) and capital_raise (no burst); event daily range coverage; own-event day width 1.6x; earnings windows; band edge calibration; FOMC announcement-day market move. **Exposure of the type-linked proven flags to the excluded events (2026-10-28): acquisition 3.7%, leadership_change 4.3%, capital_raise 6.4%, strategic_partnership 3.2% of events (4.3% overall; 1.4% of reaction rows). Exposure is not dependence: the proven flags have NOT yet been rerun on the analysis set (G7).**

### 5.2 Registered tests and verdicts
| test | registered | verdict | where |
|---|---|---|---|
| FOMC announcement day, market-wide | 10-23 | **PASS** (1.140 / 1.112) | PREREG_fomc_day_test; CL 2026-10-23-06 |
| FOMC sector contrast | 10-23 | NULL | PREREG_fomc_sector_test |
| pre-FOMC drift | 10-23 | replicated 1994-2011, faded after | PREREG_fomc_drift_test |
| multi-event-day coverage | 10-23 | could not run (under the 300-day minimum) | PREREG_multi_event_day_coverage |
| previously-announced walk-forward | 10-23 | **PASS** (k = 1.115) | PREREG_previously_announced_walkforward |
| earnings surprise sign and role bands, forward | 10-22 | **FROZEN**; evaluate once after 2027-01-05 | FROZEN_role_band_forward_test |
| government tag review v1 | 10-23 | sample frozen; no verdicts yet | PREREG_government_tag_review_v1 |
| as-quoted levels valid-from | 10-26 | closed: 479 of 492 valid, 13 excluded | PREREG_asquoted_levels_valid_from |
| round numbers: clustering; threshold move size | 10-26 | both NULL | PREREG_round_number |
| T3a Fed change days; T3b executive-order days | 10-22 | did not pass | results/prediction_tally_2026-10-22.md |
| Phase 6 theory tests | 10-13 | direction, overreaction, size, context, time-to-threshold: null | CL 2026-10-13-10 to 12 |

### 5.3 Corrections and retractions (so no one cites the old claim)
1. "6 of 13 tags significant" (and "2 of 13", "4 tags"): tested against an EVEN null; 0 of 13 survive against the overall reaction mix [CL 2026-10-26-13, -15]. **Rerun on the corrected labels is pending.**
2. "Events are calmer than random windows" (60.2% against 63.7%) and "implied 55.7% for the sealed third": withdrawn [CL 2026-10-26-17].
3. "D3 and D4 are not defined in any file": wrong; they are in PROJECT_PLAN Section 6 [CL 2026-10-26-18]. "Fatigue is answered by the compounding effect" and "the labels measure the wrong horizon": withdrawn.
4. "No script writes event_market_reactions_corrected": wrong; tag_reaction_character.py writes it [CL 2026-10-19-01].
5. **"Reaction tags agree with their columns" was false for 15.3% of explore-set events until 2026-10-26** (the tagger measured from the event-day close). Fixed and relabeled; 0 mismatches since.
6. **"Every event traces to its source filing" is false for 1,215 events (5.2%) on 10-28 and 1,169 on 10-29** (README, 2026-10-08, and earlier handoffs). See section 3.5.
7. **"The stored firm states are point-in-time" is false**: they use the latest quarter that ENDED before the event (42% of the proposed new tags used a quarter ended fewer than 45 days earlier), and the quarterly filing dates are retroactive before about 2010.
8. **"The diverged tag is a stable property of an event" is not supported** (section 3.5 item 6).

### 5.4 Prediction calibration
Oct 22 tally: 54 range predictions, **56% strictly inside** (target about 80%), 83% inside or within noise, 17% real misses; 7 probability calls [results/prediction_tally_2026-10-22.md]. Oct 26: the round-number priors missed by 5.6 and 17.6 SE (no anchor). Ranges run too narrow where no anchor existed. During the 2026-10-28 audit the working calls (a point or range and a confidence, scored afterwards) were informal; the misses worth keeping: the origin column of events, the count of unsourced events, the survival rates of the point-in-time rule and the number of proposed `diverged` additions.

---

## 6. What needs to be done

### 6.1 The Phase 6 gate list (decided 2026-10-28: thoroughness first; each item has a pass/fail test)
**Gate A: before any Phase 6 statistic is trusted**
| | item | state |
|---|---|---|
| G1 | Phase 5 gate as a runnable check | **DONE 10-28**: scripts/sql/phase5_gate.sql, 5 of 5 PASS. The first run read 319 gaps at component 5 (the earlier 31 counted a provenance note as a reason); the causes are fixed in the ripple builder (CHANGELOG 2026-10-28-08); the review backlog was closed by G5 on 10-29 and the gate re-passed on the final data |
| G2 | analysis-set view (event_analysis_set) | **DONE 10-28** (22,162 rows then; 21,670 on 10-29) |
| G3 | independence audit and the effective-n rule | **DONE 10-28** (69.8% independent, rule 12); cross-company same-date dependence still unmeasured (MacKinlay anchor) |
| G4 | systematic price-artifact detection below the 60% scan (spin-offs, special dividends, splits): peer-relative and event-free large moves, the adjustment-factor table, review, record in event_exclusions | open |
| G7 | rerun the 15 proven flags and the significance audit on the analysis set; record in the ledger evidence (rerun on the corrected data: 314 ripple events were added 10-28 and 508 events left the analysis set 10-29; re-measure independence, which was 69.8% on 10-28; 3 of the 15 only say a type uses the pooled number) | open |

**Gate B: before claims go in writing**
| | item | state |
|---|---|---|
| G5 | review groups: the 333 review events, the 514 fast quarterly filings, provenance and duplicates of the curated events | **DONE 10-29.** 8 multi-row bundles and 263 corrected-date bundles (each repeats a real sibling's return) and 236 curated duplicates of promoted events (same 8-K) were excluded, plus 2 narrative rollups and JCI (a 2007 price artifact); HIG and LVS (real violent moves) and P&G and Valero (single occurrences) were kept as notes; 36 boundary events (spin-offs, IPOs, emergences) are explained notes; 17 stale tags were recomputed (13 of 13 plain labels reproduced exactly) and 16 now have reaction rows; the 514 fast filings are genuine early filers (513 match a real filing on the same day); 46 curated events were linked to their filings |
| G6 | firm state done right: rebuild the point-in-time table with a capped availability date, report by era and number of terms, store the raw score, then decide the fate of `diverged` (no tag is written before the definition is settled; backup event_tags_backup_20261028 exists). **New 10-29:** sec_filings holds the real 10-Q filing date for each quarterly row, and the stored filed_date is retroactive for periods ending 2008 to 2010 (a real 10-Q more than 30 days earlier exists for 358 of 638 rows in 2008, 435 of 1,119 in 2009, 217 of 1,342 in 2010): a join can move the usable point-in-time state from about 2011 back to about 2008; 2006 and 2007 (181 rows) have no filing record and keep the cap; Q4 rows were not tested against 10-Ks | open |
| G8 | Phase 1 to 4 gate checks from NAMING.md as pass/fail SQL | open |
| G9 | documents: this file (v1.1), README, PROJECT_PLAN v2 and THEORY v2 (ledger-anchored, with a Retired section) done 10-28; OPERATIONS refresh and the SCRIPTS_REFERENCE regeneration open | in progress |
| G10 | housekeeping (section 6.4), anytime | open |

Phase 6 DESIGN (the D3 registration: a walk-forward split purging overlapping 20-day windows, purge window 28 days from G3) can be drafted now; running it waits for Gate A.

### 6.2 Gated by the frozen forward tests (after 2027-01-05)
Runbook steps 0-15: backups, 8-K refresh, additive statements refresh, prices, caches, matrices, readiness, evaluate each forward test once, point-in-time repair of stored statement cells (only after both verdicts; fold in G6), card changes, as-quoted refresh with the class C re-repair, backup cleanup (including the scratch and backup tables of 10-26 and 10-28), descriptive coverage analysis, anchor search session.

### 6.3 Phase 6 and Engine work after the gate
D3 walk-forward split at tag level; D4 similarity-key hierarchy (event type, era, sector, firm state; surprise sign needs analyst estimates and is unbuilt; firm state waits for G6); a matched baseline per tag; z-unit labels; fatigue test in magnitude terms. (The unprocessed events are now fully accounted for.) Engine: event sign labels from text meaning, relevance weights, decay, compounding by measuring overlaps; the five-factor attribution factors 4 and 5 stay unbuilt until a registered test shows factors 1-3 add beyond own volatility. Registrations not yet written: the forward tariff executive-order test (lead t +3.98), the pre-FOMC press-conference split; the government tag validation is PARKED behind the tariff test; Galen's own 30-decision read of the tag sample is not done.

### 6.4 Data, universe and housekeeping
8-K predecessor-CIK gaps (DIS, LIN, CI, MDT, ETN, APA, VTRS, MRVL, BG, APO, PSKY); survivorship scope (today's index members only); EA and AVB have no prices; HON level shift; as-quoted class B repair not built (8 tickers); stock_day_z ends 2026-07-31 and the script that builds it is unknown. Housekeeping: retitle changelog index titles; decide on scripts/card; untrack the three checkpoint files in the repo root (find out who writes .populate_sectors_checkpoint); drop dates for the scratch tables; replace the Project knowledge snapshot (PROJECT_HANDOFF and SCRIPTS from September) with START_NEW_DAY.md and this file; run `git config core.hooksPath scripts/hooks` in any fresh clone; add the 100-row editor cap and the progress-line convention (a script prints `PROGRESS done/total` lines so the monitor draws a bar) to OPERATIONS.

---

## 7. Known inconsistencies and open questions

**Resolved since v0:** tags versus columns (fixed 10-26); the unprocessed third (accounted for 10-28: every event is measured or has a recorded reason); phase naming (NAMING.md and the Phase 4 decision).
1. **Resolved 10-28 and 10-29:** the ripple gap (319 events, CHANGELOG 2026-10-28-08), the whole review backlog (G5) and the source-filing gap (section 3.5). **Open items:** (a) the FOMC calendar holds one spurious row, the meeting of 2003-09-15 (the Fed's schedule has eight meetings, September's on the 16th); no finished test counted it; the fix belongs in build_fomc_calendar.py; (b) the ledger repair of 2026-10-29 fixed five of the ten stale rows (THEORY section 8 lists the five that remain, none urgent); (c) ADBE's 10-Q for the quarter ended 2026-05-29 has no row in sec_filings; (d) the independence figure (69.8%) predates 508 exclusions and must be re-measured (G7).
2. **Documents:** README, PROJECT_PLAN and THEORY were rewritten 10-28 (the README held-and-not-held section was corrected against the ledger the same day). OPERATIONS is partly stale (its "known bug" note on multi-entity tagging predates the fix); SCRIPTS_REFERENCE does not list files added since 10-26.
3. **The data limits of section 3.5**, especially the point-in-time and `diverged` findings.
4. **The same test counted three ways** (2, 4 and 6 of 13 tags): all superseded by 5.3 item 1.
5. **Folders:** scripts/card holds 79 files but the hook names scripts/card paths, so it cannot move casually.
6. **Repo root:** three runtime checkpoint files are tracked; two GDELT scripts write them, the sectors one is unexplained.
7. **Changelog:** 15 entries have approximate dates (marked `~`); a few index titles are cosmetically wrong; the plan addenda carry the label PROJECT_PLAN and the date each was first committed.
8. **Infrastructure:** the handoff planned to self-host Postgres; work continued on Supabase. Database 3,163 MB on Supabase, 163 tables and 34 views on 2026-10-29 [LIVE]; the host and plan are not recorded here.
9. **Prediction log:** results/prediction_log.csv is an empty header; the tally exists for 10-22 only.
10. **Project knowledge** is a September snapshot without results/ or recent work.
11. **Monitor:** a job without a status record keeps the old 24-hour rule (only jobs with a status record stay under ATTENTION until acknowledged).

---

## 8. Calendar

| date | what | source |
|---|---|---|
| 2026-10-28 | **DONE:** FOMC calendar rebuilt after the 18:00 UTC statement, 2026-10-28 added to the independent list, loaded with --apply (310 rows; 1 row changed) | CHANGELOG 2026-10-28-07 |
| after 2026-11-28 | drop the scratch and backup tables: fomc_meetings_backup_20261028, event_ripple_timeline_backup_20261028, flag_ledger_backup_20261029, event_exclusions_backup_20261029, event_exclusions_backup_20261029b, event_source_links_added_20261029, scratch_diverged_new_20261028, scratch_diverged_v2_20261028 (G10) | CHANGELOG |
| before 2027-01-05 | the forward-test windows need ingestion resumed: 8-K item 2.02 filings dated 2026-10-14 to 2026-12-31 and prices after 2026-10-13 (the frozen file was written BEFORE either was loaded). ANSWERED 10-29 (results/JANUARY_2027_RUNBOOK.md was read): step 1 imports the 8-Ks (import_8k_filings.py), step 3 refreshes prices (refresh_market_prices.py --all --apply), steps 4 and 5 rebuild the caches and matrices, and the forward tests are evaluated only at step 7 | results/FROZEN_role_band_forward_test_2026-10-22.md |
| after 2026-10-31 (Mon 11-02) | October sentiment top-up: `backfill_gdelt_sentiment.py 2026-10 2026-10 --ignore-checkpoint` | runbook 8 |
| any time | anchor search session; first registration from the template (D3 walk-forward, the press-conference split or the tariff test) | runbook 15 |
| 2027-01-04 | earliest the role-band forward test can read "matrices end" | runbook 5 |
| after 2027-01-05 | January runbook, run ONCE, steps 0-15; evaluate each forward test once; record verdicts on the ledger rows; THEN the point-in-time repair, the card changes (FROZEN_OK=1), the backup cleanup | runbook 0-15 |
| forward holdout | range product: events after 2026-07-31 scored against 80%; first readable verdict about 6 months after 2026-08-01 | [DOC 10-16] |

---
*v1.3, 2026-10-29. Update at the end of every session and add a CHANGELOG entry. Next revision: fill the `[PENDING]` slots (table inventory, Phase 1-4 gate checks, the analysis-set split), then G6 (the sec_filings join), G7 and G4.*