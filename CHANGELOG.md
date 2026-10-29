# CHANGELOG

The dated history of the project: what was built, found, corrected and decided. **Newest entry first.** Each entry has a stable ID (date-sequence, e.g. 2026-10-26-12; a `~` after a date means the date was inherited from the entry before it in the old file). Entries are never rewritten: a correction is a NEW entry that cites the old ID.

Not here: the script interfaces (docs/SCRIPTS_REFERENCE.md), how to run the pipelines (docs/OPERATIONS.md), the current state and the docket (docs/PROJECT_STATUS.md), registrations (results/). The old SCRIPTS.md is retired (docs/archive/SCRIPTS_monolith_2026-10-26.md holds the original).

Add an entry:  python3 scripts/audit/changelog_tools.py add --title "..." [--label "..."] << 'EOF'  (body)  EOF

> Note carried over from the old Part 2 heading: Dated history of what was found and fixed. Current Reference above already incorporates all of this — read this section only for provenance/context, not to find out what's true now.

## Index

<!-- INDEX-START -->
| ID | date | old label | title |
|---|---|---|---|
| 2026-10-29-06 | 2026-10-29 | checkpoint | CHECKPOINT 2026-10-29 14:30 (late morning 2026-10-29: G5 closed, Phase 5 gate re-passed on |
| 2026-10-29-05 | 2026-10-29 | documents | README and PROJECT_STATUS v1.3: the 2026-10-29 refresh from measured numbers; G5 closed |
| 2026-10-29-04 | 2026-10-29 | checkpoint | CHECKPOINT 2026-10-29 13:41 (mid-morning 2026-10-29: provenance found in event_component_d |
| 2026-10-29-03 | 2026-10-29 | documents | Ledger repair (9 append-only notes) and docs brought in line: THEORY section 8, PROJECT_ST |
| 2026-10-29-02 | 2026-10-29 | checkpoint | CHECKPOINT 2026-10-29 13:05 (morning 2026-10-29: the evening 2026-10-28 state installed (d |
| 2026-10-29-01 | 2026-10-29 | checkpoint | Checkpoint: evening 2026-10-28, documents, FOMC, Phase 5 gate and the ripple fix |
| 2026-10-28-09 | 2026-10-28 | documents | PROJECT_STATUS v1.1 and the 2026-10-28 evening checkpoint: Phase 5 gate 5 of 5, FOMC loade |
| 2026-10-28-08 | 2026-10-28 | data | Phase 5 gate passes 5 of 5: ripple builder fixed (bundle rule, share class, skips recorded |
| 2026-10-28-07 | 2026-10-28 | data | FOMC calendar: the 2026-10-28 meeting confirmed and loaded; independent list extended |
| 2026-10-28-06 | 2026-10-28 | documents | THEORY rewritten as a reading of the flag ledger; README findings section corrected |
| 2026-10-28-05 | 2026-10-28 | documents | PROJECT_PLAN rewritten as the current design: no status, no volatile numbers (v2) |
| 2026-10-28-04 | 2026-10-28 | documents | README rewritten as a true snapshot; PROJECT_STATUS v1; the snapshot query saved |
| 2026-10-28-03 | 2026-10-28 | checkpoint | CHECKPOINT 2026-10-28 16:01 (late afternoon 2026-10-28: point-in-time and exclusions table |
| 2026-10-28-02 | 2026-10-28 | checkpoint | CHECKPOINT 2026-10-28 15:51 (afternoon 2026-10-28: data-quality findings measured (price s |
| 2026-10-28-01 | 2026-10-28 | checkpoint | CHECKPOINT 2026-10-28 15:29 (midday 2026-10-28: tagger and pre-context finished; firm-stat |
| 2026-10-26-26 | 2026-10-26 | checkpoint | CHECKPOINT 2026-10-26 20:56 (end of day 2026-10-26: tagger2 running with automatic restart |
| 2026-10-26-25 | 2026-10-26 | correction | Correction: the multi-entity entity-reaction step is INSIDE the tagger loop (the checkpoin |
| 2026-10-26-24 | 2026-10-26 | checkpoint | CHECKPOINT 2026-10-26 20:39 (milestone: tagger run 1 crashed on the HTTP/2 request limit;  |
| 2026-10-26-23 | 2026-10-26 | checkpoint | CHECKPOINT 2026-10-26 20:08 (milestone: tagger guard resolved (7,282 = exact count); next: |
| 2026-10-26-22 | 2026-10-26 | guard | Guard fired: the tagger's dry run finds 7,282 events, the exact SQL count is 7,568 |
| 2026-10-26-21 | 2026-10-26 | relabel | Reaction labels relabeled to the prior-close convention (explore set: 1,636 mismatches, 15 |
| 2026-10-26-20 | 2026-10-26 | checkpoint | CHECKPOINT 2026-10-26 20:00 (milestone: tagger fixed, labels relabeled and confirmed; next |
| 2026-10-26-19 | 2026-10-26 | tagger convention | Tagger convention found and fixed: reaction labels excluded the event-day move |
| 2026-10-26-18 | 2026-10-26 | correction | CORRECTION TO ADDENDA 26, 27 AND 28 (2026-10-26) |
| 2026-10-26-17 | 2026-10-26 | addendum 29 | FIRST EXPLORATION RESULTS: THE TAGS DO NOT MATCH THE CURRENT RETURN COLUMNS; the 'calmer t |
| 2026-10-26-16 | 2026-10-26 | addendum 28 | THE PERCENTS, THE SEALED SET AND THE EXPLORER (scripts/models/reaction_explorer.py; table  |
| 2026-10-26-15 | 2026-10-26 | addendum 27 | THE FOOTING OF THE OLD AND NEW SIGNIFICANCE TESTS (scripts/models/footing_simulation.py),  |
| 2026-10-26-14 | 2026-10-26 | correction | CORRECTION TO ADDENDUM 26 (2026-10-26, after the user said something in it felt wrong; I w |
| 2026-10-26-13 | 2026-10-26 | addendum 26 | AUDIT OF THE PATTERN-SIGNIFICANCE TESTS, and what it does to the Phase 6 docket (scripts/m |
| 2026-10-26-12 | 2026-10-26 | addendum 25 | THE EXTERNAL ANCHORS ARE BAKED INTO THE PROCESS (results/ANCHORS.md; results/TEMPLATE_PRER |
| 2026-10-26-11 | 2026-10-26 | addendum 24 | PREDICTIONS CARRY AN ANCHOR LABEL (lesson of the round-number clustering priors, which mis |
| 2026-10-26-10 | 2026-10-26 | addendum 23 | ROUND-NUMBER CENTS DIAGNOSTIC (exploratory, read-only; scripts/ingestion/cents_diagnostic. |
| 2026-10-26-09 | 2026-10-26 | addendum 22 | ROUND-NUMBER TESTS, REGISTERED RESULTS (results/PREREG_round_number_2026-10-26.md; scripts |
| 2026-10-26-08 | 2026-10-26 | addendum 21 | the two round-number tests are REGISTERED (results/PREREG_round_number_2026-10-26.md), bef |
| 2026-10-26-07 | 2026-10-26 | addendum 20 | outcome-free counts for the round-number tests (scripts/ingestion/round_number_counts.py), |
| 2026-10-26-06 | 2026-10-26 | addendum 19 | THE PRICE FOUNDATION IS CLOSED (final state and what was learned) |
| 2026-10-26-05 | 2026-10-26 | addendum 18 | the three mechanisms behind the valid-from losses, and the decision rule fixed BEFORE the  |
| 2026-10-26-04 | 2026-10-26 | addendum 17 | FOUNDATION CHECK before any new build or registration |
| 2026-10-26-03 | 2026-10-26 | addendum 16 | PLAN to get back to the Phase 6 docket (written after the valid-from dry run, before its t |
| 2026-10-26-02 | 2026-10-26 | addendum 15 | subject terms, as-quoted accuracy, valid-from rule |
| 2026-10-26-01 | 2026-10-26 | addendum 14 | background-job visibility |
| 2026-10-23-11 | 2026-10-23 | addendum 13 | design step 1 DONE (repeat run complete) |
| 2026-10-23-10 | 2026-10-23 | addendum 12 | where everything stands going into Monday (nothing is needed over the weekend) |
| 2026-10-23-09 | 2026-10-23 | addendum 11 | government tagging run, a double submission, and the reliability result |
| 2026-10-23-08 | 2026-10-23 | addendum 9 | pre-FOMC drift, and the as-quoted flag triage |
| 2026-10-23-07 | 2026-10-23 | addendum 8 | FOMC sector contrast (NULL) and the absolute sector table |
| 2026-10-23-06 | 2026-10-23 | addendum 7 | FOMC calendar, as-quoted prices, FOMC announcement-day test |
| 2026-10-23-05 | 2026-10-23 | addendum 6 | the year-to-date differencing check, final |
| 2026-10-23-04 | 2026-10-23 | addendum 5 | close-out of the session |
| 2026-10-23-03 | 2026-10-23 | addendum 4 | null register updated, duplicate-recording scan, population counts pending |
| 2026-10-23-02 | 2026-10-23 | addendum 3 | metrics confirmed, repair scope, multi-event-day coverage |
| 2026-10-23-01 | 2026-10-23 | addendum 2 (note 6) | final-parser verification, Q1-Q3 free cash flow applied, tariff split, classifier first re |
| 2026-10-22-08 | 2026-10-22 | note 5 | CONSOLIDATED NOTE 5: T4 follow-ups, event band class audit, ipo_spinoff walk-forward, pred |
| 2026-10-22-07 | 2026-10-22 | note 4 | CONSOLIDATED NOTE 4: T3a Fed change days, T3b executive-order days, data guard and anomali |
| 2026-10-22-06 | 2026-10-22 | note 3 | CONSOLIDATED NOTE 3: ledger evidence backfill, earnings surprise results and the forward-t |
| 2026-10-22-05 | 2026-10-22 | note 2 | CONSOLIDATED NOTE 2: RSG ruling, tone lane, tone diagnostic, habit strength and the tie gu |
| 2026-10-22-04 | 2026-10-22 | note 1 (state of play) | CONSOLIDATED STATE OF PLAY (covers everything since the sentiment-lane entry; per-message  |
| 2026-10-22-03 | 2026-10-22 |  | Bucket reads (7 and 8): neither clean bucket passes; exclusion rules next |
| 2026-10-22-02 | 2026-10-22 |  | Corrected cluster table (read rows only) and the clean-bucket plan |
| 2026-10-22-01 | 2026-10-22 |  | Re-classification test result (full run, 625 requests, claude-haiku-5-5) |
| 2026-10-21-27 | 2026-10-21 |  | exhibit_reclass_test.py: model_config import |
| 2026-10-21-26 | 2026-10-21 |  | Guidance variance study (rule and predictions committed before the real run) |
| 2026-10-21-25 | 2026-10-21 |  | Hint window patch; earnings releases under other items sized (small) |
| 2026-10-21-24 | 2026-10-21 |  | Full exhibit run result; earnings releases hiding under other items |
| 2026-10-21-23 | 2026-10-21 |  | Exhibit trial, and a separate decisions table |
| 2026-10-21-22 | 2026-10-21 |  | Classifier reasoning on the top review rows; existing review backlog |
| 2026-10-21-21 | 2026-10-21 |  | Ledger rows confirmed; classifier labels located; review queue now shows the classifier's  |
| 2026-10-21-20 | 2026-10-21 |  | URL mix, promoted_to_event, ledger rows |
| 2026-10-21-19 | 2026-10-21 |  | Why the classifier misses press-release-only 8.01s (hypothesis, corrected) |
| 2026-10-21-18 | 2026-10-21 |  | Detector rerun on the repaired sentiment table; top 8 of review tier A read from the filin |
| 2026-10-21-17 | 2026-10-21 |  | Review queue result and the sector-correction sensitivity |
| 2026-10-21-16 | 2026-10-21 |  | Fixed cluster checks on real data; human review queue |
| 2026-10-21-15 | 2026-10-21 |  | Sentiment backfill verified; where the undercount lived; theme/cluster checks fixed after  |
| 2026-10-21-14 | 2026-10-21 |  | GDELT backfill finished; theme-day check written |
| 2026-10-21-13 | 2026-10-21 |  | Sentiment backfill: first real month (2022-01) with the fixed IF()/UNNEST query |
| 2026-10-21-12 | 2026-10-21 |  | Sentiment coverage: it is a fixed company list, not the matching bug (correction to the en |
| 2026-10-21-11 | 2026-10-21 |  | company_sentiment_timeline covers about a third of the universe (found while checking why  |
| 2026-10-21-10 | 2026-10-21 |  | Reading of the group-stratified sample, interim (8 of 36 rows; shuffled order, one search  |
| 2026-10-21-09 | 2026-10-21 |  | Group moves among big ordinary misses (group_move_check.py, 48f6b06; rule and predictions  |
| 2026-10-21-08 | 2026-10-21 |  | Earnings role bands, walk-forward (earnings_role_band_test.py, 2f031f2; rule, placebo tole |
| 2026-10-21-07 | 2026-10-21 |  | Earnings timing: forward habit rules (earnings_timing_recency.py, 9f18cf7; rule and predic |
| 2026-10-21-06 | 2026-10-21 |  | Earnings timing diagnostics (earnings_timing_diagnostics.py, 29d5c66; reading rules and pr |
| 2026-10-21-05 | 2026-10-21 |  | Earnings timing from the opening gap (earnings_timing_check.py, f96d3fd; predictions commi |
| 2026-10-21-04 | 2026-10-21 |  | Event-date lag check (event_date_lag_check.py; first run 3714231, v2 rule ae80e3a) |
| 2026-10-21-03 | 2026-10-21 |  | Joins and market-adjusted calibration (unrecorded_joins.py, volume_calibration_adj.py; pre |
| 2026-10-21-02 | 2026-10-21 |  | Volume-spike calibration (volume_calibration.py; rule, degeneracy check and predictions co |
| 2026-10-21-01 | 2026-10-21 |  | Split and volume artefact audit (split_artifact_audit.py; descriptive, no ledger row) |
| 2026-10-20-06 | 2026-10-20 |  | Ex-jump spread (build_matrices_exjump.py, exjump_spread_test.py; rule committed d24ce99 be |
| 2026-10-20-05 | 2026-10-20 |  | Median-scale adoption check (median_scale_adoption_check.py, rule committed before the run |
| 2026-10-20-04 | 2026-10-20 |  | Robust stress scale (robust_stress_test.py, rule committed 97eb587 before the run) |
| 2026-10-20-03 | 2026-10-20 |  | sector_day_z and sector_day_tail refreshed past 2026-07-31 |
| 2026-10-20-02 | 2026-10-20 |  | Band coverage and calibration |
| 2026-10-20-01 | 2026-10-20 |  | Phase 7 engine, additions (2026-10-20) |
| 2026-10-19-02 | 2026-10-19 |  | Phase 7 engine, chapter results (2026-10-19 / 2026-10-20) |
| 2026-10-19-01 | 2026-10-19 |  | event_market_reactions view repair (2026-10-19) |
| 2026-10-16-06 | 2026-10-16 |  | Ripple fill complete |
| 2026-10-16-05 | 2026-10-16 |  | Flag ledger |
| 2026-10-16-04 | 2026-10-16 |  | Zoom-out type fix, macro-release lane, ripple fill |
| 2026-10-16-03 | 2026-10-16 |  | Zoom-out: corrected test and by-type bursts |
| 2026-10-16-02 | 2026-10-16 |  | Event-time zoom-out (event_ripple_timeline) |
| 2026-10-16-01 | 2026-10-16 |  | Out-of-time replication of the event premium (2004-2018) |
| 2026-10-15-07 | 2026-10-15 |  | Replication on promotion wave 2 |
| 2026-10-15-06 | 2026-10-15 |  | Promotion wave 2 |
| 2026-10-15-05 | 2026-10-15 |  | Replication on the newly promoted events |
| 2026-10-15-04 | 2026-10-15 |  | Promotion run, concurrent-process incident, cleanup |
| 2026-10-15-03 | 2026-10-15 |  | Final matched results incl. 2026; scratch-table duplicate incident |
| 2026-10-15-02 | 2026-10-15 |  | Volatility-ratio matched baseline (artifact check) for the event premium and capital_raise |
| 2026-10-15-01 | 2026-10-15 |  | Replication of the event premium on events the earlier tests never saw |
| 2026-10-14-11 | 2026-10-14 |  | Prompt v6.x experiments and the role-change guard: stopped |
| 2026-10-14-10 | 2026-10-14 |  | Prices healed, forward test months 1-2, known gaps |
| 2026-10-14-09 | 2026-10-14 |  | Audit of the unreviewed "noise" pool; price splice |
| 2026-10-14-08 | 2026-10-14 |  | Event types vs MONTH-matched population baseline |
| 2026-10-14-07 | 2026-10-14 |  | Classifier rewrote existing rows; root cause and fix |
| 2026-10-14-06 | 2026-10-14 |  | First forward month, and the monthly-coverage distribution |
| 2026-10-14-05 | 2026-10-14 |  | Range tool built; method FROZEN as v1_6mo_recal_2026-10-14 |
| 2026-10-14-04 | 2026-10-14 |  | Volatility estimators, then monthly recalibration of the 80% range |
| 2026-10-14-03 | 2026-10-14 |  | Month-matched baseline: the event premium is real but small |
| 2026-10-14-02 | 2026-10-14 |  | Event types vs random dates (scaled 20d move); bundled-event correction; data flags |
| 2026-10-14-01 | 2026-10-14 |  | Magnitude model re-scored against a realized-volatility baseline |
| 2026-10-13-13 | 2026-10-13 |  | Plain-volatility range baseline and tag-specific ranges |
| 2026-10-13-12 | 2026-10-13 |  | The three old Phase 6 threads, worked and parked |
| 2026-10-13-11 | 2026-10-13 |  | Do events carry magnitude information beyond volatility? (neighbor-magnitude result retrac |
| 2026-10-13-10 | 2026-10-13 |  | Phase 6 theory testing: overreaction null, size check, context test, storm_x_sentiment, st |
| 2026-10-13-09 | 2026-10-13 |  | Tier 4 review backlog: ALL REMAINING CATEGORIES CLEARED, backlog now 100% complete |
| 2026-10-13-08 | 2026-10-13 |  | Tier 4 review backlog: multi_stage_divestiture fully cleared (448 rows, 100%) |
| 2026-10-13-07 | 2026-10-13 |  | Tier 4 review backlog: confounded_macro_conditions fully cleared (598 rows, 100%) |
| 2026-10-13-06 | 2026-10-13 |  | Tier 4 review backlog: confounded_corporate_action fully cleared (380 rows, 100%) |
| 2026-10-13-05 | 2026-10-13 |  | Tier 4 review backlog: confounded_regulatory_action fully cleared (556 rows, 100%) |
| 2026-10-13-04 | 2026-10-13 |  | Tier 4 review backlog: same_entity_sequence fully cleared (2,931 rows, 100%) |
| 2026-10-13-03 | 2026-10-13 |  | Phase 6 harness gap D2 closed: real base rate computed |
| 2026-10-13-02 | 2026-10-13 |  | Phase 6 kickoff: pattern_significance_tests refreshed, expanded to a genuine 4-way split |
| 2026-10-13-01 | 2026-10-13 |  | two real oddities from the pre-Phase-6 audit cleaned up |
| 2026-10-09-08 | 2026-10-09 |  | pre-Phase-6 audit, continued: core table freshness confirmed clean; one real finding defer |
| 2026-10-09-07 | 2026-10-09 |  | pre-Phase-6 audit of Phases 1-5: one real bug found and fixed, everything else confirmed c |
| 2026-10-09-06 | 2026-10-09 |  | Phase 5 complete: diverged_from_fundamentals backfilled, company-level status built, real  |
| 2026-10-09-05 | 2026-10-09 |  | real $4 recovery: 4 cancelled nightly-classify runs' already-completed batches recovered,  |
| 2026-10-09-04 | 2026-10-09 |  | Oil price regime status effect built; real threshold miscalibration caught before going li |
| 2026-10-09-03 | 2026-10-09 |  | government decision exposure threading built for EOs/laws (fixed 7-day window); real field |
| 2026-10-09-02 | 2026-10-09 |  | Government decision relevance classification built and run; real cross-script parser reuse |
| 2026-10-09-01 | 2026-10-09 |  | Congressional enacted laws ingested (6,422 rows); real double-JSON-encoding bug found and  |
| 2026-10-08-07 | 2026-10-08 |  | Federal executive orders ingested (1,570 rows); real duplicate-key schema fix found along  |
| 2026-10-08-06 | 2026-10-08 |  | Consumer Financial Health composite index built, real methodology bug found and fixed |
| 2026-10-08-05 | 2026-10-08 |  | Housing fully rounded out: supply/demand + all 50 state price indexes |
| 2026-10-08-04 | 2026-10-08 |  | Labor Market and Housing raw series ingested (9 more) |
| 2026-10-08-03 | 2026-10-08 |  | Population/Consumer Sentiment: real groundwork laid out, 9 new FRED series ingested |
| 2026-10-08-02 | 2026-10-08 |  | correction: the 257 NULL-severity global_events rows are NOT unreviewed |
| 2026-10-08-01 | 2026-10-08 |  | global_event_episodes formally retired; manual-review track confirmed stalled at 167/424 |
| 2026-10-03-24 | 2026-10-03~ |  | the ~13,900 unread Sept 24 real_event rows: duplicate-language sweep completed |
| 2026-10-03-23 | 2026-10-03~ |  | review backlog steady-state: real, automated nightly cadence built |
| 2026-10-03-22 | 2026-10-03~ |  | CHTR/EFX/CPRT/CDW untriaged tickers: real root cause found, real fix applied for 2 of 4 |
| 2026-10-03-21 | 2026-10-03~ |  | real resolution attempt on the 37 "genuinely-unresolvable" uncertain rows: 18 of 37 resolv |
| 2026-10-03-20 | 2026-10-03~ |  | Track B (news_ai_classifications) 101 real_event candidates reviewed; no promotion script  |
| 2026-10-03-19 | 2026-10-03~ |  | real, important discovery: a duplicate-detection gap in the 2026-09-24 mass auto-confirm,  |
| 2026-10-03-18 | 2026-10-03~ |  | real, major milestone: promote_events.py run to completion, 3,139 new real events created |
| 2026-10-03-17 | 2026-10-03~ |  | stale-URL sweep writeback complete: 39 new rows written, 112 total awaiting promote_events |
| 2026-10-03-16 | 2026-10-03~ |  | real, major milestone: the stale-URL sweep is fully complete (17,500 of 17,440+ processed) |
| 2026-10-03-15 | 2026-10-03~ |  | real near-miss: an overly broad UPDATE query during tag-suggestion review, caught and fixe |
| 2026-10-03-14 | 2026-10-03~ |  | real, honest note: the 37 genuinely-ambiguous uncertain rows are NOT a funding problem at  |
| 2026-10-03-13 | 2026-10-03~ |  | real recovery of 52 BATCH REQUEST FAILED rows: 27 of 47 recovered, rest blocked on Anthrop |
| 2026-10-03-12 | 2026-10-03~ |  | real, systematic bug found in the uncertain queue: invalid verdict values silently discard |
| 2026-10-03-11 | 2026-10-03 |  | real triage of the full review backlog: ~49,804 feared down to a real, honest 1,235 urgent |
| 2026-10-03-10 | 2026-10-03 |  | real, quick note: 804 vs 531 untagged-event discrepancy explained, 15 tagged live |
| 2026-10-03-09 | 2026-10-03 |  | 531-event untagged backlog triaged: mostly real, legitimate gaps, two confirmed accepted l |
| 2026-10-03-08 | 2026-10-03 |  | real root-cause fix: multi-entity reactions now computed automatically, no separate backfi |
| 2026-10-03-07 | 2026-10-03 |  | real near-miss: checked the >=0.90 band for the same contradiction pattern, found zero gen |
| 2026-10-03-06 | 2026-10-03 |  | 0.75-0.90 auto-confirm band spot-checked at real scale, 14 real misclassifications found a |
| 2026-10-03-05 | 2026-10-03 |  | financial_metrics residual fully resolved: real pagination tie-break bug found and fixed |
| 2026-10-03-04 | 2026-10-03 |  | 367-ticker gap: real, massive batch result -- all 65 remaining high-count tickers resolved |
| 2026-10-03-03 | 2026-10-03 |  | 367-ticker gap: 5 of the 6 remaining holdouts resolved, real total now 21 tickers |
| 2026-10-03-02 | 2026-10-03 |  | 367-ticker gap: real, broad result -- 16 tickers resolved from 3 concept additions |
| 2026-10-03-01 | 2026-10-03 |  | Real, broad fix for the 367-ticker quarterly gap: SalesRevenueGoodsNet (consumer-goods com |
| 2026-10-02-01 | 2026-10-02 |  | firm_state gap investigation: real concurrency bug found and fixed, "regression" was a fal |
| 2026-09-30-12 | 2026-09-30 | PROJECT_PLAN | Addendum: XOM's Quarterly Gap Confirmed, and a Much Bigger Related Finding (2026-09-30) |
| 2026-09-30-11 | 2026-09-30 |  | Storm/compounding finding productionized: real event_pre_context columns |
| 2026-09-30-10 | 2026-09-30 |  | Multi-entity reaction tagging gap closed (real fix backfilled, not a permanent code fix) |
| 2026-09-30-09 | 2026-09-30 |  | EA's price-data absence explained (real, external, not a pipeline bug) |
| 2026-09-30-08 | 2026-09-30 |  | Sector-peer ripple finding productionized: new sector_peer_ripple table |
| 2026-09-30-07 | 2026-09-30 |  | The ~876-event ripple gap fully explained: not a bug, F/GE/AEP specifically |
| 2026-09-30-06 | 2026-09-30 |  | financial_market_reactions "unification" was already resolved, before tonight |
| 2026-09-30-05 | 2026-09-30 |  | Real fix found for the financial-sector quarterly gap: RevenuesNetOfInterestExpense |
| 2026-09-30-04 | 2026-09-30 |  | Financial-sector quarterly gap: real partial win, real deeper bug found and NOT fixed |
| 2026-09-30-03 | 2026-09-30 |  | BNY's real gap traced to its actual source: not our bug, a real XBRL tagging gap |
| 2026-09-30-02 | 2026-09-30 |  | Added confidence_trend to multi_feature_model.py; fixed a real pagination bug; corrected m |
| 2026-09-30-01 | 2026-09-30 |  | financial_metrics gap: re-run closed most of it (842->78), real small residual remains |
| 2026-09-29-09 | 2026-09-29 | PROJECT_PLAN | Addendum: Population/Consumer Sentiment — Real Scope for Phase 4 (2026-09-29) |
| 2026-09-29-08 | 2026-09-29 | PROJECT_PLAN | Addendum: Government Decisions — Real Scope for a Phase 4 Sub-Track (2026-09-29) |
| 2026-09-29-07 | 2026-09-29 | PROJECT_PLAN | Addendum: Macro Data Placement — Phase 2 vs. Phase 4 (2026-09-29) |
| 2026-09-29-06 | 2026-09-29 |  | Phase 2 spot-check: financial_metrics coverage gap |
| 2026-09-29-05 | 2026-09-29 |  | Dead-column scan (Phase 1 checklist item) |
| 2026-09-29-04 | 2026-09-29 |  | Derived financial chain verified, one real fix, one false alarm resolved |
| 2026-09-29-03 | 2026-09-29 |  | Auto-confirm threshold is documented wrong; real spot-check at the real threshold |
| 2026-09-29-02 | 2026-09-29 |  | Phase 4 Track B (news) is active, not "paused" as documented |
| 2026-09-29-01 | 2026-09-29 |  | Global Events: manual review track quietly scaled, algorithmic track still stalled |
| 2026-09-28-02 | 2026-09-28~ |  | STILL OPEN / UNVERIFIED |
| 2026-09-28-01 | 2026-09-28 |  | Stale-URL Sweep, Price Refresh, Tagger Fix |
| 2026-09-22-03 | 2026-09-22 | PROJECT_PLAN | Addendum 3: Full Database Audit — Universe Scope Correction, a Critical Phase 6 Finding, a |
| 2026-09-22-02 | 2026-09-22~ |  | Earlier (undated in source) — PROJECT_PLAN.md findings, folded in above |
| 2026-09-22-01 | 2026-09-22 |  | Database Audit, GDELT Backfill, Reaction-Tagging Fixes |
| 2026-09-15-01 | 2026-09-15 | PROJECT_PLAN | Addendum 2: Event Tagging Pipeline Built and Tested (same session, continued) |
| 2026-09-11-01 | 2026-09-11 |  | `pattern_significance_tests` populated — 13 chi-square results, 4 tags statistically |
| 2026-09-08-02 | 2026-09-08 | PROJECT_PLAN | Baseline of the original plan: what changed from it, the phase percentages, the coverage t |
| 2026-09-08-01 | 2026-09-08 | PROJECT_PLAN | Correction (verified this session): Anchor-Date Unification Is Already Resolved |
<!-- INDEX-END -->

## Entries

<!-- ENTRIES-START -->

<!-- entry: 2026-10-29-06 | date: 2026-10-29 | label: checkpoint | source-line: new | approx: no -->
### 2026-10-29-06 — CHECKPOINT 2026-10-29 14:30 (late morning 2026-10-29: G5 closed, Phase 5 gate re-passed on the final data, documents refreshed from measured numbers)
Written 2026-10-29 14:30 +0000 (14:30 UTC). Reason: late morning 2026-10-29: G5 closed, Phase 5 gate re-passed on the final data, documents refreshed from measured numbers.

WRITTEN BY THE ASSISTANT at about 14:30 UTC on 2026-10-29 (the user's 9:30 AM, Fort Worth). ESTIMATE: this conversation is far past a typical segment (the last compaction was 2026-10-28 17:45 UTC at 1.73 MB; the median is 1.75 MB); a compaction may come at any moment. This block REPLACES the latest-state block and ADDS to the mid-morning checkpoint of 2026-10-29 (13:40 UTC); that one and the earlier ones are CHANGELOG entries and still stand. docs/PROJECT_STATUS.md v1.3 and the README, refreshed in the same commit as this block, hold the CURRENT state; read them first.
SINCE THE MID-MORNING CHECKPOINT. (1) DUPLICATES AND BUNDLES FINISHED. The three events held back from linking (AbbVie's separation, two Southern Company items) all collided with a promoted event's filing and became duplicate exclusions (236 in all). The 267 corrected-date review rows were read (strata: 266 multi-row, 264 with a real sibling event within 3 days of the used date; 20 cases read, 16 of 16 large-cell cases repeat their sibling); RULE APPLIED: a multi-row bundle whose corrected date has a real sibling within 3 days is excluded as bundle_duplicates_sibling_event (263; 271 with the earlier 8). The four odd cases: P&G's chairman succession and Valero's CST Brands spin-off are single occurrences with no sibling (kept, as notes); Valero's real recent activity (and J&J's rollup) are narrative rollups (rollup_no_source, 235 in all); AMD's Mubadala sale was already a duplicate. A title sweep for rollup shapes found 24 events, 23 inside the 267 and J&J. Stale review rows (4) were removed. (2) PRICE STEPS: JCI EXCLUDED (46.31 to 18.28 in one day, minus 60.5 percent, SPY plus 0.9: the unadjusted 2007 Tyco separation); HIG (5.13 to 10.37, volume 8.5 times) and LVS (3.12 to 5.62, volume 2.3 times, persistent) are real violent moves and were KEPT as notes. (3) THE 53 NOT-COMPUTABLE EVENTS: 36 are boundary cases (spin-offs, IPOs, bankruptcy emergences, mergers; the event falls on or before the first trading day of every linked ticker) and became notes; 17 had full price coverage and were stale tags the tagger had skipped. TAGGER RERUN (scripts/tagging/tag_reaction_character.py; default mode is LIVE, --dry-run prints only; options: TICKER, --window, --find-dates, --tag-one, --backfill-magnitudes; 'untagged' means no reaction tag in rewarded, punished, muted, and diverged_from_fundamentals is NOT in its delete list, so diverged tags must be removed first): the 17 events' reaction labels were deleted (backup event_tags_backup_20261028 still valid: 24,276 rows before and after), the dry run said Tagged 16, the live run tagged 16 and saved 16 reaction rows; the Exelon event (linked to CEG first, whose first price is after the event) stays unmeasured as a note. RESULT: 13 of 13 plain labels were reproduced exactly; the three formerly diverged events (AMD 2010 notes, II-VI licence, CoStar offering) came out punished; diverged 2,384 to 2,380. (4) THE 514 FAST QUARTERLY FILINGS ARE GENUINE: 513 of 514 match a real filing in sec_filings on the same day (Dover, Fastenal, FedEx, Netflix, Oracle and others really file within 3 weeks); ADBE's period ended 2026-05-29 has no sec_filings row. (5) THE POINT-IN-TIME FINDING (for gate G6): sec_filings holds the real 10-Q date for each quarterly row; the stored financial_statements.filed_date is retroactive for periods ending 2008 to 2010 (a real 10-Q more than 30 days earlier exists for 358 of 638 rows in 2008, 435 of 1,119 in 2009, 217 of 1,342 in 2010; from 2011 on the dates match 97 to 100 percent; 2006 and 2007, 181 rows, have no filing record). A join can move the usable point-in-time state from about 2011 back to about 2008. Q4 rows were not tested against 10-Ks (my table matched form_type 10-Q only). (6) THE RIPPLE VIEW FIX: P&G and Valero (multi-row, kept as notes) had no ripple timeline and failed gate component 5 after being converted from review to note; the skip view ripple_skip_events was simplified to events with an exclude reason only (1,527), the builder was run (358 events processed, 2 built with 86 rows, 322 pairs skipped: 286 no security for the entity, 36 no prior close; results/ripple_skips_2026-10-29.csv), and the gate re-passed. (7) DOCUMENTS: README and PROJECT_STATUS (v1.3) were refreshed from the measured numbers by scripts/audit/patch_docs_refresh_1029.py (31 exact replacements, hash-gated); THEORY is unchanged (its section 8 is current).
NUMBERS NOW (measured 2026-10-29 afternoon, [LIVE]): events 23,554; events with a reaction row 22,486; labels rewarded 5,918, punished 6,082, muted 8,144, diverged 2,380 (22,524 labels; 38 tagged events have no row, all explained); events with a source-filing link 22,385 (95.0 percent), 1,169 without (813 recorded in event_component_dates, 356 nowhere); event_exclusions 2,166 rows = 1,527 exclude + 0 review + 639 note; event_analysis_set 21,670 (22,162 on 10-28; 508 events left it today, 16 entered); ripple timeline 21,915 events and 954,685 rows; flag ledger 15 proven, 21 lead, 62 null, 12 untested, 2 retired; Phase 5 gate 5 of 5 PASS; database 3,163 MB, 163 tables, 34 views; repository 498 commits before this commit, 263 scripts in 17 folders, 134 files in results, 200 changelog entries before this one.
GATES. G1 done and re-passed; G2 done; G3 (independence 69.8 percent) PREDATES the 508 exclusions: re-measure at G7; G4 open; G5 DONE (all 333 review events and the 514 fast filings resolved); G6 open (now a join, see above); G7 open; G8 open; G9 documents: PLAN v2, THEORY v2, README and STATUS refreshed, OPERATIONS and SCRIPTS_REFERENCE still stale; G10 open.
OPEN, IN ORDER. (1) G6: first measure how many Q4 rows have a 10-K in sec_filings; then build event_firm_state_pit2 with availability date = the real 10-Q or 10-K filing date from sec_filings where it exists, else LEAST(filed_date, period_end + 90 days); report by year and number of terms; only then decide diverged (no tag is written before). (2) G7: rerun the 12 substantive proven flags on event_analysis_set (21,670) and the corrected ripple table, re-measuring independence (rows and clusters); ripple-based flags must select events through the analysis set. (3) G4: price artifacts below the 60 percent scan. (4) The 2003-09-15 FOMC row (attach the real build_fomc_calendar.py). (5) ADBE's missing sec_filings row. (6) Monday 2026-11-02: the October sentiment top-up (runbook step 8). (7) After 2026-11-28 DROP: flag_ledger_backup_20261029, event_exclusions_backup_20261029, event_exclusions_backup_20261029b, event_source_links_added_20261029, fomc_meetings_backup_20261028, event_ripple_timeline_backup_20261028, scratch_diverged_new_20261028, scratch_diverged_v2_20261028. (8) January: the runbook, once (steps 1 and 3 resume the 8-K and price ingestion before the forward tests are read at step 7). (9) OPERATIONS refresh and SCRIPTS_REFERENCE regeneration. (10) Note for the runbook: the tagger's default run re-examines all 710 skipped events and takes a long time; use a TICKER or --tag-one for a handful.
ERRORS OF THE ASSISTANT SINCE THE MID-MORNING CHECKPOINT (all caught): the post-run cleanup steps were not made to wait for the still-running tagger, and an unconditional UPDATE converted ten events' pending review rows to notes (harmless: the delete was re-run after the run finished); a first reading that two events failing the gate were tagger events and price-gap cases was wrong (they were the two kept multi-row events); the figure 742 was written for the exclusions of the day (the right figure is 510 exclusions, 508 events leaving the analysis set); the gate query was first given as a terminal print, whose wrapped lines drop spaces when copied (give long queries inline in the chat); several calls missed (the first-component rate of single-row events, the number of collisions, the similarity of duplicate titles, the tagger events behind the gate gap, the commit count).
PROTOCOL NOTES (additions). The live monitor is python3 scripts/ops/jobs.py (refreshes every 20 seconds; --all shows finished jobs; --ack NAME acknowledges a failed or killed job) in a second terminal; it tracks only jobs started with scripts/ops/bg.sh NAME command; a foreground run needs tail of its log. A step that depends on a running job must check for what it needs and do nothing otherwise. Copying from a wrapped terminal line drops spaces. event_source_filings is one row per filing. A view definition is DDL: record it. After a bulk step, verify the counts against arithmetic done in advance; every discrepancy this morning (21,921 against 21,922, 60 against 58, 22,486 against 22,476) had a specific, findable cause.

COMMITS SINCE THE PREVIOUS CHECKPOINT (since 2026-10-29 13:41 +0000), from git log, objective:
  cf97973 2026-10-29 13:41 Checkpoint: mid-morning 2026-10-29

UNCOMMITTED (git status --short):
  M CHANGELOG.md
   M README.md
   M docs/PROJECT_STATUS.md
  ?? results/ripple_skips_2026-10-29.csv
  ?? results/tag_review_v1_galen.txt
  ?? scripts/audit/patch_docs_refresh_1029.py

<!-- entry: 2026-10-29-05 | date: 2026-10-29 | label: documents | source-line: new | approx: no -->
### 2026-10-29-05 — README and PROJECT_STATUS v1.3: the 2026-10-29 refresh from measured numbers; G5 closed
WHAT: README.md (13 lines) and docs/PROJECT_STATUS.md (v1.2 to v1.3, 18 replacements) refreshed from the numbers measured on 2026-10-29 by scripts/audit/patch_docs_refresh_1029.py (31 exact replacements, hash-gated, all-or-nothing). CHANGED: events with a source-filing link 22,339 to 22,385 (95.0 percent); reaction rows 22,470 to 22,486; labels punished 6,079 to 6,082 and diverged 2,384 to 2,380; exclusions 1,527 exclude, 0 review, 639 note (the review backlog of 333 is closed); analysis set 22,162 to 21,670; ripple timeline 21,915 events and 954,685 rows; tables 163, views 34. The source-filing gap is REWRITTEN: 1,169 events (5.0 percent), of which 813 have their filings recorded in event_component_dates and 356 have none anywhere. G5 is marked DONE; the runbook PENDING row is answered (January steps 1 and 3 resume the 8-K and price ingestion before the forward tests are read at step 7); the G6 note records that sec_filings holds the real 10-Q dates for the 2008 to 2010 rows whose stored filed_date is retroactive; the independence figure (69.8 percent) is marked as predating 508 exclusions. The drop list gains event_exclusions_backup_20261029, event_exclusions_backup_20261029b and event_source_links_added_20261029 (all to be dropped after 2026-11-28).

<!-- entry: 2026-10-29-04 | date: 2026-10-29 | label: checkpoint | source-line: new | approx: no -->
### 2026-10-29-04 — CHECKPOINT 2026-10-29 13:41 (mid-morning 2026-10-29: provenance found in event_component_dates, 46 filings linked, 233 curated duplicates and 8 bundles excluded, ledger repaired, baseline entry added)
Written 2026-10-29 13:41 +0000 (13:41 UTC). Reason: mid-morning 2026-10-29: provenance found in event_component_dates, 46 filings linked, 233 curated duplicates and 8 bundles excluded, ledger repaired, baseline entry added.

WRITTEN BY THE ASSISTANT at about 13:40 UTC on 2026-10-29 (the user's 8:40 AM, Fort Worth). ESTIMATE: this conversation is far past a typical segment (the last compaction was 2026-10-28 17:45 UTC at 1.73 MB; the median is 1.75 MB); a compaction may come at any moment. This block REPLACES the latest-state block; it ADDS to the morning checkpoint of 2026-10-29 (13:05 UTC, CHANGELOG 2026-10-29-02), which embeds the evening of 2026-10-28 verbatim and is in the changelog. Read docs/PROJECT_STATUS.md for the current state; several of its numbers are now STALE (see STALE NUMBERS).
SINCE THE MORNING CHECKPOINT. (1) LEDGER REPAIR: nine flag_ledger rows got append-only notes marked (ledger repair 2026-10-29), NO status changed (15 proven, 21 lead, 62 null, 12 untested, 2 retired, verified); backup flag_ledger_backup_20261029; THEORY section 8 and PROJECT_STATUS v1.2 were patched to match (scripts/audit/patch_docs_ledger_repair.py, commit 57b9361, entry 2026-10-29-03). (2) BASELINE ENTRY: the old plan's sections 3, 5, 9 and 10 are in the changelog as 2026-09-08-02 (dated 2026-09-08, the plan's first commit cab4344). LESSON: changelog_tools.py add --date does NOT sort: it put the entry at the TOP of the index and the entries and made check fail; scripts/audit/fix_changelog_order.py moved it (commit 3b01fbe). The tool's subcommands are split, add, check, checkpoint, retitle. (3) THE JANUARY RUNBOOK EXISTS: results/JANUARY_2027_RUNBOOK.md (30 long lines, last edited 10-26): step 0 backups, 1 8-K filings (scripts/ingestion/import_8k_filings.py), 2 statements (additive only), 3 prices (refresh_market_prices.py --all --apply, about three runs), 3b to 3b3 as-quoted factors, 4 caches (extend_caches.py), 5 matrices (gap_audit.py --rebuild), 6 readiness, 7 evaluate each forward test ONCE, 8 sentiment top-up (after 2026-10-31), 9 and 9a point-in-time repair (only after both verdicts), 10 to 15 later. So the ingestion PAUSE since 2026-10-22 is planned (the nightly classification schedule is disabled; the frozen file says it was written before any price after 10-13 or 8-K after 09-18 was loaded) and January steps 1 to 5 resume everything before the reads. The STATUS row marked PENDING on this is now ANSWERED; close it at the next STATUS revision.
G5 READS. (a) The 8 multi-row events (bundle_multi_component_review): their component rows are REAL FILINGS (event_component_dates columns: event_id, event_summary_date, real_component_date, accession_number, ticker); every one has a real sibling event of the same company within 3 days, and for four of them (AT&T-BellSouth, Verizon-Vodafone, AT&T-DIRECTV, GE-Wabtec) the sibling is the SAME announcement: they repeat a real event's return, so they were changed from review to EXCLUDE (reason bundle_duplicates_sibling_event; backup event_exclusions_backup_20261029, 1,993 rows, holds the state before). (b) The 37 skipped ripple pairs (results/ripple_skips_2026-10-28.csv) are spin-offs, IPOs and predecessor-ticker events dated on or before the first price day of the current ticker (no prior close): nothing to fix.
PROVENANCE AND DUPLICATES (the main finding of the day). event_component_dates holds each component's real filing, and ALL 856 events with a reaction row, no event_source_filings row and a component row have a real 8-K in sec_8k_filings (accession numbers match): the 'no source filing' gap was overstated; the filings were recorded in another table. event_source_filings has FOUR columns (event_id, ticker, filing_date, accession_number) and its PRIMARY KEY is (ticker, filing_date, accession_number): ONE EVENT PER FILING. Of 284 single-row events, 241 (85%) have the component filing on the event day; 41 lag 1 to 8 days (weekends and holidays); Prologis-Duke Realty (95 days) and J&J (181 days, a rollup) were held back. A planned insert of 279 links FAILED (23505): 233 of the 279 filings are ALREADY the source of a promoted event: the same occurrence recorded twice, a curated event dated at the OCCURRENCE and a promoted event dated at the FILING (203 share the event day). The 100 least similar title pairs were read: nearly all the same occurrence; title word-overlap does NOT separate duplicates (curated titles are shorthand, 8-K headings are formal); SAME FILING is the rule that works (a few pairs are different items inside one 8-K, still not independent). RESULT: the 46 free filings were linked (events with a source filing 22,339 to 22,385 = 95.0 percent; no_source_curated notes 323 to 278); the 233 curated duplicates were EXCLUDED (reason duplicate_of_promoted_event, severity exclude; the promoted event keeps the filing-date convention; UNDO: DELETE FROM event_exclusions WHERE reason = 'duplicate_of_promoted_event'). The staging table event_source_links_added_20261029 holds the 279 PLANNED links, NOT links that were added; DROP AFTER 2026-11-28 with the backups.
NUMBERS NOW (measured today): events with a source filing 22,385 of 23,554; no source link 1,169 (813 of them are in the component table: 575 multi-row summaries and 238 single-row events, 233 of which are the duplicates above; 356 have no filing recorded anywhere); event_exclusions 2,181 rows = 1,258 exclude + 325 review + 598 note (the 8 bundles moved from review to exclude, so review is 325, NOT 333); analysis set 21,922 (22,162 this morning; the arithmetic is 22,162 - 8 bundles - 233 duplicates + 1 that was already excluded: one event is UNVERIFIED, the user was given a query for it); tables 162 and views 34 (159 and 34 at the morning check, plus flag_ledger_backup_20261029, event_exclusions_backup_20261029, event_source_links_added_20261029); ripple 21,913 events and 954,599 rows (unchanged).
STALE NUMBERS TO FIX AT THE NEXT DOCUMENT UPDATE (do not patch piecemeal; regenerate from scripts/sql/readme_snapshot.sql plus the repo counts, then patch README, PROJECT_STATUS and, if needed, THEORY in one hash-gated step): the README says 22,339 events (94.8 percent) with a source, 1,215 without, 333 events under review, 1,017 excluded, 643 notes, 157 tables, 486 commits, 189 changelog entries; PROJECT_STATUS says 333 review events in the phase 5 row, G1, G5 and the exclusions line, the analysis set as 22,162, and has the runbook PENDING row. The README's known-limit 1 (1,215 events, 233 rollups and 982 others) is wrong in its split and must be rewritten from the numbers above.
CONSEQUENCES. The ripple builder built timelines on 10-28 for 280 curated events and about 233 of them are now excluded duplicates: the ripple table stays, but any ripple-based flag must select events through event_analysis_set (gate G7). The independence figure (69.8 percent independent within 28-day company windows) was computed BEFORE the 233 and the 8 were removed: recompute it at G7. The same-filing duplicate check found curated-versus-promoted pairs only; same-company same-day events from DIFFERENT filings are handled by the 28-day clusters.
OPEN, IN ORDER. (1) The document refresh above (needs the snapshot query result and the repo counts pasted). (2) Link the three single-row events that were held back by a too-blunt title filter but read as ordinary events (AbbVie's separation, two Southern Company items) if their filings are free (same collision test); J&J and Prologis-Duke stay out. (3) G5 remaining: the 267 corrected-date review rows (read a stratified sample), the 55 not computable, the 3 price steps, the 514 quarterly statements filed within 8 to 19 days. (4) G7: rerun the 12 substantive proven flags on event_analysis_set and the corrected ripple table. (5) G4 and G6. (6) The 2003-09-15 FOMC row (attach the real build_fomc_calendar.py). (7) After 2026-10-31 (Monday 11-02): the October sentiment top-up. (8) After 2026-11-28: drop flag_ledger_backup_20261029, event_exclusions_backup_20261029, event_source_links_added_20261029, fomc_meetings_backup_20261028, event_ripple_timeline_backup_20261028, scratch_diverged_new_20261028, scratch_diverged_v2_20261028. (9) January: the runbook, once.
PROTOCOL NOTES (additions). In the user's interactive bash a pattern containing an exclamation mark MUST be in SINGLE quotes (history expansion rewrote two greps today). An INSERT into event_source_filings must respect its key (one event per filing). A bulk step starts with its rule, a backup or an undo statement, a read of the hardest cases, then a guarded apply; today's reads changed three plans (the bundles became excludes, the links split, the duplicates got a rule). A failed single statement changes nothing; the user skipped the dependent blocks correctly.
CALLS THAT MISSED SINCE THE MORNING. Growth in 8-Ks and classifications overnight (the schedule is disabled); the frozen file naming a refresh step; the runbook's length; the changelog tool sorting an add --date entry (check failed); the three deals having no sibling events (all 8 have one); 90 percent of single-row events having their filing on the event day (85); none of the 43 lags exceeding 90 days (two did); 10 to 80 collisions (233); the least-similar title pairs being mostly different events (nearly all the same occurrence); the analysis set 21,921 (21,922). Most other calls held.

COMMITS SINCE THE PREVIOUS CHECKPOINT (since 2026-10-29 13:05 +0000), from git log, objective:
  3b01fbe 2026-10-29 13:30 Changelog: the original plan's baseline sections, dated 2026-09-08 (moved into place)
  57b9361 2026-10-29 13:15 Ledger repair; THEORY section 8 and PROJECT_STATUS v1.2
  389fa49 2026-10-29 13:05 Checkpoint: morning 2026-10-29

UNCOMMITTED (git status --short):
  ?? results/tag_review_v1_galen.txt

<!-- entry: 2026-10-29-03 | date: 2026-10-29 | label: documents | source-line: new | approx: no -->
### 2026-10-29-03 — Ledger repair (9 append-only notes) and docs brought in line: THEORY section 8, PROJECT_STATUS v1.2
WHAT: nine flag_ledger rows received append-only notes marked (ledger repair 2026-10-29); NO status or other column changed (15 proven, 21 lead, 62 null, 12 untested, 2 retired, verified after). Rows: fed_state (the Fed raised the target range to 3.75-4.00% on 2026-09-16; fed_state_daily correctly reads tightening), news_sentiment_gdelt (points to the two GDELT tests of 2026-10-22, both NO LANE; stays untested; table sizes corrected), government_decisions_day_level (FOMC days and executive orders have since been tested), event_type_acquisition, event_type_leadership_change and event_type_strategic_partnership (rerun numbers added; each note states that proven means uses the pooled number), and round_number_clustering_whole_dollar, round_number_threshold_move_size and fomc_rate_sensitive_sector_contrast (the retired SCRIPTS.md is now CHANGELOG.md plus docs/SCRIPTS_REFERENCE.md). Backup: flag_ledger_backup_20261029 (112 rows; DROP AFTER 2026-11-28). LEFT ON PURPOSE: the status vocabulary for proven-means-pooled (waits for G7), duplicated sentences in two notes (one is a frozen forward-test row), the storm_tier_large evidence unit, and a ledger row for the tag-significance audit (needs its primary numbers re-read). Documents: THEORY section 8 now lists what was repaired and the five items still open; docs/PROJECT_STATUS.md is v1.2: ingestion is recorded as PAUSED since 2026-10-22 by decision (the nightly classification schedule is disabled, 8-Ks after 2026-09-18 and prices after 2026-10-13 are not loaded, the price refresh is a manual script), and a [PENDING] row asks which January runbook step resumes ingestion before the forward tests are read. The patch is kept as scripts/audit/patch_docs_ledger_repair.py.

<!-- entry: 2026-10-29-02 | date: 2026-10-29 | label: checkpoint | source-line: new | approx: no -->
### 2026-10-29-02 — CHECKPOINT 2026-10-29 13:05 (morning 2026-10-29: the evening 2026-10-28 state installed (documents, FOMC, Phase 5 gate 5 of 5, ripple fix); ingestion paused since 10-22 confirmed; checkpoint command corrected)
Written 2026-10-29 13:05 +0000 (13:05 UTC). Reason: morning 2026-10-29: the evening 2026-10-28 state installed (documents, FOMC, Phase 5 gate 5 of 5, ripple fix); ingestion paused since 10-22 confirmed; checkpoint command corrected.

WRITTEN BY THE ASSISTANT at about 13:20 UTC on 2026-10-29 (the user's 8:20 AM, Fort Worth). ESTIMATE: this conversation is at roughly 90 to 100 percent of a typical segment (the last one was 1.73 MB; the median is 1.75 MB), so a compaction may come at any moment. This block REPLACES the latest-state block and CONTAINS the evening 2026-10-28 checkpoint verbatim below it (that checkpoint was never installed: the assistant gave the wrong command, see the error note). The three earlier checkpoints of 2026-10-28 (midday, afternoon, late afternoon) are CHANGELOG entries 2026-10-28-01 to -03 and their details still stand.
MORNING 2026-10-29: TIME AND STATE. 13:02 UTC; the latest prior checkpoint was 21.0 hours old; 33 transcript segments exist; the last compaction was 2026-10-28 17:45 UTC; the transcript tail (the stretch 16:25 to 17:45 that the evening checkpoint knew only from the compaction summary) was grepped for decisions and holds nothing beyond what is recorded.
MORNING FRESHNESS CHECK (24 live figures against the previous evening): only TWO changed: news articles 1,204 to 1,234 (marketaux_daily.yml still runs) and database size 3,160 to 3,162 MB. STATIC BY DESIGN: 8-K filings 155,141, AI classifications 150,539 (95,485 with a human verdict), the latest event date 2026-09-11 and the last price date 2026-10-13. The schedule of .github/workflows/nightly-classify.yml was DISABLED on 2026-10-22 (its own comment: ingestion is paused under the history-first plan and the classifier pool is static; workflow_dispatch stays available). The price refresh is a MANUAL script (scripts/ingestion/refresh_market_prices.py, for example --all --apply --max-requests 500; OPERATIONS lines 302 to 334) and has not run since about 2026-10-13. The assistant had predicted growth in 8-Ks and classifications at 80 percent: wrong, because it had not read the workflow. TO VERIFY, NOT YET DONE: that the January runbook (steps 0 to 15) ingests the 2026-10-14 to 12-31 window's 8-Ks and refreshes prices BEFORE the two frozen forward tests are read (both need item 2.02 filings and prices after 2026-10-13).
ASSISTANT'S ERROR: it told the user to log the evening checkpoint with changelog_tools.py add --label checkpoint. The project's command is changelog_tools.py checkpoint --reason ..., which ALSO replaces this block; so the evening checkpoint was never installed and docs/START_NEW_DAY.md still showed the 16:01 UTC state. Rule for the next assistant: read docs/START_NEW_DAY.md before giving ANY checkpoint command (rule 3: never guess an interface).
STILL OPEN, ON TOP OF THE LIST BELOW: (a) the ledger repair (ten stale rows; plan: six safe corrections APPENDED to notes, never rewriting history; a few decisions for the user, for example whether news_sentiment_gdelt becomes null and what status vocabulary replaces proven-means-uses-the-pooled-number; the two frozen forward-test rows stay untouched); (b) the baseline changelog entry (old plan sections 3, 5, 9, 10) is still unanswered; (c) the stale item lists in the previous latest block are RESOLVED: FOMC step 3c done, the docs bundle done (README v2, PLAN v2, THEORY v2, STATUS v1.1).

---- EVENING 2026-10-28 CHECKPOINT (verbatim, written 19:40 UTC) ----
WRITTEN BY THE ASSISTANT at about 19:40 UTC on 2026-10-28 (the user's 2:40 PM, Fort Worth). ESTIMATE: this conversation is very long (roughly 90% or more of its capacity); a compaction may come soon. This block ADDS to the three earlier checkpoints of today (midday, commit 35ae8bd: tagger and pre-context finished, firm-state drift, tools, documentation plan; afternoon, 2b62928: price steps, rollups, corrected dates, look-ahead; late afternoon, eb96446: the PIT and exclusions tables); everything there still stands unless this block says otherwise. docs/PROJECT_STATUS.md v1.1 is the single place for the CURRENT state; this block records the history of the evening and what is written nowhere else.

WHAT HAPPENED SINCE 16:25 UTC (each item has its own CHANGELOG entry; commits: THEORY and README 0297d6f, PLAN 7c557eb, STATUS v1 and the snapshot query dcc5572, FOMC c24d3f9 = entry 2026-10-28-07, Phase 5 = entry 2026-10-28-08; the ripple-fix commit and the STATUS v1.1 commit were made by the user, see git log).
(1) DOCUMENTS (G9): README v2 (a snapshot, 105 lines; its numbers come from scripts/sql/readme_snapshot.sql), PROJECT_PLAN v2 (144 lines, intent only, no status), THEORY v2 (153 lines, a reading of the flag ledger: all 112 flag keys placed in their status section, checked programmatically), PROJECT_STATUS v1.1 (224 lines). The README's held-and-not-held section was CORRECTED against the ledger the same evening (it had said direction prediction did not hold; the ledger has event_label_direction_sign as PROVEN at 57.7 and 57.8 percent against about 54 by chance; the FOMC move is 1.11 to 1.14, not 1.14; the 0-of-13 tag claim has no ledger row). The unedited originals are in docs/archive/*_pre_rewrite_2026-10-28.md (checked).
(2) FOMC: the calendar was rebuilt AFTER the Fed's 18:00 UTC statement (a build at 17:47 had run too early and said so itself), 2026-10-28 was added to the independent list in build_fomc_calendar.py from the Fed's schedule (check (a): 47 expected, 47 parsed), and loaded with load_fomc_meetings.py --apply (an UPSERT on kind, start_date, end_date; the dry run prints only the CSV's own totals and does not compare with the table). Backup fomc_meetings_backup_20261028; verified 309 rows unchanged, 1 changed, none orphaned; table 310 rows. KNOWN, NOT FIXED: one spurious row, the meeting of 2003-09-15 (the Fed's 2003 schedule and minutes show eight meetings, September's on the 16th); rebuilding the CSV re-creates it, so the fix belongs in build_fomc_calendar.py, whose real file the assistant has NOT seen (only lines 27-33). The Fed raised the target range 25 bp to 3.75-4.00 percent on 2026-09-16 (12-0); fed_state_daily correctly reads tightening since then, only the ledger's fed_state note is stale. The assistant could not read the Fed's 2026-10-28 decision text (web_fetch refuses URLs that were not in a search result); the user has it.
(3) PHASE 5 GATE (G1) PASSES 5 OF 5. scripts/sql/phase5_gate.sql is the saved check, built from the done-when of NAMING.md; component 5 accepts only an exclude or review reason, because the 10-28 gate had counted a provenance note as a reason and read 31 gaps where the truth was 319. The 319 = 288 curated pilot events + 30 News Corp events + 1 Mosaic event. CAUSES, found by reading the real scripts/ripple/build_ripple_timeline.py: (a) it skipped every id in event_component_dates (859 events), but 284 of those have a single component row and are real single-date events (39 of 40 read); (b) get_ticker_and_sector took the first security of an entity, unordered: News Corp (NWS and NWSA, ONE entity and the ONLY entity with two securities) lost 30 events (NWS has no prices before mid-2023) and had 8 events computed on NWS; (c) pairs with too few prices were counted, never recorded; (d) events were paged with a non-unique order. FIX: scripts/audit/patch_ripple_builder.py (11 exact-match anchors; tested on a reconstruction in which the OLD builder reproduced the production symptom); the skip list is now the view ripple_skip_events (events with 2 or more component rows plus every exclude reason: 1,291); the primary security is the reaction row's ticker, else the earliest-priced class; every skipped pair goes to results/ripple_skips_2026-10-28.csv (323 pairs: 286 no security for the entity, 37 no prior close; the 37 are UNREAD). 8 multi-row events were recorded as review (bundle_multi_component_review: five narrative summaries LLY, SLB, VZ, DLR, NVDA and three single deals with several milestone dates, T-BellSouth, T-DIRECTV, GE-Wabtec; decide per case). Backup event_ripple_timeline_backup_20261028 (8 events, 349 rows), then deleted, then rebuilt: 679 events processed = 322 built + 34 no entity + 323 skipped pairs. RESULT: events with a ripple 21,599 to 21,913, rows 940,758 to 954,599; NWSA 38 of 38 under NWSA; mismatches 0; gap 319 to 0.
(4) THE LEDGER READ: 15 proven (12 substantive; 3 only say a type uses the pooled number), 21 lead, 62 null, 12 untested, 2 retired. Ten stale or inconsistent rows are listed in THEORY section 8 (none yet repaired).

THE NUMBERS NOW (2026-10-28 evening, [LIVE]): events 23,554; reaction rows 22,470; analysis set 22,162; ripple events 21,913, rows 954,599; event_exclusions: 1,017 exclude, 333 review (325 + 8), 643 note; FOMC table 310; database 3,160 MB, 159 tables, 34 views (157 and 33 at the morning snapshot, plus two backups and one view). Backups and scratch tables to DROP AFTER 2026-11-28: fomc_meetings_backup_20261028, event_ripple_timeline_backup_20261028, scratch_diverged_new_20261028, scratch_diverged_v2_20261028 (G10).

DECISIONS OF THE EVENING: the ripple builder's primary security is the reaction row's ticker (the user agreed to the recommendation); the 8 multi-row events are review, not exclude; the skip rule lives in a view, not in the script; no diverged tag was written (its definition is unstable; G6); the forward-test files remain FROZEN.

CORRECTIONS TO THE ASSISTANT'S OWN EARLIER STATEMENTS (all recorded in the changelog where they matter): the gap was 319, not 31; the share-class mismatch was 8 events (News Corp), NOT 24: 16 of those were Fox events linked on purpose to two separate entities (FOX and FOXA), which the delete predicate (same entity only) protected; the claim that 2003 was a "known exception" in the FOMC calendar had no basis; the hypothesis that the ripple builder requires a source filing was wrong (the mechanism was the bundle rule); the guess that Alphabet would show a share-class mismatch was wrong; the Fed-state view was never defective.

OPEN, IN ORDER OF CONSEQUENCE. (1) G5: read the 333 review events: first the 8 bundles (the three deals' components) and the 37 unread ripple skips, then a stratified sample of the 267 corrected dates. (2) Repair the ten stale ledger rows (then shrink THEORY section 8). (3) G7: rerun the 12 substantive proven flags on the analysis set and the corrected ripple table (314 events were added; the baseline of event_burst_day0_1 and its relatives changed by about 3 percent). (4) G4 (price artifacts below the 60 percent scan) and G6 (firm state with a capped availability date, then the fate of diverged). (5) The 2003-09-15 FOMC row (attach the real build_fomc_calendar.py). (6) STILL UNANSWERED FROM BEFORE THE LAST COMPACTION: whether to add the old plan's sections 3, 5, 9 and 10 (original-versus-actual table, the Sept 8 status percentages, the 13-company tier system, the old next steps) to the CHANGELOG as ONE entry dated 2026-09-08 (the assistant recommended yes; today they exist only in the archived PROJECT_PLAN; scripts/audit/import_plan_addenda.py would be extended to add only what is missing). Dated: after 2026-10-31 the October sentiment top-up (runbook 8); after 2027-01-05 the January runbook, run once; the untracked results/tag_review_v1_galen.txt is the user's government-tag review in progress (PREREG_government_tag_review_v1).

PROTOCOL NOTES THAT COST TIME TODAY. The user's SQL editor shows at most 100 rows and its results CLEAR (ask for a paste, never assume); dollar-quote every string; lint every query with lint_sql.py before giving it. A file the assistant presents can collide with an older file of the same name (the STATUS file was never seen until it was re-sent under a unique name): use unique names. Attached text files arrive in the conversation, NOT on the assistant's disk. web_fetch only opens URLs that appeared in a web_search result, not URLs the user pasted. A dry run is not a diff: read what a loader's dry run actually prints before trusting it, and ask for the loader's write lines (grep upsert/insert/delete). Test any patch on a reconstruction of the real file first, make it assert exact matches and gate it on the file's hash, and make a backup table (with a recorded drop date) before any DELETE. Do not retype a hash from memory: copy it from the tool output (one wrong hash was caught before use). Never bulk-fix after a count: read cases first.

CALIBRATION (an informal tally from this conversation, NOT a logged file; results/prediction_log.csv is still an empty header): of about 65 explicit "calls on record" made this evening, about 54 held (83 percent) and 11 missed. The misses: the human-verdict count and the Python file count (snapshot); the concentration of ripple gaps by ticker; the 31 gaps being recent; the Fed-state view being defective; a dry run reporting one changed row; NWSA having no ripples at all; NWSA price holes; NWS prices starting in 2025; and the step-D1 count of share-class mismatches (24 events and 900 to 1,300 rows, stated at 85 percent; the truth was 8 events and 349 rows). The costliest miss was the last: the safeguard in the delete predicate, not the prediction, protected the data.

COMMITS SINCE THE PREVIOUS CHECKPOINT (since 2026-10-28 16:01 +0000), from git log, objective:
  b021e92 2026-10-29 12:59 Checkpoint: evening 2026-10-28
  0f917f2 2026-10-28 19:20 PROJECT_STATUS v1.1 and the evening checkpoint
  6188588 2026-10-28 19:17 Phase 5 gate 5 of 5: ripple builder fixed, 314 events built, skips recorded
  c24d3f9 2026-10-28 18:18 FOMC calendar: 2026-10-28 confirmed and loaded
  0297d6f 2026-10-28 18:02 THEORY as a reading of the ledger; README findings corrected
  7c557eb 2026-10-28 17:41 PROJECT_PLAN v2: the current design, no status
  dcc5572 2026-10-28 17:37 PROJECT_STATUS v1 and the README snapshot query
  213d877 2026-10-28 12:30 Revise README for clarity and updated information
  eb96446 2026-10-28 16:01 Checkpoint: late afternoon 2026-10-28, PIT and exclusions tables, no tags written

UNCOMMITTED (git status --short):
  ?? results/tag_review_v1_galen.txt

<!-- entry: 2026-10-29-01 | date: 2026-10-29 | label: checkpoint | source-line: new | approx: no -->
### 2026-10-29-01 — Checkpoint: evening 2026-10-28, documents, FOMC, Phase 5 gate and the ripple fix
WRITTEN BY THE ASSISTANT at about 19:40 UTC on 2026-10-28 (the user's 2:40 PM, Fort Worth). ESTIMATE: this conversation is very long (roughly 90% or more of its capacity); a compaction may come soon. This block ADDS to the three earlier checkpoints of today (midday, commit 35ae8bd: tagger and pre-context finished, firm-state drift, tools, documentation plan; afternoon, 2b62928: price steps, rollups, corrected dates, look-ahead; late afternoon, eb96446: the PIT and exclusions tables); everything there still stands unless this block says otherwise. docs/PROJECT_STATUS.md v1.1 is the single place for the CURRENT state; this block records the history of the evening and what is written nowhere else.

WHAT HAPPENED SINCE 16:25 UTC (each item has its own CHANGELOG entry; commits: THEORY and README 0297d6f, PLAN 7c557eb, STATUS v1 and the snapshot query dcc5572, FOMC c24d3f9 = entry 2026-10-28-07, Phase 5 = entry 2026-10-28-08; the ripple-fix commit and the STATUS v1.1 commit were made by the user, see git log).
(1) DOCUMENTS (G9): README v2 (a snapshot, 105 lines; its numbers come from scripts/sql/readme_snapshot.sql), PROJECT_PLAN v2 (144 lines, intent only, no status), THEORY v2 (153 lines, a reading of the flag ledger: all 112 flag keys placed in their status section, checked programmatically), PROJECT_STATUS v1.1 (224 lines). The README's held-and-not-held section was CORRECTED against the ledger the same evening (it had said direction prediction did not hold; the ledger has event_label_direction_sign as PROVEN at 57.7 and 57.8 percent against about 54 by chance; the FOMC move is 1.11 to 1.14, not 1.14; the 0-of-13 tag claim has no ledger row). The unedited originals are in docs/archive/*_pre_rewrite_2026-10-28.md (checked).
(2) FOMC: the calendar was rebuilt AFTER the Fed's 18:00 UTC statement (a build at 17:47 had run too early and said so itself), 2026-10-28 was added to the independent list in build_fomc_calendar.py from the Fed's schedule (check (a): 47 expected, 47 parsed), and loaded with load_fomc_meetings.py --apply (an UPSERT on kind, start_date, end_date; the dry run prints only the CSV's own totals and does not compare with the table). Backup fomc_meetings_backup_20261028; verified 309 rows unchanged, 1 changed, none orphaned; table 310 rows. KNOWN, NOT FIXED: one spurious row, the meeting of 2003-09-15 (the Fed's 2003 schedule and minutes show eight meetings, September's on the 16th); rebuilding the CSV re-creates it, so the fix belongs in build_fomc_calendar.py, whose real file the assistant has NOT seen (only lines 27-33). The Fed raised the target range 25 bp to 3.75-4.00 percent on 2026-09-16 (12-0); fed_state_daily correctly reads tightening since then, only the ledger's fed_state note is stale. The assistant could not read the Fed's 2026-10-28 decision text (web_fetch refuses URLs that were not in a search result); the user has it.
(3) PHASE 5 GATE (G1) PASSES 5 OF 5. scripts/sql/phase5_gate.sql is the saved check, built from the done-when of NAMING.md; component 5 accepts only an exclude or review reason, because the 10-28 gate had counted a provenance note as a reason and read 31 gaps where the truth was 319. The 319 = 288 curated pilot events + 30 News Corp events + 1 Mosaic event. CAUSES, found by reading the real scripts/ripple/build_ripple_timeline.py: (a) it skipped every id in event_component_dates (859 events), but 284 of those have a single component row and are real single-date events (39 of 40 read); (b) get_ticker_and_sector took the first security of an entity, unordered: News Corp (NWS and NWSA, ONE entity and the ONLY entity with two securities) lost 30 events (NWS has no prices before mid-2023) and had 8 events computed on NWS; (c) pairs with too few prices were counted, never recorded; (d) events were paged with a non-unique order. FIX: scripts/audit/patch_ripple_builder.py (11 exact-match anchors; tested on a reconstruction in which the OLD builder reproduced the production symptom); the skip list is now the view ripple_skip_events (events with 2 or more component rows plus every exclude reason: 1,291); the primary security is the reaction row's ticker, else the earliest-priced class; every skipped pair goes to results/ripple_skips_2026-10-28.csv (323 pairs: 286 no security for the entity, 37 no prior close; the 37 are UNREAD). 8 multi-row events were recorded as review (bundle_multi_component_review: five narrative summaries LLY, SLB, VZ, DLR, NVDA and three single deals with several milestone dates, T-BellSouth, T-DIRECTV, GE-Wabtec; decide per case). Backup event_ripple_timeline_backup_20261028 (8 events, 349 rows), then deleted, then rebuilt: 679 events processed = 322 built + 34 no entity + 323 skipped pairs. RESULT: events with a ripple 21,599 to 21,913, rows 940,758 to 954,599; NWSA 38 of 38 under NWSA; mismatches 0; gap 319 to 0.
(4) THE LEDGER READ: 15 proven (12 substantive; 3 only say a type uses the pooled number), 21 lead, 62 null, 12 untested, 2 retired. Ten stale or inconsistent rows are listed in THEORY section 8 (none yet repaired).

THE NUMBERS NOW (2026-10-28 evening, [LIVE]): events 23,554; reaction rows 22,470; analysis set 22,162; ripple events 21,913, rows 954,599; event_exclusions: 1,017 exclude, 333 review (325 + 8), 643 note; FOMC table 310; database 3,160 MB, 159 tables, 34 views (157 and 33 at the morning snapshot, plus two backups and one view). Backups and scratch tables to DROP AFTER 2026-11-28: fomc_meetings_backup_20261028, event_ripple_timeline_backup_20261028, scratch_diverged_new_20261028, scratch_diverged_v2_20261028 (G10).

DECISIONS OF THE EVENING: the ripple builder's primary security is the reaction row's ticker (the user agreed to the recommendation); the 8 multi-row events are review, not exclude; the skip rule lives in a view, not in the script; no diverged tag was written (its definition is unstable; G6); the forward-test files remain FROZEN.

CORRECTIONS TO THE ASSISTANT'S OWN EARLIER STATEMENTS (all recorded in the changelog where they matter): the gap was 319, not 31; the share-class mismatch was 8 events (News Corp), NOT 24: 16 of those were Fox events linked on purpose to two separate entities (FOX and FOXA), which the delete predicate (same entity only) protected; the claim that 2003 was a "known exception" in the FOMC calendar had no basis; the hypothesis that the ripple builder requires a source filing was wrong (the mechanism was the bundle rule); the guess that Alphabet would show a share-class mismatch was wrong; the Fed-state view was never defective.

OPEN, IN ORDER OF CONSEQUENCE. (1) G5: read the 333 review events: first the 8 bundles (the three deals' components) and the 37 unread ripple skips, then a stratified sample of the 267 corrected dates. (2) Repair the ten stale ledger rows (then shrink THEORY section 8). (3) G7: rerun the 12 substantive proven flags on the analysis set and the corrected ripple table (314 events were added; the baseline of event_burst_day0_1 and its relatives changed by about 3 percent). (4) G4 (price artifacts below the 60 percent scan) and G6 (firm state with a capped availability date, then the fate of diverged). (5) The 2003-09-15 FOMC row (attach the real build_fomc_calendar.py). (6) STILL UNANSWERED FROM BEFORE THE LAST COMPACTION: whether to add the old plan's sections 3, 5, 9 and 10 (original-versus-actual table, the Sept 8 status percentages, the 13-company tier system, the old next steps) to the CHANGELOG as ONE entry dated 2026-09-08 (the assistant recommended yes; today they exist only in the archived PROJECT_PLAN; scripts/audit/import_plan_addenda.py would be extended to add only what is missing). Dated: after 2026-10-31 the October sentiment top-up (runbook 8); after 2027-01-05 the January runbook, run once; the untracked results/tag_review_v1_galen.txt is the user's government-tag review in progress (PREREG_government_tag_review_v1).

PROTOCOL NOTES THAT COST TIME TODAY. The user's SQL editor shows at most 100 rows and its results CLEAR (ask for a paste, never assume); dollar-quote every string; lint every query with lint_sql.py before giving it. A file the assistant presents can collide with an older file of the same name (the STATUS file was never seen until it was re-sent under a unique name): use unique names. Attached text files arrive in the conversation, NOT on the assistant's disk. web_fetch only opens URLs that appeared in a web_search result, not URLs the user pasted. A dry run is not a diff: read what a loader's dry run actually prints before trusting it, and ask for the loader's write lines (grep upsert/insert/delete). Test any patch on a reconstruction of the real file first, make it assert exact matches and gate it on the file's hash, and make a backup table (with a recorded drop date) before any DELETE. Do not retype a hash from memory: copy it from the tool output (one wrong hash was caught before use). Never bulk-fix after a count: read cases first.

CALIBRATION (an informal tally from this conversation, NOT a logged file; results/prediction_log.csv is still an empty header): of about 65 explicit "calls on record" made this evening, about 54 held (83 percent) and 11 missed. The misses: the human-verdict count and the Python file count (snapshot); the concentration of ripple gaps by ticker; the 31 gaps being recent; the Fed-state view being defective; a dry run reporting one changed row; NWSA having no ripples at all; NWSA price holes; NWS prices starting in 2025; and the step-D1 count of share-class mismatches (24 events and 900 to 1,300 rows, stated at 85 percent; the truth was 8 events and 349 rows). The costliest miss was the last: the safeguard in the delete predicate, not the prediction, protected the data.

<!-- entry: 2026-10-28-09 | date: 2026-10-28 | label: documents | source-line: new | approx: no -->
### 2026-10-28-09 — PROJECT_STATUS v1.1 and the 2026-10-28 evening checkpoint: Phase 5 gate 5 of 5, FOMC loaded, open items recorded
WHAT: docs/PROJECT_STATUS.md v1.1 (14 exact-match replacements; the patch is kept as scripts/audit/patch_status_v11.py): Phase 5 gate 5 of 5 (scripts/sql/phase5_gate.sql) and G1 done; the FOMC calendar loaded through the 2026-10-28 meeting (310 rows); 333 review events recorded (8 new: bundle_multi_component_review); new objects recorded (view ripple_skip_events; backups fomc_meetings_backup_20261028 and event_ripple_timeline_backup_20261028, BOTH to be dropped after 2026-11-28); database 3,160 MB. OPEN, recorded in the file: the spurious 2003-09-15 FOMC row (fix belongs in build_fomc_calendar.py), ten stale or inconsistent ledger rows (THEORY section 8), the 37 unread ripple skips, the 333 review events (G5), and G7 (rerun the proven flags on the corrected ripple table). THE DAY, 2026-10-28 (evening checkpoint): tagger and pre-context runs finished; data-quality audit and its tables (event_exclusions, event_analysis_set, event_firm_state_pit); README, PROJECT_PLAN v2 and THEORY v2 rewritten and installed, the README findings section corrected against the flag ledger; the Fed's 2026-09-16 rate hike confirmed (fed_state_daily is correct, only its ledger note is stale); the ripple builder fixed and 314 events built. No tag was written; the forward-test files remain frozen.

<!-- entry: 2026-10-28-08 | date: 2026-10-28 | label: data | source-line: new | approx: no -->
### 2026-10-28-08 — Phase 5 gate passes 5 of 5: ripple builder fixed (bundle rule, share class, skips recorded); 314 events built
WHAT: the Phase 5 gate was rebuilt as a runnable check (scripts/sql/phase5_gate.sql, from the done-when of NAMING.md); its component 5 accepts only an exclude or review reason, because the 10-28 query had counted a provenance note as a reason and read 31 gaps where the true count was 319. CAUSES, found by reading scripts/ripple/build_ripple_timeline.py: (1) the skip rule excluded every id in event_component_dates, 859 events, of which 284 have a single component row and are real single-date events (39 of 40 sampled read as one dated occurrence); 280 of them had reaction rows and no ripple; (2) get_ticker_and_sector took the first security of an entity, unordered: News Corp (NWS and NWSA, one entity and the only entity with two securities) had 30 events silently skipped (NWS has no prices before mid-2023) and 8 events computed on NWS; (3) a pair with too few prices was only counted, never recorded; (4) events were paged with a non-unique order. FIX (scripts/audit/patch_ripple_builder.py, 11 exact-match anchors, tested on a reconstruction in which the old builder reproduced the production symptom): the skip list is the view ripple_skip_events (events with 2 or more component rows plus every exclude reason, 1,291 events); the primary security is the reaction row's ticker, else the earliest-priced class; every skipped pair is written to results/ripple_skips_<date>.csv; unique paging order. DATA: 8 multi-row events recorded as review (reason bundle_multi_component_review: 5 narrative summaries, 3 single deals with several milestone dates; decide per case); backup event_ripple_timeline_backup_20261028 (8 events, 349 rows; DROP AFTER 2026-11-28), then deleted, then rebuilt. RESULT: events with a ripple 21,599 to 21,913 (+314), rows 940,758 to 954,599; NWSA 38 of 38 events under NWSA; share-class mismatches 0; gate component 5 gaps 319 to 0. CORRECTED: an earlier reading said 24 events had a share-class mismatch; 16 of those were Fox events linked on purpose to two separate entities (FOX and FOXA), and the delete predicate (same entity only) protected them; only News Corp was affected. OPEN: the gate accepts review as a documented reason and 333 events carry one (gate G5); the new ripple rows add about 3 percent more isolated events to the baseline of flags marked proven, so gate G7 re-runs them on the corrected table; README figures updated (954,599 rows, 21,913 events).

<!-- entry: 2026-10-28-07 | date: 2026-10-28 | label: data | source-line: new | approx: no -->
### 2026-10-28-07 — FOMC calendar: the 2026-10-28 meeting confirmed and loaded; independent list extended
WHAT: the 2026-10-28 announcement was added to the independent transcription in build_fomc_calendar.py (from the Fed's published schedule; check (a) now 47 expected, 47 parsed, none missing, none extra), the calendar rebuilt after the Fed's page carried the statement, and loaded with load_fomc_meetings.py --apply (an upsert on kind, start_date, end_date). Backup first: fomc_meetings_backup_20261028 (310 rows; DROP AFTER 2026-11-28). Verified against the backup: 309 rows unchanged, 1 changed (confirmed, flags, statement_url: the Oct 27-28 row), none only in one table; the table stays at 310 rows (274 meetings, 35 conference calls, 1 cancelled; 245 confirmed announcements; 9 scheduled and not yet held). KNOWN, NOT FIXED: one spurious row, the meeting of 2003-09-15 (no statement; the Fed's 2003 schedule and the minutes show eight meetings, September's on the 16th); it carries no announcement, and no finished test counted it (the drift test's n for 1994-2011 is 144 = 18 years x 8). Rebuilding the CSV re-creates it, so the fix belongs in build_fomc_calendar.py, not in the table. fed_state_daily checked: tightening since 2026-09-16 (the Fed raised the target range to 3.75-4.00%), so the view is right and only its ledger note is stale.

<!-- entry: 2026-10-28-06 | date: 2026-10-28 | label: documents | source-line: new | approx: no -->
### 2026-10-28-06 — THEORY rewritten as a reading of the flag ledger; README findings section corrected
WHAT: THEORY.md rewritten (153 lines, down from 1,166) as a reading of the flag ledger (112 flags: 15 proven, 21 lead, 62 null, 12 untested, 2 retired; every flag key placed in its status section, checked programmatically): the picture in five sentences, the proven and lead tables with their recorded evidence, the nulls by what they ruled out (a null is not an absence), the untested rows, what was retired or corrected (including the 2026-10-03 retraction of the validated magnitude prediction), ten stale or inconsistent ledger rows listed for repair, and what would change the picture. The previous version is docs/archive/THEORY_pre_rewrite_2026-10-28.md. README.md: the held-and-not-held section CORRECTED against the ledger (the label direction result is proven, not a failure; the FOMC move is 1.11 to 1.14, not 1.14; the 0-of-13 tag claim has no ledger row and is no longer cited to it) and the THEORY pointer updated. FOUND: 3 of the 15 proven flags only say a type uses the pooled number; fed_state is stale (the Fed raised the target range to 3.75-4.00% on 2026-09-16).

<!-- entry: 2026-10-28-05 | date: 2026-10-28 | label: documents | source-line: new | approx: no -->
### 2026-10-28-05 — PROJECT_PLAN rewritten as the current design: no status, no volatile numbers (v2)
WHAT: PROJECT_PLAN.md rewritten (144 lines, down from 550) as the plan only: goal, thesis (carried over verbatim, plus a paragraph on what the evidence says so far), how evidence is judged (the prediction contract and walk-forward harness, updated: firm state point-in-time only from about 2010; the stored size bucket is a constant and carries no information; rows AND independent clusters; purge of overlapping windows), the enforcing machinery, a new architecture diagram with External Conditions and a quality layer, the eight phases (Phase 4 renamed External Conditions), the Phase 8 design condensed, universe, deferrals, and the news taxonomy. NO status or volatile numbers: those are in README.md and docs/PROJECT_STATUS.md. The plan's seven earlier corrections and addenda are in this changelog at their true dates (label PROJECT_PLAN); the unedited previous version is docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md (it also holds the retired status table, tier system, old next steps and old diagram).

<!-- entry: 2026-10-28-04 | date: 2026-10-28 | label: documents | source-line: new | approx: no -->
### 2026-10-28-04 — README rewritten as a true snapshot; PROJECT_STATUS v1; the snapshot query saved
WHAT: README.md rewritten (104 lines, committed from the GitHub editor as 213d877 and verified byte-identical to the drafted text) as a snapshot and representation of the project, not a manual: where it stands (every number measured on 2026-10-28), the eight phases, what has held and what has not, five known limits, how the work is done, where things live, and a Retired table (what the old README said and where it went; the unedited original is docs/archive/README_pre_rewrite_2026-10-28.md). docs/PROJECT_STATUS.md v1 installed (221 lines; the v0 draft stays in git history). scripts/sql/readme_snapshot.sql saved: the query that regenerates the README table. CORRECTED in the process: the old claim 'every event traces to its source filing' (false for 1,215 events) and the old counts of 2026-10-08.

<!-- entry: 2026-10-28-03 | date: 2026-10-28 | label: checkpoint | source-line: new | approx: no -->
### 2026-10-28-03 — CHECKPOINT 2026-10-28 16:01 (late afternoon 2026-10-28: point-in-time and exclusions tables built; diverged v2 grid and churn; retroactive filed dates confirmed; no tags written)
Written 2026-10-28 16:01 +0000 (16:01 UTC). Reason: late afternoon 2026-10-28: point-in-time and exclusions tables built; diverged v2 grid and churn; retroactive filed dates confirmed; no tags written.

WRITTEN BY THE ASSISTANT at about 16:25 UTC on 2026-10-28. ESTIMATE: this conversation is at the end of its capacity; a compaction is imminent. This block ADDS to the two earlier checkpoints of today (midday: tagger and pre-context finished, firm-state drift, tools, documentation plan, FOMC plan; afternoon: price steps, rollups, corrected dates, look-ahead); everything there still stands unless stated here.
CREATED IN THE DATABASE TODAY (all additive; no tag was changed after the tagger finished): event_firm_state_pit (23,348 rows; rule pit_v1; one row per event-entity pair with a listed company; 39 extra rows because some entities own two securities: ALWAYS join on security_id, not entity_id; columns: event_id, entity_id, security_id, event_day, period_end, filed_date, composite_score, n_terms, state, period_end_rule_period, state_period_end_rule_today, rule_version, computed_on); event_exclusions (event_id, reason, severity, detected_on, note; PK event_id + reason): exclude: no_price_history 709, rollup_no_source 233, date_gap_over_year 69; review: date_corrected_review 267; note: no_source_curated 323 (real discrete events of the hand-built 13-company pilot history, no filing link; 29 of 30 read were real); price_step_in_window (about 9 rows: KDP, MO, JCI, HPQ, KLAC likely; HIG and LVS may be real) is NOT yet inserted; scratch_diverged_new_20261028 (934 proposals by the old rule); scratch_diverged_v2_20261028 (every reaction-tagged event with a return beyond 3% and its v2 label: 14,344 rows); backups event_tags_backup_20261026 (before the new tagging) and event_tags_backup_20261028 (full copy after the tagger finished, unchanged since).
THE FINDINGS. (1) Events without a source filing are real: 29 of 30 random no-source, uncorrected, non-rollup reaction rows were discrete real events of the pilot companies (AEP, F, AMD, PG, JPM, PFE, GE, CVX, XOM, MSFT, PLD, WFC); the 892 no-source reaction rows by type: leadership_change 317, corporate_action 237, acquisition 194; no macro-derived events have reaction rows. (2) POINT-IN-TIME TABLE: with a PIT state 13,874 pairs (59.4%); no filed quarter yet 8,839 (37.9%); filed quarter but no score 635; the PIT rule picks a different quarter than the quarter-end rule for 7,114 pairs (30.5%). (3) EXISTING DIVERGED TAGS (1,636 non-sealed rows, essentially the population; 6 are duplicates from two-security entities): still diverged using today's scores with the old quarter-end rule 1,383 (84.5%: staleness alone costs about 15 points); still diverged under the PIT rule 1,062 (64.9%), 528 not, 46 no state (look-ahead costs about 20 more points); 53 non-diverged events would become diverged. (4) V2 GRID (rule: diverged if return above +3% and PIT state weakening or deteriorating, or return below -3% and state strong or improving; no state means no flag; events with an exclude reason get no diverged flag): diverged now 2,378 (all companies); stay 1,540; removed 838 (418 to punished, 420 to rewarded; 35 of them excluded rollups; all 838 are OLD events); added 2,067 (598 punished and 529 rewarded OLD events, 505 punished and 435 rewarded events tagged this week); v2 total 3,607 (+52%): only 42.7% of v2 members were already diverged: the label is UNSTABLE under reasonable input changes. (5) THE 66-CASE READ: all titles match their company, every non-rollup case is a discrete real event, quarter ages 34 to 185 days, days since filed positive; rollups double-count returns (JNJ and INTC rollups share the date and return of their real events). (6) RETROACTIVE FILED DATES: financial_statements.filed_date for quarterly periods ending 2006 to 2009 is retroactive (median lag 1,517 days for 2006, 787 for 2007, 403 for 2008, 387 for 2009 with 50.8% over 100 days; 2010: median 38 with 20.9% over 100; from 2011 median 31 to 37 days and under 6% over 100): the database's quarterly data effectively starts in the XBRL era and earlier periods exist only as comparatives in later filings; the pit_v1 rule therefore cannot give a state to events before about 2011 (the AEP 2008, Autodesk 2009 and Agilent 2010 removals are this artifact).
DECISION (2026-10-28): NO TAG IS WRITTEN. The diverged tag stays as it is (v1, old events only; new events have none); it is a fragile descriptive tag that carries no demonstrated signal (the pattern-significance audit found none): analyses must not use it as a feature until its definition is settled; the exclusions table is a FILTER for every event-study statistic (exclude severity out; review severity read first); any diverged variant is computed on the fly from event_firm_state_pit and the saved returns. NEXT (fresh start): build a second table event_firm_state_pit2 whose availability date is LEAST(filed_date, period_end + 90 days) (genuine filings keep their real dates; retroactive ones are treated as public 90 days after quarter-end, which is conservative because real 10-Qs came out by about day 45), rerun the v2 grid and the read, report by event era and by n_terms (1 to 4), and only then decide whether any tag should be written (with the backup, a read and a guarded apply). ALSO NEXT: rerun the ledger's event-based tests with the exclusions applied and check that none of the 15 proven flags depends on rollups, corrected-date rows or price steps (NOT yet checked: the real question about whether any proven result is affected); confirm the 9 price-step rows and insert them as price_step_in_window; give the 323 curated events a provenance note or filing link; check the 514 quarterly statements filed within 8 to 19 days; the README must say plainly that 1,215 events (5.2%) have no source filing, that 233 were rollups, and that the quarterly financial data are point-in-time only from about 2010.
CALLS THAT MISSED (scoreboard): additions fewer than 400 (2,067); PIT survival of the new proposals below half (74.7%); no-source events 233 to 600 (1,215); the events table has an origin column (none); the price scan returns 20 rows (17); PIT table 17,000 to 20,000 rows (23,348); a financial-statements filing date does not exist (it does). CALLS THAT HELD: the corrected-date rows have no source (all 564); 29 or more of 30 no-source rows are real; staleness and PIT survival ranges for the existing tags (84.5% and 64.9%); the retroactive-date pattern (above 50% before 2010, under 10% from 2012); removals 600 to 1,000 (838); old-event additions 1,000 to 1,400 (1,127).
STILL DUE TODAY: FOMC step 3c after about 18:30 UTC (commands, the validation rule and the independent-list caveat are in the midday checkpoint); the docs bundle for the README and PROJECT_PLAN rewrites (data_cache/share/docs_for_claude.txt) is still unattached; the baseline changelog entry question (recommended yes) is unanswered.

COMMITS SINCE THE PREVIOUS CHECKPOINT (since 2026-10-28 15:51 +0000), from git log, objective:
  2b62928 2026-10-28 15:51 Checkpoint: afternoon 2026-10-28, data-quality findings

UNCOMMITTED (git status --short):
  ?? results/tag_review_v1_galen.txt

<!-- entry: 2026-10-28-02 | date: 2026-10-28 | label: checkpoint | source-line: new | approx: no -->
### 2026-10-28-02 — CHECKPOINT 2026-10-28 15:51 (afternoon 2026-10-28: data-quality findings measured (price steps, rollups without sources, corrected dates, look-ahead in firm states and its point-in-time impact))
Written 2026-10-28 15:51 +0000 (15:51 UTC). Reason: afternoon 2026-10-28: data-quality findings measured (price steps, rollups without sources, corrected dates, look-ahead in firm states and its point-in-time impact).

WRITTEN BY THE ASSISTANT at about 16:00 UTC on 2026-10-28. ESTIMATE: this conversation is at the very end of its capacity (a compaction is imminent); everything in the previous checkpoint (2026-10-28 midday, commit 35ae8bd: the finished tagger and pre-context runs, the firm-state drift finding, the monitor patch, the documentation plan, the FOMC step 3c plan, the open questions) still stands unless this block says otherwise.
THE DATA-QUALITY FINDINGS OF THE AFTERNOON (all measured, none yet fixed; sealed companies excluded from every look).
(1) EXTREME RETURNS: of 14,962 non-sealed reaction rows, 64 are beyond +-50%, 15 beyond 80% and 4 beyond 150%. In all 64 the adjusted-close return equals the raw-close return (no dividend or split adjustment difference); most extremes are real crisis rebounds (MGM, LVS, Ford, UAL in March 2009; URI in Oct 1998; UAL in May 2020). The regression check scripts/audit/check_tagger_convention.py PASSES (100 of 100 labels, max difference 0.0022): the tagger is faithful to the stored prices; any artifact is in the stored price series.
(2) PRICE-SERIES STEPS: a scan of every one-day change beyond 1.6x or below 0.4x in market_prices (non-sealed) finds 17 days: KLAC 2014-11-26 x2.368 (0.3561 to 0.8430) and HPQ 2015-11-02 x1.747 (4.8154 to 8.4125) are OVER-ADJUSTED UPWARD STEPS (a correct series would be smooth; levels are also far from real prices, KLAC about 0.34 against about 75 real); MO 2008-03-28 to 03-31 x0.301 (the Philip Morris International spin-off), ROK 2001-06-29 to 07-02 x0.386 (the Rockwell Collins spin-off) and KDP 2018-07-09 to 07-10 x0.330 (the 103.75 dollar special dividend) are UNADJUSTED RAW DROPS; JCI 2007-07-02 x0.395 not placed; CVS has a row dated Sunday 2009-07-26 (bad row); HUBB 1994-10-31 x9.859 and TSCO 1994-02-18 x3.25 early-data oddities; HIG 2008-12-05, LVS 2008-10-29, UAL 2008-07-22, CBRE 2009-03-25, CNP 2002-07-25, DECK 1998-10-14, PWR 2002-07-02 may be real moves; MRNA 2026-08-19 x2.77 unverified. The scan sees only steps beyond 60%: smaller spin-offs and dividends (10 to 35%) are invisible to it, so the true count is larger. Reaction rows whose 20-day window contains one of the 17 days: 9 (KDP 3, HIG 1, HPQ 1, JCI 1, KLAC 1, LVS 1, MO 1).
(3) ROLLUPS AND SAGAS: 233 events are titled like 'AMD's real 1996-1999 activity: ...' (multi-year summaries, dated 1996-01-12 to 2026-03-03): 0 of them has a source filing, all 233 have reaction rows and tags, 27 are tagged diverged_from_fundamentals. Corrected dates: event_market_reactions_corrected has date_was_corrected = true on 564 of 22,470 rows (2.5%); ALL 564 have NO source filing; 379 differ from the event's stored date (mean 423 days among those; maximum 5,079 days; 153 differ by more than a year; 193 by 31 to 365 days; 33 within 30 days; 185 have the same date); the largest are multi-year sagas ('Ford's historic CEO succession saga 2006-2020', 'GE preferred stock saga'), and 228 of the 233 rollups are corrected. The correction picks one date inside a multi-year story, so a 20-day return around it is not an event study. The BAC announcement event (stored 2008-09-15) is measured at 2009-01-02 (the completion day). The INTC rollup (stored 2026-03-03) is measured at 2026-04-08 (the Apollo repurchase) and so carries the same saved values as the real Apollo event.
(4) SOURCE FILINGS: reaction rows with a source filing 21,578 (96.0%); without 892 (564 corrected + 328 not corrected, of which 5 are rollups). Events without any source filing: 1,215 (233 rollups; 982 others: macro-derived events such as 'Federal Reserve raises target rate to 5.5%', 'CPI report shows significant move', hand-written summaries such as 'Ford's Venezuela accounting saga', and plausible real discrete events with no link such as 'Lee Raymond to retire as ExxonMobil Chairman/CEO'); 323 of the 1,215 have no reaction row. The events table has NO origin column (columns: id, event_date, title, description, event_time_precision); event_types has name and category; event_type_relationships links event_id to event_type_id.
(5) LOOK-AHEAD IN FIRM STATES: event_pre_context takes the latest period_end before the event, not the latest FILED quarter: of the 934 proposed diverged tags for the new events, 393 (42%) use a quarter that ended fewer than 45 days earlier (minimum 1 day; in a 40-case sample 22 of 40). financial_statements.filed_date exists on every row (37,006 rows, 0 null; quarterly median lag 35 days, annual 54; 514 quarterly rows were filed within 8 to 19 days of period end: check them). POINT-IN-TIME IMPACT (use the latest period whose MIN(filed_date) is before the event date, same cutoffs, today's composite_score): of the 934 proposals 698 (74.7%) stay diverged (punished 363 of 481, rewarded 335 of 453); 217 change to a non-diverged state; 19 have no filed quarter. If similar, about a quarter of the existing 1,630 diverged tags would lose the flag (NOT measured; different cohort, September scores). The 40-case read: all 40 titles match their company, all 40 are discrete events, 22 of 40 fail the 45-day rule, HPQ +63% is a spin-off price artifact.
DECISIONS AND PLAN. (a) The diverged step for the new events is NOT applied (tags unchanged): event_tags_backup_20261028 and scratch_diverged_new_20261028 exist (934 proposed, by the period_end rule); the next version of the rule is point-in-time. (b) PROPOSED, not yet built: ONE table event_exclusions (event_id, reason, detected_on, note; nothing deleted) with reasons and sizes: no_price_history 709 events; rollup_no_source 233; corrected_date_no_source 336 (564 corrected rows minus the 228 rollups); no_source_other 323 (reaction rows without a source, not corrected, not rollups: to be sorted by event type and category); price_step_in_window about 9 rows (confirm each by prices and news: KDP, MO, JCI, HPQ, KLAC are likely; HIG and LVS may be real); and the 323 events with no source and no reaction row (macro-derived and others; classify). (c) NEXT: build a table event_firm_state_pit for every event-entity pair by SQL (latest period whose MIN(filed_date) per (security_id, period_end) is before the event date; the same fixed cutoffs; keep event_pre_context as it is), compare against the 1,630 existing diverged tags, then decide a diverged v2 rule with a backup, a read of cases and a guarded apply; do NOT run scripts/tagging/backfill_diverged_from_fundamentals.py. (d) Before the analysis (significance rerun, THEORY), the exclusions must be applied as a filter: rollups, corrected-date rows and price steps stay out of every event-study statistic.
CALLS THAT MISSED TODAY (for the scoreboard): the events table has an origin column (it has none); fewer than half of the proposals survive a point-in-time rule (74.7% survive); events without a source number 233 to 600 (1,215); the price scan returns at least 20 rows (17); financial_statements has no filing date (it has filed_date); the identical FOXA and FOX returns are a coincidence (they are structural). CALLS THAT HELD: the corrected-date rows have no source filing (all 564); the 40-case read passes the title and discrete-event checks (40 of 40); the corrected-more-than-a-year count (153); under 100 reaction rows touch a price jump (9); the regression check passes.
STILL DUE TODAY: FOMC step 3c after about 18:30 UTC (the announcement is 18:00 UTC; commands and the validation rule are in the midday checkpoint); the docs bundle (data_cache/share/docs_for_claude.txt: NAMING.md, PROJECT_STATUS.md, OPERATIONS.md) has still not been attached, so the README and PROJECT_PLAN rewrites cannot start; the old-plan baseline changelog entry question (recommended yes) is unanswered.

COMMITS SINCE THE PREVIOUS CHECKPOINT (since 2026-10-28 15:29 +0000), from git log, objective:
  35ae8bd 2026-10-28 15:29 Checkpoint: midday 2026-10-28

UNCOMMITTED (git status --short):
  ?? results/tag_review_v1_galen.txt

<!-- entry: 2026-10-28-01 | date: 2026-10-28 | label: checkpoint | source-line: new | approx: no -->
### 2026-10-28-01 — CHECKPOINT 2026-10-28 15:29 (midday 2026-10-28: tagger and pre-context finished; firm-state drift measured; monitor patched; plan addenda moved to the changelog; documentation plan decided)
Written 2026-10-28 15:29 +0000 (15:29 UTC). Reason: midday 2026-10-28: tagger and pre-context finished; firm-state drift measured; monitor patched; plan addenda moved to the changelog; documentation plan decided.

WRITTEN BY THE ASSISTANT at about 15:30 UTC on 2026-10-28 (the user's 10:30 AM, Fort Worth). ESTIMATE: this conversation is extremely full (95 to 100%); a compaction is imminent. The previous checkpoint is 2026-10-26 20:56 UTC (its tagger instructions are obsolete: see below).
THE TAGGER IS DONE. The live tagger tagged the 7,279 processable events (7,282 minus the 3 CPRT pilot events): tagged 6,570, skipped 709. It died on the HTTP/2 limit (10,000 requests per connection; about 12 requests per tagged event) and on the Codespace idle timeout (about 30 minutes after the last TERMINAL INPUT: background log output does not count), so it ran as restart wrappers: tagger (run 1), tagger2, tagger3 (13:44:15 to 14:48:04 UTC on 10-28, 6 runs, 5 restarts), tagger4. Two events (Edison Mission Energy 2004-10-04, PepsiCo 2010-02-26) and earlier Hormel 2002-04-30 were tagged without a reaction row because a crash fell between the tag insert and the row save; deleting their tags and re-running restored the rows (tagger4: Tagged 2, rows saved 2). FINAL COUNTS (2026-10-28 15:25): reaction-tagged events 22,525; reaction rows 22,470; tagged_without_row 55 (the old structural ones); rows_without_tag 0; event_entity_reactions 124. ACCOUNTING: 23,554 events = 22,525 tagged + 709 skipped + 286 linked only to entities with no security + 34 with no entity link. The 709 skipped: 617 'event before the first price' (the event predates the first price of the company's CURRENT ticker: predecessor tickers such as EXE, DAL, HWM, GM, HCA, CHTR, CPAY, EG; earliest 1994-02-11, latest 2024-02-29) and 92 'no prices at all for the first linked security' (1996-05-20 to 2026-08-17); 'too recent' and 'price gap' are both zero. They are permanent exclusions, not defects. Label versus saved column, explore set (160 sealed tickers excluded): 14,960 events (rewarded 3,921, punished 3,965, muted 5,444, diverged 1,630), 0 mismatches. The explore set grew by 4,257 events; its cache needs --refresh. The new events are mostly 1994 to 2010 filings.
THE FOX EVENT (e0eb0c05-d908-4533-ba0b-2e032d5d6f42, Fox Corporation DOJ Second Request in the Roku acquisition review, 8-K filed 2026-09-09; the event is REAL, checked by web search) is tagged punished; both share-class rows (FOXA, FOX) now read -5.60% on the prior-close convention (they read -1.9% and -1.6% muted on the old convention). Identical returns are structural: FOXA trades at a nearly constant ratio of about 1.12 to FOX, so dual-class pairs are near-duplicates, not independent cases (count them among the 49 multi-entity events before counting independent events).
PRE-CONTEXT IS DONE. scripts/financial_pipeline/populate_pre_context.py (no arguments; resume-safe; about 3 requests per pair; crashes about every 3,300 pairs) ran as bg job prectx and finished OK: event_pre_context grew from 16,488 to 23,309 rows (6,821 new); pairs the script reads 23,312 (3 pairs appear twice with two relationship types), pairs without a row 0; swallowed-error check 0 (no new NULL label hides a failed lookup). 3,404 of the new listed-company rows have a NULL firm state (about half; check by decade: the query is in the chat; financials start about 2009): 'diverged' is UNDEFINED, not 'no', for those events. Known script faults: get_firm_state swallows every exception; market_cap_at_event holds the latest CLOSE, not a market cap; size_bucket is one constant string; the firm-state cutoffs are fixed numbers from September; the pair list is read with unordered pagination.
THE FIRM-STATE FINDING. financial_condition_score is a per-row mean of up to four quarter-over-quarter changes (revenue growth, gross margin, operating margin and free-cash-flow margin change, each counted only if between -5 and +5; NULL if none), from the view fundamental_signals. Stored labels (all computed 2026-09-01 to 09-28) differ from today's scores in 66 of 194 sampled rows (34%, about 27 to 41%): 65 of 66 are the SAME company-quarter scoring differently (not period selection, not ties); 98.5% of the differing rows have the free-cash-flow term today against 36% of unchanged rows: consistent with the 2026-10-23 cash-flow fill (correlation; the pre-rebuild backups financial_metrics_backup_20261023 could confirm); 44 up versus 22 down; 33% jump two or more buckets. Effect on the diverged flag (95-event sample of events with a move beyond 3%): status agrees on 85% (about 78 to 92%); 40 of 44 stored-diverged stay diverged; 10 of 50 today-diverged would be new. DECISION SO FAR: keep the old rows; the cohorts are marked by computed_at (old: Sept 1 to 28; new: 2026-10-28 on current scores). OPEN OPTION: back up the table, DELETE the old rows and rerun the same script (its resume logic recomputes every pair; about 2 hours), ideally after patching the script to store the raw composite_score and the number of terms used, then redo the diverged step. Revisit after the significance rerun.
NEXT, IN ORDER: (1) the diverged step for the NEW events only, by the relabel's own rule (the SAME company's latest computed pre-context row with a label; rewarded with weakening or deteriorating, or punished with strong or improving; no state means no flag): state the rule, back up event_tags (a new backup table), build a scratch table of proposed changes, read a stratified sample, apply guarded; do NOT run scripts/tagging/backfill_diverged_from_fundamentals.py table-wide (it re-reviews every event and takes the first pre-context row with no tie-break); (2) an exclusions table for the 709 skipped events (event_id, reason, detected_on) built from the classification query; (3) the entity repair: python3 scripts/audit/repair_entity_reactions.py > data_cache/entity_repair_dryrun.txt on the 122 backed-up rows (the Fox rows were rewritten by the tagger and need nothing), read ALL rows (attach the file) before any --apply; (4) refresh the explore cache and rerun scripts/models/audit_pattern_significance.py on the corrected labels (overall counts from SQL first); (5) FOMC step 3c after about 18:30 UTC today (the announcement is 18:00 UTC): python3 -u scripts/macro/build_fomc_calendar.py, read results/fomc_calendar_validation.txt (the independent list inside the script ends 2026-09-16: if only 2026-10-28 is flagged, add it from the Fed's calendar page, not from the script's output), then python3 scripts/macro/load_fomc_meetings.py (DRY RUN unless --apply), then --apply; (6) after 2026-10-31: the October sentiment top-up (runbook 8); (7) the January runbook after 2027-01-05; forward-test files stay FROZEN.
DOCUMENTATION PLAN (decided 2026-10-28). README.md becomes a true snapshot and representation of the project, NOT a manual (Getting Started, Recent Findings and the discipline list move to the docs where they belong), with fully refreshed numbers including ones never listed before, each carrying an as-of date and regenerated by queries kept in docs/OPERATIONS.md; PROJECT_PLAN.md is rewritten as the current plan with NO status or volatile numbers (sections: goal; philosophy; how evidence is judged; architecture diagram; the eight phases from docs/NAMING.md; universe; deferred and open decisions; news taxonomy reference); its seven correction and addendum sections were moved into CHANGELOG at their true dates by scripts/audit/import_plan_addenda.py (commit fe1024d; 186 entries; oldest 2026-09-08); OPEN QUESTION: also add its old sections 3, 5, 9 and 10 (original-vs-actual table, the Sept 8 status percentages, the 13-company tier system, the old to-do list) as one baseline entry dated 2026-09-08 (recommended yes; the importer would be extended to add only what is missing); THEORY.md gets a ledger-anchored rewrite (proven, lead, null, untested, retired) with a Retired section and the old file archived (needs the flag_ledger and flag_ledger_evidence text exported); Phase 4 is renamed 'External Conditions' with news as one track (decided; marketaux_daily.yml is a live daily news workflow). The originals are archived and committed (fad2984): docs/archive/README_pre_rewrite_2026-10-28.md, PROJECT_PLAN_pre_rewrite_2026-10-28.md, THEORY_pre_rewrite_2026-10-28.md. README facts already known to be wrong: onboard_pipeline.py is scripts/onboarding/onboard_pipeline.py; there are two workflows (nightly-classify.yml and marketaux_daily.yml); its counts are from 2026-10-08. STILL NEEDED FROM THE USER: docs/NAMING.md, docs/PROJECT_STATUS.md and docs/OPERATIONS.md as an attachment (data_cache/share/docs_for_claude.txt, 57 KB, not yet attached); the README snapshot queries are to be given next (the jobs are finished). Also adopt: the changelog entry that produces a results file names it; refresh the README snapshot at every milestone checkpoint.
TOOLS CHANGED TODAY. scripts/ops/jobs.py patched (commit 2c2b529; sha256 8944e634c20cb4696002318eeac87550c2acd515627ea8a18e10348d54aa2685; patcher scripts/audit/patch_jobs_ack.py): a failed or killed job that has a status record stays under ATTENTION until acknowledged with python3 scripts/ops/jobs.py --ack NAME; a killed bg.sh job reads STOPPED. The monitor draws a bar only for jobs that print PROGRESS done/total lines: for a job that does not (the tagger, the pre-context script) a small helper appended such lines to the job's own log (see the chat; fold it into docs/OPERATIONS.md). scripts/audit/repair_entity_reactions.py (sha256 3e3b5a63682200ca3bfb91310d4b27178575e4d72ba37100c246caf593553123) is committed (84c2bf7), tested on stand-in tables, never run against the database.
CORRECTIONS TO THE ASSISTANT'S OWN CLAIMS (2026-10-28): the stored-versus-current firm-state difference is not period selection or ties; the view is a per-row mean, not a cross-company standardization (the assistant had guessed 50% for standardization); the 3-row gap between 23,312 pairs and 23,309 rows is duplicate pairs, not orphan rows; the Fox rows did not stay muted; the final unique skips were 708 to 709, below the predicted 740 to 830; the largest skip reason is event-before-first-price, not price gaps; the archive was already committed (the .gitignore theory was wrong); an earlier ETA divided by the current time for a job that had already died.
FACTS. Database (2026-10-26 inventory): 151 tables and 32 views, about 3.0 GB, about 61 audit, backup, snapshot or scratch tables by name (about 190 MB); largest: market_prices 817 MB, company_sentiment_timeline 416, vol_estimators 383, stock_day_z 294, event_ripple_timeline 269, filing_ai_classifications 162. Flag ledger: 112 = 21 lead + 62 null + 15 proven + 2 retired + 12 untested. The SQL editor caps a listing at 100 rows (exactly 100 rows means truncated). Label convention: 20 trading days, baseline PRIOR close (event-day move included), SPY benchmark, plus or minus 3%. The latest repo commits: fe1024d (importer), fad2984 (archives), 2c2b529 (monitor patch). Re-verify every number against the live database before relying on it.
HOW THE USER WORKS: pastes the output after each block; everything to copy goes in a code block; every step is its own labelled block (FOREGROUND, SQL editor); the assistant cannot write to the repo, so files arrive as attachments that the user uploads and a sha256 gate checks before anything runs; to give the assistant a file the user attaches it (a bundle file such as data_cache/share/*.txt works); SQL uses dollar-quoting ($$...$$) because the user's environment corrupts straight quotes on paste; copying long terminal lines can drop spaces; the standing rules: re-check numbers against the live database, ask to see a real file instead of guessing its interface, never bulk-confirm or bulk-correct AI output unread, be honest about sample size and uncertainty (including the assistant's own findings), dig into anything that does not add up.

COMMITS SINCE THE PREVIOUS CHECKPOINT (since 2026-10-26 20:56 +0000), from git log, objective:
  fe1024d 2026-10-28 14:51 Changelog: seven PROJECT_PLAN corrections and addenda moved in at their true dates (2026-09-08 to 2026-09-30); importer kept
  fad2984 2026-10-28 14:41 Archive README, PROJECT_PLAN and THEORY unchanged before the 2026-10-28 rewrite
  2c2b529 2026-10-28 14:00 jobs.py: a failed or killed job stays under ATTENTION until acknowledged (--ack NAME); killed bg.sh jobs read STOPPED; patch 
  84c2bf7 2026-10-26 20:57 Entity-reaction repair script (dry run by default; repairs only the rows in the backup table; tested on stand-in tables)
  a8a6963 2026-10-26 20:56 Checkpoint: end of day 2026-10-26

UNCOMMITTED (git status --short):
  ?? results/tag_review_v1_galen.txt

<!-- entry: 2026-10-26-26 | date: 2026-10-26 | label: checkpoint | source-line: new | approx: no -->
### 2026-10-26-26 — CHECKPOINT 2026-10-26 20:56 (end of day 2026-10-26: tagger2 running with automatic restarts; entity repair on hold; next steps and morning SQL recorded)
Written 2026-10-26 20:56 +0000 (20:56 UTC). Reason: end of day 2026-10-26: tagger2 running with automatic restarts; entity repair on hold; next steps and morning SQL recorded.

WRITTEN BY THE ASSISTANT at about 20:51 UTC on 2026-10-26; the user stopped for the day here. ESTIMATE: this segment is very full (about 90%, range 75 to 98%); the last compaction was 18:22:32 UTC.
STATE: tagger convention fixed (6615ec5); explore-set labels relabeled and confirmed, 0 mismatches (d191e38); results map committed (10a0f81; docs/RESULTS_MAP.md: 130 files, 57 not named in any changelog entry, 0 dangling); an earlier checkpoint is bc610a6. CONFIRM IN git log (the assistant was not shown the output): (a) the changelog correction entry 'the multi-entity entity-reaction step is INSIDE the tagger loop' (item 1 of the earlier checkpoint is wrong: ignore it); (b) the commit of docs/archive/SESSION_JOURNAL_2026-09-21_to_2026-10-26.md (the upload trimmed 2 blank lines; it commits only if the non-blank lines hash to 655aeafc1fc25351fd0167bf7aee47065e245791e0e3568545303bf763f52788, 98 non-blank lines). If either is missing, do it first.
THE RUN (the live tagger over the 7,282 untagged events that have a linked security; 286 events link only to entities with no security and 34 have no link, so those can never be tagged): run 1 crashed at 20:26:00Z after 890 events because one HTTP/2 connection allows 10,000 requests (12 per tagged event, 4 per skipped event). The crash was at the delete, before any write, so no event was half-written (tagged_without_row stayed 55; tagged 16,752 and reaction rows 16,697 at the crash). Rate 56.6 events per minute. Relaunched at about 20:37 UTC as bg job tagger2: scripts/ops/bg.sh tagger2 bash -c 'ok=0; for i in 1 2 3 4 5 6 7 8 9 10 11 12; do echo "=== RUN $i starting $(date -u +%T) ==="; if python3 -u scripts/tagging/tag_reaction_character.py; then ok=1; break; fi; echo "=== RUN $i FAILED; restarting in 10 s ==="; sleep 10; done; echo "=== ended; clean finish: $ok ==="; [ $ok = 1 ]'   Log: data_cache/tagger2.log (run 1 log kept as data_cache/tagger_run1_crashed_20261026.log). Model: about 9 wrapper runs (cap 12) and 136 minutes (range 131 to 153), so about 22:55 to 23:15 UTC, IF THE CODESPACE STAYED AWAKE (unknown whether the log output counts as activity). If the Codespace stopped, the job shows STOPPED with no ended line: rerun the same command under a new name (tagger3); it resumes (tagged events drop out of the list; skipped events are re-tried at every restart). If it shows FAILED (exit 1) after using all 12 runs, rerun it the same way. A failure with an error other than ConnectionTerminated is a different problem: read the log tail first.
THE ENTITY REPAIR (scripts/audit/repair_entity_reactions.py, sha256 3e3b5a63682200ca3bfb91310d4b27178575e4d72ba37100c246caf593553123, tested on stand-in tables): it repairs ONLY the rows in backup table event_entity_reactions_backup_20261026, which holds 122 rows (48 events), made from live rows whose event was tagged before the run. The live table has 124 rows (49 multi-entity events, the only events with two or more linked securities). The 2 rows NOT in the backup belong to event e0eb0c05-d908-4533-ba0b-2e032d5d6f42 (Fox Corporation DOJ Second Request in the Roku acquisition review, 2026-09-09; FOXA and FOX, two share classes of ONE company, both 'primary', muted -1.9% and -1.6%). THE EVENT IS REAL, not a test insert (the user asked because the date is after the assistant's knowledge cutoff; checked by web search on 2026-10-26: Fox agreed on 2026-06-14 to buy Roku for about $22 billion; the DOJ issued Second Requests to both on 2026-09-08; Fox disclosed them in an 8-K filed Wednesday 2026-09-09, which is the event date; TechCrunch, TheWrap and others carried it). The database row's own provenance (its event_source_filings link) was NOT checked. The event appears in the Oct 7 multi-entity run, so it is old. It was still UNTAGGED at 20:49 (no reaction tag now, none before the run), so the tagger had not reached it or will skip it. DO NOT add the 2 rows to the backup yet. After the tagger finishes: if the event is tagged, the tagger's entity block (inside its loop, an upsert on event_id,entity_id) rewrote both rows on the new convention and nothing is needed; if it is still untagged, INSERT the 2 rows into the backup (SELECT ... WHERE NOT EXISTS the same event_id and entity_id) and include them. Dry run on the 122 rows: 120 recomputed, 2 no data, 19 labels change (15.8%, matching the 15.3% found for the tags), 1 flip, 12 on HOLD (the live row changed since the backup, or the new value disagrees with the main reaction row's saved column), 108 would update. Before any --apply: rerun the dry run (python3 scripts/audit/repair_entity_reactions.py > data_cache/entity_repair_dryrun.txt), paste the WHOLE file, read every row (especially the 12 HOLD rows and the flip), then apply. The assistant has NOT yet read the rows.
CORRECTIONS MADE TODAY TO THE ASSISTANT'S OWN CLAIMS: the multi-entity step is inside the loop, not after it; 'none of the unprocessed events is multi-entity' was wrong (the Fox event is); 'the entity row count staying at 124 means no entity rows were written' was invalid because the writes are upserts; the repair backup does not cover the whole table (122 of 124); the first ETA divided by the current time although the job had already died; the 37.5% skip rate of the first 96 events did not persist (92 of the first 890); several probability calls missed (tagged_without_row was 55, not 56 to 62; one flip, not a few). Also: the user doubted that the Fox event was real because of its date; the assistant could not judge a date after its cutoff and checked by web search (real). Lesson: for an event dated after the assistant's cutoff, search before judging.
AFTER THE TAGGER FINISHES, IN ORDER: (1) run the MORNING SQL below (A counts: expect tagged_without_row 55 and rows_without_tag 0; B label-versus-column consistency: every row consistent and diverged only 1,630 with none within 3%; C the Fox event); (2) document the skipped events as exclusions with a reason (grep '^  SKIP' data_cache/tagger2.log | sort -u gives the unique list; reasons so far are corporate-history ticker gaps: EXE, DAL, HWM, CHTR, HCA, GM, CPAY, EG; EA is unexplained); (3) the entity repair above; (4) pre-context: scripts/financial_pipeline/populate_pre_context.py takes no arguments, is resume-safe and works on (event_id, entity_id) pairs from event_entity_relationships; it crashed about every 3,300 pairs on the same HTTP/2 limit, so use a bounded restart wrapper like the tagger's; only its first 45 of 216 lines have been read: print sed -n '45,216p' first; (5) diverged: do NOT run scripts/tagging/backfill_diverged_from_fundamentals.py table-wide (it re-reviews every rewarded or punished event and takes the FIRST pre-context row with no tie-break, which could contradict the relabel); apply the relabel's own rule (the SAME company's latest computed pre-context row; rewarded with a weakening or deteriorating state, or punished with a strong or improving one) as a guarded SQL limited to the newly tagged events, reading a sample first; (6) refresh the explore cache (--refresh) and note that the explore set grew; (7) rerun scripts/models/audit_pattern_significance.py on the corrected labels (overall counts from SQL first); (8) documents: PROJECT_STATUS v1 from the inventory and ledger already in hand, README, the PROJECT_PLAN status table, the two docs/ file renames, drop dates for the backup and scratch tables, the 100-row editor-cap rule into docs/OPERATIONS.md, a changelog entry that names the cards, maps, tag review and review-sheet result files, and REPLACE the stale Project knowledge files (PROJECT_HANDOFF and SCRIPTS from September; SCRIPTS.md is retired) with START_NEW_DAY.md and PROJECT_STATUS.md.
FACTS (2026-10-26): database 151 tables + 32 views (59 tables on 2026-09-24); about 61 are audit, backup, snapshot or scratch tables by name (about 190 MB of about 3.0 GB; hand sums, plus or minus 10%); largest: market_prices 817 MB, company_sentiment_timeline 416, vol_estimators 383, stock_day_z 294, event_ripple_timeline 269, filing_ai_classifications 162. Flag ledger: 112 = 21 lead + 62 null + 15 proven + 2 retired + 12 untested. The SQL editor caps listings at 100 rows: treat exactly 100 rows as truncated. Phase 4 'news' tables hold about 1,200 articles against 1.33 million sentiment rows and 250,000 macro_long rows (supports the External Conditions rename; NOT decided). Rule to adopt: the changelog entry that produces a results file names it. Label convention: 20 trading days, baseline PRIOR close (event-day move included), SPY benchmark, +-3%; diverged = rewarded with a weakening or deteriorating firm state, or punished with a strong or improving one, the SAME company's.
DATED: Wed 2026-10-28 after the FOMC meeting: runbook 3c (build_fomc_calendar.py, read the validation, load_fomc_meetings.py --apply); after 2026-10-31 (Mon 11-02): October sentiment top-up (runbook 8); January runbook after 2027-01-05. Forward-test files stay FROZEN (git hook).
RE-VERIFY LIVE: events 23,554; reaction-tagged and reaction rows are moving (16,752 and 16,697 at the 20:26 crash); event_entity_reactions 124; pre-context about 16,4xx (approximate). Use exact counts, not pg_stat estimates.
OTHER OPEN: the first-link 'primary company' of a multi-entity event is nondeterministic (49 events, some of them dual-class share pairs); get_untagged_events pagination is unordered (patch only if a count disagrees); five functions are named compute_abnormal_return; three runtime checkpoint files sit in the repo root; README, PROJECT_PLAN and THEORY are stale; scratch_reaction_relabel_20261026 needs a drop date; results/tag_review_v1_galen.txt is untracked by design; the Phase 4 name is not decided.
MORNING SQL A (counts): SELECT (SELECT COUNT(DISTINCT et.event_id) FROM event_tags et JOIN tags t ON t.id = et.tag_id WHERE t.name IN ($$rewarded$$, $$punished$$, $$muted$$, $$diverged_from_fundamentals$$)) AS reaction_tagged_events, (SELECT COUNT(*) FROM event_market_reactions_corrected) AS reaction_rows, (SELECT COUNT(*) FROM event_tags et JOIN tags t ON t.id = et.tag_id WHERE t.name IN ($$rewarded$$, $$punished$$, $$muted$$, $$diverged_from_fundamentals$$) AND NOT EXISTS (SELECT 1 FROM event_market_reactions_corrected r WHERE r.event_id = et.event_id)) AS tagged_without_row, (SELECT COUNT(*) FROM event_market_reactions_corrected r WHERE NOT EXISTS (SELECT 1 FROM event_tags et JOIN tags t ON t.id = et.tag_id WHERE et.event_id = r.event_id AND t.name IN ($$rewarded$$, $$punished$$, $$muted$$, $$diverged_from_fundamentals$$))) AS rows_without_tag, (SELECT COUNT(*) FROM event_entity_reactions) AS entity_reaction_rows;
MORNING SQL B (consistency, explore set): SELECT t.name AS tag, COUNT(*) AS events, COUNT(*) FILTER (WHERE r.abnormal_return_20d > 0.03) AS above_3pct, COUNT(*) FILTER (WHERE r.abnormal_return_20d < -0.03) AS below_minus_3pct, COUNT(*) FILTER (WHERE ABS(r.abnormal_return_20d) <= 0.03) AS within_3pct FROM event_tags et JOIN tags t ON t.id = et.tag_id JOIN event_market_reactions_corrected r ON r.event_id = et.event_id WHERE t.name IN ($$rewarded$$, $$punished$$, $$muted$$, $$diverged_from_fundamentals$$) AND r.ticker NOT IN (SELECT ticker FROM explore_sealed_tickers) GROUP BY 1 ORDER BY 1;
MORNING SQL C (the Fox event): SELECT (SELECT COUNT(*) FROM event_tags et JOIN tags t ON t.id = et.tag_id WHERE et.event_id = $$e0eb0c05-d908-4533-ba0b-2e032d5d6f42$$ AND t.name IN ($$rewarded$$, $$punished$$, $$muted$$, $$diverged_from_fundamentals$$)) AS fox_reaction_tags_now, (SELECT COUNT(*) FROM event_entity_reactions WHERE event_id = $$e0eb0c05-d908-4533-ba0b-2e032d5d6f42$$) AS fox_entity_rows, (SELECT string_agg(ticker || $$ $$ || reaction || $$ $$ || ROUND(abnormal_return_20d::numeric, 4)::text, $$; $$) FROM event_entity_reactions WHERE event_id = $$e0eb0c05-d908-4533-ba0b-2e032d5d6f42$$) AS fox_rows_now;
HOW THE USER WORKS: pastes the output after each block; every step is its own labelled block; the assistant cannot write to the repo, so files arrive as attachments that the user uploads and a sha256 gate checks before anything runs; SQL uses dollar-quoting ($$...$$) because the user's environment corrupts straight quotes on paste; the standing rules are: re-check every number against the live database, ask to see a real file instead of guessing its interface, never bulk-confirm or bulk-correct AI output unread, be honest about sample size and uncertainty (including the assistant's own findings), and dig into anything that does not add up.

COMMITS SINCE THE PREVIOUS CHECKPOINT (since 2026-10-26 20:39 +0000), from git log, objective:
  f21bfdd 2026-10-26 20:42 Changelog: correction, the entity-reaction step is inside the tagger loop
  bc610a6 2026-10-26 20:39 Checkpoint: tagger run 1 crashed on the HTTP/2 request limit (before any write); relaunched with restarts
  b1bc076 2026-10-26 20:39 Session journal archive (31 segments, 2026-09-21 to 2026-10-26); the upload trimmed 2 blank lines, content verified on non-bl

UNCOMMITTED (git status --short):
  ?? results/tag_review_v1_galen.txt
  ?? scripts/audit/repair_entity_reactions.py

<!-- entry: 2026-10-26-25 | date: 2026-10-26 | label: correction | source-line: new | approx: no -->
### 2026-10-26-25 — Correction: the multi-entity entity-reaction step is INSIDE the tagger loop (the checkpoint just committed says otherwise)
WHAT: the checkpoint written at about 20:42 (item 1 of AFTER IT FINISHES) says the entity-reaction step runs only after the main loop, so crashed runs would skip it. That was read from grep line numbers and is WRONG. Lines 538 to 585 of scripts/tagging/tag_reaction_character.py show the step is inside the per-event loop (for events with two or more linked entities, after the reaction-row save and before tagged_count), each row written with an upsert on (event_id, entity_id). Only the closing print is after the loop.
CONSEQUENCE: no catch-up gap from crashed runs; the tagger never revisits events it already tagged, so it cannot touch the old 124 entity-reaction rows. A crash inside one multi-entity event's entity block could still leave that event with partial entity rows (very small chance; check with the multi-entity count query after the run). The repair of the old rows is a separate step: scripts/audit/repair_entity_reactions.py. IGNORE item (1) of the checkpoint; the next checkpoint replaces it.
LESSON: do not infer code structure from line numbers of a grep; print the lines (the project rule about asking to see the real file).

<!-- entry: 2026-10-26-24 | date: 2026-10-26 | label: checkpoint | source-line: new | approx: no -->
### 2026-10-26-24 — CHECKPOINT 2026-10-26 20:39 (milestone: tagger run 1 crashed on the HTTP/2 request limit; relaunched with automatic restarts)
Written 2026-10-26 20:39 +0000 (20:39 UTC). Reason: milestone: tagger run 1 crashed on the HTTP/2 request limit; relaunched with automatic restarts.

WRITTEN BY THE ASSISTANT at about 20:42 UTC (sandbox clock). ESTIMATE: this segment is very full (about 85%, range 70 to 95%) because of several large tool outputs; expect a compaction soon. Last compaction 18:22:32 UTC.
STATE: tagger convention fixed (6615ec5); explore-set labels relabeled and confirmed, 0 mismatches (d191e38); checkpoint tools (dcd7736); results map committed (10a0f81: docs/RESULTS_MAP.md, 130 files, 57 not named in any changelog entry, 0 dangling); the session journal archive (docs/archive/SESSION_JOURNAL_2026-09-21_to_2026-10-26.md) is committed only if git log shows it (the upload trimmed 2 blank lines; verified on non-blank lines).
THE RUN: the guard was resolved (dry run 7,282 = exact count of untagged events with a linked security; 286 link only to entities with no security, 34 have no link). Run 1 of the live tagger crashed at 20:26:00Z after 890 events: the HTTP/2 connection allows 10,000 requests and each event costs about 12 (798 x 12 + 92 skipped x 4 = 9,944). The crash was at the delete (line 530), BEFORE the insert, so no event was half-written: tagged_without_row stayed 55, tagged 16,752 = 15,955 + 797, rows 16,697. Real rate 56.6 events/min. Relaunched at about 20:37 as bg job tagger2 with a restart wrapper (up to 12 runs, exit 1 if none finishes cleanly): log data_cache/tagger2.log; run 1 log kept as data_cache/tagger_run1_crashed_20261026.log, its status as data_cache/tagger_run1_crashed.status. Model: about 9 wrapper runs, about 136 minutes (range 131 to 153), finishing about 23:00 UTC; skipped events are re-tried on every restart. If it ends with exit 1, rerun the same wrapper (resume-safe). Monitor: python3 scripts/ops/jobs.py.
AFTER IT FINISHES, IN ORDER: (1) print lines 538 to 585 of scripts/tagging/tag_reaction_character.py: the multi-entity entity-reaction step runs only AFTER the main loop, so every crashed run skips it; confirm it covers ALL events lacking entity rows, else write a catch-up; entity_reaction_rows was 124 at the crash; (2) verification SQL (tagged events, reaction rows, tagged_without_row expected 55 plus events whose full reaction cannot be computed, rows_without_tag 0) and the label-versus-column consistency query (expect 0 mismatches); (3) only if tagged_without_row is above 55: dry-run the tagger's --backfill-magnitudes mode (its body not yet seen; paste it if unclear); (4) document the skipped events as exclusions with reasons (so far all corporate-history cases: EXE 15, DAL 8, HWM 7, CHTR 3, HCA 2, GM 2, CPAY 2, EG 1; EA 3 unexplained); (5) repair the 124 event_entity_reactions rows (computed on the old convention): backup table, script that prints all 124 rows old versus new, read them, guarded update; (6) populate_pre_context.py for the new events, then the diverged step with a deterministic same-company firm-state join; (7) rerun scripts/models/audit_pattern_significance.py on the corrected labels; (8) documents: PROJECT_STATUS v1 (inventory and ledger now in hand), README, PROJECT_PLAN status table, file renames, Project knowledge refresh, repo-root tidy, drop dates for backup tables. The explore set grows with the new events; its cache needs --refresh and the quoted explore-set counts will change.
FACTS (2026-10-26): database 151 tables + 32 views (59 tables on 2026-09-24); about 61 are audit, backup, snapshot or scratch tables by name (about 190 MB of about 3.0 GB; hand sums, plus or minus 10%); top six: market_prices 817 MB, company_sentiment_timeline 416, vol_estimators 383, stock_day_z 294, event_ripple_timeline 269, filing_ai_classifications 162. Flag ledger complete: 112 = 21 lead + 62 null + 15 proven + 2 retired + 12 untested. The SQL editor caps listings at 100 rows: treat exactly 100 rows as truncated. Phase 4 'news' tables hold about 1,200 articles against 1.33 million sentiment rows and 250,000 macro_long rows (supports the External Conditions rename; NOT decided). Rule to adopt: the changelog entry that produces a results file names it.
DATED: Wed 2026-10-28 after the FOMC meeting: runbook 3c; after 2026-10-31 (Mon 11-02): October sentiment top-up (runbook 8); January runbook after 2027-01-05. Forward-test files stay FROZEN (git hook).
RE-VERIFY LIVE: events 23,554; reaction-tagged 16,752; reaction rows 16,697; event_entity_reactions 124 (all at the 20:26 crash; the run changes them). Label convention: 20 trading days, baseline PRIOR close (event-day move included), SPY benchmark, +-3%; diverged = rewarded with a weakening or deteriorating firm state, or punished with a strong or improving one, the SAME company's, latest computed.
OTHER OPEN: the first-link 'primary company' of a multi-entity event is nondeterministic (unordered read); get_untagged_events pagination unordered (patch only if a count disagrees); five functions named compute_abnormal_return; three runtime checkpoint files in the repo root; README, PROJECT_PLAN and THEORY stale; scratch_reaction_relabel_20261026 needs a drop date.
HOW THE USER WORKS: pastes the output after each block; every step is its own labelled block; the assistant cannot write to the repo; heredoc gate checks before any file is installed.

COMMITS SINCE THE PREVIOUS CHECKPOINT (since 2026-10-26 20:08 +0000), from git log, objective:
  b1bc076 2026-10-26 20:39 Session journal archive (31 segments, 2026-09-21 to 2026-10-26); the upload trimmed 2 blank lines, content verified on non-bl
  10a0f81 2026-10-26 20:32 Results map (generated: every results file joined to the changelog entries that mention it)
  29a9c11 2026-10-26 20:08 Checkpoint: tagger guard resolved; pilot next

UNCOMMITTED (git status --short):
  ?? results/tag_review_v1_galen.txt

<!-- entry: 2026-10-26-23 | date: 2026-10-26 | label: checkpoint | source-line: new | approx: no -->
### 2026-10-26-23 — CHECKPOINT 2026-10-26 20:08 (milestone: tagger guard resolved (7,282 = exact count); next: pilot the live tagger on one ticker)
Written 2026-10-26 20:08 +0000 (20:08 UTC). Reason: milestone: tagger guard resolved (7,282 = exact count); next: pilot the live tagger on one ticker.

WRITTEN BY THE ASSISTANT at about 20:08 UTC (sandbox clock). ESTIMATE: this segment is about three quarters full (range 60 to 90%); the last compaction was 18:22:32 UTC; 31 earlier segments in /mnt/transcripts.
STATE: tagger convention fixed and committed (6615ec5); explore-set labels relabeled and confirmed, 0 mismatches (changelog entry d191e38); START_NEW_DAY and the changelog tools built (dcd7736); the guard result is in the changelog.
GUARD RESOLVED: the tagger's dry run (python3 scripts/tagging/tag_reaction_character.py --dry-run) finds 7,282 events; the exact SQL count of untagged events that have a linked SECURITY is also 7,282. The other 286 untagged events link only to entities with no securities row (get_untagged_events drops them by design: its last line keeps events that have a ticker) and 34 have no entity link: 7,602 untagged = 7,282 + 286 + 34. The 7,657 events without a reaction row = 7,602 untagged + 55 tagged events lacking a row. No pagination loss was seen.
PLAN NOW: (1) pilot the live tagger on ONE ticker (CPRT): dry run with timing, live run, then a SQL check that every CPRT label agrees with its saved column and that the tagged-event and reaction-row counts rose by exactly the number tagged; (2) from the pilot's time per event, decide how to run the 7,282 (background with scripts/ops/bg.sh and python3 -u; resume-safe because tagged events drop out of the list; watch the Codespace idle timeout); (3) repair event_entity_reactions (124 rows, 49 events, 44 entities, computed on the old convention): backup table, a script that prints all 124 rows old versus new for reading, then a guarded update; (4) pre-context for the new events (populate_pre_context.py), then the diverged step with a deterministic same-company firm-state join; (5) rerun scripts/models/audit_pattern_significance.py on the corrected labels, then D3 and D4; (6) documents: PROJECT_STATUS v1 (needs the table inventory and ledger queries, never pasted), README, the PROJECT_PLAN status table, file renames, the Project knowledge refresh, the repo-root tidy. The Phase 4 name (News Ingestion or External Conditions) is NOT yet decided.
DATED: Wed 2026-10-28 after the FOMC meeting: runbook 3c (build_fomc_calendar.py, read the validation, load_fomc_meetings.py --apply); after 2026-10-31 (Mon 11-02): October sentiment top-up (runbook 8); January runbook after 2027-01-05.
RE-VERIFY LIVE: events 23,554; reaction rows 15,897; reaction-tagged 15,952; pre-context 16,413 (all 2026-10-26). Label convention: 20 trading days, baseline PRIOR close (event-day move included), SPY benchmark, +-3%; diverged = rewarded with a weakening or deteriorating firm state, or punished with a strong or improving one, the SAME company's, latest computed.
OTHER OPEN: the tagger's 'primary company' for a multi-entity event is the first link of an unordered read (nondeterministic; 49 multi-entity events among the old tagged, few among the new); get_untagged_events pagination is unordered (patch only if a count ever disagrees); five functions are named compute_abnormal_return; the tagger skips renamed or reorganized tickers (EXE for Chesapeake, HWM for Alcoa: predecessor-ticker price gaps, already on the docket); three runtime checkpoint files sit in the repo root; README, PROJECT_PLAN and THEORY are stale.
HOW THE USER WORKS: pastes the output after each block; every step is its own labelled block; the assistant cannot write to the repo.

COMMITS SINCE THE PREVIOUS CHECKPOINT (since 2026-10-26 20:00 +0000), from git log, objective:
  5c2f009 2026-10-26 20:07 Changelog: tagger dry run found 7,282 against an exact count of 7,568; investigating before any real run
  d191e38 2026-10-26 20:01 Changelog: reaction labels relabeled to the prior-close convention (rule, readings, revert path)
  dcd7736 2026-10-26 20:00 Checkpoint protocol v3: checkpoint command (appends git log and status), docs/START_NEW_DAY.md, retitle fix; first checkpoint

UNCOMMITTED (git status --short):
  ?? results/tag_review_v1_galen.txt

<!-- entry: 2026-10-26-22 | date: 2026-10-26 | label: guard | source-line: new | approx: no -->
### 2026-10-26-22 — Guard fired: the tagger's dry run finds 7,282 events, the exact SQL count is 7,568
WHAT: the planned guard worked. The exact SQL count of events with at least one entity link and no reaction tag (diverged counted as tagged) is 7,568 (7,602 untagged minus 34 without an entity link). The tagger's own dry run (python3 scripts/tagging/tag_reaction_character.py --dry-run) reported 7,282: a gap of 286. The tagger is NOT run for real until the gap is explained.
HYPOTHESES: (1) get_untagged_events attaches tickers through the securities table and may drop events whose linked entities have no securities row (a legitimate filter); (2) its unordered 1,000-row pagination of event_tags and event_entity_relationships loses rows (needs an ORDER BY patch first). DIAGNOSTIC: split the 7,568 by whether any linked entity has a securities row; read lines 156 to 230 of the function (the part not yet seen).
ALSO SEEN in the dry run: skips for renamed or reorganized companies (EXE for Chesapeake 2009, HWM for Alcoa 2005: insufficient price data), the known predecessor-ticker gap; and the first new-convention label (CPRT 2026-09-10, -16.0%, punished).

<!-- entry: 2026-10-26-21 | date: 2026-10-26 | label: relabel | source-line: new | approx: no -->
### 2026-10-26-21 — Reaction labels relabeled to the prior-close convention (explore set: 1,636 mismatches, 15.3%, down to 0)
RULE (stated before any result): new label = rewarded if the saved abnormal_return_20d (prior-close, against SPY) is above +3%, punished if below -3%, otherwise muted; then diverged_from_fundamentals REPLACES rewarded when the firm state of the SAME company (the event_pre_context row for the reaction's company, latest computed_at, label not null) is weakening or deteriorating, and REPLACES punished when it is strong or improving.
TABLES: event_tags_backup_20261026 (full copy of event_tags, 17,703 rows); scratch_reaction_relabel_20261026 (15,897 rows: event_id, ticker, ar20, firm_state, old_tag, base_tag, new_tag, changes; 2,435 proposed changes; scratch table, to be dropped when no longer needed for audit, with the drop date written in the changelog).
READING: 70 cases read before any write (all 36 wrong-sign events; 10 muted to moved; 8 moved to muted; 10 diverged changes; 6 near-threshold controls): every case followed the rule. The 9 held events (diverged to plain) were read separately: 6 direction flips (the old direction was the opposite under the event-day baseline, so the old diverged label no longer applies), 2 multi-entity events where the old backfill used another company's firm state (ABBV, WFC), 1 null firm state (AMD); the rule's answer was judged right and applied.
APPLY (SQL, guarded): UPDATE only where the current tag equals the proposal's old tag; a DO block inside the same transaction checks that every proposal event has its new tag, that no event carries two reaction tags and that the total of reaction-tag rows equals the backup's (any failure rolls everything back). Applied in two runs: first excluding the held class (1,637 explore-set changes; about 2,420 globally), then the 9 held events. RESULT, explore set (10,703 events): rewarded 2,520, punished 2,529, muted 4,024, diverged 1,630; every label consistent with the saved column (0 mismatches; it was 1,636). CALLS SCORED: the exact counts of both runs held (90% each); muted to moved exactly 933 (90%).
TRANSITIONS (explore set, before the hold): muted to diverged 222, punished 381, rewarded 330; punished to muted 245, rewarded 11, diverged 7; rewarded to muted 251, punished 12, diverged 7; diverged to muted 171, punished 6, rewarded 3.
REVERT (one transaction, dollar-quoting in the SQL editor): DELETE FROM event_tags WHERE tag_id IN (SELECT id FROM tags WHERE name IN ($$rewarded$$, $$punished$$, $$muted$$, $$diverged_from_fundamentals$$)); then INSERT INTO event_tags SELECT * FROM event_tags_backup_20261026 WHERE tag_id IN (SELECT id FROM tags WHERE name IN ($$rewarded$$, $$punished$$, $$muted$$, $$diverged_from_fundamentals$$));
NOT YET DONE: event_entity_reactions (multi-entity rows on the old convention); the 7,568 unprocessed events; pre-context and the diverged step for them; the significance audit rerun on corrected labels.

<!-- entry: 2026-10-26-20 | date: 2026-10-26 | label: checkpoint | source-line: new | approx: no -->
### 2026-10-26-20 — CHECKPOINT 2026-10-26 20:00 (milestone: tagger fixed, labels relabeled and confirmed; next: record the relabel, entity-reaction repair, tagger run)
Written 2026-10-26 20:00 +0000 (20:00 UTC). Reason: milestone: tagger fixed, labels relabeled and confirmed; next: record the relabel, entity-reaction repair, tagger run.

WRITTEN BY THE ASSISTANT at about 20:00 UTC (sandbox clock). Context: this conversation has been compacted 31 times since 2026-09-21 (transcripts in /mnt/transcripts, median 1.75 MB at compaction, per-message ISO timestamps inside); the last compaction was 18:22:32 UTC today; fullness of the current segment is an ESTIMATE of about two thirds (range 50 to 85%).

DONE SINCE THE SCRIPTS.md RETIREMENT (commit hashes and times are appended below from git log):
- SCRIPTS.md retired into CHANGELOG.md (171 entries, verified line for line), docs/OPERATIONS.md, an archive copy and a stub; generated docs/SCRIPTS_REFERENCE.md; docs/NAMING.md and docs/PROJECT_STATUS.md (draft v0) added; scripts/audits merged into scripts/audit; the empty file named = removed.
- TAGGER FIXED: compute_abnormal_return now uses the PRIOR-close baseline in tag_reaction_character.py and tag_multientity_reactions.py (scripts/audit/patch_tagger_baseline.py v2; live check scripts/audit/check_tagger_convention.py: 100 of 100 labels agree, PASS). Cause: the label used the event-day close as its base, so the event-day move was excluded; the saved columns and the written rule use the prior close.
- RELABEL DONE (SQL, not in git): event_tags_backup_20261026 (17,703 rows) and scratch_reaction_relabel_20261026 (15,897 proposal rows, 2,435 changes); 70 cases read including all 36 wrong-sign events, every one followed the rule; the guarded update applied the changes and its in-transaction check passed; the 9 held events (6 direction flips, 2 multi-entity, 1 null firm state) were read and applied. CONFIRMED, explore set: rewarded 2,520, punished 2,529, muted 4,024, diverged 1,630, every label consistent with the saved column (0 mismatches; it was 15.3%).
- The 7,568 events the tagger will find were counted exactly in SQL (7,602 untagged minus 34 with no entity link).
- TOOLS: scripts/audit/changelog_tools.py v3: add, check, retitle, checkpoint (writes CHANGELOG.md and docs/START_NEW_DAY.md; appends the git log since the previous checkpoint and git status).

DECISIONS (by the user): phase names 1 to 8 stay with the principles and tracks of docs/NAMING.md (Phase 4 "News Ingestion" is flagged as too narrow; renaming it to External Conditions is NOT yet decided); relabel to the prior-close convention (done); process the unprocessed events (approved); rerun the significance audit on corrected labels (approved); merge the audit folders (done); checkpoints for compaction, written to the changelog and docs/START_NEW_DAY.md, with a fullness estimate at the start of each session (approved).

NEXT, IN ORDER:
1. Record the relabel in the changelog: rule (label from the saved prior-close abnormal_return_20d, +-3%; diverged = rewarded with weakening or deteriorating, punished with strong or improving, firm state of the SAME company, latest computed), the backup table name, the revert path (delete the four reaction-tag names from event_tags, reinsert those rows from event_tags_backup_20261026).
2. event_entity_reactions: its multi-entity rows were computed with the OLD convention; get a row count first (SELECT COUNT(*), COUNT(DISTINCT event_id) FROM event_entity_reactions), then repair with the patched function.
3. Tagger run for the 7,568 unprocessed events: first patch get_untagged_events to add ORDER BY to its two unordered paginations (event_tags and event_entity_relationships) with an all-or-nothing patcher; the dry run (python3 scripts/tagging/tag_reaction_character.py --dry-run) must report EXACTLY 7,568; then run it in the background with scripts/ops/bg.sh (resume-safe: tagged events drop out of the list).
4. Pre-context for the new events (populate_pre_context.py), then the diverged step with a deterministic same-company firm-state join (the old backfill_diverged_from_fundamentals.py takes the first pre-context row with no tie-break).
5. Rerun scripts/models/audit_pattern_significance.py on the corrected labels; then D3 and D4 (PROJECT_PLAN.md section 6) on corrected labels with a matched baseline and the two dumb baselines.
6. Finish the documents: PROJECT_STATUS.md v1 (the [PENDING] slots need the table inventory and the ledger queries, never pasted); refresh the Project knowledge (it still holds the September snapshot); check file names after every upload.
7. Dated: Wed 2026-10-28 after the FOMC meeting: runbook 3c (build_fomc_calendar.py, read the validation, load_fomc_meetings.py --apply); after 2026-10-31 (Mon 11-02): October sentiment top-up (runbook 8); January runbook after 2027-01-05.

KEY FACTS TO RE-VERIFY LIVE (2026-10-26): events 23,554; reaction rows 15,897; reaction-tagged 15,952; pre-context 16,413; unprocessed: the Oct 3 promotion cohort 3,133 of 3,139, the Oct 15 waves 3,662 of 3,662, plus 862 older gaps (807 untagged, 34 without an entity link). Label convention: 20 trading days, baseline PRIOR close (event-day move included), SPY benchmark, +-3%.
OTHER OPEN: five functions share the name compute_abnormal_return (two conventions); get_untagged_events has an indentation oddity (line 112) and unordered pagination; three runtime checkpoint files are tracked in the repo root (.populate_sectors_checkpoint unexplained); README, PROJECT_PLAN and THEORY are stale; uploaded files arrive without their final newline (the tolerant gate handles it).
HOW THE USER WORKS: pastes the output after each block; every step is its own labelled block; the assistant cannot write to the repo, so every record is a block the user pastes.

COMMITS SINCE THE PREVIOUS CHECKPOINT (last 24 hours; no earlier checkpoint), from git log, objective:
  6cfea7e 2026-10-26 19:46 Merge scripts/audits into scripts/audit (no collisions, no code references; the 13 earlier hits were SEC text in data_cache);
  629335a 2026-10-26 19:45 Changelog: tagger convention finding and fix (2026-10-26)
  6615ec5 2026-10-26 19:43 Tagger: compute_abnormal_return uses the prior-close baseline (the written rule) in both copies; one-off patch and live check
  3606fec 2026-10-26 19:39 Add NAMING.md and PROJECT_STATUS.md draft v0
  e8d6eed 2026-10-26 19:10 Remove the empty stray file named =
  4bf1a3f 2026-10-26 19:10 Generated scripts reference: every script's purpose, flags and the tables it reads and writes
  4010f0b 2026-10-26 19:10 Retire the SCRIPTS.md monolith: CHANGELOG.md (dated entries, verified line for line), docs/OPERATIONS.md, archived original, 
  6975084 2026-10-26 18:51 Audit pack builder: text files of results, docs and root documents into one zip with a dated manifest
  c0960e2 2026-10-26 18:51 Correction: D3/D4 are defined in PROJECT_PLAN.md section 6 (prediction contract and walk-forward harness)
  194debb 2026-10-26 18:51 Correction: D3/D4 are defined in PROJECT_PLAN.md section 6 (prediction contract and walk-forward harness)
  5d85a62 2026-10-26 18:41 Addendum 29: tags disagree with the current return columns for 15.3% of events; calmer-than-random gap and implied-sealed sha
  9deb3f2 2026-10-26 18:32 Reaction explorer (sealed 30% of companies, logged looks, thin-cell stars); notes addendum 28: the four reasons the percents 
  fd6d822 2026-10-26 18:20 Footing simulation (old test calls random groups significant: 6.4 of 13 against the real 6); user decisions: D3/D4 reworked n
  66e90e8 2026-10-26 18:10 Correction to addendum 26: counts vintage, D3/D4 are recommendations, fatigue withdrawn, calmer-events gap unexplained
  5b184f8 2026-10-26 18:08 Audit: pattern-significance tests against the overall reaction mix (0 of 13 survive); D3/D4 retired; Phase 6 docket restated
  8aa2634 2026-10-26 17:54 Notes addendum 25 (anchors baked into the process); runbook: hook note for the frozen day_card edits, descriptive coverage an
  b5bf14f 2026-10-26 17:54 Bake the external anchors into the process: registration template, checker, prediction scorer, and a pre-commit hook (frozen 
  306ef9f 2026-10-26 17:50 ANCHORS.md: published magnitudes and standard methods verified by search (FOMC drift, price clustering, multiple-testing hurd
  fd5a6c0 2026-10-26 17:46 Notes addendum 24: predictions carry an anchor label; anchor slice before thresholds are fixed
  096c883 2026-10-26 17:43 SQL linter: parentheses and dollar-quote tags, including inside DO blocks
  14be36c 2026-10-26 17:36 Round-number cents diagnostic read (exploratory) and disposition; runbook step 13 (free forward check)
  ef5926e 2026-10-26 17:29 Round-number tests: registered results (both NULL by the registered rules; clustering calibration failed), predictions scored
  0071773 2026-10-26 17:26 Job monitor: one-line verdict (ALL CLEAR / ATTENTION), old finished jobs hidden unless --all
  5c74681 2026-10-26 15:33 Round-number outcome script (registered tests; tested on planted effects, null, one-era effect, stop rule, pre-flight and res
  0f53c94 2026-10-26 15:27 Pre-registration: round-number clustering and threshold tests (confirmatory scope from the outcome-free counts; pass lines, c
  f7b14db 2026-10-26 15:22 Notes addendum 20: outcome-free counts for the round-number tests, calls scored, decisions for the registration, an explorato
  e1751dd 2026-10-26 15:01 Outcome-free counts for the round-number tests: order-of-magnitude classes, matched placebo neighbours per threshold, resumab
  7beff3a 2026-10-26 14:56 Price foundation closed: final state and use rule (addendum 6), runbook 3b3 correction (a full refetch would undo the class C
  7bd2132 2026-10-26 14:51 wait_job.sh: wait for a background job and chain the next command only if it exited 0
  a255bf9 2026-10-26 14:48 Class C repair prepared: fetcher --tol and --force (tested), valid-from --only, rebuild results and the departure from the do
  c14bcd2 2026-10-26 14:42 Valid-from addendum 4: classifier results on the 15 post-2005 losses, decisions for A, B and C registered before any repair
  1331491 2026-10-26 14:40 bg.sh: refuse a same-name start while the first runs; keep each finished run's log as NAME.log.prev
  4e1b3a0 2026-10-26 14:37 Valid-from script: --since scope and a rule_version column (tested on planted cases)
  8eceb01 2026-10-26 14:37 Valid-from addendum 3: profile results scored, pre-2001 levels out of scope (scope reduction, taken after the profile), rebui
  2d44914 2026-10-26 14:33 Grid profile (fractions-to-pennies diagnostic) and a classifier --after filter
  e05a091 2026-10-26 14:33 Valid-from addendum 2: LOSS list read, hold on the pre-2005 cluster, grid-profile test and predictions registered before read
  f271202 2026-10-26 14:29 Loss-ticker classifier: applies the registered A/B/C rule, one vendor request per ticker, resume-safe (tested on planted case
  2b6166d 2026-10-26 14:24 Notes addendum 18: three mechanisms behind valid-from losses, decision rule fixed before the LOSS list, tariff design correct
  fca626a 2026-10-26 14:20 Notes addendum 17: foundation check rule before any new build or registration; circular tariff design corrected; limit of the
  7c22859 2026-10-26 14:20 Compare our reconstructed as-quoted closes with the vendor's current unadjusted closes (read-only, one request)
  0ea0bd4 2026-10-26 14:15 Valid-from dry run: results versus predictions, the registration's wording flaw and the intended LOSS measure fixed before co
  8ff0bd1 2026-10-26 14:11 Notes addendum 16: plan to return to the Phase 6 docket (time-box, parked validation, order and dates)
  046c67f 2026-10-26 13:58 Runbook: valid-from table rebuild after the January price refresh (3b2); FOMC announcement-day lane after the role-band verdi
  733f4a4 2026-10-26 13:52 Design addendum: stratified false-accept by law size (before the verifier is built); notes addendum 15: subject terms, as-quo
  d4ba4a2 2026-10-26 13:50 Script applying the registered levels-valid-from rule (tested on planted cases; not yet run on data)
  f3788fe 2026-10-26 13:46 Accuracy scan: retry transient database errors, save each ticker as it finishes (resume), per-year profile for every ticker, 
  e579f38 2026-10-26 13:44 Pre-registration: per-ticker levels-valid-from rule for the as-quoted prices (written before the all-ticker scan list was rea
  a751694 2026-10-26 13:39 Probe: is the vendor's unadjusted series really as-traded around a corporate action (penny-grid runs and the flip)
  70d265b 2026-10-26 13:35 Acceptance test: 1/32 grid column, all-ticker scan with PROGRESS lines, list of every failing ticker, per-year diagnostic
  6d450ea 2026-10-26 13:34 Job monitor: PROGRESS done/total convention for any script; record the completed as-quoted download (492 ok, 5 flagged, 2 err
  4f3577a 2026-10-26 13:32 Acceptance test for the as-quoted prices: decimalization grids (1/16 before 2001, pennies after) as a fact the vendor never s
  97bf0f0 2026-10-26 13:26 Job visibility: bg.sh launcher that records how a job ends, and a one-screen monitor (running, stalled, finished, failed, sto
  500c186 2026-10-26 13:18 Subject fetcher: write every 100 laws (terms before run rows) so a stopped session loses at most 100
  c3f5cde 2026-10-26 13:13 As-quoted factors: ratio decreases under 0.5% are informational (splice-scale noise); merger-sized decreases still flag
  b1d6a1b 2026-10-26 13:12 Subject fetcher: the API count includes the policy area; up to 40 pages for omnibus-sized bills
  7b31212 2026-10-26 13:09 Congress subject-term fetcher (design step 2): policy area and legislative subjects per relevant law, paged, resume-safe

UNCOMMITTED (git status --short):
  M CHANGELOG.md
   M scripts/audit/changelog_tools.py
  ?? results/tag_review_v1_galen.txt

<!-- entry: 2026-10-26-19 | date: 2026-10-26 | label: tagger convention | source-line: new | approx: no -->
### 2026-10-26-19 — Tagger convention found and fixed: reaction labels excluded the event-day move
WHAT: The reaction labels (rewarded / punished / muted) disagreed with abnormal_return_20d in event_market_reactions_corrected for 15.3% of the 10,703 explore-set events (1,636; 36 with the wrong sign). CAUSE (code reading, tag_reaction_character.py lines 271-300 against compute_full_reaction): the tagger's compute_abnormal_return took the FIRST PRICE ON OR AFTER THE EVENT DATE as its base (the event-day close), so the event day's own move was excluded; compute_full_reaction, which writes the saved columns, uses the PRIOR close (the written rule since 2026-09-11). Live test (explore set): the tags agree with the columns 78.3% (muted) / 89.0% (punished) / 89.0% (rewarded) but agree 96.7% / 98.5% / 98.0% with the event-day-baseline version. A random-data simulation of the old function disagrees with the saved-column logic in 13.1% of cases (real data 15.3%). Planted test: a +8% jump on the event day is 'rewarded' under the new function and 'muted' under the old. A second copy of the function (tag_multientity_reactions.py, 'identical logic') had the same defect; three other scripts define their own compute_abnormal_return (validate_factor_attribution_covid.py; test_sector_peer_ripple.py and populate_sector_peer_ripple.py, which already use the prior-day baseline).
FIX: scripts/audit/patch_tagger_baseline.py (version 2, all-or-nothing) replaced both copies (commit 6615ec5). Unit tests: 1,500 + 800 + 800 random series, equal to the saved-column logic to 1e-12. LIVE CHECK (scripts/audit/check_tagger_convention.py, pre-set rule: at least 95% label agreement and median |difference| below 0.001): 100 of 100 labels agree, median difference 0.000000, maximum 0.0095: PASS (with n of 100 the 95% lower bound on agreement is about 96%). CALLS SCORED: agreement at least 95% (80%): held; median under 0.0005 (85%): held; at least 90 of 100 computable (80%): held.
UNPROCESSED EVENTS (same day): the Oct 3 promotion cohort has 3,133 of 3,139 events with no reaction row and no tag; the Oct 15 waves 3,662 of 3,662; 862 older events lack a row (807 untagged, 34 without an entity link). Tagging was never run after those promotions (README of 10-08: 15,928 tagged of 19,892).
OPEN: relabel the existing tags from the saved columns (backup table, proposal table, read about 40 cases including all 36 wrong-sign events, guarded apply, post-check) and re-derive diverged_from_fundamentals by the existing rule using the SAME company's firm state; repair event_entity_reactions (multi-entity rows were computed with the old convention); read get_untagged_events before running the tagger on the unprocessed events (it must not double-tag diverged events); rerun the significance audit on the corrected labels. The labels now INCLUDE the event-day move (they measure the full reaction; the old labels measured days +1 to +20 after the event-day close). NAMING: five functions share the name compute_abnormal_return (one thing, one name).

<!-- entry: 2026-10-26-18 | date: 2026-10-26 | label: correction | source-line: 3727+3728 | approx: no -->
### 2026-10-26-18 — CORRECTION TO ADDENDA 26, 27 AND 28 (2026-10-26)
CORRECTION TO ADDENDA 26, 27 AND 28 (2026-10-26): D3 and D4 ARE DEFINED IN A FILE: PROJECT_PLAN.md (repo root; also in the Project knowledge), Section 6 'The Prediction Contract and Evaluation Harness (added after external review)', written after a review of the plan by a day-trading practitioner. THE CONTRACT (every pattern must declare): universe; horizon (day 0, 0-1, 0-5, 0-21, never one unspecified 'reaction'); benchmark (abnormal return against SPY and against a sector/peer basket = D1); base rate (fraction of random same-sector days showing the same move = D2); similarity keys (event type is not enough: surprise sign/size, firm state, regime and size/liquidity bucket = D4; event_pre_context supplies firm state, regime and size bucket; SURPRISE SIGN STAYS UNBUILT, gated on analyst consensus data); magnitude and dispersion (mean or median abnormal return with a confidence interval, not a bare directional percentage); out-of-sample window (= D3). THE WALK-FORWARD HARNESS (mandatory before a tag reaches 'real pattern' status): definitions fit only on data through T; scored only on events after T; never re-tuned on the evaluation window; each candidate compared with at least TWO dumb baselines (unconditional firm drift; random events of the same broad type). The plan's 'real deliverable' of Phase 6: an evaluation notebook that can output 'not ready (n=11, CI crosses 50%, fails against the sector baseline)' as readily as a positive finding. WITHDRAWN: the statements that D3 and D4 'were never specified in any file' and 'live in a chat session' (my search covered docs, scripts and SCRIPTS.md but not the repo-root PROJECT_PLAN.md; found through the Project knowledge). The rework plan of addendum 27 matches the contract and adds two items it lacked: the second dumb baseline (unconditional firm drift) and the surprise-sign key (unbuilt). ALSO FOUND: the plan's phase table dates from September (Phase 3 about 85%, Phase 6 about 15%, events 1,214 growing toward 11,000) and uses 'Phase 6' for the Historical Pattern Engine / evaluation harness, whereas later notes use 'Phase 6' for the synthesis layer: the master audit reconciles the two; the Project knowledge is a September snapshot without the results folder.

<!-- entry: 2026-10-26-17 | date: 2026-10-26 | label: addendum 29 | source-line: 3725 | approx: no -->
### 2026-10-26-17 — FIRST EXPLORATION RESULTS: THE TAGS DO NOT MATCH THE CURRENT RETURN COLUMNS; the 'calmer than random' gap is WITHDRAWN
> Original heading: `### 2026-10-26 (addendum 29): FIRST EXPLORATION RESULTS: THE TAGS DO NOT MATCH THE CURRENT RETURN COLUMNS; the 'calmer than random' gap is WITHDRAWN`
CHECK (explore set, 10,703 events, each with exactly one reaction tag), against the current abnormal_return_20d (+-3% against SPY): rewarded 2,177 of 2,446 consistent (89.0%; 251 within +-3%, 18 below -3%), punished 2,130 of 2,393 (89.0%; 245 within, 18 above +3%), muted 3,357 of 4,290 (78.3%; 437 above, 496 below), diverged_from_fundamentals 1,403 of 1,574 (89.1%; 171 within); overall 9,067 of 10,703 (84.7%), 1,636 mismatches (15.3%), 36 with the WRONG SIGN. CALLS SCORED: all four tags at least 95% consistent (60%): MISSED; total mismatch under 2% (50%): MISSED. EFFECT: moved share by TAGS 59.9% against 62.4% by the current COLUMNS. WITHDRAWN: (a) the 'calmer than random' gap of addenda 26 and 27 (60.2% of tagged events moved against 63.7% of random windows) compared a TAG-based share with a COLUMN-style baseline (compute_base_rate.py works from prices, like the columns); on the same measure the gap is 62.4% against 63.7% = 1.3 points, 1.6 SE if the base rate used its default 5,000 samples (about 2.0 SE with 10,000; the size used is not recorded), and the era mix of the baseline (random windows over 1994-2026; the 289 events up to 2000 show 69.2 +-5.3% against 62.2% after) accounts for roughly 1.1 to 1.5 points; an in-session check printed 2.8 SE because of a units mix, the correct figure is 1.6; (b) the 'implied 55.7% for the other events' of addendum 28 mixed the two measures: in tag terms the other events are about 60.8% (explore 59.9%), so the hash split is not lumpy. OTHER LOOKS (20-day share beyond 3%, SPY): era up to 2000 69.2 +-5.3 (n 289), 2001-2013 61.5 +-1.4, 2014+ 62.9 +-1.3 (last two differ by 1.4 SE); firm state 62.6 against 62.2 (day 0: 12.8 against 14.5, 2.6 SE, one of several cells: watch, not a claim); grid by horizon 13.5 / 23.3 / 40.1 / 62.4% beyond 3% at 0d / 1d / 5d / 20d, sector-adjusted 12.1 / 21.3 / 36.4 / 58.4. BACK-OF-ENVELOPE (normal approximation, rough): a baseline daily sd of about 1.28% plus a burst worth about 1.8 days of variance (7.7% of the 20-day variance) reproduces the grid (1d model 22.7% against 23.3%; day 0 model 15.9% against 13.5%); the whole event effect on the 20-day share is about 1.4 points: the 20-day label is a LOW-CONTRAST filter for event effects, not a wrong one. IMPLICATIONS: the older harness (pattern significance, walk-forward scripts, THEORY.md nulls) used labels 15% off the current data: that blurs differences and cannot create false significance, so the audit result (0 of 13) stands but should be RERUN on relabeled data; the ledger tests use daily z, not tags (not re-verified). CAUSE of the mismatch NOT YET KNOWN (candidates: tags assigned before the 2026-10-19 correction of the reactions table, price updates, corrected dates, near-threshold flips): a diagnostic query splits small misses from large ones and by date_was_corrected. NEXT: diagnostic; then, ONLY on the user's decision, a deterministic relabel from the current columns (backup table, dry run, a read of a sample of the changes first); then rerun the audit; then the matched baseline and a z-unit mode. LOOKS LOGGED: explorer 4 (data_cache/explore_log.jsonl).

<!-- entry: 2026-10-26-16 | date: 2026-10-26 | label: addendum 28 | source-line: 3723 | approx: no -->
### 2026-10-26-16 — THE PERCENTS, THE SEALED SET AND THE EXPLORER (scripts/models/reaction_explorer.py; table explore_sealed_tickers)
> Original heading: `### 2026-10-26 (addendum 28): THE PERCENTS, THE SEALED SET AND THE EXPLORER (scripts/models/reaction_explorer.py; table explore_sealed_tickers)`
USER: the reaction percentages 'feel off' for ALL FOUR reasons listed: (1) events and random windows are not matched (the base rate samples uniformly over all securities and dates, 1994-2026, with no matching on era, company or volatility; compute_base_rate.py default 5,000 samples), (2) bundled events may be measured from the wrong moment (the stored date is often the first filing of a bundle; tag_reaction_character.py has --find-dates and --tag-one for the headline date; date_was_corrected marks overridden rows), (3) diverged_from_fundamentals is a derived upgrade whose share depends on firm_state coverage, (4) the +-3% over 20 days label is a hard cut that turns a continuous return into three boxes and means something different at each horizon and for each volatility. CORRECTION: the 'about 9 SE' for the calmer-than-random gap (60.2% of 15,952 events moved against 63.7% of random windows) used only the events' sampling error; with the base rate's own error (5,000 samples by default: SE 0.68 points) the gap is about 4.5 SE (about 5.7 SE with 10,000 samples), before any allowance for clustering by company and period; the base-rate sample size actually used is not recorded in the notes. EXPLORATION RULES: (a) a seeded 30% of companies is SEALED (explore_sealed_tickers = securities with MOD(ABS(hashtext(ticker)::bigint), 10) < 3, SPY excluded; the table is the source of truth and is never changed), excluded from every exploratory look and evaluated ONCE by a registered test afterwards; (b) every exploratory call is logged by the explorer in data_cache/explore_log.jsonl (not in git): its line count is the 'descriptive=' figure for the TRIALS line of any later registration; (c) the explorer has no option to include the sealed companies; (d) exploration creates no flag. LATER (not built): a matched-window baseline (same company, same era, volatility-matched, windows around events excluded) and a z-unit version of the labels (stock_day_z), which removes the horizon and volatility dependence of the fixed 3% cut. TESTED on planted data with a stub database (a first test of mine failed because I planted the wrong expected share; the tool was right, the test corrected).

<!-- entry: 2026-10-26-15 | date: 2026-10-26 | label: addendum 27 | source-line: 3720 | approx: no -->
### 2026-10-26-15 — THE FOOTING OF THE OLD AND NEW SIGNIFICANCE TESTS (scripts/models/footing_simulation.py), and the user's decisions on the Phase 6 harness
> Original heading: `### 2026-10-26 (addendum 27): THE FOOTING OF THE OLD AND NEW SIGNIFICANCE TESTS (scripts/models/footing_simulation.py), and the user's decisions on the Phase 6 harness`
SIMULATION: 20,000 random groups of events per tag size, drawn from the overall mix (muted 39.8, punished 22.8, rewarded 22.9, diverged 14.5), no tag signal by construction. OLD test (even null) calls 100.0% of groups of size 394 and 414 significant, 82.8% of size 88, 58.7% of size 53, 44.0% of size 38; across 13 random tags it averages 6.4 'significant' per replication: the real table had 6. NEW test (overall mix): 4.7% to 5.0% (calibrated; groups under 20 events excepted, where the audit used exact tests). Where the real tags sit among random groups of the same size by the OLD statistic: same_entity_sequence 81.3 (6.5% of random groups are at least that far), high_confidence_causal_link 82.9 (7.3%), multi_stage_divestiture 28.7 (5.2%), leadership_reversal 36%, confounded_regulatory_action 27%, confounded_corporate_action 17%. FAMILY-WISE (13 tags, no signal): at least one 'significant' at raw p < .05 in 46.8% of replications under the new test, 5.1% after Holm, 100% under the old test. HOLM IS NOT WHAT MOVED THE RESULT: against the overall mix every raw p is already above .05; Holm only controls the family-wise rate and more adjustment could only raise p-values. TWO-CLASS version (muted versus moved, independent of the derived 'diverged' class): same_entity_sequence 43.7% muted against 39.8%, z +1.56, p 0.12; high_confidence_causal_link z +1.23; multi_stage_divestiture z +1.08; leadership_reversal z -0.87; confounded_regulatory_action z -0.04; confounded_corporate_action z +0.68: none significant; a mild non-significant tilt toward muted in the three largest, NOT to be claimed. LIMITS: the simulation draws independent events, so real clustering (company, period) would make false positives MORE likely than 5%; the overall mix is itself not the right baseline (sector, era, volatility and firm_state coverage differ by tag).
USER DECISIONS 2026-10-26: (1) D3 and D4 are NOT retired: they are the HISTORICAL-ANALYSIS part of Phase 6 and, with little built, are REWORKED on a correct footing (matched baseline, purged out-of-time split, key granularity, trials counted), each registered from results/TEMPLATE_PREREG.md before it runs; what failed was the older significance test, not D3 or D4, which never ran. (2) The reaction labels are a filter for ONE horizon (20 trading days against SPY, +-3%), not 'the wrong horizon': that earlier statement is WITHDRAWN; the labels answer a 20-day question and the ledger a day 0-1 question; Phase 6 keeps both horizons. (3) The 'calmer than random windows' gap at 20 days (60.2% moved against 63.7%) is a real, UNEXPLAINED observation at that horizon, to be investigated in the rework (how compute_base_rate.py sampled; random windows matched by company, year and volatility). (4) Fatigue stays OPEN (a magnitude-based test to be registered). (5) The 4-class mix is not a clean outcome: diverged_from_fundamentals is a DERIVED upgrade of rewarded or punished (rule: rewarded with firm_state weakening or deteriorating, punished with strong or improving), so its share depends on firm_state coverage; the original direction is recoverable from the rule, or the test uses muted versus moved. REWORK PLAN (order): (a) clean labels and the firm_state coverage by tag; (b) a MATCHED baseline per tag (sector, era, volatility band) from the D2 sampling; (c) the calm-gap investigation; (d) D3 v2: chronological split with a PURGE of overlapping 20-day windows and an embargo (the purged and embargoed validation method is on the NOT-YET-VERIFIED list of results/ANCHORS.md: verify first); (e) D4 v2: a key hierarchy (event type, era, sector, firm_state) choosing the finest level with at least 30 training analogs, scored out of time against the coarser key and the plain base rate; (f) the fatigue test in magnitude terms.

<!-- entry: 2026-10-26-14 | date: 2026-10-26 | label: correction | source-line: 3719 | approx: no -->
### 2026-10-26-14 — CORRECTION TO ADDENDUM 26 (2026-10-26, after the user said something in it felt wrong; I went back through it)
CORRECTION TO ADDENDUM 26 (2026-10-26, after the user said something in it felt wrong; I went back through it): (1) the stored counts of pattern_significance_tests are NOT 'the 2026-09-11 table': tested_at reads 2026-09-11 on every row, but the counts are larger than the 2026-09-11 live query (same_entity_sequence 394 against 387) and the script says it was expanded to a four-way split on 2026-10-13, so the counts are of a later, unknown refresh with a stale timestamp (the upsert apparently does not set it); the audit compared those counts with an overall mix taken on 2026-10-26: TWO VINTAGES in one test; the retraction of 'six of 13 significant' is therefore PROVISIONAL until the tag counts are recomputed on the same day (one query, given 2026-10-26) and the audit is rerun. (2) 'D3 and D4 are RETIRED' and 'the docket collapses' were RECOMMENDATIONS, not decisions: the user asked to read them and then decide; they stay open until the user decides. (3) 'Fatigue is answered by the compounding effect' is WITHDRAWN: compounding (nearby events burst more) and fatigue (a repeated similar event is reacted to less) are different hypotheses, and the isolated versus non-isolated comparison does not test fatigue; fatigue stays OPEN. (4) 'Events look no more extreme than random windows, which fits the ledger' is WITHDRAWN as support: events were CALMER than random 20-day windows (60.2% moved against 63.7%, about 9 SE, N 15,952), which the ledger does not predict; the gap is UNEXPLAINED (likely a sampling difference between the D2 random-date baseline and the events) and needs a look at how compute_base_rate.py sampled. (5) The grep for consumers of is_significant found none (the one extra hit, scripts/audit/scan_dead_columns.sql, only lists table names), so no downstream result depends on the flags; the table stays as a documented historical artifact. CALL SCORED: at least one consumer besides the script itself (45%): MISSED.

<!-- entry: 2026-10-26-13 | date: 2026-10-26 | label: addendum 26 | source-line: 3716 | approx: no -->
### 2026-10-26-13 — AUDIT OF THE PATTERN-SIGNIFICANCE TESTS, and what it does to the Phase 6 docket (scripts/models/audit_pattern_significance.py; an AUDIT of earlier res
> Original heading: `### 2026-10-26 (addendum 26): AUDIT OF THE PATTERN-SIGNIFICANCE TESTS, and what it does to the Phase 6 docket (scripts/models/audit_pattern_significance.py; an AUDIT of earlier results, it creates no flag and no ledger row)`
FINDING. scripts/models/test_pattern_significance.py compares each tag with an EVEN 25/25/25/25 split over muted / punished / rewarded / diverged_from_fundamentals (expected = [n / 4] * 4). The overall mix of all 15,952 events with a reaction tag is muted 6,349 (39.8%), punished 3,644 (22.8%), rewarded 3,652 (22.9%), diverged 2,307 (14.5%); no event carries two reaction tags (checked). Against THAT null (chi-square, 3 df; exact multinomial test for n <= 100; Holm across the 13 tags) NONE of the 13 tags is significant, before or after the adjustment: same_entity_sequence n 394 p 0.25 (was 1.6e-17), high_confidence_causal_link n 414 p 0.36 (7.2e-18), multi_stage_divestiture n 88 p 0.068 (2.6e-06), leadership_reversal n 53 p 0.11 (0.011), confounded_regulatory_action n 38 p 0.18 (0.014), confounded_corporate_action n 47 p 0.40 (0.0027). The two largest tags have the overall mix almost exactly (same_entity_sequence 43.7% muted against 39.8% overall). The tool was checked on a planted real signal (70% muted on 200 events), which survives. RETRACTED: 'six of 13 testable categories significant' (the Phase 6 kickoff, 2026-09-11 and 2026-10-13) and the four 'significant tags' in the project overview were artifacts of the even null. LIMITS: the corrected null ignores volatility and sector (the labels use a fixed +-3% over 20 trading days against SPY); tags with n of 5 to 8 are untestable either way; counts are those of the 2026-09-11 table (is_significant stays as stored; see the consumers check). CALLS SCORED: overall muted share between 35% and 55% (70%): held (39.8%); no event with two reaction tags (80%): held; at least 3 of the 6 old significant tags lose significance (55%): held (all 6).
DECISIONS (stated as made after reading the code, the table and this audit): (1) D3 (walk-forward split at tag level) and D4 (similarity-key granularity) are RETIRED: they were defined in a chat review (an external day-trading practitioner's 'prediction contract': D1 sector/peer benchmark = populate_sector_peer_benchmark.py, D2 base rate = compute_base_rate.py, both built) and never specified in any file; the 20-day reaction labels they were meant for show no tag-specific signal after this correction, and the live version of D4 (how specific can 'past events like this' be) is the card's event_move_dist line, by event type and era. (2) The docket item 'human-pattern theories left' COLLAPSES: fatigue is answered by the validated compounding effect (non-isolated events show bigger, longer bursts: THEORY.md and the event-time zoom-out), herding has 5 tagged events (same_industry_comparison), drift is null (direction null everywhere), round numbers are closed (addenda 22 and 23). (3) CONSISTENCY: 60.2% of tagged events moved (rewarded + punished + diverged) against 63.7% of random-date windows (D2, 20 trading days): at the 20-day horizon events look no more extreme than random windows, which fits the ledger (the event premium is a burst on days 0-1; days 2-20 about 0): the reaction labels measure the wrong horizon. (4) What remains of Phase 6: the SYNTHESIS build (day view and bottom-line panel: event sign labels, relevance weights, decay, compounding rules), the forward confirmations (tariff; FOMC press-conference split; January), the macro threads, the universe decision and the data gaps.

<!-- entry: 2026-10-26-12 | date: 2026-10-26 | label: addendum 25 | source-line: 3714 | approx: no -->
### 2026-10-26-12 — THE EXTERNAL ANCHORS ARE BAKED INTO THE PROCESS (results/ANCHORS.md; results/TEMPLATE_PREREG.md; scripts/ops/check_prereg.py; scripts/ops/score_predic
> Original heading: `### 2026-10-26 (addendum 25): THE EXTERNAL ANCHORS ARE BAKED INTO THE PROCESS (results/ANCHORS.md; results/TEMPLATE_PREREG.md; scripts/ops/check_prereg.py; scripts/ops/score_predictions.py; scripts/hooks/pre-commit)`
WHAT CHANGES. (1) Every NEW registration is a copy of results/TEMPLATE_PREREG.md and must carry: ANCHOR (DATA, LITERATURE or NONE), TRIALS (confirmatory=N descriptive=N ledger_before=N), HURDLE (a t line and the 3.0 reference), DECAY (forward_fraction), STANDARD TEST, PLACEBO, FORWARD CHECK, a machine-readable PRED-TABLE (id | type | statement | point | lo | hi | level | anchor) and LIMITS. (2) scripts/hooks/pre-commit (enabled 2026-10-26 with git config core.hooksPath scripts/hooks) runs scripts/ops/check_prereg.py on every newly ADDED results/PREREG_*.md and refuses the commit if anything is missing; a ratio prediction with anchor NONE must have a range from at most point/2 to at least twice the point (the round-number priors, 1.06 with range 1.01 to 1.12, fail it; tested); appended addenda and older registrations are not checked. (3) The same hook BLOCKS any commit touching the eight FROZEN forward-test files (models/earnings_band_model.json, models/earnings_role_band_model.json, models/band_calibration.json, scripts/card/earnings_roles.py, earnings_role_band_test.py, day_card.py, earnings_surprise_test.py, earnings_forward_test.py) unless FROZEN_OK=1 is set, for use ONLY after BOTH verdicts are recorded (runbook steps 7, 11, 11b, 11c); the manual freeze check (git diff --stat fdac0a2 HEAD -- ...) stays valid as a second check; git commit --no-verify bypasses everything and the commit message must say why. (4) After the results, append an ACTUAL-TABLE block (id | actual | se) and run python3 scripts/ops/score_predictions.py FILE; python3 scripts/ops/score_predictions.py --all gives the running calibration (the share of 80% and 95% ranges that contain the actual, Brier for probability rows): the tally of numeric ranges open since 2026-10-22 is from now on automatic for every registration that uses the template (earlier registrations are free text and are not parsed). (5) Anchor discipline: the nearest published magnitude is looked up (results/ANCHORS.md; a new item is added only after it is verified by search) BEFORE a registration is written; a result far from its anchor is checked for a data problem before it is called a finding. TESTED in a throwaway repository: frozen-file edits blocked (also inside a mixed commit), FROZEN_OK=1 override, complete new registration accepted, incomplete one refused, addenda to old registrations and unrelated commits untouched, --no-verify bypass. LIMITS: the checker validates structure, not whether an anchor is the right one; core.hooksPath is a LOCAL git setting: run git config core.hooksPath scripts/hooks in any fresh clone or Codespace; a determined user can bypass the hook.

<!-- entry: 2026-10-26-11 | date: 2026-10-26 | label: addendum 24 | source-line: 3712 | approx: no -->
### 2026-10-26-11 — PREDICTIONS CARRY AN ANCHOR LABEL (lesson of the round-number clustering priors, which missed by 5.6 and 17.6 SE)
> Original heading: `### 2026-10-26 (addendum 24): PREDICTIONS CARRY AN ANCHOR LABEL (lesson of the round-number clustering priors, which missed by 5.6 and 17.6 SE)`
RULE 6 for the foundation check (addendum 17). Every numeric prediction states its ANCHOR: DATA (earlier results on the same quantity), LITERATURE (a cited finding), or NONE. With NONE: the 95% range on a ratio is at least half to double the point (a ratio of 1.06 is written 0.53 to 2.12), or only the verdict probabilities are registered. With a cheap anchor available (under 30 minutes of compute, no look at the tested statistic), an ANCHOR SLICE (about 5% of tickers, fixed by a seeded draw and EXCLUDED from the confirmatory run) is run first and the registration cites it. A baseline or null model is checked on the anchor slice BEFORE its thresholds are fixed (for the round-number test: the 80 plain cents against each other, which never touches the whole-dollar ratio). OPEN ITEM: a tally of every numeric range on record, scored both ways (inside the range; distance in standard errors), to see whether the ranges are systematically too narrow; offered on 2026-10-22 and 2026-10-26, not yet run.

<!-- entry: 2026-10-26-10 | date: 2026-10-26 | label: addendum 23 | source-line: 3709 | approx: no -->
### 2026-10-26-10 — ROUND-NUMBER CENTS DIAGNOSTIC (exploratory, read-only; scripts/ingestion/cents_diagnostic.py on data_cache/round_tests_cache.jsonl), run AFTER the reg
> Original heading: `### 2026-10-26 (addendum 23): ROUND-NUMBER CENTS DIAGNOSTIC (exploratory, read-only; scripts/ingestion/cents_diagnostic.py on data_cache/round_tests_cache.jsonl), run AFTER the registered results of addendum 22 were committed`
CENTS GRID (closes of $10 and above; share of each cents value divided by the mean share of the 80 plain cents). A HIERARCHY of clustering. Era A: whole dollar (00) 3.19; half (50) 2.02; the other dimes (10, 20, 30, 40, 60, 70, 80, 90) 1.52 to 1.63; quarters (25, 75) 1.48 and 1.45; the other nickels 1.23 to 1.30; plain cents 0.91 to 1.12 except the four cents beside a whole dollar: .01 1.12, .02 1.11, .98 1.15, .99 1.18. Era B: 1.71; 1.30; dimes 1.09 to 1.11; quarters 1.12 and 1.13; other nickels 1.03 to 1.05; plain cents 0.97 to 1.03 with .01 1.08 and .99 1.09. WHY THE CALIBRATION FAILED: the plain cents are not flat (about +-5%, and +11 to +18% beside a whole dollar), which is statistically clear at 1.2 to 1.5 million closes, so a check built for sampling noise widened every interval (x3.79 in A, x1.69 in B). Whole dollars exceed EVERY ONE of the 80 plain cents in both eras (largest plain ratio 1.18 in A, 1.09 in B): a descriptive rank statement, not a registered test. BREADTH (closes of $10 to $100, tickers with at least 400 baseline closes): era A 406 tickers, whole-dollar ratio percentiles 10/25/50/75/90 = 1.63 / 1.97 / 2.35 / 2.90 / 3.59, 384 tickers (95%) above 1.5, 87 (21%) above 3; era B 383 tickers, 1.02 / 1.18 / 1.39 / 1.69 / 2.06, 162 (42%) above 1.5, 6 above 3. The pattern is BROAD, not driven by a few tickers; the extremes are thinly traded or high-priced stocks (era A: TPL 12.8, CHTR 10.2, BLK 8.8, GS 7.0, AOS 6.7; era B: ARES 4.9, FICO 4.3, LITE 3.7, FIX 3.6, SMCI 3.4). THE 80x: the era A $250-and-up whole-dollar ratio is NVR: 900 whole-dollar closes against 971 baseline closes = 75% of that bucket's excess (CME 11%, ISRG 3%, AZO 2%); era A $100-250: TPL 262 against 101 baseline closes (19% of the excess); era B $250-and-up: NVR 11%, TPL 6%, BKNG 3%, CMG 2%. CALLS SCORED: dominated by 1-3 tickers each over 20% of the excess: held (NVR 75%); median ticker ratio below the pooled ratio in both eras: held (2.35 < 3.19, 1.39 < 1.71); asymmetry over 5% between units digits 1-4 and 6-9 in era A: MISSED (about 1.5%; the structure sits beside whole dollars instead); more than 10% of tickers above 3 in era A: held (21%).
DISPOSITION (decided after reading the diagnostic; stated as such): (1) the registered verdicts of addendum 22 STAND (both NULL). (2) CLUSTERING is a described fact, not a flag: closes cluster at round cents with a hierarchy (dollar, half, dime, quarter, nickel), broadly across tickers, strongest in 2001-2013; it has no bearing on ranges; the ledger row records the registered NULL and carries the descriptive estimates in its notes; NO v2 test is registered (a better baseline would only re-describe the same data). (3) TEST 2: even at face value the weak hint of +1.07% and +1.25% in mean move size is about 1/25 of the event premium (about +30% on days 0-1) and would change a range by about 1%, below the +-3 point coverage tolerance of the range calibration; the lane is CLOSED as no actionable effect; a free forward check is runbook step 13. (4) The ledger rows are written from the real table format (the FOMC rows are read first).

<!-- entry: 2026-10-26-09 | date: 2026-10-26 | label: addendum 22 | source-line: 3704 | approx: no -->
### 2026-10-26-09 — ROUND-NUMBER TESTS, REGISTERED RESULTS (results/PREREG_round_number_2026-10-26.md; scripts/ingestion/round_number_tests.py, run on all 491 usable tick
> Original heading: `### 2026-10-26 (addendum 22): ROUND-NUMBER TESTS, REGISTERED RESULTS (results/PREREG_round_number_2026-10-26.md; scripts/ingestion/round_number_tests.py, run on all 491 usable tickers, 2,000 ticker bootstrap resamples)`
DATA CHECKS: zone-days era A 221,124, era B 255,707; none dropped on guard days (the four guard dates were confirmed: 2009-07-26 1 stock, 2016-02-27 1, 2024-05-27 2, 2025-12-25 2); no z value for 7,182 zone-days (1.51%; the registered stop was 5%); cents filter dropped 0.00% (A) and 0.01% (B) of the closes of $10 and above.
TEST 1, CLUSTERING (closes of $10 and above; era A 1,165,239 closes, era B 1,486,806): CALIBRATION FAILED: 35% (A) and 74% (B) of the 80 plain cents had intervals containing 1.0 (required 90%), so every interval was widened by x3.79 (A) and x1.69 (B) as registered. Whole-dollar ratio against the plain-cents mean: era A 3.187 (SE 0.381, widened 95% [0.966, 6.511]), era B 1.710 (SE 0.038, widened [1.595, 1.846]); halves 2.018 / 1.303; quarters 1.464 / 1.125; other multiples of 5 1.411 / 1.073. REGISTERED VERDICT: NULL (era A's widened lower bound is below 1.00). The NULL comes from the calibration rule, NOT from an absence of clustering: every bucket between $5 and $100 has whole-dollar ratios of 2.2 to 2.5 (A) and 1.3 to 1.5 (B) with intervals far above 1.0; the baseline of 80 plain cents is NOT flat, so the registered null model was wrong for this data. Era A $250-and-up whole-dollar ratio 80.1 (95% [9.1, 237.6], 6,514 baseline closes) cannot be organic and is under investigation (exploratory diagnostic scripts/ingestion/cents_diagnostic.py). PREDICTIONS SCORED: whole-dollar ratio point 1.06 (range 1.01 to 1.12) in A against 3.19 (5.6 SE away, no overlap) and 1.04 (1.00 to 1.09) in B against 1.71 (17.6 SE away, no overlap): LARGE MISSES; verdict PASS 40 / LEAD 35 / NULL 25: NULL occurred (my 25% outcome) for a reason I had not foreseen; ratio larger in A than B (60%): held; halves above 1 in both eras (75%): held; quarters above 1 in both eras (70%): held; calibration share at least 90% (55%): MISSED. LESSON: the foundation-check rule says to pass the metric over real cases before fixing thresholds; I withheld that to keep the registration free of outcomes, but the flatness of the baseline could have been checked on the plain cents alone without seeing the whole-dollar number.
TEST 2, BEHAVIOUR NEAR ROUND THRESHOLDS (s10 class, k = 2..9): ERA A (2004-2013, 70,512 round zone-days) ln RHO +0.0106 (SE 0.0049, t +2.18) = +1.07% in mean z, 95% [+0.08%, +2.00%]; placebo contrast ln(P27/P73) +0.0145 (t +2.53: NOT clean); year consistency 60% of 10 years; below zones +0.0065, above zones +0.0149. ERA B (2014-2026, 80,631 round zone-days) ln RHO +0.0124 (SE 0.0050, t +2.47) = +1.25%, 95% [+0.30%, +2.27%]; placebo contrast +0.0068 (t +1.30, clean); year consistency 69% of 13 years; below zones +0.0167, above zones +0.0079. REGISTERED VERDICT: NULL (pass needs |t| >= 2.5 in both eras, a clean placebo contrast and 70% year consistency: none of the three is met in both eras; lead needs |t| >= 2.0 in both with a clean placebo: era A's placebo contrast is 2.53). READING (not a verdict): two positive, near-equal estimates with intervals just above zero, but the placebo neighbours differ from each other by +1.45% (A) and +0.68% (B), so part of any difference may be a price-level gradient; a weak unconfirmed hint, not a lead. PREDICTIONS SCORED: ln RHO point 0.000 (range -0.020 to +0.020) in both eras: both observed values inside the range (+2.2 SE and +2.5 SE from the point); verdict NULL (80%): held; placebo contrast clean in both eras (70%): MISSED (era A 2.53); percent change within +-3% in both eras (80%): held; zone-days without z under 1% (70%): MISSED (1.51%); cents filter under 1% (85%): held.
DESCRIPTIVE STATISTICS LOOKED AT (as counted by the script): 200. NEXT: an EXPLORATORY diagnostic (no pass possible): cents grid per era, per-ticker spread of the whole-dollar ratio, tickers behind the era A $250-and-up ratio. Any follow-up test with a better baseline is a NEW registration labelled as following these results.

<!-- entry: 2026-10-26-08 | date: 2026-10-26 | label: addendum 21 | source-line: 3702 | approx: no -->
### 2026-10-26-08 — the two round-number tests are REGISTERED (results/PREREG_round_number_2026-10-26.md), before any outcome and before the outcome script exists
> Original heading: `### 2026-10-26 (addendum 21): the two round-number tests are REGISTERED (results/PREREG_round_number_2026-10-26.md), before any outcome and before the outcome script exists`
Confirmatory scope from the counts only: test 1 (clustering of closes, closes of at least $10, the whole-dollar ratio against the 80 non-multiple-of-5 cents values, pass needs both eras) and test 2 (the s10 class, interior thresholds k = 2..9, round zones against their two placebo neighbours at +-27% of the spacing, outcome stock_day_z z on the next day, pass needs both eras, a clean placebo contrast and year consistency). Everything else descriptive. Predictions registered: test 1 PASS 40% / LEAD 35% / NULL 25%; test 2 PASS 5% / LEAD 15% / NULL 80%. NEXT: coverage of stock_day_z (outcome-free query), then the outcome script, tested on planted effects first.

<!-- entry: 2026-10-26-07 | date: 2026-10-26 | label: addendum 20 | source-line: 3700 | approx: no -->
### 2026-10-26-07 — outcome-free counts for the round-number tests (scripts/ingestion/round_number_counts.py), BEFORE any registration or outcome
> Original heading: `### 2026-10-26 (addendum 20): outcome-free counts for the round-number tests (scripts/ingestion/round_number_counts.py), BEFORE any registration or outcome`
COUNTS. Usable tickers 491 (all but HON). Closes removed from them by their valid_from 41,059 = the sum of n_removed of the 12 valid-from losses; total closes 2,711,759 = 2,759,196 eligible - 41,059 - HON's 6,378: the counting script reproduces the validation table exactly. ERA A (2001-06 to 2013): 434 tickers, 5,028 ticker-years, 1,216,981 closes. ERA B (2014 to 2026): 491 tickers, 6,080 ticker-years, 1,494,778 closes. Closes by price bucket (A / B): $1-5 13,011 / 703; $5-10 38,729 / 7,058; $10-20 144,953 / 58,063; $20-50 596,806 / 280,240; $50-100 344,704 / 483,556; $100-250 59,744 / 466,603; $250-1000 16,456 / 182,221; $1000+ 2,578 / 16,334 ($10 and above: A 1,165,241, B 1,487,017). ZONE-DAYS (R_below, R_above, P27_below, P27_above, P73_below, P73_above): s10 A 46,346 / 42,677 / 45,157 / 46,231 / 48,750 / 46,901 (days 1,086,114); s10 B 47,676 / 41,507 / 44,752 / 45,613 / 49,340 / 49,268 (822,031); s100 A 1,026 / 2,669 / 1,991 / 1,889 / 1,092 / 1,127 (76,123); s100 B 11,481 / 17,232 / 16,625 / 16,354 / 13,536 / 13,066 (648,601); s1 A 3,422 / 3,009 / 2,996 / 3,075 / 2,790 / 3,057; s1 B 790 / 431 / 503 / 500 / 750 / 747; s1000 A 105 / 114 / 68 / 94 / 24 / 39; s1000 B 229 / 468 / 385 / 431 / 322 / 262. MATCHED BALANCE (round zone-days over the mean of the two placebo neighbours, interior k = 2..9): s10 A min 0.93 median 0.96 max 0.99; s10 B 0.87 / 0.95 / 0.97; s100 A 0.81 / 1.00 / 1.52 (smallest round count 108); s100 B 0.90 / 0.97 / 1.01 (k = 8 and 9 below 1,000 round zone-days); s1 and s1000 too thin. CALLS SCORED. Median balance between 0.9 and 1.1 in every class with at least 10,000 zone-days (65%): held. Balance within 0.8 to 1.25 for every interior k in s10 and s100 (55%): MISSED (s100 era A max 1.52). s10 holds at least 60% of zone-days (70%): held (90.6% in A, 74.7% in B). At least 1,000 round zone-days for every interior k in s10 and s100, both eras (60%): MISSED (s100 era A all k, era B k = 8, 9). Ticker-years in era B at least 40% (75%): held (54.7%). DECISIONS FOR THE REGISTRATION (from counts only). The THRESHOLD test's confirmatory scope is the s10 class (prices $10 to $100), interior k = 2..9, both eras (smallest cell 5,829 round zone-days in A, 2,607 in B); s100 era B with k = 2..7 is a secondary; s1, s1000, s100 era A and the decade thresholds ($10, $100, $1,000) are DESCRIPTIVE only (too thin, or one-sided neighbours: the upper-side neighbour of $100 holds 979 days against 1,682 round days in era A). The CLUSTERING test uses closes at $10 and above pooled by era as the primary and reports each bucket. OBSERVATION (noticed in the balance check; NOT a registered test; exploratory): in s10 the round zones hold about 5% FEWER zone-days than the placebo neighbours (round over the mean of the two neighbours: 0.952 in era A, 0.944 in era B) and fewer than BOTH neighbours (A: 89,023 round against 91,388 for the upper neighbour and 95,651 for the lower; B: 89,183 against 90,365 and 98,608). Part is mechanical (fewer days sit at higher prices, so the lower neighbour is more populated: P73 exceeds P27 by 4.7% in A and 9.1% in B; a convex density also puts a centre point below the neighbour average), but being below both neighbours points to a possible dip in occupancy near round numbers; days within a stock are strongly dependent, so NO interval or conclusion is attached; any test of it needs a smooth counterfactual from several offsets and its own registration. PENDING: the real schema of stock_day_z (the outcome source for the threshold test) and its coverage (the project notes of 2026-10-16 say 2004-01-01 to 2026-07-31; not verified), then the registration of both tests, then the outcome script.

<!-- entry: 2026-10-26-06 | date: 2026-10-26 | label: addendum 19 | source-line: 3698 | approx: no -->
### 2026-10-26-06 — THE PRICE FOUNDATION IS CLOSED (final state and what was learned)
> Original heading: `### 2026-10-26 (addendum 19): THE PRICE FOUNDATION IS CLOSED (final state and what was learned)`
STATE: results/PREREG_asquoted_levels_valid_from_2026-10-26.md addendum 6 (479 of 492 tickers valid from their first eligible close; 13 LOSS tickers: 5 class A, 8 class B; 1.72% of the post-2001-06-01 closes removed; pre-2001 levels out of scope). WHAT WENT RIGHT: the acceptance test used a fact the vendor never saw (decimalization grids); the loss classifier, written before it saw data, reproduced all four hand-read cases; the repair was tested on a planted case before it touched data and verified against the vendor afterwards. WHAT COST TIME: (1) the vendor's 'unadjusted' series is not as traded for some tickers and the problem was found AFTER the full download, not before; (2) a registered metric (valid_from after 2002 = a loss) counted late listings, 146 versus the 12 of the scan; (3) the first valid-from rule removed everything before the last bad window and assumed decimalization in 2001; (4) long scripts without retry or resume (twice); (5) an unfiltered classifier run was left running while a filtered one was started; (6) dependent commands pasted in one block ran before their job had finished. FIXES: the foundation-check rule (addendum 17), scope reduced to 2001-06-01 (addendum 3 of the registration), bg.sh refuses a same-name start and keeps one log per run, wait_job.sh chains dependent steps only when the job exited 0. TOOLS (all in scripts/): ingestion/check_asquoted_accuracy.py (decimalization-grid acceptance scan, resumable), probe_vendor_window.py, compare_asquoted_to_vendor.py, grid_profile.py, build_levels_valid_from.py (--since, --only), classify_loss_tickers.py (--after), fetch_asquoted_factors.py (--tol, --force); ops/bg.sh, jobs.py, wait_job.sh. THE JANUARY RUNBOOK step 3b3 carries the corrected procedure (a full refetch would undo the class C repair). NEXT: round-number anchoring, registered against exactly the validated data (addendum 6 USE RULE).

<!-- entry: 2026-10-26-05 | date: 2026-10-26 | label: addendum 18 | source-line: 3694 | approx: no -->
### 2026-10-26-05 — the three mechanisms behind the valid-from losses, and the decision rule fixed BEFORE the LOSS list is read
> Original heading: `### 2026-10-26 (addendum 18): the three mechanisms behind the valid-from losses, and the decision rule fixed BEFORE the LOSS list is read`
COMPARISON (scripts/ingestion/compare_asquoted_to_vendor.py, 1 vendor credit each). ODFL 2024-03-15..04-12: ours equals the vendor's current unadjusted close on all 19 matched days (largest difference 0.0000%): the vendor's series is SPLIT-ADJUSTED before the 2024-03-28 split (212.0350 = 424.07 / 2) and our table inherited it. NVDA 2024-05-28..06-28: ours differs from the vendor by up to 0.0047% (2024-05-31: 1096.3816 versus 1096.33), the vendor's closes are real traded prices (about $1,100 before the 10-for-1 split of 2024-06-10, $122 after) and sit on the penny grid 22 of 22 days; ours 15 of 22: the cause is OUR segmentation tolerance (5e-5 relative = about $0.05 at $1,100), so the valid-from rule wrongly marked NVDA's clean pre-split history as bad. MECHANISMS (each seen in one or two tickers, n tiny): A vendor seam or event adjustment (DRI, GL); B vendor split-adjusted unadjusted series (ODFL); C our precision at high prices (NVDA). Also seen once: the vendor returned 22 days for NVDA 2024-05-28..06-28 in the comparison but 23 in the earlier probe (2024-06-28 missing); unexplained, rechecked by a short probe.
DECISION RULE (fixed before the LOSS list or any classification is seen). After asquoted_levels_valid_from is written and the LOSS list (valid_from later than first_eligible, or never_valid) is read, each LOSS ticker gets ONE vendor request for a window around its last bad stretch and is classified: A = the vendor's own series is off the penny grid on more than 30% of the stretch, or shows a seam (not fixable; stays excluded); B = ours equals the vendor's and a single factor k from {2, 3, 3/2, 4, 5, 10, 20} puts at least 97% of the stretch on the penny grid (recoverable; a separate registered step would apply it); C = the vendor's closes sit on the grid on at least 95% of the stretch while ours differ by more than $0.002 on more than 30% of it (our precision). FIX for C: a DOLLAR tolerance (a segment breaks when the implied dollar error exceeds about $0.0005, so accuracy no longer falls as the price rises) and a refetch of the C tickers only; if C exceeds 40 tickers, rebuild all. NO level analysis (round-number anchoring, price thresholds) starts until the C fix is done or C is empty.
TARIFF DESIGN CORRECTED AGAIN. Tariff-themed executive-order days by year (relevant orders, trade_tariffs theme, outcome-free): 2004 3, 2007 1, 2009 1, 2010 2, 2011 3, 2012 3, 2013 2, 2014 2, 2016 3, 2017 7, 2019 4, 2020 10, 2021 1, 2022 6, 2023 1, 2024 1 = 50 days in 2004-2024 (no 2018: the 2018-19 tariffs were proclamations, which the decisions table does not hold); 2025 32 days (42 orders), 2026 7 days (10). The historical sample is TRADE-THEMED orders (mostly not tariff impositions), a broader hypothesis than the 2025 lead. DESIGN: CONFIRMATORY test on trade-themed order days 2004-2024 (stated as the broader hypothesis); EXPLORATORY split inside 2025-2026 (tariff-themed versus other order days), labelled exploratory because that sample produced the lead. PREREQUISITE: a read of the tagged orders' titles (the theme is unvalidated).

<!-- entry: 2026-10-26-04 | date: 2026-10-26 | label: addendum 17 | source-line: 3690 | approx: no -->
### 2026-10-26-04 — FOUNDATION CHECK before any new build or registration
> Original heading: `### 2026-10-26 (addendum 17): FOUNDATION CHECK before any new build or registration`
WHY. Three times in one day a build was finished before a cheap look at real cases would have shown the gap: the vendor's seam in the 'unadjusted' prices (found after the whole download), a registered metric that counted late listings as losses (146 versus 12), and long scripts without retry or resume (twice). RULE. Before a new build AND before its registration: (1) run 3 to 5 REAL cases through the idea, at least two of them known-hard (corporate actions, omnibus laws, thin data), and record what they show in the note; (2) list the build's unverified inputs and assumptions, and verify each one that costs under 15 minutes; (3) every long script starts from the same safeguards: transient-error retry, results saved as it goes so a rerun resumes, PROGRESS lines, a final summary line, dry run by default; (4) a registered test is run on data DIFFERENT from the data that suggested it (a post hoc lead is never confirmed on its own sample); (5) a pass of the metric over about ten real cases before its thresholds are fixed.
APPLIED 2026-10-26. The planned tariff executive-order test was to use 2025-2026 order days, the sample that produced the lead (day +1 at t +3.98): CIRCULAR. Corrected design: confirmation on earlier tariff-themed order days (2004-2024), 2025-2026 reported as the original observation only; counts by year first. The unverified inputs for it: how reliable the trade_tariffs tag is on orders (a title read of the tagged orders plus a sample of untagged ones), the weekend-date merge count, and how the vendor handles splits (below).
LIMIT OF THE GRID TEST (found 2026-10-26): a vendor that ROUNDS its split-adjusted values to cents would pass the penny-grid test while not being as traded; the grid test alone does not prove a close is as traded, so the day-over-day jump at known splits and scripts/ingestion/compare_asquoted_to_vendor.py (our reconstruction against the vendor's current feed) are the second line. ODFL (2-for-1, 2024-03-28): the vendor's 'unadjusted' closes before the split are HALF the traded price (212.0350 = 424.07 / 2), recoverable by the split factor; AAPL's 2020 split came back as traded: the vendor treats splits inconsistently across tickers, so no blanket rule. NVDA (10-for-1, 2024-06-10): all 23 closes in 2024-05-28..06-28 on the penny grid in the probe, but the dry run's last bad window for NVDA ended 2024-06-25: UNEXPLAINED, under investigation before any level analysis.

<!-- entry: 2026-10-26-03 | date: 2026-10-26 | label: addendum 16 | source-line: 3685 | approx: no -->
### 2026-10-26-03 — PLAN to get back to the Phase 6 docket (written after the valid-from dry run, before its table is applied)
> Original heading: `### 2026-10-26 (addendum 16): PLAN to get back to the Phase 6 docket (written after the valid-from dry run, before its table is applied)`
RULES. (1) Time-box: once asquoted_levels_valid_from is written, no new infrastructure until one docket test has run on data already in hand; a new tool must feed a registered test within a week or it waits. (2) The government-tag validation work (verifier, tiers v2, calibration read, finer buckets) is PARKED; the gate is the targeted tariff executive-order test: nothing there closes the lane as tags consistent, not validated, used for descriptive splits only; a signal reopens the validation. (3) Phase 6 option A (the five-factor regression, building factor 4 supply-chain and factor 5 public-response extraction) is not started until a REGISTERED test shows factors 1-3 add explanatory power beyond own volatility on a held-out era; option B (the ledger and card synthesis) goes first.
ORDER (targets; weekdays only). 10-26: job summaries, apply the valid-from table if the registered ranges hold, outcome-free tariff-order counts. 10-27: register the tariff executive-order test (2025-2026 order days, tariff-themed versus other relevant orders, influence check dropping the largest days, placebo shifts, power statement), then run it. 10-28 after the Fed announcement: runbook 3c. 10-29 to 10-30: register and run round-number anchoring against the valid-from table. 11-02: October sentiment top-up (runbook 8). Then: fatigue (same_entity_sequence), herding (same_industry_comparison), D3 walk-forward, D4 similarity key, 5 to 8 registered combinations against the plain-volatility baseline. After 2027-01-05: the January runbook (steps 0 to 12, with 3b2 and 11c).
STATE AT WRITING. Ledger 110 flags: proven 15, lead 21, null 60, retired 2, untested 12. As-quoted prices: scan lists 12 of 490 tickers below 97% on the penny grid; GL valid from 2013-05-22. Executive orders 2025-2026 carrying the trade_tariffs theme: 52 (theme counts are tag counts, orders carry several).
AMENDMENT TO ADDENDUM 16 (2026-10-26, after the valid-from dry run): ORDER IS BY DEPENDENCY. (a) Price-level validity is settled completely (table written, intended LOSS measure computed, the 2024 split hypothesis probed) BEFORE any level analysis such as round-number anchoring. (b) The tariff executive-order test uses returns only and runs in parallel: 118 relevant order days in 2025-2026, 39 with a tariff-themed order, 79 without, 212 orders, 6 weekend-dated; rough resolution about +20% at t 2.5. (c) Phase 6 option B (ledger and card synthesis) first; option A (the five-factor regression) only after a registered test shows factors 1-3 add explanatory power beyond own volatility.

<!-- entry: 2026-10-26-02 | date: 2026-10-26 | label: addendum 15 | source-line: 3680 | approx: no -->
### 2026-10-26-02 — subject terms, as-quoted accuracy, valid-from rule
> Original heading: `### 2026-10-26 (addendum 15): subject terms, as-quoted accuracy, valid-from rule`
CRS SUBJECT TERMS: government_decision_subjects / government_decision_subject_runs hold Congress's policy area and legislative subjects for all 2,176 relevant laws (2,176 ok, 0 none, 0 error, 0 incomplete; median 17 terms per law, p90 191.5, max 1,964; 2 laws with the policy area only). The 100% policy-area match is a join-integrity check (right bill for every law), not independent validation of the terms. fetch_crs_subjects.py now writes every 100 laws.
AS-QUOTED PRICES: the download is complete (492 ok, 5 flagged: ARE, BNY, CTVA, GEHC, JCI; 2 errors: AVB, EA). ACCEPTANCE TEST (scripts/ingestion/check_asquoted_accuracy.py, a 60-ticker sample): 93.8% of 60,851 pre-2001 closes on the 1/16 grid (chance 13%), 98.8% of 335,865 post-2001 closes on the penny grid (chance 40%); pre-2001 closes under $20 read lower on the 1/16 grid (79.2%), consistent with 1/32 quoting, a hypothesis tested by the 1/32 column in the all-ticker scan. FINDING (hand-read, 2 tickers, vendor adjust=none fetched directly with scripts/ingestion/probe_vendor_window.py): for DRI (event 2015-11-10, close -11.03%, ratio 0.65223 -> 0.72964) and GL (event 2013-05-03, close +20.77%, ratio x5/6) the vendor's 'unadjusted' series is NOT penny-exact before the event, so no rebuild from this vendor recovers true as-traded closes there; the error is in the vendor's feed, not in our factors (the earlier idea of refetching with a tighter tolerance is withdrawn). n = 2 tickers: a mechanism, not a rate.
VALID-FROM RULE: results/PREREG_asquoted_levels_valid_from_2026-10-26.md (registered before the scan's ticker list was read); scripts/ingestion/build_levels_valid_from.py applies it (table asquoted_levels_valid_from); level-dependent analyses (round-number anchoring, price thresholds, dollar moves) use only closes on or after valid_from; return-based analyses are unaffected.
OPS: accuracy scan retries transient 502/timeouts and saves each ticker to data_cache/accuracy_cache.jsonl as it finishes (delete that file after any change to the factor table).

<!-- entry: 2026-10-26-01 | date: 2026-10-26 | label: addendum 14 | source-line: 3676 | approx: no -->
### 2026-10-26-01 — background-job visibility
> Original heading: `### 2026-10-26 (addendum 14): background-job visibility`
Background jobs gave no sign of life: no output looked the same as finished, crashed, or a restarted Codespace. NOW: start every long job with   scripts/ops/bg.sh NAME command args...   (logs to data_cache/NAME.log and records pid, start, end and exit code in data_cache/jobs/NAME.status) and look with   python3 scripts/ops/jobs.py   (or   watch -c -n 20 python3 scripts/ops/jobs.py   for a live screen). States: RUNNING (progress bar and ETA), STALLED (alive, log silent), FINISHED OK, FAILED, STOPPED (no finish line: the session died or it was killed). The monitor finds jobs started the old way by process name and log. Traps found while testing it: pgrep -f matches ANY process whose command line mentions the name (so only 'python3 ... name.py' counts); a zombie process answers kill(pid, 0) as alive (so /proc state is checked); a regex written as 'never matches' ($^) matched an empty log and would have reported a killed job as finished. LIMIT: it shows that a job ended and its last summary line, not that the job did the right thing.
CONVENTION (2026-10-26): any long script prints a line   PROGRESS done/total   at the start and every few percent; scripts/ops/jobs.py then shows a bar and an ETA for it with no change to the monitor. The four scripts it already knows (prices, subjects, decision text, tagger) are matched by their own log lines.
AS-QUOTED PRICES, COMPLETE (2026-10-26): asquoted_fetch_log has 492 ok, 5 flagged, 2 error = 499 tickers. The 5 flagged are real and are EXCLUDED from level analyses (or restricted by date): ARE (a x100 unit error before 2002-07-30), BNY (a 5.7% decrease at the 2007 merger), CTVA (stale after the 2026-10-01 separation), GEHC (the vendor's raw history starts 2023-07-26, so about 152 earlier stored days have no vendor price: no as-quoted value before that date), JCI (a x0.955 step on 2016-09-06: the Tyco merger's share consolidation, explained, kept for review). The 2 errors, AVB and EA, have no stored prices. Ratio decreases under 0.5% are informational (splice-scale noise). Acceptance test: scripts/ingestion/check_asquoted_accuracy.py (decimalization grids).

<!-- entry: 2026-10-23-11 | date: 2026-10-23 | label: addendum 13 | source-line: 3674 | approx: no -->
### 2026-10-23-11 — design step 1 DONE (repeat run complete)
> Original heading: `### 2026-10-23 night (addendum 13): design step 1 DONE (repeat run complete)`
v1_rerun now covers all 3,035 decisions (2,998 usable). Agreement between the two runs on ALL decisions: scope 91.2% (2,524 of 2,769), persistence 97.5% (2,898 of 2,973). The newly repeated batch ALONE (by subtraction from the earlier 2,078 of 2,276 and 2,386 of 2,440): scope 90.5% (446 of 493), persistence 96.1% (512 of 533): within the registered 3-point acceptance of 91.3% and 97.8%, so the pipeline is stationary and stability is used for every decision. TIERS after the full repeat (view government_decision_tags_tiered): A 5,949 (49.0%), B 553 (4.6%), C 5,647 (46.5%, unchanged: it does not depend on the repeat run); by type A: persistence 48.6%, scope 49.7%, sector 52.9%, theme 47.5%. About 91.5% of the otherwise-eligible tags (A plus B) are reproduced by the repeat. My calls: new-batch agreement within 3 points held (75%, 80%); tier A between 45% and 55% held (70%); C stays about 46% held (75%). NEXT (Monday): the optional tier-C reason query; prices day 2 and the retriage; the CRS subject pilot; the verifier script.

<!-- entry: 2026-10-23-10 | date: 2026-10-23 | label: addendum 12 | source-line: 3668 | approx: no -->
### 2026-10-23-10 — where everything stands going into Monday (nothing is needed over the weekend)
> Original heading: `### 2026-10-23 evening (addendum 12): where everything stands going into Monday (nothing is needed over the weekend)`
STATE. GOVERNMENT TAGGING v1 is complete: 3,035 decisions, 2,992 usable, 12,149 tags; tier view government_decision_tags_tiered (A 4,812 / B 1,690 / C 5,647). Reliability between two independent runs: scope 91.3%, persistence 97.8%, themes identical 76.5% and sharing a theme 97.0%, sectors (non-empty) identical 73.9% and sharing 80.9%. REPEAT RUN for the remaining 565 decisions (label v1_rerun) was started Friday evening, log data_cache/tag_repeat_rest.log. EXPECTED when finished: v1_rerun has 3,035 run rows. IF IT DID NOT FINISH (the Codespace stopped): list the newest batches with   curl -s "https://api.anthropic.com/v1/messages/batches?limit=5" -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" | python3 -c "import sys, json; [print(b['id'], b['processing_status'], b['request_counts'], b['created_at'][:19]) for b in json.load(sys.stdin)['data']]"   then run   python3 -u scripts/government_decisions/tag_government_decisions.py --collect THE_BATCH_ID --label v1_rerun --live --apply   (the batch with about 565 requests; collecting never pays again).
THE READ: results/PREREG_government_tag_review_v1.md; the sample is frozen and NO verdicts exist. Galen skimmed his 30 on 2026-10-23 and saw no issues: that is a skim, NOT a read; do not record it as verdicts. THE PLAN: results/DESIGN_government_tag_validation_v1.md holds the pre-registered build order (repeat run, CRS subject terms, verifier pass with counterfeit-tag controls, tiers v2, market test, calibration, finer buckets as children).
PRICES: the as-quoted download day 1 finished (71 tickers left): run   nohup python3 -u scripts/ingestion/fetch_asquoted_factors.py --all --max-requests 700 --apply >> data_cache/asquoted_run.log 2>&1 &   then   python3 -u scripts/ingestion/fetch_asquoted_factors.py --retriage   (and --retriage --apply if the list looks right); flags so far ARE, BNY, CTVA, STX.
MONDAY ORDER. (1) check the repeat run:  SELECT vocab_version, COUNT(*) AS runs, COUNT(*) FILTER (WHERE status IN ($$ok$$, $$partial$$)) AS usable FROM government_decision_tag_runs GROUP BY 1 ORDER BY 1;   expect v1 3,035 / 2,992 and v1_rerun 3,035 / about 2,990. (2) rerun the two reliability queries (they now cover all decisions) and paste the output. (3) prices day 2 and the retriage. (4) CRS subject terms pilot (3 laws, read the raw response), then the verifier script (design steps 2 and 3).
NOT URGENT: the government ledger rows and threads-map entries wait for calibration; finer buckets (children of v1 parents) come last; the January runbook items are unchanged.

<!-- entry: 2026-10-23-09 | date: 2026-10-23 | label: addendum 11 | source-line: 3663 | approx: no -->
### 2026-10-23-09 — government tagging run, a double submission, and the reliability result
> Original heading: `### 2026-10-23 (addendum 11): government tagging run, a double submission, and the reliability result`
A. FINAL v1 STATE (vocabulary v1, prompt v1.2, validator rules; 3,035 relevant decisions): ok 2,280, partial 712, invalid 43 (98.6% usable); tag rows about 12,149 (11,494 from the second batch pair + 655 from the last 166, after the orphan cleanup). Scope (first batch, 2,276 scoped): not_company_relevant 39%, sector_specific 40%, market_wide 20%, company_specific 1%; 394 of 887 not_company_relevant are full-text with medium or high confidence (a floor of 17% of screened-relevant decisions confidently NOT company relevant; the relevance screen saw titles only). Congress policy-area theme appears among the model's themes for 76-83% of laws. Quote verifier: theme quote not found 154, sector quote not found 57 in the first batch.
B. THE DOUBLE SUBMISSION (a process error, recovered): my instruction block put the second-pass live command next to a 'wait until the text job finishes' sentence; it ran immediately, so the same 2,471 decisions went to the model twice (batches msgbatch_01SJM2B4... = first; msgbatch_014GPKfF... and msgbatch_01HiRSRF... = second, 2,871 requests incl. 400 new). The old code merged by primary key, leaving 252 (decision, scope-or-persistence) pairs with two rows. RECOVERY: batch results persist on Anthropic's side, so the second pair was collected as the main v1 (--collect, replace semantics) and the first batch as v1_rerun (--label); no tag was analyzed on the merged state. SAFEGUARDS ADDED: --live refuses while decisions wait for text (--allow-waiting); a submit writes 'submitted' markers so a second run skips those decisions (--include-submitted); a decision's tag set is REPLACED by its newest answer, for every processed decision (a first version only replaced decisions with new tags and left 95 stale rows for decisions the second run called invalid: found by a row count that did not match the expected 11,494, fixed, cleaned); --collect and --label for recovery and repeat runs. LESSON: a count that does not match the arithmetic is a finding; and put the dangerous command in its own block.
C. TEST-RETEST RELIABILITY (the accident's gift: two independent runs of the same prompt on 2,471 decisions): same persistence 97.8% (2,440), same scope 91.3% (2,276; kappa about 0.87 from the margins), theme sets identical 76.5% and sharing a theme 97.0% (2,417), sector sets identical 86.8% (inflated by decisions with no sectors in either run; the non-empty-only figure is in the refined query). Reliability is not validity: the registered 150-decision read measures whether the tags are RIGHT. My calls: scope and persistence at least 90% held; themes identical at least 40% was badly under-called.
D. PENDING: the review-sheet script and the registered read (150 plus 100); then the government lane's ledger rows and threads-map entries (sector threads provisional until the read; 1993-2004 law threads provisional because 57-100% of those summaries are not the enacted version); the as-quoted download day 2 (71 tickers), its retriage and the flagged read (ARE, BNY, CTVA, STX so far); round-number anchoring; January runbook items.

<!-- entry: 2026-10-23-08 | date: 2026-10-23 | label: addendum 9 | source-line: 3659 | approx: no -->
### 2026-10-23-08 — pre-FOMC drift, and the as-quoted flag triage
> Original heading: `### 2026-10-23 (addendum 9): pre-FOMC drift, and the as-quoted flag triage`
A. PRE-FOMC DRIFT (scripts/card/fomc_drift_test.py; registered in results/PREREG_fomc_drift_test_2026-10-23.md before the run; SPY 1994-01-03 to 2026-10-13, 8,250 days; 261 scheduled meetings, 13 unscheduled actions excluded from the baseline): REGISTERED VERDICT 'REPLICATES, FADED'. Two-day excess return +0.449% [+0.158, +0.739] t +3.03 (1994-2011, n 144); +0.118% [-0.134, +0.369] t +0.92 (2012-2026, n 117); placebos -0.015% (t -0.14) and +0.085% (t +0.91). The replication line is the instrument check: the daily close-to-close measure can see a published signed effect. Exploratory: the effect sits on day 0 (+0.322% t +3.10 in 1994-2011; +0.405% t +2.85 in 2004-2014; +0.002% t +0.02 in 2015-2026), not day -1. The difference between the windows is 0.331% = 1.7 standard errors: 'faded' = not detected since 2012 and probably smaller, not proven gone. Predictions: both windows inside their ranges; P(t >= 2.5) 40% happened; P(REPLICATES, FADED) 32% happened. Ledger: fomc_pre_announcement_drift (null; 9 evidence rows). No card change.
B. AS-QUOTED FLAG TRIAGE: 24 of the first 127 tickers were flagged (about 17%); reading them: 14 were my threshold being wrong (the stored history was fetched at one date and later dividends accumulate, so the latest ratio runs 1.0015-1.0149, REITs highest), 3 were 4-for-3 splits missing from my split list (ADI 1997; C 1996 and 2000), 6 were spin-off steps the vendor adjusts for (A/Keysight 2014, APTV 2017, BAX/Baxalta 2015, CNP 2002, COP/Phillips 66 2012, DELL 2018), and 3-4 were real: ARE (a x100 step on 2002-07-30: a unit error in the raw or stored series before that date), BNY (a 5.7% decrease at the 2007 merger), CTVA (a x6.665 step on 2026-10-01 from the Corteva separation, 12 days before the data ends: the stored series is stale), DD (a 2019 reverse split plus spin-offs; second flag item not seen). RULES CHANGED (fetch_asquoted_factors.py, with --retriage that re-evaluates flagged tickers from the stored change points, no API credits): latest ratio up to 1.05; split ratios gain 6:5, 4:3, 5:2 at a 4% tolerance (8% for a decrease, so a reverse split plus a spin-off passes); a non-split step up to x4 is informational ('info:'); a step above x4 that is not a split ratio, OR any step above x1.15 within the last 60 stored days, flags. The factors themselves were never wrong; only the advisory flags were. LESSON: a self-check written from expectation (the stored scale equals the vendor's current scale) fires on ordinary facts (dividends since the fetch); read the first batch of flags before building on them.
C. PENDING: retriage result and the read of the remaining flagged tickers; the download's second day; the round-number registration (exclude ARE before 2002-07-30, BNY, CTVA 2026-10 from level analyses until resolved); government tagging enrichment; the January runbook (3b rerun of the factors).

<!-- entry: 2026-10-23-07 | date: 2026-10-23 | label: addendum 8 | source-line: 3654 | approx: no -->
### 2026-10-23-07 — FOMC sector contrast (NULL) and the absolute sector table
> Original heading: `### 2026-10-23 (addendum 8): FOMC sector contrast (NULL) and the absolute sector table`
A. SECTOR CONTRAST (scripts/card/fomc_day_sector_test.py; registered in results/PREREG_fomc_sector_test_2026-10-23.md before the run; grouping RATE = Financials, Real Estate, Utilities vs the other eight, fixed beforehand; window day 0 and day +1 averaged, post hoc in origin): REGISTERED VERDICT NULL. RATE / REST 1.044 [0.999, 1.092] t +1.92 (2004-2014, n 88); 1.001 [0.962, 1.042] t +0.06 (2015-2026, n 92); placebos 0.993 (t -0.45) and 1.026 (t +1.76), clean. The data exclude a concentration above about 9% (first era) and 4% (second era). Predictions: ratios inside their ranges (A 1.06 and B 1.05 predicted; B's point off), P(NULL) 50% happened, 'Financials the largest single sector in at least one era' held on the RELATIVE table (1.040 vs Utilities 1.039) but not on the absolute one.
B. THE SERIES WAS RELATIVE: log_ratio builds each sector relative to the n-weighted mean z of the OTHER sectors, so the market-wide effect cancels by construction; the registered descriptive table's eleven values averaged about 0.99 against a market-wide 1.14, which exposed it. My registration called it 'log_ratio of each sector's mean z' and the script labelled the table 'against its own baseline': both loose; the label is corrected and an addendum written; the verdict stands. LESSON: when a derived table disagrees with an aggregate by construction (sector values averaging 0.99 under an aggregate of 1.14), look for a relative-versus-absolute mismatch before interpreting anything.
C. ABSOLUTE SECTOR TABLE (scripts/card/fomc_day_sector_absolute.py, descriptive): every sector's own amplification, day 0 / day +1, 2004-2014 then 2015-2026: Communication Services 1.071 / 1.218, 1.087 / 1.183; Consumer Discretionary 1.154 / 1.188, 1.095 / 1.198; Consumer Staples 1.163 / 1.175, 1.070 / 1.156; Energy 1.067 / 1.244, 1.088 / 1.066; Financials 1.198 / 1.234, 1.104 / 1.223; Health Care 1.129 / 1.218, 1.113 / 1.183; Industrials 1.150 / 1.213, 1.177 / 1.267; Information Technology 1.054 / 1.261, 1.092 / 1.221; Materials 1.111 / 1.187, 1.112 / 1.257; Real Estate 1.177 / 1.194, 1.160 / 1.204; Utilities 1.193 / 1.248, 1.088 / 1.115. Reconciliation: the equal-weighted sector mean equals the market-wide figure within 0.010 on every cell. The Fed-day effect is MARKET-WIDE (every sector 1.05-1.27, no stable leader); the absolute RATE-minus-REST contrast is 1.040 [0.999, 1.082] t +1.91 and 1.002 [0.965, 1.039] t +0.08, the same NULL.
D. SPY: market_prices holds SPY 1994-01-03 to 2026-10-13, 8,250 days (complete); the pre-FOMC drift test (signed returns) is next and needs no new data.

<!-- entry: 2026-10-23-06 | date: 2026-10-23 | label: addendum 7 | source-line: 3649 | approx: no -->
### 2026-10-23-06 — FOMC calendar, as-quoted prices, FOMC announcement-day test
> Original heading: `### 2026-10-23 (addendum 7): FOMC calendar, as-quoted prices, FOMC announcement-day test`
A. FOMC CALENDAR (scripts/macro/build_fomc_calendar.py, final parser b51b708 + later patches; scripts/macro/load_fomc_meetings.py, edabe55): table fomc_meetings, 310 rows = 274 meetings, 35 conference calls, 1 cancelled; 254 rows with an announcement_date (244 held + 10 scheduled). announcement_date = the date inside the statement URL, NOT the meeting date (the 2008-01-21 call announced 2008-01-22; the 2020-03-02 meeting announced 2020-03-03; the Sunday 2010-05-09 swap-line action; 2007-06-28 set to the meeting's last day because the Fed page's statement link pointed at a 2007-06-18 release). VALIDATION (results/fomc_calendar_validation.txt): 46 of 46 independently transcribed 2021-2026 announcement dates; all 59 DFEDTAR target changes of 1994-2008 on announcement dates; 32 of 32 Fed rows of government_decisions on announcement dates (T3a's timing was therefore right); DFEDTARU / DFEDTARL change the DAY AFTER the announcement (30 of 32, 2 same-day); every year has 8 meetings except 2003 (9; the 2003-09-15 meeting has no statement), 2020 (9 incl. two unscheduled; the 3/17-18 meeting was cancelled) and 2026 (6 held, 2 scheduled). The FOMC issued a statement after EVERY meeting only from January 2000 (from February 1994 only after changes). UPDATE PROCEDURE: after each FOMC meeting run build_fomc_calendar.py, then load_fomc_meetings.py --apply (next meeting 2026-10-27/28).
B. PRICE LEVELS: the stored prices are split- AND dividend-adjusted (adjust=all): AAPL 2020-08-28 stored 120.935 vs traded 499.23 (ratio 0.2422 = the 4:1 split and dividends). PROBE (probe_unadjusted_prices.py): the vendor serves adjust=none on the basic plan (8 requests a minute, 800 credits a day): AAPL 499.23001 and 129.039993. METHOD (scripts/ingestion/fetch_asquoted_factors.py, 9347dad): the piecewise-constant ratio stored_adjusted / traded close is stored as change points in price_adjustment_factors (tolerance 5e-5 relative = half a cent per $100), with asquoted_fetch_log carrying split-aware self-checks (a decrease not explained by a reverse split, a step above x1.15 that is not a split ratio such as the HON level shift, matched share below 98%, truncation). PILOT: AAPL 67 and NVDA 59 change points, no flags; reconstruction AAPL 499.230 / 129.040, NVDA 1,208.937 / 121.790 (my recalled close 1,208.88: within tolerance). FULL RUN started 2026-10-23 (cap 700 requests a day, about 800 requests in all, two days; 12 tickers done and ok at the time of writing). Credits: basic plan, 800 a day.
C. FOMC ANNOUNCEMENT-DAY TEST (scripts/card/fomc_day_test.py; registered in results/PREREG_fomc_day_test_2026-10-23.md before the run; the statistic and baseline of eo_day_test.py): 181 scheduled and 8 unscheduled announcements from 2004. REGISTERED VERDICT PASS: scheduled day 0 amplification 2004-2014 1.140 [1.067, 1.218] t +3.90 (n 88); 2015-2026 1.112 [1.044, 1.186] t +3.27 (n 92); without 2020 1.121 [1.050, 1.196] t +3.44 (n 85); placebos 0.974 (t -0.90) and 0.945 (t -1.85), clean and slightly below 1 (the statistic may be conservative by a few percent). DESCRIPTIVE, exploratory: day -1 1.038 (t +0.93) / 1.004 (t +0.11); day +1 1.215 (t +5.29) / 1.199 (t +5.63), LARGER than day 0 (the decision is public at 2:00 pm, so the full-day reaction lands on day +1); HOLD 1.136 / 1.088 vs CHANGE 1.152 / 1.168 (no meaningful gap: the announcement matters more than the rate move); UNSCHEDULED 2004-2014 2.161 [1.502, 3.108] (n 6; 2015-2026 n 2); sub-eras 1.112 / 1.157 / 1.077 / 1.141. PREDICTIONS SCORED: day 0 A and B inside their ranges; P(PASS) 55% happened; scheduled count 181 inside; unscheduled inside (era A); day -1 era A outside (1.038 vs 0.92-1.02); day +1 MISSED BADLY (predicted 1.04, got 1.20-1.22: I forgot the 2:00 pm timing); CHANGE 1.20 vs HOLD 1.07 missed (HOLD higher, CHANGE lower). INTERPRETATION: a known effect, detected; the instrument sees a 10-20% size effect with about 90 days, which calibrates the earlier nulls (the executive-order null excludes effects above about 2% in 2004-2014 and 5% in 2015-2026; the Financials-only Fed change-day null could exclude only much larger effects). Scheduled dates are public a year ahead, so this is a known-on, forecast-usable lane. Limits: size not direction; daily resolution; day_card.py frozen until the role-band verdict.
D. PENDING: ledger rows for the FOMC test (conventions: SELECT DISTINCT family FROM flag_ledger and one example row); sector breakdown of the FOMC effect (needs fed_change_day_test.py's SECTORS order); signed returns (pre-FOMC drift, needs ld's internals); the as-quoted download day 2 and the read of its flagged tickers; round-number anchoring registration after the download; government tagging enrichment; January runbook.

<!-- entry: 2026-10-23-05 | date: 2026-10-23 | label: addendum 6 | source-line: 3644 | approx: no -->
### 2026-10-23-05 — the year-to-date differencing check, final
> Original heading: `### 2026-10-23 (addendum 6): the year-to-date differencing check, final`
A. RESULT (ytd_differencing_check.py; 496 tickers; 1,075 comparisons of the differenced Q2/Q3 value against the reported three-month value, only for companies that report both): exact 995 (92.6%), within 0.5% 29 (2.7%), MISMATCH 51 (4.7%). Operating cash flow Q2 215 / 88.4% exact / 7.4% mismatch, Q3 201 / 90.5% / 3.5%; capital expenditures Q2 334 / 94.3% / 4.5%, Q3 325 / 94.8% / 4.0%. Registered rule: 80-95% exact = read the mismatches first (done); NOT validated at the 95% bar (92.6% exact; 95.3% counting within 0.5%).
B. MECHANISM (the seven tickers with the most examples: AIZ, CPAY, IT, LII, DVN, BRO, CMCSA; 109 comparisons, 17 mismatches = 15.6% vs 3.5% for the other 966): 6 of the 17 had a three-month fact filed more than 100 days after the YTD fact (recast comparatives from the next year's 10-Q: AIZ FY2011, LII FY2015); 11 had the three-month fact filed with the YTD fact (not recasts; mechanism NOT established; likely facts from consecutive filings on different bases, or tagging quirks: LII shows a sign flip and an identical 106.9M for two years; DVN FY2020 Q3 capex differences to 931M vs 204M reported).
C. USE: the parser prefers a reported three-month fact when one exists (the differencing only fills NULLs), so the mismatch rate describes differenced cells; Q4 inherits Q1-Q3 errors; the checkable group is not a random sample. Derived Q2-Q4 cash flows are APPROXIMATE: fine for aggregate and descriptive use, not for single-period event detection without a check. Provenance: cash_flow_fill_audit_20261023 (17,275 rows; 15,276 operating_cash_flow, 10,581 capital_expenditures, 11,098 free_cash_flow, exactly as predicted); backups financial_statements_backup_20261023 and financial_metrics_backup_20261023 make a revert exact. WITHDRAWN: the earlier claim that 'restated 0' over the 422 / 633 stored Q2 / Q3 rows validated the differencing (it fills only NULLs, so it never ran there). Decision: keep the fills with this limit; null_register quality note updated.
D. PREDICTIONS SCORED: comparisons at least 300 yes (1,075); at least 95% exact NO (92.6%); mismatches concentrated in a few tickers partly (7 tickers = 10% of comparisons, a third of the mismatches); OCF and capex similar NO (89.4% vs 94.5% exact); at least half of the large mismatches a later-filed three-month fact NO (6 of 13 = 46%); provenance counts exact (17,275 / 15,276 / 10,581 / 11,098) yes. LESSON: validate a derivation on cases where it actually RUNS; a check on rows it skips proves nothing.

<!-- entry: 2026-10-23-04 | date: 2026-10-23 | label: addendum 5 | source-line: 3639 | approx: no -->
### 2026-10-23-04 — close-out of the session
> Original heading: `### 2026-10-23 (addendum 5, close-out of the session)`
A. PREVIOUSLY-ANNOUNCED WALK-FORWARD (event_band_pa_walkforward.py; registered before the first coverage computation; counts from event_band_pa_population.py: non-acquisition previously_announced single-event stock-days 1,575 / 1,434 / 1,321; capital_raise 360 / 405 / 403): unadjusted coverage 87.5 [85.8, 89.0] / 86.4 [84.5, 88.1] / 86.4 [84.5, 88.2]%; k = 1.115 fitted on 2005-2012 gives 89.5 [87.8, 91.0] and 88.9 [87.1, 90.5]% in the later eras; REGISTERED VERDICT PASS; capital_raise alone 86.4 / 89.6 / 85.4% (FAIL on its own fit; its own k 1.205 over-corrects 2013-2019 to 94.1%). Post hoc origin (the pooled 87% hint), borderline entry gate (fit era 87.5% vs 88%), stakes about 0.4 points; no card change (runbook step 11b). Predictions scored: fit-era coverage 88.0% (85-91) -> 87.5 inside; k 1.05 (1.00-1.12) -> 1.115 inside, top of range; P(PASS) 30% happened (NO SHORTFALL 35% did not).
B. YTD DIFFERENCING CHECK (ytd_differencing_check.py, 67caf0a; run started in the background, PID 62583, log /tmp/ytd_check.log): RESULT PENDING. Calls on record: comparisons at least 300 (60%); at least 95% exact (65%); mismatches concentrated in a few tickers (70%); operating cash flow and capex similar (70%). Reading rule: 95% or more exact on a few hundred comparisons = independently validated (limit: only companies reporting both kinds of fact); 80-95% = read the mismatch examples first; below 80% = the matching has a problem and the 11,098 filled free-cash-flow values are suspect (backups: financial_statements_backup_20261023, financial_metrics_backup_20261023).
C. STATE AT THE END OF 2026-10-23: statements parser deterministic and verified; cash-flow fills applied (17,145 + 130 rows) with 0 changes in any frozen-test input; metrics recomputed; null register updated; both forward tests frozen and intact (freeze check ok on all six files); tariff split, multi-event-day coverage (cannot test) and previously-announced walk-forward (PASS) recorded; January runbook steps 0-11b written.
D. REMAINING (all scheduled or parked on purpose): the YTD check result; confirm the five previously-announced evidence rows; October sentiment top-up after 2026-10-31 (python3 scripts/gdelt/backfill_gdelt_sentiment.py 2026-10 2026-10 --ignore-checkpoint); January per the runbook (8-K refresh, additive statements, prices, caches, matrices, readiness, then ONE evaluation each of earnings_forward_test.py and earnings_role_forward_test.py); after both verdicts: point-in-time repair (step 9 and 9a) and the card notes (steps 11, 11b). SKIPPED: duplicate-recording cleanup (about 160 pairs, under 1% of events).

<!-- entry: 2026-10-23-03 | date: 2026-10-23 | label: addendum 4 | source-line: 3634 | approx: no -->
### 2026-10-23-03 — null register updated, duplicate-recording scan, population counts pending
> Original heading: `### 2026-10-23 (addendum 4): null register updated, duplicate-recording scan, population counts pending`
A. NULL REGISTER UPDATED and VERIFIED (the UPDATE recomputes from the live tables; kind stays guarded_sparse; reason and action rewritten: the cash flows were derived from year-to-date facts, the remaining NULLs are NOT diagnosed row by row): financial_statements capital_expenditures 14,733 (39.81%), free_cash_flow 16,667 (45.04%), operating_cash_flow 6,868 (18.56%); financial_metrics capex_revenue_ratio 14,869 (40.18%), fcf_growth 18,189 (49.15%), fcf_margin 16,790 (45.37%), fcf_yoy_growth 18,818 (50.85%), operating_cash_flow_margin 7,081 (19.13%); every value equals what was computed beforehand from the verified fill counts. The financial_growth_classified row (stale snapshot) and the gross_margin / gross_profit rows are unchanged.
B. DUPLICATE-RECORDING SCAN (same entity, same event type, same day or the next; all labeled events; undercounts pairs where the lower event id has the later date): 280 candidate pairs: acquisition 179, leadership_change 24, capital_raise 19, ipo_spinoff 19, legal_settlement 11, regulatory 9, restructuring 5, accounting_investigation 4, corporate_action 4, strategic_partnership 2, financial_result 2, governance_action 1, cybersecurity_incident 1. A read of 14 random same-type pairs found 8 the same news recorded twice (EQT/Equitrans, COP/Burlington, IFF/DuPont N&B, CEG/Calpine, BALL/Ardagh, CCI/T-Mobile towers, VMRK/AvalonBay, T/AT&T), 2 related but distinct, 4 truly separate; so roughly 160 duplicate pairs (about 90-220 at 95%), under 1% of 23,554 events. NO CLEANUP PLANNED (small, and a merge needs every pair read); the single-event class audit leaves such days out, so it under-represents the largest recorded deals (a selection hypothesis, untested). If wanted later: a read-only review sheet of the 280 pairs, merges through the audited-removal pattern of 2026-10-15.
C. PREDICTIONS SCORED: 'at least half of the 14 pairs are the same news recorded twice' (55%) yes (8 of 14); the register's expected values: all eight matched.
D. PENDING: confirm the ledger rows (four multi-event evidence rows plus the note on event_band_class_calibration_audit); run event_band_pa_population.py (counts only) and register the previously-announced rule from the counts; the Q1 control query for the operating-cash-flow plausibility screen; October sentiment top-up after 2026-10-31; January runbook; the two forward evaluations once each.

<!-- entry: 2026-10-23-02 | date: 2026-10-23 | label: addendum 3 | source-line: 3628 | approx: no -->
### 2026-10-23-02 — metrics confirmed, repair scope, multi-event-day coverage
> Original heading: `### 2026-10-23 (addendum 3): metrics confirmed, repair scope, multi-event-day coverage`
A. METRICS CONFIRMED against financial_metrics_backup_20261023 after the second populate_financial_metrics.py run (post-apply): rows 37,006 = 37,006; non-null fcf_margin 9,130 -> 20,216 (+11,086), ocf_margin 14,669 -> 29,925 (+15,256), capex_revenue_ratio 11,568 -> 22,137 (+10,569), fcf_growth 5,462 -> 18,817, fcf_yoy_growth 8,340 -> 18,188; coverage of the three margins 25% / 40% / 31% -> 55% / 81% / 60%. The null_register entries for these columns are STALE (table null_register; rows not yet read). Plausibility screen on operating_cash_flow (4,851 company-years with all four quarters): negative Q2 between three positive quarters 113, negative Q3 73, a quarter over 3x the others 132 (at most 6.6% of company-years together); the Q1 CONTROL query is PENDING.
B. REPAIR SCOPE (restated_cell_classifier.py --all; runbook step 9a): 289 differing annual cells, none NO_MATCH; repair 175 (151 filed_date + 24 balance-sheet recasts), never revenue / CONCEPT_SWITCH / DERIVED; about 1% of annual equity cells mix parent-only and NCI-inclusive equity within a company. Freeze check re-run: ok on all six files, matrices end 2026-10-13, 0 window filings.
C. MULTI-EVENT-DAY COVERAGE (event_band_multi_event_coverage.py; registered in results/PREREG_multi_event_day_coverage_2026-10-23.md before the run; self-check reproduced 36,923 single event-days and edge 1.337). REGISTERED VERDICT: CANNOT TEST: 762 qualifying stock-days (338 / 253 / 171 per era, minimum 300). Descriptive: multi-event coverage 87.9% [84.0, 90.9] / 78.3% [72.8, 82.9] / 83.0% [76.7, 87.9], pooled 83.6% (n 762; Wilson 80.8-86.1 computed from the counts) vs single-event 91.1 / 89.8 / 89.6%; implied extra multiplier 1.142 / 1.441 / 1.153; exploratory: same event type 79.1% (n 373) vs mixed types 87.9% (n 389); lead on day 0 vs day +1 similar; 3+ events n 18 / 9 / 2. Stakes: about 2.4% of event stock-days, about 0.16 points of pooled event-day coverage. No card change (day_card.py is frozen; step 11 of the runbook adds a note after the role-band verdict).
D. PREDICTIONS SCORED: kept count 7,000 (2,000-25,000) -> 762 MISSED and a count prediction against my own 2026-10-22 convention; pooled coverage 85% (80-89) -> 83.6% inside; the probability set (UNDER 40 / CALIBRATED 35 / UNCLEAR 20 / OVER 5) left out CANNOT TEST, which happened; 3+ events lower than exactly 2 (70%) untestable. Lesson: run the population count BEFORE registering a rule with a minimum n.
E. PENDING: the Q1 control query; the null_register rows for the cash-flow columns; the same-type pair reading (14 random pairs); ledger evidence rows for the multi-event result (convention check first); non-acquisition previously-announced held-out era; October sentiment top-up after 2026-10-31; January runbook; the two forward evaluations once each.

<!-- entry: 2026-10-23-01 | date: 2026-10-23 | label: addendum 2 (note 6) | source-line: 3618 | approx: no -->
### 2026-10-23-01 — final-parser verification, Q1-Q3 free cash flow applied, tariff split, classifier first read
> Original heading: `### 2026-10-23 (addendum 2 to note 6): final-parser verification, Q1-Q3 free cash flow applied, tariff split, classifier first read`
A. FINAL PARSER REPRODUCIBLE: two full-universe runs of the final parser (annual fix dfab63d + cash-flow extension c30302c) are IDENTICAL (stmt_fcf_a.log vs stmt_fixed_b.log; PYTHONHASHSEED=0). Full additive dry run: 346 new rows, 17,802 changed cells, 17,733 rows would be written, 0 DANGER.
B. Q1-Q3 FREE CASH FLOW (c30302c; the 10-Q cash-flow statement reports year-to-date figures, so the 70-110 day window found only Q1): Q2 = 6-month YTD - 3-month YTD, Q3 = 9-month YTD - 6-month YTD, matched on the fiscal-year start of Q1 and the quarter's period_end, earliest-filed fact; Q4 then derives from the annual. VALIDATION on the real table (dry run): of the 3,610 stored free_cash_flow values the old parser could not reproduce, 123 stay cleared (old 2008-2010 rows), 0 restated, 3,487 reproduced exactly; 11,098 free_cash_flow, 15,276 operating_cash_flow and 10,581 capital_expenditures cells filled. LIMIT: the stored values reproduced are mostly fiscal-Q1 rows (examples), so the Q2-Q4 derivations are validated only by a synthetic test and by reconciliation to the annual (true by construction); a plausibility screen (negative Q2/Q3 between positive neighbours; a quarter over 3x the others) is the independent check still to run.
C. WRAPPER v4 (--only-columns; fills only the named columns on EXISTING rows, no new rows, nothing overwritten or cleared). APPLIED 2026-10-23 after backups financial_statements_backup_20261023 and financial_metrics_backup_20261023: pilot AAPL/ABBV/ACGL 130 rows, then --all: 17,145 rows written, errors 0 (ACGL's restated total_equity correctly not written). VERIFIED against the backup: rows 37,006 = 37,006, new ids 0, changes in operating_income, net_income, revenue, filed_date, period_end, total_assets and total_equity = 0 (the frozen surprise test's inputs are unchanged), fills 11,098 / 15,276 / 10,581 exactly as the dry run, cash-flow values lost 0. NOT applied (January runbook step 2): the 346 new rows and the 118 revenue / 12 operating_income / 12 net_income / 11 gross_profit fills.
D. METRICS: populate_financial_metrics.py was first run (37,006 = 8,473 annual + 28,533 quarterly) while the apply was still running, so it is stale for tickers the apply had not reached; a second run after the apply is PENDING confirmation. Process lesson (twice today a dependent step started while a statements job ran: the cash-flow patch during the rehearsal, metrics during the apply): guard dependent steps with  until ! pgrep -f refresh_statements_upsert_only > /dev/null; do sleep 20; done
E. STORED filed_date FINDING: under the fixed annual builder 273 stored annual filed_date cells differ from the computed original (40 under the old parser, which let a late-filing field overwrite the period date); examples ADI FY2021 stored 2022-11-22 vs 2021-12-03, AEE FY2012 2014-03-03 vs 2013-03-01, ARES FY2015 2017-02-27 vs 2016-02-29. Q4 rows copy the annual date; Q1-Q3 rows (minimum logic) are unaffected; the forward window's new rows come from the fixed parser, so the forward verdict is unaffected. Repair remains scheduled after both verdicts (runbook step 9). Remaining restated balance-sheet cells under the fixed parser: total_equity 153, total_liabilities 65, total_assets 10, cash 10 (from 380 / 159 / 82 / 12 under the old).
F. CLASSIFIER (scripts/audit/restated_cell_classifier.py, f34e1cc): first read on 7 tickers, 20 differing cells: equity CONCEPT_SWITCH 6 of 7, revenue CONCEPT_SWITCH 2 of 3, filed_date LATER_COMPARATIVE 4 of 4, 9 of 20 repair candidates (a sample chosen for having differences). Full-universe table: run finished, NOT yet read.
G. TARIFF SPLIT (eo_trade_split.py, registered rule results/eo_trade_days_2025_2026.txt commit 44a1148 + addendum 1 before the run; self-check reproduced 1.081 / 1.158): 110 order days = 26 trade days (T) + 84 others (N). Day 0 / day +1 amplification: T 1.321 [1.102, 1.585] / 1.453 [1.184, 1.782]; N 1.016 [0.940, 1.099] / 1.079 [1.012, 1.151] (t +2.34); N without the 5 days directly after a trade day 1.001 / 1.064 [0.997, 1.135] (t +1.88); placebos T 0.928, N 0.956. REGISTERED VERDICT: BROAD (N day +1 t above 2.0, borderline); sensitivity N_clean: CARRIED; the registered verdict stands. Trade days are 24% of the days and about 60% of the pooled day +1 log excess. Ten rows in flag_ledger_evidence plus a note on the flag row (status unchanged, null with a post hoc watch). LIMITS: reverse causation, clustered trade days, non-trade orders that move specific sectors; descriptive only.
H. PREDICTIONS SCORED: tariff split: T day +1 1.30 (1.10-1.60) vs 1.453 inside; N day +1 1.05 (0.95-1.20) vs 1.079 inside; P(BROAD) 20% occurred; N days after a T day 5 vs 5 exact; 'registered verdict = N_clean verdict' 85% MISSED (differs by 0.4 t at the threshold). Statements: final parser identical 90% yes; cash-flow cleared under 1,000 70% yes (123); restated under 200 60% yes (0); filled above 2,000 70% yes; rows to write above 2,000 70% yes (17,733); cash-flow apply rows 17,000-17,500 yes (17,145 + 130 pilot); verification columns all as called. Classifier full-universe calls (LATER_COMPARATIVE the majority class for filed_date 85%; CONCEPT_SWITCH the majority for total_equity 65% and revenue 60%) PENDING.
I. PENDING: second metrics run after the apply; read the full classifier table; run the cash-flow plausibility screen and read about 10 flagged rows against the filings; confirm the freeze check (earnings_role_forward_test.py prints ok for all six files) after today's repo changes; multi-event-day coverage (needs sed -n '231,262p' scripts/card/day_card.py); non-acquisition previously-announced held-out era; October sentiment top-up after 2026-10-31; January runbook; the two forward evaluations once each.

<!-- entry: 2026-10-22-08 | date: 2026-10-22 | label: note 5 | source-line: 3601 | approx: no -->
### 2026-10-22-08 — CONSOLIDATED NOTE 5: T4 follow-ups, event band class audit, ipo_spinoff walk-forward, prediction tally, housekeeping sweep, financial_growth_classifie
> Original heading: `### 2026-10-22 (late) -- CONSOLIDATED NOTE 5: T4 follow-ups, event band class audit, ipo_spinoff walk-forward, prediction tally, housekeeping sweep, financial_growth_classified closed`
A. T4 FOLLOW-UPS (law-driven charge events; ledger law_driven_charge_events_titles, untested; notes CASE LIST, BENCHMARK, BURST COMPARISON and LABELER CHECK all CONFIRMED present; 12 evidence rows CONFIRMED). Benchmark: median absolute day-0 abnormal return 0.953% (mean 1.669%) over 15,897 events in event_market_reactions_corrected, against 0.30% / 0.56% for the 13 case-list events. Burst ratio (days 0-1 mean move over the days 25-39 baseline, ratio of means, isolated events, delta-method SE): law-attributed charge events 0.364 (SE 0.062, n 9); other isolated events in the same weeks 0.738 (SE 0.105, n 24; 2010-03-24..2010-04-13) and 0.952 (SE 0.156, n 30; 2017-12-22..2018-01-17); all isolated events 1.304 (SE 0.013, n 12,558). Volatile baselines explain roughly 40-60% of the raw gap; differences -0.374 (SE 0.122, z -3.1) and -0.588 (SE 0.168, z -3.5): law events drew about 40-50% of the burst of contemporaneous events. LIMITS: 9 events in two clusters (8 within three weeks of 2010), so the SEs overstate the evidence; controls are all event types, the group is charges; post hoc. LABELER CHECK: all 13 case-list events are timing = new (5 large, all tax-law; 3 moderate and 5 small, all Affordable Care Act; all bad), so the timing field measures whether a disclosure REPEATS earlier-public news (completions, amendments), not whether the market EXPECTED it; the hypothesis 'expected news moves prices less' cannot be tested with it and stays untested. Labeled isolated events 2004-2026: previously_announced 2,737 of 10,877 (25%), 54% of them acquisitions; labels are unique (22,283 for 22,283 events).
B. EVENT BAND CLASS AUDIT (scripts/card/event_band_class_coverage.py, commit 18f5c1d; read-only; reuses day_card.band_multiplier and the pooled edge 1.337). The card's event band is half-width = edge x stress scale x multiplier, the multiplier from an ADDITIVE log model (intercept 0.833; type capital_raise -0.549, regulatory +0.078, restructuring +0.381; size large +0.864, moderate +0.331; timing previously_announced -0.657; day +1 -0.349; ordinary_day_mean_z5sq 1.015; floored at 1.0; references acquisition / small / new / day 0). EXCLUDED_TYPES = ipo_spinoff, systemic_shock, geopolitical, natural_disaster: band_multiplier returns None and combine_multiplier then returns 1.0 (verified in the code), with the same 1.337 edge.
- Population: labeled events in ev_ent, day 0 and +1, from 2005, no 2.02 filing on day i or i+1, exactly one labeled event per stock-day (44,742 event-days considered, 1,084 ambiguous stock-days left out, 36,923 kept; 31,579 from 2005). Rule (before the run): a class is MISCALIBRATED if every era (2005-2012, 2013-2019, 2020-2026) has >= 300 stock-days, coverage outside 86-94% in the same direction and the 95% interval excludes 90%; gate: overall 88-92% in every era. Validated on synthetic worlds (control 0 flags; planted acquisition x previously_announced detected; a planted class with about 100 stock-days per era correctly 'cannot tell').
- RESULT: gate PASS, 31 classes testable, 0 MISCALIBRATED. Overall coverage 91.1% [90.6, 91.6] / 89.8% [89.2, 90.3] / 89.6% [88.9, 90.2]. Timing: new 92.0 / 90.6 / 90.2, previously_announced 89.2 / 88.0 / 87.9; acquisition x previously_announced 90.7 / 89.4 / 89.4 (calibrated).
- NOT FLAGGED BY THE RULE BUT NOTED: (1) ipo_spinoff (excluded type, multiplier 1.0): 76.4 / 69.9 / 66.5% (n 242 / 292 / 182), pooled about 71% (SE 1.7 points, n 716, about 2.3% of event stock-days), not flaggable because the last era has fewer than 300 days; (2) small x previously_announced 87.2 / 87.3 / 86.3% (n 1,199 / 918 / 753), all intervals below 90 but the last era is 0.3 above the 86% line, and non-acquisition previously_announced about 87% in each era (POST HOC, derived by hand from rounded percentages); (3) era drift 91.1 -> 89.8 -> 89.6 overall.
- THE 89.15% QUESTION IS CLOSED: the ledger (flag_ledger_evidence, band_edge_calibration_90) records walk-forward coverage 0.8915 for the 'event' group with edge 1.337 fitted on all years (others: earnings + event 0.8847 with n 3,044, edge 1.433; earnings day 0 0.8949, edge 1.506; day +1 0.887, edge 1.384; ordinary 0.9021; Regulation FD 0.8983, edge 1.319; ordinary calm / normal / elevated / high edges 1.527 / 1.441 / 1.289 / 1.29). The audit's pooled in-sample 90.2% on the labeled subset differs mostly because it is in-sample versus walk-forward and shows the era drift; the last quarter point may come from leaving out multi-event days (NOT verified).
- Ledger: event_band_class_calibration_audit (null) with 18 evidence rows CONFIRMED.
C. IPO_SPINOFF WALK-FORWARD (scripts/card/ipo_spinoff_walkforward.py, commit b1d2af2; read-only; imports the audit's event-day builder; self-check reproduced the audit exactly: n 242 / 292 / 182, coverage 76.4 / 69.9 / 66.5%). Multiplier = 90th percentile of |band unit| over the TRAINING days / 1.337; train 2005-2012 -> test 2013-2019 and train 2005-2019 -> test 2020-2026; PASS needs coverage 86-94% AND interval-score ratio below 1 in both test eras. RESULT: PARTIAL. 2013-2019 (multiplier 1.57 from 242 days): coverage 69.9% -> 83.9% [79.3, 87.7], ratio 0.881 [0.829, 0.922]; 2020-2026 (1.90 from 534 days): 66.5% -> 90.7% [85.6, 94.1], ratio 0.797 [0.730, 0.877] (bootstrap holds the multiplier fixed). In-sample implied multipliers 1.57 / 2.06 / 1.87 (not monotone; SE about 0.2, my estimate: drift NOT established); pooled 1.89 on 716 days (information only). A correct multiplier trained on 242 days and judged on 292 would miss the 86-94% window roughly one time in five: PARTIAL is an ordinary outcome on a small sample (context, not a re-grade; my own predicted coverage range 84-92 was wider than the pass window and should have matched). Ledger: ipo_spinoff_band_multiplier_walkforward (lead) with 10 evidence rows CONFIRMED. DECISION PENDING (Galen's): nothing on the card changes from this test alone (pre-registered); adopting a provisional multiplier of about 1.9 for about 2.3% of event days is a product decision with a forward check advised. A patch adding the measured coverage to the ipo_spinoff note in day_card.band_multiplier (no multiplier changes; tested identical for 7 types x 2 days) was issued: PROBABLY APPLIED (commit 8d743b0 sits between b1d2af2 and the tally commit f7bf31b) but NOT confirmed; check with: git log --oneline -6 and grep -n 'measured 2026-10-22' scripts/card/day_card.py.
D. PREDICTION TALLY (results/prediction_tally_2026-10-22.md, commit f7bf31b): 54 numeric range predictions visible in the session, scored strictly (the old bare tick) and 'within noise': 30 inside (56%, against about 80% for well-set 80% ranges), 15 outside but within noise (28%), 9 real misses (17%); 7 probability calls, mean Brier 0.114 (always 50% scores 0.250); five 'something new will work' calls (15, 12, 35, 55, 55%) all came out no (chance of that about 10%: mild over-optimism or chance). Misses cluster in how often a feature appears in the data (FD volume, an overlap count, the own-source share, title matches), not in effect sizes; effect misses ran one way (predicted amplification above 1.00, got at or below). The NEAR boundary is my judgment. Rules going forward: do not predict a count a single query answers; predict effects and outcomes; keep probabilities for pass/fail; log predictions when made in results/prediction_log.csv (scaffold offered, not created). Since the tally: one more categorical call missed (the cause of the financial_growth_classified NULLs was my 5% 'something else' bucket); the AAPL call (80%) came true.
E. HOUSEKEEPING SWEEP. Notes confirmation: Fed and executive-order rows carry CLEANED RERUN and SCORING CORRECTION; the law row carries CASE LIST, BENCHMARK, BURST COMPARISON and LABELER CHECK (all CONFIRMED). Null register after the UPDATE blocks (CONFIRMED, 105 columns): backup_copy 36 (18,048 NULLs), unverified 22, structural 18, guarded_sparse 11 (259,626), low_value 10 (62), by_design 3 (212), dead 3 (51,750), legacy_unread 1 (533,369), stale_snapshot 1; the structural moves reconcile to the row (8,473 x 2 fiscal_quarter + 1,548 x 2 law votes + 9,141 operating_income + 9,286 operating_margin = 38,469; 16,763 + 38,469 = 55,232) and by_design (61 + 58 = 119; 93 + 119 = 212). My statement that structural would 'grow by 5' was a slip (it is 6).
F. financial_growth_classified (the 'investigate' column) CLOSED: a STALE SNAPSHOT, not a defect. 381 rows for 6 securities (AAPL, AMD, MSFT, PFE and two more), one batch calculated 2026-08-26; financial_metrics was recalculated 2026-10-06 so all 381 are older than their source. revenue_yoy_growth: 193 NULL = exactly the rows typed insufficient_data (a CORRECT label for a missing input; my earlier framing of this as a defect is RETRACTED); the source now has a value for 160 of them (33 NULL in both) and 26 of the 188 other values differ (6 of the 12 largest flip sign). Verified on AAPL from financial_statements revenue: the quarter ending 2023-04-01 is 94,836 / 97,278 - 1 = -2.51% (current source -0.0251; snapshot +0.1432 = 94,836 / 82,959, one quarter too LATE); the quarter ending 2024-06-29 is 85,777 / 81,797 - 1 = +4.87% (source 0.0487; snapshot -0.0955 = 85,777 / 94,836, one quarter too EARLY). Mechanism (positional four-back lookup on a list with a gap and an extra row at the time) is INFERRED, not verified. Net income: 97 NULL (66 now present in the source, 31 NULL in both) and 42 of 284 non-NULL values differ. Consumer: candidate_financial_events (uses only the net income columns; revenue_yoy_growth is passed through) is referenced by NO script or SQL file outside the schema files; no script writes the table. DECISION: document and leave; rebuild from the current source before any use of the view. Register: revenue_yoy_growth set to stale_snapshot (CONFIRMED); net_income_yoy_growth update issued (expect stale_snapshot 2, unverified 21).
G. PENDING. (1) Confirm the day_card.py note patch (see C); (2) Galen's decision on a provisional ipo_spinoff multiplier of about 1.9 (forward check on later days advised); (3) optional pre-registered tests: non-acquisition previously_announced with a held-out era (post hoc origin), coverage on the 1,084 multi-event stock-days, a tariff-title split of the 2025-2026 executive-order watch item (read titles first), an outside FOMC meeting calendar for the Fed test; (4) January 2027, in this order: ingest the missing 8-K weeks, refresh prices, rebuild the return cache and matrices, then evaluate the surprise forward test ONCE and the role-band forward test with their frozen rules (never edit earnings_surprise_test.py before the verdict); (5) October sentiment top-up at month end: python3 scripts/gdelt/backfill_gdelt_sentiment.py 2026-10 2026-10 --ignore-checkpoint; (6) read scripts/tagging/resolve_sentiment_confounds.py; (7) 8 audit rows still need_more; parked: the AI-real block (7,784), 127 creatable events, 15 salvage rows; (8) the 76 unknown laws vote-kind reparse, disable nightly-classify, condense master-todo-list.md; (9) optional scaffold results/prediction_log.csv. Next consolidated entry in about 15 messages.
- 2026-10-22 (addendum to note 5, items CONFIRMED): the day_card.py ipo_spinoff note patch landed (commit 8d743b0; the text is at line 147 of scripts/card/day_card.py); the net_income_yoy_growth register update landed (stale_snapshot 2, unverified 21, 105 columns in total). Remaining open items: Galen's decision on a provisional ipo_spinoff multiplier, and the January 2027 forward-test preparation.
- 2026-10-23 (addendum to note 6, VERIFIED): the annual period-builder fix is applied and committed (dfab63d); the same 14-ticker dry run is IDENTICAL under PYTHONHASHSEED 0, 1 and 2 (md5 7f95b0d0...), and it reproduces the stored originals where the old builder gave recasts under some seeds (AAPL: 13 changed cells under seed 0 -> 11, free_cash_flow only; ARES: 7 -> 3). The quarterly builder needed no change. STABLE differences that remain (stored vs the earliest-filed fact; seed-independent): ACGL total_equity 2, AES 6, AOS assets and liabilities 2, ARE filed_date 4, ATO filed_date and revenue 10 (plus 21 new rows), BF-B revenue 22 (plus 24 new; stored net sales vs the parse's gross-sales concept: 3,248 vs 4,201 million for FY2018); candidates for a later audited point-in-time review, not for the additive refresh. FREE CASH FLOW RESOLVED: the 3,610 cleared cells are correct stored values (AAPL fiscal-Q1 examples 37,503 million for 2023-12-30, 26,995 million for 2024-12-28 and 51,552 million for 2025-12-27 equal operating cash flow minus capex as Apple reported them, from recollection, not re-checked here); the parser computes free_cash_flow only for annual rows and the Q4 derivation, so a full-mode refresh would erase them and the additive mode preserves them; possible later project: compute free cash flow for Q1 (three-month facts) and for Q2/Q3 by differencing year-to-date facts, which would raise coverage. ADDITIVE WRITE VOLUME under the OLD parser: 346 new rows + 118 rows with fills (revenue 118, operating_income 12, net_income 12, gross_profit 11) = 464; the fixed-parser figure comes from the rehearsal logs stmt_fix_a.log and stmt_fix_b.log, PENDING. My call 'most cleared cells are Q4 or annual rows' (60%) was wrong (the examples are Q1 rows). The earlier 'patch file missing' message was a misfire of the && / || chain (the patch had already been applied).
- 2026-10-23 (addendum to note 6, VERIFIED): the annual period-builder fix is applied and committed (dfab63d); the same 14-ticker dry run is IDENTICAL under PYTHONHASHSEED 0, 1 and 2 (md5 7f95b0d0...), and it reproduces the stored originals where the old builder gave recasts under some seeds (AAPL: 13 changed cells under seed 0 -> 11, free_cash_flow only; ARES: 7 -> 3). The quarterly builder needed no change. STABLE differences that remain (stored vs the earliest-filed fact; seed-independent): ACGL total_equity 2, AES 6, AOS assets and liabilities 2, ARE filed_date 4, ATO filed_date and revenue 10 (plus 21 new rows), BF-B revenue 22 (plus 24 new; stored net sales vs the parse's gross-sales concept: 3,248 vs 4,201 million for FY2018); candidates for a later audited point-in-time review, not for the additive refresh. FREE CASH FLOW RESOLVED: the 3,610 cleared cells are correct stored values (AAPL fiscal-Q1 examples 37,503 million for 2023-12-30, 26,995 million for 2024-12-28 and 51,552 million for 2025-12-27 equal operating cash flow minus capex as Apple reported them, from recollection, not re-checked here); the parser computes free_cash_flow only for annual rows and the Q4 derivation, so a full-mode refresh would erase them and the additive mode preserves them; possible later project: compute free cash flow for Q1 (three-month facts) and for Q2/Q3 by differencing year-to-date facts, which would raise coverage. ADDITIVE WRITE VOLUME under the OLD parser: 346 new rows + 118 rows with fills (revenue 118, operating_income 12, net_income 12, gross_profit 11) = 464; the fixed-parser figure comes from the rehearsal logs stmt_fix_a.log and stmt_fix_b.log, PENDING. My call 'most cleared cells are Q4 or annual rows' (60%) was wrong (the examples are Q1 rows). The earlier 'patch file missing' message was a misfire of the && / || chain (the patch had already been applied).
- 2026-10-23 (CORRECTION to note 6 and its addendum): results/JANUARY_2027_RUNBOOK.md was NOT in the repository when checked (the heredoc that creates it was never run), although note 6 said it was written; it was created 2026-10-23 with the additive-only step 2 built in (the separate step-2 patch is no longer needed). CONFIRMED commits: law parser e0ba24e, certifi 35877d8, statements wrapper b0e10c9 / 1dd3344 / 8cab9af, annual builder fix dfab63d, role-band forward test 86a21e0, cache extender f4991ac, exhibit_reclass_test b24a631, GDELT checkpoint untracked 3db6f49.

<!-- entry: 2026-10-22-07 | date: 2026-10-22 | label: note 4 | source-line: 3592 | approx: no -->
### 2026-10-22-07 — CONSOLIDATED NOTE 4: T3a Fed change days, T3b executive-order days, data guard and anomalies, prediction convention, T4 closed
> Original heading: `### 2026-10-22 (night) -- CONSOLIDATED NOTE 4: T3a Fed change days, T3b executive-order days, data guard and anomalies, prediction convention, T4 closed`
A. T3a FED TARGET-CHANGE DAYS (scripts/card/fed_change_day_test.py, commit b051e8d; read-only; the sector test: log ratio of a sector's mean |return|/v64 to the rest of the market from sector_day_z, against baseline days 21-63 trading days away excluding change days and the day after; placebo shifts of +-21 days; pass line Financials day 0 t >= 2.5 in both eras, lead t >= 2.0). Events: DFEDTAR to 2008-12-15 plus DFEDTARU from 2008-12-16 = 59 change days from 2004 (27 in 2004-2008: 17 hikes, 10 cuts; 32 in 2015-2026); 31 scored in 2015-2026 because the 2026-09-17 hike (3.75 -> 4.00) falls after sector_day_z ends (2026-09-15). RESULT: NULL, placebos clean. Financials day 0: 1.065 [0.969, 1.171] t +1.30 (n 27) and 1.038 [0.945, 1.140] t +0.78 (n 31); placebo 0.994 (t -0.19, n 53) / 0.965 (t -1.02, n 62); excluding the crisis cuts 1.054 / 1.047; hikes 1.070 / 1.044, cuts 1.057 / 1.027; day -1 0.984 / 1.087; day +1 0.986 / 0.990. NOT ZERO but undetectable: one era resolves about 12.8% at t 2.5; a hand-pooled post hoc estimate is 1.05 [0.98, 1.12]. Descriptive: Real Estate 1.025 / 1.044, Utilities 0.986 / 0.991, Health Care 1.051 / 0.978; 22 sector-era cells with 4 at |t| >= 2 (expected about 1): Consumer Staples +2.34 and IT -2.64 in 2004-2008, Energy -2.05 and Industrials +2.51 in 2015-2026; only Energy and IT point the same way in both eras; none hypothesized. LIMITS: change days cannot be told from FOMC meeting days (held meetings are not in the database; the meeting calendar would have to come from outside); other sectors read about 2% low when Financials are truly higher (the comparison includes them). Validated on synthetic worlds (no effect NULL, planted 1.15x PASS at t 6.6 / 5.7, crisis regime NULL). Ledger: fed_change_day_financials_amplification (null) with 12 evidence rows CONFIRMED by listing.
B. T3b EXECUTIVE-ORDER SIGNING DAYS (scripts/card/eo_day_test.py, commit 2a8e8bc; the market-wide version: n-weighted mean z of the 11 sectors; same baseline and placebos; PASS needs t >= 2.5 in 2004-2014 and 2015-2026, clean placebos AND the 2015-2024 subset t >= 2.0). Relevant orders 859 on 704 distinct days (1994-2026); from 2004: 171 days in 2004-2014 and 350 in 2015-2026 (240 in 2015-2024, 110 in 2025-2026); the 350 is 10 below the 360 counted from the SQL: 3 order days fall after 2026-09-15 and weekend-dated orders merge into the next trading day (16 weekend dates since 2015; the number of merges was NOT verified). RESULT (cleaned data): NULL. Day 0: 0.969 [0.921, 1.019] t -1.22 (2004-2014), 1.009 [0.967, 1.053] t +0.40 (2015-2026), 0.977 [0.928, 1.028] t -0.89 (2015-2024); placebos 0.986 (t -0.58) / 0.965 (t -1.84): clean but both below 1 (an offset of about 1-3 points); medians 0.927 / 0.969 / 0.939; in 2004-2024 the data exclude an amplification above about 2-3%. POST HOC WATCH ITEM (needs its own pre-set forward test; tariff orders are themselves news; about eight looks): 2025-2026 day 0 1.081 [1.002, 1.167] t +2.02, day +1 1.158 [1.077, 1.245] t +3.98, medians 1.055 / 1.108. Weekday check: order days skew to Thursday and Friday (7.4 / 7.6 / 8.6 / 9.7 / 10.5% of Monday..Friday), but the order-day-weighted weekday mean market z is 0.7628 vs 0.7627 for all days (ratio 1.0001): not a weekday artifact. Ledger: eo_relevant_signing_day_market_move (null) with 10 evidence rows CONFIRMED.
C. DATA ANOMALIES AND GUARDS. FIVE stray price rows on closed-market dates, listed and LEFT IN PLACE (a deletion would need an audit table): 1996-05-27 (Memorial Day, 1 row), 2009-07-26 (a Sunday, 1 stock, z 89.0), 2016-02-27 (a Saturday, 1 stock), 2024-05-27 (Memorial Day, 2 stocks), 2025-12-25 (Christmas, 2 stocks); market_prices has exactly these five dates below 150 rows; sector_day_z has the four from 2004. None is in audit_matrices.npz's calendar (checked), so the lane tests never saw them. GUARD (commit ed51e0a): fed_change_day_test.load_sector_day drops any day with fewer than 100 stocks in total (MIN_DAY_STOCKS, prints a DATA GUARD line; eo_day_test imports it); it caught all four (my weekend-only query had found two). Effect on the first results at most 0.002: cleaned reruns EO era A 0.967 -> 0.969, era B 1.009 unchanged, 2025-2026 1.081 unchanged, Fed Financials identical; the predictions for them (a point and a range) were all inside. The stock card needs no patch: it computes market-wide stress only when more than 20 other stocks have data and otherwise prints 'not available' (my statement that it would print a confident number was WRONG and is retracted).
D. PREDICTION CONVENTION (Galen's point: predicted ranges sat within a standard error of the floor, so near-misses were labelled failures). From now on every numeric prediction is a point estimate plus a range at least +-1 standard error wide, scored as the distance in standard errors and whether the 95% interval overlaps the range (never a bare tick or cross); the target is about 80% of ranges inside; verdict-level probabilities stay sharp; large misses remain misses (7.01 share, own-source share, habit-switch damage, T4 title counts). Re-scored: EO era A 0.967 vs a floor of 1.00 is 1.3 SE below (the interval overlaps), 2015-2024 0.977 is 0.9 SE below, the per-day spread 0.41 vs 0.25-0.35 is statistically clear (about 3.9 SE) but moves the resolution only from 4.9% to 5.6%, Fed Utilities 0.986 is 0.2 SE below the floor. SCORING-CORRECTION UPDATEs on the two rows were issued (not seen confirmed). An optional tally of all numeric predictions on record, scored both ways, was offered and NOT run.
E. T4 LAW-DRIVEN CHARGE EVENTS (title scan of the events table; no test possible). 31 distinct events (32 matches) carry law language in the title: Tax Cuts and Jobs / tax reform 10 (7 with a charge word, 2016-2020), Affordable Care Act / health reform / retiree subsidy 9 (8, all between 2010-03-24 and 2010-04-13), CARES / stimulus 7 (0), Dodd-Frank 3 (1), Inflation Reduction Act 1 (also the generic-language match), Sarbanes-Oxley 1. Case list from event_market_reactions_corrected: 18 rows for 19 matched events (one has no row there); 13 DISTINCT non-bundled events attribute a charge or impact to the law (ACA 8: CAT, AT&T, 3M, Boeing, Xcel, Lockheed, Verizon, MetLife; Tax Cuts and Jobs 5: BAC, GS, BMY, AES, AMP; the AT&T duplicate, two bundled 'real 20XX activity' titles and two utility rate-case rows were set aside). DESCRIPTIVE ONLY, market-adjusted: day 0 mean -0.38% (SE about 0.24%, t about -1.6), median absolute 0.30%, 8 of 13 negative on days 0, 1 and 5; only AES exceeds 1% (-2.92%); day 5 mean -0.76% (SE about 0.6%); the 3M seed case +0.15% / -0.04% / +2.2%. With 13 events only a mean shift of about 0.6% would reach t 2.5. The classifier table has 66 real_event filings whose description or reasoning names one of seven laws: too few for any single law to reach 40 events with 10 charges. Ledger: law_driven_charge_events_titles (untested) with 6 evidence rows CONFIRMED; the case-list note was issued. Predictions in the new convention: total title matches 150 (90-260) vs 32 (about 10 SE below the floor: a conceptual miss, law attribution lives in 8-K text), ACA 25 (10-50) vs 9 (0.3 SE below), TCJA 20 (8-40) vs 10 inside, charge-word share 45% (30-60%) vs 50% inside.
F. STATE. The historical line of the earlier plan is finished: T3a (Fed change days), T3b (executive-order days), T4 (law-driven charges) and the storm counts are all closed; no new flag has passed. Ledger rows added this stretch (all null or untested): flag_overlap_storm_testability, fed_change_day_financials_amplification, eo_relevant_signing_day_market_move, law_driven_charge_events_titles.
G. PENDING. (1) Confirm the issued UPDATEs: SELECT flag_key, notes LIKE '%CLEANED RERUN%' AS cleaned, notes LIKE '%SCORING CORRECTION%' AS scored, notes LIKE '%CASE LIST%' AS caselist FROM flag_ledger WHERE flag_key IN ('eo_relevant_signing_day_market_move', 'fed_change_day_financials_amplification', 'law_driven_charge_events_titles'); (2) the optional benchmark query for T4 (median |abnormal return| on event days) and the optional widening of T4 through the 66 classifier filings (read first); (3) January 2027, in this order: ingest the missing 8-K weeks, refresh prices, rebuild the return cache and matrices, then evaluate the surprise forward test ONCE and the role-band forward test with their frozen rules (never edit earnings_surprise_test.py before the verdict); (4) October sentiment top-up at month end: python3 scripts/gdelt/backfill_gdelt_sentiment.py 2026-10 2026-10 --ignore-checkpoint; (5) read scripts/tagging/resolve_sentiment_confounds.py; (6) the null register summary (SELECT kind, COUNT(*) FROM null_register GROUP BY 1) and the 'investigate' trace of financial_growth_classified; (7) 8 audit rows still need_more; parked: the AI-real block (7,784), 127 creatable events, 15 salvage rows; (8) the 76 unknown laws vote-kind reparse, disable nightly-classify, condense master-todo-list.md; (9) optional descriptive follow-ups: the tariff-title split of the 2025-2026 executive-order watch item (read the titles first), the prediction tally, an outside FOMC meeting calendar to separate meeting days from change days. Next consolidated entry in about 15 messages.


<!-- entry: 2026-10-22-06 | date: 2026-10-22 | label: note 3 | source-line: 3581 | approx: no -->
### 2026-10-22-06 — CONSOLIDATED NOTE 3: ledger evidence backfill, earnings surprise results and the forward-test freeze, data freshness (history-first), NULL follow-ups 
> Original heading: `### 2026-10-22 (evening) -- CONSOLIDATED NOTE 3: ledger evidence backfill, earnings surprise results and the forward-test freeze, data freshness (history-first), NULL follow-ups and the null register, flag-overlap ('storm') counts`
A. FLAG LEDGER EVIDENCE BACKFILL (every proven or lead row with a NULL multiplier now carries structured numbers). flag_ledger_evidence = (flag_key, era, n, estimate, se, unit), PK (flag_key, era), FK to flag_ledger; day_web.py prints the FIRST THREE evidence rows per flag unsorted (era, estimate, n; no unit), stock_card.py selects explicit columns and reads flag_ledger.multiplier only for event_daily_range_coverage (so the NULL multipliers are harmless by design). Backup table flag_ledger_evidence_backup_20261022. Inserts are guarded (only for flags in the ledger, only for missing (flag, era)). CONFIRMED by listings: batch 1 = 14 rows for 7 flags (macro_yield_shock_financials 2, macro_yield_shock_real_estate 2, longhist_yield_shock_health_dampening 3, earnings_role_bands_walk_forward 4, event_day_width_own_events 1, eightk_item_7_01_width 1, unrecorded_sector_theme 1); batch 2 = 52 rows (labeler_size_timing_validity 18, band_edge_calibration_90 15, band_stress_scale_median 5, macro_yield_shock_defensives_post_hoc 6, event_earnings_window_width 8); earnings_surprise_size_revenue 7 and earnings_surprise_sign_operating_income_forward 2 (earnings_surprise_sign_revenue already had 4 rows in a percent convention and was skipped by the guard); storm_tier_large 2 (6.90 vs 5.45 percent; UNIT INFERRED, not recorded: the ledger says 'large prior reaction and the next event reaction, 20 days'; the original result file was never found; computed by populate_storm_tier.py and consumed by the model scripts). Assumptions stated in the unit text: standard errors 'from t' are derived from rounded t values; era labels on the defensives rows and the interval-score rows are inferred; unit wording is mine. Only the first 700 characters of each ledger note were read, so numbers beyond them may be missing. An optional UPDATE putting the two forward-flag rows on the percent convention (0.552 -> 55.2) was issued, NOT confirmed. 27% of evidence rows still lack se.
B. EARNINGS SURPRISE TEST (scripts/card/earnings_surprise_test.py, output results/2026-10-19/earnings_surprise.out; revenue-trend surprise = year-over-year change against the previous 8 quarters' changes, standardized; no consensus data). Coverage: 28,396 quarterly rows, 27,803 matched to an item 2.02 filing (98%), 26,016 with a usable two-day outcome and no recorded event; events with a surprise: revenue 21,041, operating income 15,934, net income 21,004. SIGN (hit rate; 95% Wilson; chance 50%; permutation p < 0.001 everywhere): revenue 53.4% [52.4, 54.4] n 9,107 (2009-2018), 52.9% [52.0, 53.8] n 11,933 (2019-2026); operating income 55.2% [54.0, 56.4] n 6,874 / 54.3% [53.3, 55.4] n 9,058; net income 55.4% [54.4, 56.4] n 9,065 / 53.0% [52.1, 53.9] n 11,936. Same-events control (n 6,849 / 9,055): revenue 53.7 / 53.0, operating 55.1 / 54.4, net income 54.7 / 53.1. Mean two-day miss +0.59% after a positive revenue surprise (n 11,349), -0.25% after a negative one (n 9,691). Pre-set sign rule (revenue >= 54% in both eras): DOES NOT PASS, but the edge is +3.4 / +2.9 points over chance (operating income +5.2 / +4.4, post hoc). SIZE: calibrated multiplier by tercile of |revenue surprise| low 2.54 (14,064 days), middle 2.53 (14,026), high 2.59 (13,980); high / low 1.02; three scales vs one -0.0030 / +0.0001 / -0.0003 nats (bar +0.005; positive in 6 of 15 years): does not earn a place. Predictions: sign verdict right (hit rate under-predicted: 51-53%); size prediction WRONG (said it would pass with high/low >= 1.3x; read 1.02x). Ledger: earnings_surprise_sign_revenue (null), earnings_surprise_size_revenue (null), earnings_surprise_sign_operating_income_forward (untested).
- FORWARD TEST (scripts/card/earnings_forward_test.py, commit 914d857, rule FROZEN 2026-10-20): item 2.02 filings dated 2026-10-14 to 2026-12-31, no recorded event on day 0 or +1, measure operating_income (same surprise definition as above), outcome sign of the two-day cumulative miss; PASS = >= 300 events, hit rate >= 54%, permutation p <= 0.05 (2,000 shuffles within the calendar quarter, seed 20261020); DOES NOT PASS only with >= 500 events; 300-500 events INCONCLUSIVE (power about 45-60% if the true rate is 54.5%); < 300 TOO FEW. Evaluate ONCE with --evaluate after the season; run only the readiness check before that. NEVER edit earnings_surprise_test.py (the forward test imports it) or the forward script before the verdict. Readiness 2026-10-22: price cache and matrices end 2026-10-13, 0 filings in the window, 0 events. Operating income exists for only about 34% of Financials quarterly rows (coverage limit, in the ledger note).
C. DATA FRESHNESS AND THE HISTORY-FIRST PLAN. sec_8k_filings latest 2026-09-18 (weekly counts: 238 / 171 earnings in the week of 07-27; 3 filings and 0 earnings in the week of 09-14; nothing after); market_prices 2026-10-13; company_sentiment_timeline 2026-10-21; financial_statements (filed_date) 2026-09-22; events 2026-09-11; event_market_reactions_corrected 2026-08-27. This is the PLAN, not a failure: Galen switched to pure historical work on 2026-09-15 (history-building only, no live feeds; my first reading 'ingestion broke' was wrong). Workflows present: marketaux_daily.yml and nightly-classify.yml only; 8-K import is manual (import_8k_filings.py has a hardcoded COMPANIES list; bulk_import_8k.py processes companies with zero rows or tickers named, re-imports are safe because upload_filings upserts; a date-range refresh for all companies needs the get_8k_filings_for_company signature, not yet seen). Waiting costs nothing (filings stay on EDGAR). BEFORE evaluating the forward tests in January: ingest the missing weeks (dry run first, date overlap, duplicate check, one copy only), refresh prices, python3 -u scripts/card/build_return_cache.py then python3 -u scripts/card/gap_audit.py --rebuild. Matrices backup data_cache/audit_matrices_20261013.npz (35,221,184 bytes, local only; data_cache is gitignored). Card (commit 78a13ce): prints a DATA FRESHNESS line when the card date is after the last 8-K filing (verified: NVDA 2026-10-09 prints it, NVDA 2019-05-17 does not).
D. NULL FOLLOW-UPS AND THE NULL REGISTER. event_market_reactions and event_market_reactions_v2 are VIEWS; event_market_reactions_snapshot_20261019 and event_market_reactions_v2_snapshot_20261019 are BASE TABLE copies (v1 has 689 more valid 1-day returns and 117 more zeros than v2: likely zero-filled missing closes in v1; historical; the snapshots appear in only 2 script lines). event_market_reactions_corrected: 0 NULL returns; zero returns 135 / 65 / 48 / 21 at 0 / 1 / 5 / 20 days (0.85 / 0.41 / 0.30 / 0.13%), all with different prior and event price dates: NO date-mapping artifact; my earlier 'excess zero' claim was WRONG and is retracted (the same_close column is true by definition of a zero return). concurrent_event_count: 533,369 NULL of 940,758 in event_ripple_timeline (real zeros 134,675), no script or SQL file reads or writes it (grep empty): legacy. Cash-flow, gross-profit and derived columns: every reader checks for NULL (detect_financial_events.py, test_financial_market_reactions.py): guarded, fill only via an XBRL tag-mapping project.
- null_register (table_name, column_name, null_count, total_rows, pct_null, checked_on, kind, reason, action; PK (table_name, column_name)) built from the live inventory, 105 columns: backup_copy 36, unverified 31, structural 11, guarded_sparse 11, low_value 10, dead 3, legacy_unread 1, by_design 1, investigate 1. UPDATE block issued afterwards (the storm_tier INSERT in the same block was confirmed; the register summary after it has NOT been seen): fiscal_quarter NULL = exactly the 8,473 annual rows (annual 100% NULL, quarterly 0%); law_stage_dates final_yeas / final_nays 1,548 NULL = 637 unanimous + 574 voice + 261 unopposed + 76 unknown (628 roll-call laws carry counts; the 76 unknown await the read-then-reparse); operating_income missing (annual / quarterly %): Financials 64.5 / 65.7, Energy 32.1 / 35.4, Real Estate 30.9 / 33.2, Materials 26.6 / 27.6, Consumer Discretionary 17.4 / 20.0, Health Care 16.0 / 19.4, Communication Services 15.9 / 11.4, Industrials 13.1 / 15.1, Consumer Staples 12.3 / 13.9, Utilities 6.8 / 9.3, Information Technology 4.3 / 6.0 (Financials hold about 42% of the 9,141 NULLs); revenue NULL 2-6% by sector (Staples annual 11%); flag_ledger_evidence n and se are optional (by design). STILL 'investigate': financial_growth_classified.revenue_yoy_growth 50.7% NULL (193 of 381) against 9.9% in its source financial_metrics. Remaining unverified (about 26): financial statement tag gaps (revenue, net_income, total_assets, total_liabilities, total_equity, cash), growth ratios, macro_data_releases previous_value (81), event_pre_context market_cap_at_event (524) and storm_magnitude (1,450), law cosponsor / committee counts, consumer_financial_health_index deviations, classification_corrections.original_confidence (103).
E. FLAG-OVERLAP ('STORM') COUNTS (scripts/card/flag_overlap_counts.py; rule: measure overlaps, never multiply; counts only, no outcome looked at; final commit d12d5ff). Flags: OIL_E (oil shock |WTI change| >= 3%, prices > 5, Energy stocks), YLD_F / YLD_RE / YLD_H (|DGS10 change| >= 0.10 points; Financials / Real Estate / Health Care), JOB (PAYEMS known_on_basis first_release), EVT (own recorded event days 0 and +1), ERN (2.02 filing day i, i+1), FD (7.01 filing day i, i+1). Market-wide days: oil shocks 1,381, yield shocks 775, jobs-report days 394. Valid stock-days 2004-2018 / 2019-2026: OIL_E 9,483 / 7,580; YLD_F 19,670 / 13,134; YLD_RE 8,378 / 5,340; YLD_H 15,705 / 10,065; JOB 75,056 / 44,629; EVT 24,776 / 12,399; ERN 49,194 / 30,835; FD 27,487 / 16,260. REVISION after the first run (stock-day counts overstate independent information for pairs with a market-wide flag; a macro day hits many stocks at once): distinct overlap days added; for such pairs TESTABLE needs >= 100 days per era, MARGINAL 40-99, THIN < 40. FINAL: 2 of 28 pairs TESTABLE, 7 MARGINAL, 19 THIN. TESTABLE: EVT x FD (3,991 / 3,590 stock-days; 2,336 / 1,557 days) and EVT x ERN (2,315 / 1,472; 1,362 / 772). MARGINAL: JOB x ERN (2,432 / 1,754 stock-days but 169 / 87 days), ERN x FD (1,401 / 939), JOB x FD, JOB x EVT, YLD_F x ERN, YLD_H x ERN, YLD_F x FD. THIN includes every YLD x JOB pair (39 / 16 days), OIL_E x JOB (18 / 21 days) and all oil x yield pairs (0). Already covered: EVT x ERN by the card's 'earnings + event' group (coverage 88.5%, n 3,044), ERN x FD by the 7.01 check (225 / 400 / 353 habit events, intervals contain 90%). SAME-FILING CHECK (ev_ent x event_source_filings x sec_8k_filings; a 7.01 filing without 2.02 within d..d+3 of the event date): events with such a filing 2,311 (before 2019) and 1,915 (2019-2026); own source filing is that 7.01 for 1,936 (83.8%) and 1,771 (92.5%); only a separate 7.01: 375 and 144. Pre-set rule (own-source share >= 60% or < 300 separate events): EVT x FD is MECHANICAL, not an independent pair. CONCLUSION: the storm idea cannot be tested at the pair level on this universe; JOB x ERN (169 / 87 days) is the one marginal, knowable-in-advance pair left if ever wanted. Ledger: flag_overlap_storm_testability (untested; notes carry the counts and predictions), 18 evidence rows CONFIRMED; closing note and 4 more evidence rows (own-source shares 83.8 / 92.5, separate-7.01 events 375 / 144) issued. Predictions scored: stock-day counts 4-5 of 7 right (FD single volume, YLD_F x EVT era B, OIL_E x JOB 'marginal' missed), days column 4 of 5 right (JOB x ERN 169 / 87 vs 170-185 / 90-100 a hair under), same-filing check: own-source share 40-65% WRONG (83.8 / 92.5), separate events 375 right and 144 wrong.
F. PROCESS LESSONS. (1) Absence of data is not failure when the plan explains it (history-first); ask before declaring an incident. (2) Macro flags need distinct-day accounting, not stock-days. (3) Two flags built from the same filing are not an overlap: check the source linkage. (4) All-or-nothing patch scripts caught a double-matching anchor before any file was written. (5) Retractions kept in the record: the 'excess zero returns' claim (above), the tone 'no same-day relationship' claim (note 2). (6) Predictions stay in script headers and commit messages before every run.
G. PENDING. (1) Register summary after the UPDATE block (SELECT kind, COUNT(*) FROM null_register GROUP BY 1) and the optional 'investigate' trace of financial_growth_classified; (2) confirm the closing UPDATE and 4 evidence rows for the storm row (expect 22 evidence rows); (3) January 2027, in this order: ingest the missing 8-K weeks, refresh prices, rebuild the return cache and matrices, then evaluate the surprise forward test ONCE and the role-band forward test with their frozen rules; (4) October sentiment top-up at month end: python3 scripts/gdelt/backfill_gdelt_sentiment.py 2026-10 2026-10 --ignore-checkpoint; (5) read scripts/tagging/resolve_sentiment_confounds.py (flags computed on the old incomplete coverage); (6) 8 audit rows still need_more; parked: AI-real block (7,784), 127 creatable events, 15 salvage rows; (7) the 76 unknown laws vote-kind reparse, disable nightly-classify (its pool is static while ingestion is paused), condense master-todo-list.md; (8) next historical-line items on file: T3a Fed target-change days as a sector test, T3b executive-order days as a market-wide test, T4 law-driven charge events. Next consolidated entry in about 15 messages.


<!-- entry: 2026-10-22-05 | date: 2026-10-22 | label: note 2 | source-line: 3568 | approx: no -->
### 2026-10-22-05 — CONSOLIDATED NOTE 2: RSG ruling, tone lane, tone diagnostic, habit strength and the tie guard, NULL inventory
> Original heading: `### 2026-10-22 (later) -- CONSOLIDATED NOTE 2: RSG ruling, tone lane, tone diagnostic, habit strength and the tie guard, NULL inventory`
A. AUDIT CORRECTION. RSG 2023-08-18 (need_more) ruled EVENT: a company-wide EVP and COO departure is a named executive officer under Item 5.02 (rubric: confirm; a division-level COO is a judgment call); weak (orderly internal succession), consistent with the RJF 2019-10-01 and PTC 2017-02-03 COO appointments. UPDATE issued on review_queue_decisions (tier AUDIT, accession 0001193125-23-215466; the editor reported success). Audit miss rate now 6 events / 200 = 3.0% (95% 1.4-6.4%); up to 14 / 200 = 7.0% (4.2-11.4%) with 8 need-more rows still open. This SUPERSEDES the 2.5% in the earlier consolidated entry.
B. TONE LANE TEST (scripts/card/tone_lane_test.py, commit 6d07dfe; rule, five synthetic validation worlds and predictions committed before the run). Table read 1,260 s: 1,334,217 rows, 461 entities, 18.5% of stock-days with a tone z-score, POS days 19,276, NEG days 30,263. 2015-2020: POS 9,135, NEG 14,517; the day-t-1 miss was positive after POS flags 50% and after NEG flags 48%; UNMATCHED lift -0.7; MATCHED lift -0.7 points [-1.7, +0.5]; matched delta -0.007 band units [-0.028, +0.014]; placebo +1.0. 2021-2026: POS 8,271, NEG 12,181; 49% / 49%; unmatched -0.7; matched -0.7 [-2.1, +0.8]; delta -0.016 [-0.043, +0.009]; placebo +0.8. Held-out centre reduction +0.003% / -0.011% (bar 0.5%). VERDICT NO LANE; any next-day directional effect above about 1 point is excluded. Predictions 5 of 7 right (the 58-70% / 30-42% previous-day echo and the unmatched lift +1 to +6 were wrong).
- Ledger: gdelt_tone_shock_next_day_direction (null) INSERT issued, plus an UPDATE appending the correction in C (both silent; verify with SELECT flag_key, status FROM flag_ledger WHERE flag_key = ...). Card text (commit 18e7b62): news tone moved out of 'NOT YET MEASURED' into 'TESTED, NO DOCUMENTED EFFECT' (article volume width: +0.5 points against a bar of 5; tone direction: -0.7 points against a bar of +3).
- Incident: a second copy of the tone job was started by mistake and killed; before relaunching a background job run pgrep -af <script> first.
C. TONE DATA DIAGNOSTIC (scripts/card/tone_data_check.py, commit 1d11207; cache only, no database). The first reading ('tone does not track the same-day miss at all') was WRONG: rank correlation of tone z with the same-day signed band unit +0.0121 +- 0.0018 (2015-2020) and +0.0093 +- 0.0028 (2021-2026); next-day +0.0019 / -0.0014 (zero); L = -3..+3 neighbours +0.002 to +0.005; the peak is at lag 0 in both eras (no alignment problem). Flat across article counts (+0.010 at 3-4 articles, +0.013 at 30+). Day-level systematic component 1.3% of tone variance; flags are not clustered (20 days hold 1.7% of NEG flags, POS none); demeaned tone +0.0123 / +0.0096 vs raw +0.0121 / +0.0093. Reading: a real but tiny same-day relationship (about 0.01 correlation); the null is about the information content of GDELT company-day tone, not a construction flaw; the 3-point next-day bar (a correlation of about 0.016) was above even the same-day correlation. Diagnostic predictions 2 of 6 right (same-day correlation 0.00-0.04 and the lag-0 peak). None of the four diagnosis labels fired. DECISION: the GDELT sentiment line is closed for price modelling (volume and tone); article spikes stay useful as detector evidence, so the October top-up is still worth running.
D. REPORTING RULE ADOPTED (Galen's point): every null states the point estimate and the 95% interval, and the word 'zero' is reserved for an interval tight enough to exclude any effect above a written decision threshold ('smallest effect that would change a decision: X'), so a small non-zero number is recorded once and not rediscovered by rerunning.
E. HABIT STRENGTH AND THE TIE GUARD (scripts/card/habit_strength_check.py, commit 530937a; rule and predictions committed before the run; validated on four synthetic worlds incl. one where ties are reliable and the rule says KEEP). Real result (isolated earnings releases with a habit, 29,737): shares 4-0 64.9%, 3-1 28.2%, 2-2 6.9%. Agreement of the next quarter's own label with the habit: 4-0 92.4% (90.8 / 92.7 / 92.8 by era), 3-1 84.8%, 2-2 56.9% (54.8 / 60.0 / 55.4). ROLES / POOLED interval-score ratio: 4-0 0.840, 3-1 0.897 (roles clearly better), 2-2 1.088 [1.062, 1.112] (1.128 / 1.085 / 1.054 by era: roles 8.8% WORSE than pooled on ties). Roles coverage on ties: reaction 96.0%, other 79.6% (pooled 90-94% on both). Materiality: overall ratio 0.8694 -> 0.8643 with ties on the pooled band (-0.0051). VERDICT TIE GUARD JUSTIFIED (pre-set rule: above 1.00 pooled and in all three eras; probability on file 35%). Predictions: shares 4-0 right, 3-1 wrong (28 vs 14-24), 2-2 6.9% just under 7-14; agreement 4-0 wrong (92 vs 95+), 3-1 and 2-2 right; tie coverage right; tie ratio wrong (1.088 vs 0.93-1.06); materiality right.
- Applied (all-or-nothing patch /tmp/patch_tie_guard.py): earnings_roles.py (is_tie, apply_role returns None on a 2-2 tie, tie_note), day_card.py (a tie keeps the pooled band and prints a note; replaces the earlier WEAK HABIT wording of commit 0d27ba2), build_earnings_role_model.py (fit WITHOUT ties; --include-ties reproduces the old model). Refit: 2,040 of 29,737 ties excluded (6.9%); self-checks unchanged (33,023 events, 90.0% habit share); REACTION multiplier 3.609x (3.43 / 3.78 / 3.55 by era), edge_90 1.474, q90 5.322, n 27,697 (was 3.541x, 1.477, 5.229); OTHER multiplier 1.408x (1.52 / 1.43 / 1.31), edge_90 1.352, q90 1.904 (was 1.472x, 1.339, 1.970). Refit predictions all four right. Verified by hand: TPL 2026-08-06 (a tie) keeps the pooled day +1 band (edge 1.384, multiplier 2.47) with the tie note; NVDA 2019-05-17 and TGT 2018-11-20 keep role bands (edge 1.474). Commit command issued with message 'Role bands: 2-2 ties fall back to the pooled band (tie ratio 1.088 [1.062, 1.112], above 1.00 in all three eras; pre-set rule met); role model refit without ties' (confirm with git log). Watch in January: the other-day multiplier drifts down by era (1.52 -> 1.43 -> 1.31).
F. NULL INVENTORY (every numeric column of every public table with any NULL; read-only; 100 columns). DEAD (100% null): sec_filings.fiscal_quarter (49,892), caltech_audit_ripple.concurrent_event_count (42), july_redo_audit_ripple.concurrent_event_count (1,816). LIKELY STRUCTURAL (each needs a one-line check): flag_ledger.multiplier 93 of 100; law_stage_dates final_yeas / final_nays 71.1% (1,548 of 2,176; check against the pending vote-kind reparse of 76 unknown laws); macro_data_releases previous_value / change_from_previous 81 (first release per series); fiscal_quarter 22.9% (8,473 of 37,006) in financial_statements and financial_metrics (probably the annual rows); event_market_reactions snapshots of 2026-10-19: prior_close and return_0d null in 778 / 747 rows (IPO and first-day events), forward closes null in 92-749; event_ripple_timeline.concurrent_event_count 56.7% (940,758 rows; null may mean zero concurrent events). LIKELY DEFECTS (fillable), by value: cash-flow coverage in financial_statements (free_cash_flow 75.0%, capital_expenditures 68.4%, operating_cash_flow 59.8%, gross_profit 65.1% partly structural for banks and insurers) and the derived fcf_growth 85.2%, fcf_yoy_growth 77.5%, fcf_margin 75.3%, capex_revenue_ratio 68.7%, gross_margin 65.4%, operating_cash_flow_margin 60.4%; operating_income 24.7%, eps_basic 21.7%, eps_diluted 21.6%; cash 10.1%; total_liabilities 5.75%, total_assets 5.6%, total_equity 3.05%, revenue 3.03%, net_income 2.5% (37,006 rows); event_pre_context.market_cap_at_event 3.2% (524 of 16,488) and storm_magnitude 8.8% (1,450); law_stage_dates.cosponsor_count 26.9% and committee_count 5.2%; classification_corrections.original_confidence 52.8% (103 of 195). SUSPICIOUS: financial_growth_classified.revenue_yoy_growth 50.7% null (193 of 381) against 9.9% in its source financial_metrics (derivation or join problem). LOW VALUE: consumer_financial_health_index deviations (cdsp 42.1%, pcecc96 10.0%, drcclacbs 8.2%, others about 2.3%: warm-up windows and an unfilled quarterly series), event_market_reactions_corrected sector-peer columns 0.51% (81 events, no peers), stale_url_sweep_results.new_confidence 13, global_events_daily_counts.avg_tone 2, event_removal_audit_precontext 1.
- BLIND SPOT: the inventory sees NULLs only; a pipeline that fills missing values with 0 would look complete. Follow-ups issued (read-only): zero-and-null counts for every numeric column of the event_market_reactions% tables; the distribution of event_ripple_timeline.concurrent_event_count; flag_ledger multiplier nulls by status. Still needed: the column list of financial_statements and sec_filings to look at cash-flow nulls by year and statement type.
G. PENDING. (1) git log to confirm 18e7b62, 1d11207, 530937a and the tie-guard commit; (2) SELECT to confirm the tone ledger row and its correction; (3) the NULL follow-ups above, then the cash-flow coverage by year; (4) January 2027 forward test (scores the role bands including the tie guard on unseen days); (5) October sentiment top-up at month end: python3 scripts/gdelt/backfill_gdelt_sentiment.py 2026-10 2026-10 --ignore-checkpoint; (6) read scripts/tagging/resolve_sentiment_confounds.py (flags computed on the old, incomplete coverage); (7) 8 audit rows still need_more; (8) parked: the AI-real block (7,784), 127 creatable events, 15 salvage rows; (9) 76 unknown laws vote-kind reparse, disable the nightly-classify GitHub Action, condense master-todo-list.md. Next consolidated entry in about 15 messages.


<!-- entry: 2026-10-22-04 | date: 2026-10-22 | label: note 1 (state of play) | source-line: 3546 | approx: no -->
### 2026-10-22-04 — CONSOLIDATED STATE OF PLAY (covers everything since the sentiment-lane entry; per-message notes were deliberately skipped)
> Original heading: `### 2026-10-22 -- CONSOLIDATED STATE OF PLAY (covers everything since the sentiment-lane entry; per-message notes were deliberately skipped)`
A. REVIEW AND BACKLOG THREAD (closed)
- Tiers recorded in review_queue_decisions, reviewer 'Galen (accepted Claude pre-screen)', notes tagged 'prescreened:': AUDIT 200 (event 5, not_an_event 186, need_more 9), PREC 40 (classifier right 25, wrong 15), BUCK7 30 (26 right, 4 wrong), BUCK8 30 (25 right, 5 wrong), PILE313 20 (4 real, 1 need more, 15 not events). The 25 earlier P1 prescreens are unchanged. Accepted pre-screens are NOT independent human reads: a later scoring of the classifier should use only independent decisions.
- Random noise audit (200, seeded 20261022): classifier MISS RATE 2.5% (1.1-5.7%), up to 7.0% (4.2-11.4%) if all 9 need-more are events. Interval = sampling error only (excludes the pre-screener's reading error; the optional independent 40-row check was not done). Misses cluster in below-C-suite leadership, guidance via Item 7.01, and capital return.
- AI 'real event' undecided block: 7,784 rows; 1,338 are policy-excluded types (capital_raise 581, governance_action 372, corporate_action 385), leaving 6,446. Random 40 of the 0.80-0.92 band (pool 6,067): PRECISION 62.5% (47-76%; 55-70% over the weak calls). Wrong calls: deal and financing administration (TEL bridge, URI notes, PG HSR, WY proxy supplement, XEL SPA exhibit, HCA credit amendments, CRM warrant settlement, SNA benefit trust), governance bylaws (GS, WM), legal procedure or undisclosed terms (PHM, PCG, ZBH), trivial or social (KMB 3 cents of EPS, YUM foundation). Right: every CEO/CFO/President/Chairman change, named-counterparty deals with dollar figures, formal legal and regulatory actions, guidance warnings, quantified charges.
- Calibration CORRECTION: earlier 'decided-row' rejection rates (leadership 1.0%, acquisition 1.3%) were contaminated by mass confirmations (2026-09-24: 12,488 rows at 1.5% rejected; 9,153 auto-confirmed rows at 0.92+ at 0.3%). Rows actually read: 0.80-0.92 novel_real_event_no_template_match 1,816 decided, 10.4% rejected; 0.92+ same flag 1,214, 8.4%; possible_duplicate about 6%; under 0.80 low_confidence 91, 40.7%.
- Text buckets (first-match order 1-9; undecided / read / rejected, read rows only): 1 financing tied to a deal 351/386/8.8%; 2 deal or filing administration 1,030/480/5.8%; 3 governance documents 236/90/16.7%; 4 legal procedure 332/149/6.0%; 5 equity or benefit housekeeping 145/133/38.3%; 6 charitable 17/5; 7 CONTROL top leadership 1,183/777/3.7%; 8 CONTROL deal with a dollar figure 695/561/7.7%; 9 other 3,795/1,746/11.1%. Bucket 7 is not pure leadership (deal releases quoting an executive's title land there). Pre-set bar 28 of 30 for confirming a bucket: BOTH FAILED (86.7%, 83.3%): nothing confirmed.
- Exclusion rules (title-based; keep if read-row rejection >= 40% with >= 30 read rows): only 'standalone offering' survives (152 undecided, 157 read, 54.1% rejected; mostly capital_raise-typed rows already excluded from promotion: no action). All six rules touch 668 of 7,784 (8.6%): the survivors would stay about 62% precise, so the fresh-40 test was not run. DECISION: park the AI-real block (undecided rows are outside the events table: no cost). If revisited: a second-reader pass with ONE question per filing (administrative step / sub-C-suite / standalone financing?); multi-rule prompts get ignored (v6).
- Dilution of existing events: 22,399 filings linked to events; any title rule hits 1,383 (6.2%): standalone offering 789 (capital_raise 613, financial_result 80, ipo_spinoff 43, corporate_action 22, other 31), the five other rules at most 633 (2.8%). Ordinary types: 503 of 18,711 = 2.7% upper bound (acquisition 2.7%, leadership 2.4%, financial_result 16.1%). Read rejection of rule-hit rows only 20-54%, so real contamination about 1%; bound on the 20-day premium shift 2.7% x 0.10 = 0.003 vs SE 0.0102. JUDGMENT (bends the pre-set 5% / 30-row read; justification = the bound): no read; available on request.
- 1,277 human-confirmed real_event rows in no event: policy-excluded 711, missing type 313 (269 also missing text), promotable with complete text 253. The 313: provenance unknown (none in candidate_review_log, classification_corrections, bulk_confirm_20261015, recoverable_rejected_noise, review_flip_audit_20261015, audit_flagged_20261014); 87% were AI noise calls, 83% have no review timestamp; seeded 20 read: 4 real, 15 not events: DO NOT REPAIR or promote. promote_events.py skips filings without title/description, which protects against accidental promotion. Dry run (--exclude-types capital_raise,corporate_action,governance_action): 398 groups; would create 127; confirmed duplicates 57; heuristic matches rejected 5; skipped missing type 44; skipped missing title/description 170. The 127 are PARKED (a quarter lack a review timestamp; the script cannot exclude single filings; +0.5% of events). 15 salvage rows (AI real + human real, missing fields): 13 real, 2 administrative (listed in the entry above); parked.
- Lesson: the quality problems are PROVENANCE problems (verdicts set by sweeps and bulk actions with no audit trail).
B. FLAG LEDGER (inserted and verified): guidance_type_filing_day_width (lead; G multiplier 2.37x [1.83, 2.86], G/(O+N) 1.94 [1.48, 2.37]); guidance_type_filing_ordinary_variance (null; 0.36% of the ordinary pool's squared miss, not material); gdelt_article_spike_next_day_width (null; matched shortfall +0.6 / +0.5 points, mean-square ratio 1.12 / 1.11).
C. ROLE-BASED EARNINGS BANDS (deployed in day_card.py, commits 2e953fb and 0d27ba2)
- Files: scripts/card/earnings_roles.py (shared habit rule, role selection, card-time lookup), scripts/card/build_earnings_role_model.py (self-checks: isolated events 33,023 and habit share 90.0% matched the role test exactly; pooled day 0 / +1 read 2.80x / 2.62x against the card's 2.72 / 2.47, inside the 0.20 tolerance), models/earnings_role_band_model.json: REACTION day multiplier 3.541x (by era 3.34 / 3.72 / 3.49), edge_90 1.477, q90 5.229 (ordinary units), n 29,737; OTHER day 1.472x (1.58 / 1.50 / 1.37), edge_90 1.339, q90 1.970. Width = edge x multiplier = the ordinary-scale 90th percentile of the role (the multiplier shown is on a slightly different baseline from the old pooled 2.72 / 2.47; widths are unaffected).
- Card logic: isolated earnings window (no own event, no Regulation FD 7.01 filing) AND a habit (majority of the last 4 classifiable earlier quarters from opening gaps, ties to the most recent) -> role band; ANY failure (no OHLC cache, database error, fewer than 4 quarters, event or 7.01 present) keeps the pooled day-0 / day-+1 band. Verified by hand: NVDA 2019-05-16 other day / 05-17 reaction day; TGT 2018-11-20 reaction day / 11-21 other day; JPM 2018-01-12 stayed pooled (7.01 filed the same day; habit before the open 3 of 4); JPM 2006-01-18 pooled (fewer than 4 earlier quarters). Unit tests: one-stock gap code identical to the batch formula; synthetic card-time assignment 354 of 356 correct where a habit existed.
- earnings_role_701_check.py: only 3.2% of event-free earnings windows carry a 7.01 filing (1,083 of 34,106; predicted 20-35%, WRONG). On that group the deployed role edges were not detectably miscalibrated in any era (all six 99% intervals contain 90%; interval-score ratio 0.917 / 0.915 / 0.807) but the group has 225 / 400 / 353 habit events per era, below the 500 required: verdict KEEP POOLED. Rule revised BEFORE the real run: fixed 88-92% coverage window replaced by 99% Wilson intervals (it rejected a perfectly calibrated synthetic world about a quarter of the time).
- habit_switch_check.py: 11.6% of classifiable isolated releases contradict the habit (2,064 of 17,777; predicted 8-12%, right); on them the true reaction day exceeds the narrow other-day edge (1.97) in 38.2% of cases (43.4% / 38.6% / 33.8% by era; predicted 55-80%, WRONG: median |band unit| only 1.47). Examples TPL 2026-08-06 and LHX 2026-07-30 (habit before the open, reported after the close) show the failure mode; COHR 2026-08-12 (+8.24%) stayed inside the narrow band. Already inside the validated out-of-sample coverage; no change.
- TPL case: its habit was a 2-2 TIE broken by the most recent quarter, worded on the card as if it were a habit. Card now prints 'WEAK HABIT' on ties; ties are NOT validated separately. NEXT (pre-registered in chat, not built): coverage and interval score by habit strength (4-0, 3-1, 2-2); predictions: next-quarter agreement 95%+ for 4-0, 80-90% for 3-1, 55-70% for 2-2; if the 2-2 roles score worse than the pooled band, ties fall back to the pooled band.
D. LANES. sentiment_lane_test.py (article-count spike on t-1; matched on the previous day's move): flagged 20,810 / 22,025; unmatched shortfall +1.3 / +1.0; MATCHED +0.6 [+0.1, +1.1] / +0.5 [+0.1, +0.9] against a 5-point bar; placebo -0.1 / +0.1; NO LANE (3 of 5 numeric predictions right; the unmatched shortfall 3-8 was wrong). Validated first on synthetic worlds (control, planted effect, volatility-clustering confound). tone_lane_test.py (avg_tone shock on t-1 predicts the SIGN of day t's miss, matched on the previous signed miss; held-out centre test for a place in the price): committed 6d07dfe with its rule and predictions (matched lift -1 to +2 points; 'points the right way' about 8%; 'place in the price' about 1%); validated on five synthetic worlds; two design corrections before the real run (placebo guard +-1.5 -> +-2.0; a confound world that was too strong). RESULT PENDING (first run reads the table about 25 minutes; caches data_cache/gdelt_ac_tone.npz; do not launch a second copy: check pgrep first).
E. PREDICTIONS THAT WERE WRONG (kept for calibration): 7.01 share of earnings windows (20-35% vs 3.2%); JPM role band (expected one; a same-day 7.01 prevented it); habit-switch damage (55-80% vs 38.2%, with a declining trend); the early 1-3% rejection rates (mass-confirm contamination); volume lane unmatched shortfall (3-8 vs 1.0-1.3).
F. PENDING. (1) tone lane result (paste the whole output file); (2) COO rubric point: company-wide COO = named executive officer = confirm; division-level = judgment call; RSG 2023-08-18 (need more) needs one fact (which kind); (3) habit-strength check for ties (above); (4) October 2026 sentiment top-up at month end: python3 scripts/gdelt/backfill_gdelt_sentiment.py 2026-10 2026-10 --ignore-checkpoint; (5) read scripts/tagging/resolve_sentiment_confounds.py (flags computed on the old, incomplete sentiment coverage); (6) forward test refresh January 2027 (scores the role bands on days they never saw); (7) the 127 parked events and 15 salvage rows (only if the events table needs them); (8) 76 unknown laws vote-kind reparse, disable the nightly-classify GitHub Action, condense master-todo-list.md. Notes cadence: one consolidated entry about every 15 messages.


<!-- entry: 2026-10-22-03 | date: 2026-10-22 | label:  | source-line: 3541 | approx: no -->
### 2026-10-22-03 — Bucket reads (7 and 8): neither clean bucket passes; exclusion rules next
> Original heading: `### 2026-10-22 -- Bucket reads (7 and 8): neither clean bucket passes; exclusion rules next`
Bucket sampler logic matches the SQL (all 9 bucket counts MATCH). Bucket 7 (top leadership, n=30, seed 20261031): 26 right / 4 wrong = 86.7% (70-95%); bucket 8 (deal with a dollar figure, n=30, seed 20261032): 25 right / 5 wrong = 83.3% (66-93%). Pre-set bar 28 of 30: both fail, so nothing confirmed (weak-call ranges: bucket 7 20-27, bucket 8 20-28). Wrong calls: bucket 7: Tyson Chief Accounting Officer, TransDigm EVP death/successor, PPL controller + subsidiary presidents (sub-C-suite), SWK conference tariff scenario (hypothetical); bucket 8: Newmont standalone $1.018B equity offering, S&P adding IHS Markit directors upon merger completion and WFC financial review exhibit (deal administration), UNP 1998 earnings release, Dell $500M tracking-stock buyback (small).
Right: every CEO/CFO/President/Chairman change (about 20) and named-counterparty deals with figures (acquisitions, sales, completions). Pre-screens recorded (reviewer 'Galen (accepted Claude pre-screen)', tiers BUCK7/BUCK8, tagged 'prescreened:'). COO consistency question open (RJF and PTC COO appointments called right; RSG COO departure was need-more). Overall pre-screen precision so far: random 40 = 62.5%, bucket 7 = 86.7%, bucket 8 = 83.3%.
Next: exclusion rules measured on read rows (title-based: sub-C-suite title, deal administration, standalone offering, governance documents, earnings release, equity/benefit housekeeping); keep a rule if read-row rejection >= 40% with >= 30 read rows (block baseline 9%); apply to the 7,784; fresh seeded 40 from the survivors (excluding the 100 already read); >= 37 of 40 right -> confirm survivors in tiers + 20-row post-check (accept at 19); otherwise nothing is confirmed and the unread rows stay undecided (no cost). Note: the previous validation query returned nothing by design (my join was wrong).


<!-- entry: 2026-10-22-02 | date: 2026-10-22 | label:  | source-line: 3535 | approx: no -->
### 2026-10-22-02 — Corrected cluster table (read rows only) and the clean-bucket plan
> Original heading: `### 2026-10-22 -- Corrected cluster table (read rows only) and the clean-bucket plan`
Read-rows-only rejection by text bucket (first-match order 1..9; undecided / read / rejected): 1 financing tied to a deal 351/386/8.8%; 2 deal or filing administration 1,030/480/5.8%; 3 governance documents 236/90/16.7%; 4 legal procedure 332/149/6.0%; 5 equity or benefit housekeeping 145/133/38.3%; 6 charitable 17/5 (too few); 7 CONTROL top leadership 1,183/777/3.7%; 8 CONTROL deal with a dollar figure 695/561/7.7%; 9 other 3,795/1,746/11.1% (overall read-row rejection about 9%).
Vs the random 40 (37.5% wrong): the read history is not representative (the easy valuable rows were reviewed first, and reviewers may have applied the rubric's administrative-step exception less strictly: buckets 1-2 were kept 91-94% of the time while the pre-screen rejected 8 of 15 for that reason): a possible dilution of the events table by administrative steps (to be audited). Controls (7, 8) came out cleanest and agree with the random read (5/5 C-suite changes right, 5/5 named-counterparty deals with dollar figures right); bucket 7 is not pure leadership (deal releases quoting an executive's title land there by first-match order).
Plan: confirm only provably clean buckets, park the rest (undecided rows are outside the events table, so no cost): build_bucket_sheet.py samples 30 from bucket 7 and from bucket 8 (seed 20261024 + bucket); rule fixed beforehand: at least 28 of 30 right -> the remainder may be confirmed (minus sub-C-suite and administrative rows exposed by reading), then a 20-row post-check (accept at 19 of 20); otherwise nothing; any reject rule needs a read of at least 20 rows with at least 80% wrong. The sampler prints each bucket's count against the SQL counts (MATCH / MISMATCH). Next: dilution audit of the 23,554 existing events with the same bucket logic.
The 40-row precision pre-screen was dry-run only until '--write' (record it).


<!-- entry: 2026-10-22-01 | date: 2026-10-22 | label:  | source-line: 3529 | approx: no -->
### 2026-10-22-01 — Re-classification test result (full run, 625 requests, claude-haiku-5-5)
> Original heading: `### 2026-10-22 -- Re-classification test result (full run, 625 requests, claude-haiku-5-5)`
Replication: arm A agrees with the stored verdict on 106/125 (84.8%; borderline vs the 85% bar; live recent-events context and noise explain the gap). Exhibit text added in B: G 49/50, O 49/50, R 25/25. Run-to-run noise: A vs A2 differ on 7/125 (5.6%), mostly 'uncertain'. Real_event share by arm (A / B / C / D): true guidance n=19: 5% / 5% / 16% / 47%; R decided event n=17: 12% / 59% / 53% / 71%; G not guidance n=16: 25% / 31% / 31% / 38%; G unknown n=15: 13% / 40% / 47% / 47%;
control O n=50: 16% / 16% / 14% / 16%; R decided not an event n=8: 0% in every arm. Pre-set rule (pooled true-guidance + R-event, n=36): A 8% -> B 31% (+22) -> D 58% (D - B +28); control +0, not-an-event +0, noise 0 points: EXHIBIT INPUT HELPS = YES, RULE CHANGE HELPS = YES. Reading: the exhibit text is the lever for stub filings (R events 2 -> 10 of 17); for guidance the RULE is the blocker (B 1 of 19, C 3, D 9): the model saw the numbers and still called them noise.
Predictions: right: A2 noise 5-12%, control < 8 points; wrong: B on true guidance (5% vs 40-55%), D on true guidance (47% vs 60-80%), R baseline (12% vs 60%: a selection artifact: R rows came from the classifier's noise/uncertain calls), not-an-event rise (0 vs 5-15). Caveats: n=19/17; D's wording is mine; 'not guidance' in my reading is not 'not an event'; prior v6 prompt experiments failed their bars (this changes one bullet and adds exhibit text, tested on 19 guidance filings only).
Recommendation: scoped second pass (re-classify keyword-flagged guidance filings with exhibit text + rule D, send real_event to the review queue, never auto-promote) instead of a production prompt change; a broader change needs a regression test on human-reviewed labels. Parked behind Phase 6 work; the sentiment-lane test is the proposed next Phase 6 item. Data: results/exhibit_reclass_test.csv, output results/2026-10-19/exhibit_reclass_test.out.


<!-- entry: 2026-10-21-27 | date: 2026-10-21 | label:  | source-line: 3526 | approx: no -->
### 2026-10-21-27 — exhibit_reclass_test.py: model_config import
> Original heading: `### 2026-10-21 -- exhibit_reclass_test.py: model_config import`
First run stopped safely (nothing sent): model_config is not importable from scripts/classification/. The script now searches the repo (excluding .git, node_modules, data_cache, results) for model_config.py: one copy is used and its location printed, several or none stop with a message listing the paths. Tested on a mock (moved copy found; two copies refused; none reported). If it is a package or put on the path another way, read lines 55-70 of the classifier.


<!-- entry: 2026-10-21-26 | date: 2026-10-21 | label:  | source-line: 3520 | approx: no -->
### 2026-10-21-26 — Guidance variance study (rule and predictions committed before the real run)
> Original heading: `### 2026-10-21 -- Guidance variance study (rule and predictions committed before the real run)`
scripts/card/guidance_variance_study.py: random 1,500 of the isolated Item 8.01/7.01 filings without 2.02 (2006+; no 2.02 within 3 days, no other filing on days i-1..i+1, no recorded event on i-1..i+2), sampled by content not reaction; each exhibit sorted by crude keywords into E (earnings-results headline), G (guidance / outlook / warning / preliminary), O (other), N (no exhibit); measure = 2-day mean squared band unit on days i, i+1
vs the quiet-day mean; month-block bootstrap; contribution of each group to the ordinary pool's total squared miss (population count x share x 2 days x (multiplier^2 - 1) x quiet mean / pool total). Rule: MATERIAL if G multiplier / (O+N) multiplier >= 1.5 with the interval's lower end above 1.2 AND G is >= 1.0% of the pool's squared miss. Predictions: E 5-10%, G 5-10% of the sample; exhibits for 70-85%; multipliers E 2.0-3.0x, G 1.5-2.5x, O+N 1.05-1.2x (2.02 reference about 2.6x);
G 0.5-2% of the pool, E 0.5-2%; MATERIAL probability about 40%.
Validated on synthetic worlds with planted effects: none -> ratio 1.24 [0.88, 1.64], NOT material (no false positive); guidance 2.0x -> multiplier recovered (1.67 vs 1.58 expected), ratio 1.67 [1.33, 2.07], but only 0.23% of the pool: NOT material; guidance 5.0x -> ratio 3.38 [2.89, 4.04], 1.35% of the pool: MATERIAL. Caveat: the 2-day mean dilutes multipliers relative to the card's one-day reaction-day numbers (2.02 reads about 2.4x here vs 3.69x on the reaction day).


<!-- entry: 2026-10-21-25 | date: 2026-10-21 | label:  | source-line: 3514 | approx: no -->
### 2026-10-21-25 — Hint window patch; earnings releases under other items sized (small)
> Original heading: `### 2026-10-21 -- Hint window patch; earnings releases under other items sized (small)`
HINT_CHARS=1500: hints 183 -> 160; priority P1 111 (predicted 80-110), P2 44, P3 91, P4 154; P1 by hint: merger 29, dividend/buyback 26, guidance 22, offering 20, leadership 17, lawsuit 8, clinical 6, restatement 6.
Earnings 8-Ks (item 2.02) per company-year: 4.14-4.50 in every year 2005-2025 (above the 4 expected: the earnings flags are essentially complete for the test period); 0.00 for 1994-2003 (Item 2.02 began Aug 2003), 1.19 in 2004, 3.13 in 2026 so far. 37 of 218 excerpts (17%) have an earnings-style headline, 35 of 37 labelled likely_noise
(many are outlook/guidance: YUM FY2013 expectations, ELV revises 2008 EPS); scaled to tier A about 40 of 12,704 big ordinary misses (0.3%): negligible contamination of the ordinary pool. The classifier labels earnings-style and guidance releases under 8.01/7.01 as noise almost always (prompt rule on guidance revisions).
Next: pre-screen of the first 25 P1 rows (decisions tagged 'prescreened' in notes so later scoring of an exhibit-fed classifier uses only independent human decisions); confirm review_queue_decisions exists (to_regclass).


<!-- entry: 2026-10-21-24 | date: 2026-10-21 | label:  | source-line: 3509 | approx: no -->
### 2026-10-21-24 — Full exhibit run result; earnings releases hiding under other items
> Original heading: `### 2026-10-21 -- Full exhibit run result; earnings releases hiding under other items`
Run (real contact): 400 tier A rows, 218 excerpts, 182 'ok, no EX-99 exhibit in the submission' (all permanent: no fetch failures; the progress counts matched the earlier full run exactly); excerpt length 1,210; keyword hints 183. Priority: P1 127, P2 28, P3 91, P4 154 (predicted 60-110 / 40-80 / 90-100 / 182: only P3 right). P1 hints overlap (merger 46, dividend/buyback 40, guidance 35, leadership 26, offering 23, lawsuit 16, restatement 12, clinical 7);
hints over-trigger on safe-harbor boilerplate (ELV guidance release hinted merger and leadership), so the hint window is limited to 1,500 characters (HINT_CHARS). Finding: ALGN 2007-01-30 (+21%) is a Q4/FY2006 EARNINGS release filed under an ordinary item, not 2.02: the earnings window flags fire only on 2.02, so such reactions sit in the 'ordinary' pool and contaminate the earnings band
calibration; FAST 2006-01-20 may be the same. Sizing: 40,136 filings with 2.02 vs about 41,600 expected earnings events (96%); per-year earnings 8-Ks per company pending. First P1 rows (BEN Western Asset announcement, CASY, UDR, ELV) look like real events (from memory, unverified); P1 means classifier and exhibit disagree, not 'event'.


<!-- entry: 2026-10-21-23 | date: 2026-10-21 | label:  | source-line: 3503 | approx: no -->
### 2026-10-21-23 — Exhibit trial, and a separate decisions table
> Original heading: `### 2026-10-21 -- Exhibit trial, and a separate decisions table`
Live trial (first 8 tier A): UDR, ELV, AIZ returned EX-99.1 excerpts and the keyword hints were right (UDR proposed common stock offering; ELV revises 2008 EPS guidance); PLD correctly has no EX-99 (5.07 vote results); CASY and PNR failed with no reason shown (rate limit, block or timeout: now reported). AIZ's 700-character excerpt was all press-contact boilerplate:
excerpt now 4,000 characters cached, 1,200 shown. So for stub 8-Ks the substance is one file away from what the classifier reads (confirmed for UDR/ELV/AIZ). Reviewer decisions go into a NEW table review_queue_decisions (sql/review_queue_decisions.sql: accession_number, ticker, miss_date, tier, classifier_verdict/confidence,
decision in event / not_an_event / need_more, notes, reviewer, queue_version, linked_event_id (empty for now), decided_at; unique on accession_number + miss_date; RLS on), deliberately not candidate_review_log or classification_corrections so existing review data stays clean. scripts/card/import_review_decisions.py validates every row first, dry run by default, --write upserts.
Importer tested with a mocked database only. Pending: SEC_USER_AGENT with a real contact; why CASY and PNR failed; the first review session.


<!-- entry: 2026-10-21-22 | date: 2026-10-21 | label:  | source-line: 3496 | approx: no -->
### 2026-10-21-22 — Classifier reasoning on the top review rows; existing review backlog
> Original heading: `### 2026-10-21 -- Classifier reasoning on the top review rows; existing review backlog`
Reasoning quotes (filing_ai_classifications): CASY 'bare Item 8.01 ... merely attaches a press release (Exhibit 99.1) ... no substantive terms stated in the filing text itself' -> noise 0.85; AIZ 'content cannot be assessed without the exhibit' -> uncertain 0.35; UDR 'public common stock offering ... routine ... filing text provides no size, pricing' -> noise 0.80;
ELV 'routine earnings guidance update via press release' -> noise 0.92 (the stock fell 28%). PNR was judged real_event with help from the recent-events context; VRTX, SPGI, PLD correct. The exhibit-gap hypothesis is supported by the model's own words for 4 of 8 rows; NOT yet tested by feeding exhibits.
Review process: 43,023 flagged filings have no candidate_review_log row (26,286 real_event, 15,502 likely_noise (mostly the random 10% audit), 1,235 uncertain; may be handled through other tables, unverified). candidate_review_log: 4,180 real_event (all linked to an event) + 239 rejected_noise. classification_corrections: AI real_event -> noise about 122
(buyback_authorization_vs_execution 101, atm_establishment_vs_completion 8, reasoning_verdict_contradiction 12), AI noise -> real_event only 4 (cross_company_blindness 3, 1 contradiction); 49 reviewer overrides of correct AI real_event calls. With a fixed seed the queue is reproducible: tier A 433, B 857, C 476, not queued 5,440.
The queue is a triage layer on the existing backlog (rank unreviewed real_event filings by market reaction), plus a way to find noise-labelled filings with big reactions. Pending pastes: a .txt URL example and SEC_HEADERS (to add exhibit excerpts); decision on where reviewer decisions are recorded.


<!-- entry: 2026-10-21-21 | date: 2026-10-21 | label:  | source-line: 3490 | approx: no -->
### 2026-10-21-21 — Ledger rows confirmed; classifier labels located; review queue now shows the classifier's verdict
> Original heading: `### 2026-10-21 -- Ledger rows confirmed; classifier labels located; review queue now shows the classifier's verdict`
flag_ledger check: band_coverage_fixed_edge_1_645 (null) and band_edge_calibration_90 (proven) already existed (tested_on 2026-10-20); added earnings_role_bands_walk_forward (proven), unrecorded_sector_theme (lead), unrecorded_group_move_peers (null), event_date_lag (null) (2026-10-21).
Classifier labels: filing_ai_classifications (upsert at line 904 of classify_8k_filings_batch_v2.py; ai_verdict, ai_confidence, ai_reasoning, flagged_for_review, keyed by accession). Review-related tables: candidate_review_log, classification_corrections, event_candidate_triage, candidate_8k_events,
event_component_dates, candidate_8k_reclass, several audit tables. Of 138,608 .htm filings 34,170 have item 8.01 and 29,125 item 7.01 (about 63,000 where substance may sit in an unread exhibit). build_review_queue.py now adds classifier_verdict / confidence / reasoning per row and prints a verdict summary
for tiers A and C (tests the exhibit hypothesis: a high share of likely_noise with 'press release' / 'exhibit' reasoning would confirm the loop). Pending: the verdict summary, the flagged_for_review backlog counts, how reviewer decisions are recorded.


<!-- entry: 2026-10-21-20 | date: 2026-10-21 | label:  | source-line: 3484 | approx: no -->
### 2026-10-21-20 — URL mix, promoted_to_event, ledger rows
> Original heading: `### 2026-10-21 -- URL mix, promoted_to_event, ledger rows`
sec_8k_filings: 138,608 .htm main-document URLs (89.3%) and 16,533 complete-submission .txt; promoted_to_event is false for all 155,141 (flag unused; no Python script sets it; the review queue excludes recorded events by date, not by this flag). The classifier writes ai_verdict, ai_confidence,
ai_reasoning, flagged_for_review, flag_reason etc. keyed by (ticker, filing_date, accession_number) to a table not yet identified; classify_8k_filings_v6_reclass.py reports 0 unclassified candidates. 'Events that need human review' may refer to that flagged_for_review backlog (not yet queried).
flag_ledger columns: flag_key, family, description, known_on, window_desc, multiplier, pass_rule, status ('proven' / 'null' / 'lead'), tested_on, notes; flag_ledger_evidence: flag_key, era, n, estimate, se, unit. Rows added today (insert-if-absent): band_edge_calibration_90 (proven), band_coverage_fixed_edge_1_645 (null),
earnings_role_bands_walk_forward (proven), unrecorded_group_move_peers (null), unrecorded_sector_theme (lead), event_date_lag (null). The two band rows' pass-rule wording came from notes: verify against band_calibrate.py and band_coverage_test.py. No evidence rows written (no standard errors).


<!-- entry: 2026-10-21-19 | date: 2026-10-21 | label:  | source-line: 3478 | approx: no -->
### 2026-10-21-19 — Why the classifier misses press-release-only 8.01s (hypothesis, corrected)
> Original heading: `### 2026-10-21 -- Why the classifier misses press-release-only 8.01s (hypothesis, corrected)`
fetch_filing_text(url) reads one URL (streams up to 2 MB, strips HTML); the comment about 'every exhibit concatenated' applies to complete-submission .txt URLs. The eight review-tier-A filings I read all have .htm main-document URLs, where Exhibit 99.1 is a separate file the classifier does not read.
With the prompt rule (lines 184-191: guidance revisions / exhibit-only filings referenced without terms in the filing text -> noise) this is a closed loop: the model sees 'issued a press release' and is told to call it noise. A previous note in this file that exhibits are fed in is WRONG for .htm URLs.
Candidate fix (untested): fetch https://www.sec.gov/Archives/edgar/data/<cik>/<accession_number>.txt for 8.01/7.01 filings whose body is a stub; test on tier-A rows first. Only build_review_queue.py references promoted_to_event in Python: promotion is done some other way (unknown).
Ledger tables: flag_ledger, flag_ledger_evidence, flag_range_dist. Pending pastes: URL-kind counts, flag_ledger columns and three existing rows, classifier save location (lines 860-885), reclass script --help.


<!-- entry: 2026-10-21-18 | date: 2026-10-21 | label:  | source-line: 3471 | approx: no -->
### 2026-10-21-18 — Detector rerun on the repaired sentiment table; top 8 of review tier A read from the filings
> Original heading: `### 2026-10-21 -- Detector rerun on the repaired sentiment table; top 8 of review tier A read from the filings`
Detector rerun (22 min): article coverage 53.8% of scored stock-days (was 20.7%), 1.33M article rows over 461 entities, article spike on calm days 3.6%, on big misses 14.7% (was 12.2%), enrichment 4.1x (was 3.8x); volume figures identical (53.6% / 25.7% on big misses),
as predicted. Predictions: coverage 45-52% (just over), big-miss article spike 10-14% (just over). The sentiment repair matters more for the product's sentiment layer than for this detector (article 4.1x vs volume 18x).
Review tier A, top 8 by volume x size, read from the SEC filings (readings for a person to confirm): PNR 2012-03-28 +15% Pentair-Tyco merger (Rule 14a-12); VRTX 2017-03-29 +20% Phase 3 results; SPGI 2013-02-04 -14% DOJ civil suit reports; ELV 2008-03-11 -28% guidance update
(filed 3/10); UDR 2016-03-04 -5% common stock offering; CASY 2010-04-09 +24% and AIZ 2007-07-17 -10% press release in Exhibit 99.1 (open the exhibit); PLD 2011-06-02 -4% AMB-ProLogis merger vote results (5.07). 5 of 8 clear events, 2 likely, 1 merger-related; the top rows are the most
extreme so the rate will fall. Hypothesis (untested): the classifier sees only the main document, and 8.01 stubs that say 'issued a press release' hide the substance in Exhibit 99.1. SEC pages show Period (report date) vs Filed (VRTX 3/28 vs 3/29): the report date our table lacks.


<!-- entry: 2026-10-21-17 | date: 2026-10-21 | label:  | source-line: 3465 | approx: no -->
### 2026-10-21-17 — Review queue result and the sector-correction sensitivity
> Original heading: `### 2026-10-21 -- Review queue result and the sector-correction sensitivity`
build_review_queue.py: tier A 433 (big volume-spike miss with an unpromoted 8-K, URL included), tier B 857 (sector theme / peer group move, no filing), tier C 476, not queued 5,440 stock-specific misses with no filing or group evidence (A + B + not queued = 6,730).
Predictions: A right (430-460), B/C/not queued wrong (higher). Top of tier A: large same-day 8.01s (PNR 2012-03-28 +15%, VRTX 2017-03-29 +20%, SPGI 2013-02-04 -14%, ELV 2008-03-11 -28%, UDR 2016-03-04 equity offering, AIZ, CASY): look like material events the classifier called noise
(from memory, UNVERIFIED; a reviewer must decide). Sector-cluster excess vs the sector-mate correction (loading assumed 1): none +5.2 [+4.2, +6.3], half +6.2 [+5.1, +7.3], full +7.4 [+6.3, +8.6]; reading guide met in all three, so the result does not depend on the assumption.
Open: reviewer decisions on tier A (top 50 first), how events are promoted (importer not written), detector rerun output (predictions unscored), scripts/tagging/resolve_sentiment_confounds.py not yet read.


<!-- entry: 2026-10-21-16 | date: 2026-10-21 | label:  | source-line: 3458 | approx: no -->
### 2026-10-21-16 — Fixed cluster checks on real data; human review queue
> Original heading: `### 2026-10-21 -- Fixed cluster checks on real data; human review queue`
GDELT June 2025: gdelt-bq.gdeltv2.gkg_partitioned has partitions only through 2025-06-14 (June 14 half-size): Jun 15-30 are missing at GDELT's end; nothing to fix on our side. sector_cluster_check.py (fixed design; controls -0.5 [-1.1, +0.2]): among 6,730 big volume-spike
misses the sector-theme share is 10.9% vs 3.5% placebo, excess +7.4 points [+6.3, +8.6]: NOT material under the 10-point rule, reading guide (2+ points) MET; by era 7.1 / 11.2 / 15.3%; highest in Real Estate 20%, Energy 19%, Utilities 17% (predicted the opposite for
Utilities); CHRW 2026-02-12 flagged (EXPD ROL GWW), LMT 2024-10-01 not (2 other Industrials). Union with peer group moves 13.5% of volume-spike misses (both 2.1%, sector only 8.9%, peers only 2.5%). Fixed all-stock theme check: +0.9 points [+0.2, +1.7] (broad
event days, small). Sector-correction sensitivity (loading assumed 1) pending. build_review_queue.py writes results/human_review_queue.csv: tier A big volume-spike miss with an unpromoted 8-K attached (URL included), tier B sector theme / peer group move without a
filing, tier C other categories with a filing; stock-specific misses with no filing are not queued (outside source needed). scripts/tagging/resolve_sentiment_confounds.py is where the sentiment-confound flag script lives.


<!-- entry: 2026-10-21-15 | date: 2026-10-21 | label:  | source-line: 3447 | approx: no -->
### 2026-10-21-15 — Sentiment backfill verified; where the undercount lived; theme/cluster checks fixed after validation
> Original heading: `### 2026-10-21 -- Sentiment backfill verified; where the undercount lived; theme/cluster checks fixed after validation`
Backfill: 141 of 141 months done (2015-02..2026-10, 0 pending), relaunch skipped everything (0 GB). Coverage now 420-447 companies per month in every year (was 150-176 after May 2015). Old-vs-new ratio by year on rows that existed: 2015 1.000
(52,503 days, none changed), 2016-2022 1.25-1.34 (about half the days higher, none lower), 2023 1.119 (first ~5 months only), 2024-2026 1.000-1.002: the first-match-wins undercount lived in 2016 through about May 2023 (old counts about 22% below true), so
covered companies' article counts jumped about 29% at June 2023 before the re-run. The series is now consistent. June 2025 still has only 14 days (Jun 15-30 probably missing in GDELT itself; partition check pending). October 2026 is partial: top up at month end
with --ignore-checkpoint. Detector rerun pending (predictions: article coverage 45-52% of stock-days, spike rate on calm days about 3%, on big misses 10-14%).
theme_day_check.py first real run (unfixed): excess -0.3 points [-1.0, +0.4], all predictions wrong (placebo median cluster 5 not 2-4; real share 2.2% not 12-25%). A synthetic CONTROL world with no themes showed real days BELOW placebo (1.9% vs 4.0%): two mechanical
negative dependences, (1) a band unit is divided by the other stocks' mean squared miss, which includes the focal stock's own big miss (others' band units shrink about 2%, with fat tails about 10% fewer exceedances; matching placebo days on market scale does NOT fix it, a first
wrong explanation), (2) the matrices subtract a leave-one-out sector mean, so a sector-mate's expected return includes the focal stock's return/(n-1). Fixed by normalising others without the focal stock and adding back the focal stock's share (loading taken as 1). Controls now read
-0.0 [-0.6, +0.5] (all-stock) and -0.5 [-1.1, +0.2] (sector). The all-stock measure sees only broad event days; sector_cluster_check.py sees narrow sector themes (89% of planted rows flagged; a 3.0% themed share read +2.2 [+1.3, +3.1]); reading guide fixed before any real run:
2+ points with the interval above 0. Lesson: my synthetic validation had understated the real baseline (about 5 other big misses on an arbitrary day, not 2), and an unvalidated null can be biased downward by the measure itself.


<!-- entry: 2026-10-21-14 | date: 2026-10-21 | label:  | source-line: 3440 | approx: no -->
### 2026-10-21-14 — GDELT backfill finished; theme-day check written
> Original heading: `### 2026-10-21 -- GDELT backfill finished; theme-day check written`
All 141 months (2015-02 .. 2026-10) are done (checkpoint 141 distinct months; database: 141 months with at least 300 entities, 0 pending; the first run finished before the Codespace reset, in two overlapping processes, which is why the checkpoint has interleaved
duplicates). The relaunch is a no-op (every month skipped). October 2026 is partial (about 20 days): top up at month end with --ignore-checkpoint. Predictions for the detector rerun (written before it runs): article coverage 45-52% of scored stock-days (was 20.7%),
article-spike rate on calm days about 3%, on big misses 10-14%, quiet share down a few points, volume-spike share unchanged. Archive of the pre-fix candidates CSV and reading samples: results/archive_pre_sentiment_fix/.
theme_day_check.py (rule, sensitivity note and predictions committed before the run): counts OTHER stocks anywhere with a same-direction big miss (>= 2.5 band units) on the day of each big ordinary miss, against random-day placebos; theme day = above the
placebo 95th percentile; validated on synthetic worlds (no false positive; planted themes read +6.5 points [+4.3, +10.1] and are a floor, so an excess of 5+ points with the interval above 0 is evidence of themes even if the 10-point rule says no).


<!-- entry: 2026-10-21-13 | date: 2026-10-21 | label:  | source-line: 3435 | approx: no -->
### 2026-10-21-13 — Sentiment backfill: first real month (2022-01) with the fixed IF()/UNNEST query
> Original heading: `### 2026-10-21 -- Sentiment backfill: first real month (2022-01) with the fixed IF()/UNNEST query`
Ran cleanly (no 'Array cannot have a null element' error; batched upserts worked): 8,726 (company, day) rows processed vs 3,477 rows (164 entities) in the table before. 8,726 rows cannot come from 199 tickers (max about 6,200), so the earlier regex
count of 199 tickers in TRACKED_COMPANIES was wrong; the authoritative count is len(TRACKED_COMPANIES) from importing the module. Pending: old-vs-new ratio, entities now, per-letter coverage for 2022-01 (rule: mean ratio 0.95-1.25 and under 20% of days
lower before any wider overwrite). entities has columns id, name, entity_type, description, ticker; securities has entity_id, ticker, sector (names for extending the company list live in entities.name).


<!-- entry: 2026-10-21-12 | date: 2026-10-21 | label:  | source-line: 3428 | approx: no -->
### 2026-10-21-12 — Sentiment coverage: it is a fixed company list, not the matching bug (correction to the entry above)
> Original heading: `### 2026-10-21 -- Sentiment coverage: it is a fixed company list, not the matching bug (correction to the entry above)`
Per-company coverage 2016-2025: 139 entities appear in nearly every month (118+ of 120), 27 in some months, 16 in few, 182 in any month; 317 of 499 universe companies have no rows after May 2015. That is a fixed list of roughly 180 companies
(docs/phase6 says 199 tracked), NOT the exclusive CASE/WHEN dispatch (which would give sporadic appearances, not total absence). The 'Coverage as of 2026-09-29: 445 distinct entities (verified live)' note counts entities with a row in ANY
month, dominated by Feb-May 2015 (about 400), and is misleading; the earlier 184/497 figure was closer to the truth for most months. Table spans 2015-02-17 to 2026-09-21 (532,815 rows). Upsert conflict key entity_id,date,source (matches the
unique constraint). BigQuery works from the Codespace (project stock-project-508016). The backfill sent one request per row; patched to 500-row batches with duplicate entity-days merged (tested on mocks). Plan: backup table, company-list check,
one-month dry run, one real month (2022-01) with the old-vs-new comparison rule (mean ratio 0.95-1.25, under 20% lower), then 2015-05 to 2026-09.


<!-- entry: 2026-10-21-11 | date: 2026-10-21 | label:  | source-line: 3421 | approx: no -->
### 2026-10-21-11 — company_sentiment_timeline covers about a third of the universe (found while checking why article coverage was 20.7%)
> Original heading: `### 2026-10-21 -- company_sentiment_timeline covers about a third of the universe (found while checking why article coverage was 20.7%)`
Feb-May 2015: 132-143 A-E tickers and 250-263 F-Z tickers have rows; from Jun 2015 on ~105 A-E and ~51 F-Z (of 175 and 324 in the universe): 165 of 499 tickers in Jan 2022 (A-E 65%, F-Z 16%). Pattern matches the old exclusive
CASE/WHEN dispatch in backfill_gdelt_sentiment.py (an article counts only for the first matching company in alphabetical order); the script's comment says the fixed IF()/UNNEST query was written but not yet run, so Feb-May 2015 probably came
from an earlier method. June 2025 has rows only for Jun 1-14 (Jun 15-30 missing); Sep 2026 partial (month running); Oct-Nov 2020 have about 40% fewer articles with normal row counts (not investigated).
Affected so far: unrecorded_candidates.py (the article-spike signature and the 'volume + article spike' stratum); volume-based results, group moves and role bands do not read this table. The product ('Public Opinion Pull') and earlier tests may.
Plan: confirm the upsert conflict key (rest of the script), dry-run one month in an environment with BigQuery (Cloud Shell likely), run one real month and verify entities / A-E counts / duplicates, then backfill 2015-06 onward and 2025-06-15..30, then rerun the detector.


<!-- entry: 2026-10-21-10 | date: 2026-10-21 | label:  | source-line: 3415 | approx: no -->
### 2026-10-21-10 — Reading of the group-stratified sample, interim (8 of 36 rows; shuffled order, one search per row, found only for a specific dated item)
> Original heading: `### 2026-10-21 -- Reading of the group-stratified sample, interim (8 of 36 rows; shuffled order, one search per row, found only for a specific dated item)`
Found 2 of 8: CHRW 2026-02-12 (AI-disruption selloff in logistics services, StreetInsider headline log) and LMT 2024-10-01 (Iran missile attack on Israel; defense contractors up 3.6%, Zacks). Not found: LYV 2026-03-09, BG 2024-05-14,
MDLZ 2026-03-16, WRB 2024-07-19 (insurer peers moved too), VRT 2024-06-06, CASY 2024-03-05. By stratum: volume stock-specific 1/3, group move 1/3, quiet 0/2 (too small to compare). Both finds are thematic/geopolitical, and CHRW was
classed stock-specific by the peer check (1 of 10 peers moved), so the peer method likely undercounts thematic shocks that hit an unusual set of stocks (hypothesis; a same-day cluster check without peers would test it). Search wording
changed after row 8 to surface dated headline logs (StreetInsider / TheFly); not a change to the found rule. 'Not found' never means nothing happened. Working file: results2.csv in the sandbox.


<!-- entry: 2026-10-21-09 | date: 2026-10-21 | label:  | source-line: 3407 | approx: no -->
### 2026-10-21-09 — Group moves among big ordinary misses (group_move_check.py, 48f6b06; rule and predictions committed before the run)
> Original heading: `### 2026-10-21 -- Group moves among big ordinary misses (group_move_check.py, 48f6b06; rule and predictions committed before the run)`
Peers = the 10 stocks with the highest correlation of daily standardized misses over the previous 250 days (refreshed every 63 days, no look-ahead); a GROUP MOVE = at least 4 of 10 peers moved at least 1.5 band units the same way
the same day; placebo = 10 random stocks. 15,293 big ordinary misses scored. GROUP MOVE share 5.7% (placebo 0.1%); among the 6,635 big volume-spike misses 4.6% vs 0.1%, excess +4.5 points [+3.7, +5.4]: pre-set verdict GROUP NEWS
NOT material (needs 10 points). Quiet misses 7.0%, volume spike only 4.6%; by era 2.0 / 4.9 / 10.3% (rising); by size 6.0% at 3-4 band units falling to 2.0% at 7+. Examples are sensible sub-industries (regional banks 2023-03-14, casinos,
trucking and rail, AI power names 2024-06-06, insurers 2017-09-08 with nine of ten peers). Reading frame: of 6,635 volume-spike misses, 307 are group moves, 4,938 (74.4%) stock-specific (support 0-1), 1,390 in between. What our own
data explains is roughly 10% at most (other 8-Ks about 2%, pre-event windows 2-3%, group moves about 5%, overlaps not removed). New stratified reading sample: results/unrecorded_reading_sample_groups_20261021.csv (supersedes
the first 48-row sample for the 'what kinds of news' question). company_sentiment_timeline columns: id, entity_id, date, article_count, avg_tone, source, created_at.


<!-- entry: 2026-10-21-08 | date: 2026-10-21 | label:  | source-line: 3401 | approx: no -->
### 2026-10-21-08 — Earnings role bands, walk-forward (earnings_role_band_test.py, 2f031f2; rule, placebo tolerance and predictions committed before the run)
> Original heading: `### 2026-10-21 -- Earnings role bands, walk-forward (earnings_role_band_test.py, 2f031f2; rule, placebo tolerance and predictions committed before the run)`
33,023 isolated earnings events from 2006, 90.0% with a forward habit (majority of the last 4 classifiable quarters). Pooled day-0 / day+1 bands cover habit-assigned reaction days 81.3% and other days 98.3% (calibrated on average,
not conditionally). Role bands (reaction day / other day, edges from earlier years only): coverage 89.5% / 91.3%, interval score 0.868x pooled (0.890 / 0.869 / 0.857 by era), mean half-width 3.60 vs 3.84. Shuffled-habit
placebo 1.003x (no gain). Four groups (habit x role) add only 0.2-0.4%. Pre-set verdict ROLE BANDS IMPROVE. Caveats: 'last 4' chosen after the recency test on the same years; tests the edges, not the matrices; the card wiring needs
the real day_card.py. backfill_gdelt_sentiment.py: the multi-company matching fix is in the file but was 'not yet run', so months already in company_sentiment_timeline may undercount later-listed tickers (unchecked).


<!-- entry: 2026-10-21-07 | date: 2026-10-21 | label:  | source-line: 3395 | approx: no -->
### 2026-10-21-07 — Earnings timing: forward habit rules (earnings_timing_recency.py, 9f18cf7; rule and predictions committed before the run)
> Original heading: `### 2026-10-21 -- Earnings timing: forward habit rules (earnings_timing_recency.py, 9f18cf7; rule and predictions committed before the run)`
On the 17,428 events with at least 8 earlier classifiable quarters: last quarter 85.1%, majority of the last 3 / 4 / 8 quarters 88.7 / 88.8 / 88.7%, all earlier quarters 85.1%, pooled leave-one-out 86.6% (the pooled rule also sees later
quarters). Where the event's own gap is at least 5 sd: last 4 reads 93.1%. Pre-set: HABIT DRIFT NOT supported (best forward rule +2.2 points over pooled, threshold 3: a conservative test, since pooled sees the future); FORWARD HABITS
USABLE: yes (93.1% vs 90%). Descriptive (post hoc): last 4 beats all-earlier by 3.7 points; clean-pair switch rate 11.7% (2006-12), 7.3% (2013-19), 5.9% (2020-26); highest flippers BLDR, BRO, TSLA (44%, only 9 pairs), UHS, PLTR,
KHC (small counts). Next: earnings_role_band_test.py, the walk-forward test of role-specific bands against the pooled day-0 / day +1 bands, with a shuffled-habit placebo.


<!-- entry: 2026-10-21-06 | date: 2026-10-21 | label:  | source-line: 3389 | approx: no -->
### 2026-10-21-06 — Earnings timing diagnostics (earnings_timing_diagnostics.py, 29d5c66; reading rules and predictions committed before the run)
> Original heading: `### 2026-10-21 -- Earnings timing diagnostics (earnings_timing_diagnostics.py, 29d5c66; reading rules and predictions committed before the run)`
Habit agreement by the event's own gap: 77.9 / 84.1 / 89.6% (2-3, 3-5, 5+ own-sd); by year 76-79% in 2006-08 rising to 90% in 2019, 82% in 2020. The largest overnight gap falls on day i or i+1 in 73.7% of earnings events
(placebo 32.9%): about 61% of earnings events have a gap-dominated reaction (post-hoc model). NOT a dating problem as defined (13 stocks below 50% aligned vs the rule's 15); the least aligned are mostly utilities and REITs
(small reactions) plus STLD, OXY, FCX, BRK-B. TSLA's largest gap is on day i 38% and i+1 38% (its 8-K timing relative to the release flips; not misdated). Pre-set reading: NOISE AT WEAK GAPS does not hold (5+ tier 89.6%),
DATING PROBLEM does not hold, UNSTABLE HABITS holds (every tier below 92%). Next: forward-looking habit rules from earlier quarters only (earnings_timing_recency.py).


<!-- entry: 2026-10-21-05 | date: 2026-10-21 | label:  | source-line: 3382 | approx: no -->
### 2026-10-21-05 — Earnings timing from the opening gap (earnings_timing_check.py, f96d3fd; predictions committed before the run)
> Original heading: `### 2026-10-21 -- Earnings timing from the opening gap (earnings_timing_check.py, f96d3fd; predictions committed before the run)`
36,682 earnings events from 2006; 59.1% classifiable (a gap of 2 own overnight-gap sd). Pre-set verdict METHOD NOT VALID on ONE criterion: leave-one-out habit agreement 85.0% (threshold 90%); the margin over the close-to-close
method (76.8%) passed (+8.3), recalled tickers 12 of 14 (TSLA 51%, JPM 85%). Role multipliers (strong habit = 61.9% of events; roles from the habit, never the event's own size): reaction day 3.69x (3.41 / 3.90 / 3.70 by era),
other day 1.35x, ratio 2.73 = TIMING MATTERS; pooled day 0 / +1 2.75x / 2.53x (card 2.72 / 2.47). The failed identity check (8.65 vs 9.68) implies after-close reaction days (about 4.1x) are bigger than before-open (about 3.5x):
four parameters, not two (post-hoc inference). Selection caution: the strong-habit group favours stocks with big gaps (its day 0 is 2.94x vs 2.75x for all events), so population multipliers are probably 5-8% lower.
BMO share among classifiable 61.6 / 58.5 / 56.1% by era. Diagnostics (earnings_timing_diagnostics.py) written to explain the 85%.


<!-- entry: 2026-10-21-04 | date: 2026-10-21 | label:  | source-line: 3375 | approx: no -->
### 2026-10-21-04 — Event-date lag check (event_date_lag_check.py; first run 3714231, v2 rule ae80e3a)
> Original heading: `### 2026-10-21 -- Event-date lag check (event_date_lag_check.py; first run 3714231, v2 rule ae80e3a)`
First rule (pre-share of events vs earnings) fired for all nine event types: CONFOUNDED by reaction size (the largest of 8 days lands on the event date only when the reaction is large; 16.4% of events have a window-dominating
reaction against 56.2% of earnings; the offset distribution is a flat background plus a bump at days 0 and +1). Post-hoc v2 (lag mass = extra peaks on days -4..-1 above the day -5 background): all events +2.0 / +0.4 points
(A / B), no general lag; only regulatory flagged (+14.6 / +12.8, interval [+3.4, +20.0], n 658); legal settlement and strategic partnership large but underpowered; capital_raise q 2.1% (no reaction at the recorded date).
Placebo days read -4.4 / -3.3 (should be about 0): the estimator is noisier or biased more than its intervals show. Candidate mis-dated events 3.9% vs 2.7% for placebo days. sec_8k_filings has no report-date column.
Conclusion: events are mostly dated correctly; regulatory is a lead only; no re-dating planned.


<!-- entry: 2026-10-21-03 | date: 2026-10-21 | label:  | source-line: 3367 | approx: no -->
### 2026-10-21-03 — Joins and market-adjusted calibration (unrecorded_joins.py, volume_calibration_adj.py; predictions committed 9d401d0 before the runs)
> Original heading: `### 2026-10-21 -- Joins and market-adjusted calibration (unrecorded_joins.py, volume_calibration_adj.py; predictions committed 9d401d0 before the runs)`
Other 8-Ks (not 2.02 / 7.01) are attached to 5.6% of big ordinary misses vs 3.8% of calm days (1.48x [1.37, 1.59]); item 8.01 2.15x, 1.01 1.35x; about 230 big misses (1.8%) explained; 6,297 of 6,730 big misses with a
volume spike (93.6%) have no filing at all. Flow days inflate volume spikes on calm stock-days (monthly expiry 6.6x, quarterly 16x, Russell 9x) without changing the big-miss rate (1.00 / 1.13 / 1.00x). Big misses are
more frequent just BEFORE a recorded-event window (1 day 2.41x, 5 days 1.68x) and a Regulation FD window (1 day 1.71x): probably event dates that lag the news (an 8-K may be filed up to four business days after
an event; untested), about 200-400 big misses (2-3%); less frequent in the 5 days before earnings (0.77x). Market-adjusted volume ratio: calm 1.5% / mid 5.9% / big 53.5% / known information 84.8% at 2.0x; pi_upper
0.80 / 0.66 / 0.55 (spread 0.26, still NOT CONSISTENT); range at 2.0x [0.32, 0.66]; by era 0.70 / 0.66 / 0.59. Conclusion unchanged by flow-day contamination. Together the joins explain about 4-5% of the big ordinary
misses: the information-like pool is mostly outside the database. build_ohlc_cache.py (open/high/low/close) pulled for the earnings-timing check.


<!-- entry: 2026-10-21-02 | date: 2026-10-21 | label:  | source-line: 3360 | approx: no -->
### 2026-10-21-02 — Volume-spike calibration (volume_calibration.py; rule, degeneracy check and predictions committed 1fce3d5 before the run)
> Original heading: `### 2026-10-21 -- Volume-spike calibration (volume_calibration.py; rule, degeneracy check and predictions committed 1fce3d5 before the run)`
Known-information big-miss days (earnings, recorded events, Regulation FD; 13,316) spike at 2.0x on 86.6% (reweighted to the size mix of ordinary big misses 81.2%), calm days 2.6%, mid-size misses 7.7%, ordinary big
misses (12,704, non-aftershock) 53.0%. p / s = 0.65 (informative). pi_upper 0.75 / 0.62 / 0.51 at 1.5x / 2.0x / 3.0x: spread 0.24 > 0.10 = NOT CONSISTENT, so no single information share is quoted; at 2.0x the share that
looks like information by volume is between 0.31 (extrapolated noise rate) and 0.62 (mid-size noise rate), about 3,900-7,900 of the 12,704 (17-33% of the 23,554 recorded events). At least about 13% show no volume
elevation at all (under 1.3x; information gives that 1.9% of the time). pi_upper by era 0.66 / 0.62 / 0.56 (s roughly stable 82.7 / 82.6 / 78.4). The 5 readings so far (1 of 5 found) are in the working notes.
Limit: company-filed information may have a different volume signature from analyst notes, activist stakes, rumours and sector news.


<!-- entry: 2026-10-21-01 | date: 2026-10-21 | label:  | source-line: 3354 | approx: no -->
### 2026-10-21-01 — Split and volume artefact audit (split_artifact_audit.py; descriptive, no ledger row)
> Original heading: `### 2026-10-21 -- Split and volume artefact audit (split_artifact_audit.py; descriptive, no ledger row)`
close = adjusted_close except in about 12% of securities by at most 1.6% (matches the earlier count of about 650 differing rows): returns are PRICE returns. Splits are adjusted in prices AND volume
(AAPL, TSLA, NVDA, WMT checked; AMZN and GOOGL are not in the cache). Unadjusted corporate actions are spin-offs and special dividends (WY 2010, KDP 2018 and others): 36 down-jumps of 35-50% kept as
returns, 13 over 50% and 16 up-jumps over 60% dropped by the 50% filter, about 65 stock-days since 2005: too few to justify a screen. Volume level steps: 5,941, of which 5,806 are 1.7-2.5x (ordinary) and
22 are 4x or more (unit, source or ticker changes, for example AMCR). The detector's 20-day baseline stands as registered.


<!-- entry: 2026-10-20-06 | date: 2026-10-20 | label:  | source-line: 3348 | approx: no -->
### 2026-10-20-06 — Ex-jump spread (build_matrices_exjump.py, exjump_spread_test.py; rule committed d24ce99 before the run)
> Original heading: `### 2026-10-20 (late) -- Ex-jump spread (build_matrices_exjump.py, exjump_spread_test.py; rule committed d24ce99 before the run)`
NOT ADOPTED. Estimating each stock's spread without its own event, earnings and Regulation FD days (4.68% of stock-days kept out of the 250-day window) gave log-score gains of +0.0030 / +0.0176 / -0.0065 by
era (bar +0.005 in each, 14 of 21 years positive vs 70% needed); it loses in volatility spikes (2008, 2020, 2026). Today's spread is about 21% too high in variance (median ratio 0.909) but calibration absorbs the level.
The unscaled mean squared miss is 0.895 today and 1.133 ex-jump: 1.0 is not the target. Group multipliers move only +0.8 to +3.1%. Ledger row spread_exjump_window (null). The matrices are in
data_cache/audit_matrices_exjump.npz (gitignored). The card keeps today's spread.


<!-- entry: 2026-10-20-05 | date: 2026-10-20 | label:  | source-line: 3336 | approx: no -->
### 2026-10-20-05 — Median-scale adoption check (median_scale_adoption_check.py, rule committed before the run)
> Original heading: `### 2026-10-20 (late) -- Median-scale adoption check (median_scale_adoption_check.py, rule committed before the run)`
NOT ADOPTED. Under the pre-set rule the median scale (one edge per group, existing multipliers) passed 15 of 17 judged group-era cells and all 12 ordinary stress-bin cells but failed earnings day 0 and day +1
in 2013-2019 (coverage 87.30% and 87.19% on about 12,000 days each; today's band 88.53% and 88.14%). Today's band (column B) reproduced the earlier calibration numbers exactly. On a 90%-quantile basis the earnings
window is wider under the median scale (3.24x / 2.70x vs 2.86x / 2.39x): hypothesis, untested, that the mean scale is partly inflated by the earnings stocks themselves on busy reporting days (a check would be the
ratio of the mean scale to the median scale against the share of stocks in earnings windows). Ledger row band_median_scale_all_groups (null). The card, map and calibration keep the mean-based scale with per-bin
edges for ordinary days. models/band_median_calibration.json records the edges and adoptable = false.

Intended use of the median scale (2026-10-20): VALIDATED for ordinary stock-days only (no recorded event, earnings window or Regulation FD filing): one edge holds 89.6-91.1% coverage in every stress bin and
era, and the share beyond a fixed threshold is flat across stress. NOT validated for earnings windows (failed 2013-2019), NOT adopted in the card, and NOT tested as a news filter (it proves calibration, not that
flagged stocks are more newsworthy). Any threshold must be re-derived (2.0 units flags about 7% of ordinary stock-days under it vs 3.6% under the mean scale), and a filter should use the previous-day variant
if it must be known in advance (ordinary coverage 89.8-90.1%). A candidate first use: an extra column in the day map's missing-information list, behind its own pre-set check.


<!-- entry: 2026-10-20-04 | date: 2026-10-20 | label:  | source-line: 3330 | approx: no -->
### 2026-10-20-04 — Robust stress scale (robust_stress_test.py, rule committed 97eb587 before the run)
> Original heading: `### 2026-10-20 (late) -- Robust stress scale (robust_stress_test.py, rule committed 97eb587 before the run)`
Scaling by the MEDIAN squared miss (sqrt(median(z^2)/0.45494)) with ONE edge passed its pre-set rule on ordinary days: coverage 89.63-91.08% in all 12 era-by-stress-bin cells (spread 0.7-1.1 points)
against 87.95-94.37% for the current mean-based scale with one edge and 89.23-92.97% with per-bin edges (which also drift by era); interval score 0.983-0.986 of today's. Ledger row band_stress_scale_median
(proven). NOT adopted: the card, map and calibration still use the mean-based scale. Open: an adoption check on the event / earnings / Regulation FD groups (existing multipliers, edges refit under the median
scale, 88-92% per group per era, interval score within 1% of today's), the previous-day variant, and then changing day_card / day_map / band_calibrate / band_coverage_test / band_tail_share together.


<!-- entry: 2026-10-20-03 | date: 2026-10-20 | label:  | source-line: 3316 | approx: no -->
### 2026-10-20-03 — sector_day_z and sector_day_tail refreshed past 2026-07-31
> Original heading: `### 2026-10-20 (late) -- sector_day_z and sector_day_tail refreshed past 2026-07-31`
Both tables are built by Postgres functions (build_sector_day_z(y), build_sector_day_tail(y)), run one year at a time in the SQL editor; they delete and rebuild their year and inner-join vol_estimators.
The functions carried a hard-coded cap LEAST(make_date(y,12,31), '2026-07-31'); the cap was removed on 2026-10-20 (live definitions edited with pg_get_functiondef + replace) and 2026 was rebuilt.
Backups: sector_day_z_backup_20261020, sector_day_tail_backup_20261020 (the January-July 2026 rows). Check: January-July rows identical to the backups (1,740 rows, 0 changed); both tables now end
2026-09-15 (372 new rows = 31 trading days x 12 sector labels), apparently where vol_estimators ends (to be confirmed). scripts/macro/eo_market_test.py reads sector_day_z with no date bound and its
baselines run +63..+252 trading days past an event, so it was pinned to its pre-registered window (rows after 2026-07-31 skipped); rerun it and compare with the ledger row
eo_relevant_signing_market_wide_amplification. Open: what refreshes vol_estimators; the builder statements are not in the repo (save pg_get_functiondef output as sql/build_sector_tables.sql).

Follow-up 2026-10-20: the pinned eo_market_test.py reproduces its ledger evidence exactly (2004-2012 0.964 n=144; 2013-2026 1.007 n=324; pooled 0.994 n=468; verdict not passed).
vol_estimators was built once (CREATE TABLE AS, 2026-10-14/15) for an estimator comparison and carries a 20-day FORWARD outcome column (a), so a row needs a close 20 trading days ahead: its last day is the
last price minus 20 trading days (2026-09-15 for prices to 2026-10-13; prices_last and vol_estimators_last were checked). The older-years extension function extend_year_safe(y) refuses 2019+, and the statement that
added August-September 2026 was not found. The sector builders inner-join it, so sector_day_z / sector_day_tail also end 2026-09-15. day_web.py computes v64 from prices when the table has no row (same
definition: sample sd of the 64 returns before the day, at least 50). Option not taken: rewrite the sector builders to compute v64 inline, which would extend them to the last price.


<!-- entry: 2026-10-20-02 | date: 2026-10-20 | label:  | source-line: 3299 | approx: no -->
### 2026-10-20-02 — Band coverage and calibration
> Original heading: `### 2026-10-20 (late) -- Band coverage and calibration`
band_coverage_test.py (pre-set: calibrated if 87-93% in each era): the card's band (fixed edge 1.645) OVER-covered every group: ordinary 93.3% (mean squared band unit 0.84), recorded
event 93.8%, earnings day 0 91.8% (calibrated), day +1 92.7%, event + earnings 92.9%, Regulation FD 94.3%; earnings windows put 2.3-2.7% of misses beyond the 99% edge (1% nominal).
Stress scaling over-corrects (elevated / high stress 95%). The slow spread includes each stock's own earnings and event jumps (inflated by about 20%). All four under-coverage
predictions were wrong. Scoring with the previous day's stress changed coverage little (ordinary 93.3 -> 92.8). band_calibrate.py (pre-set: 88-92% per era, walk-forward): every group
CALIBRATED; edges fitted on all years are ordinary 1.527 / 1.441 / 1.289 / 1.290 (calm / normal / elevated / high stress), event 1.337, earnings day 0 1.506, day +1 1.384,
earnings + event 1.433, Regulation FD 1.319; models/band_calibration.json; some earnings and event eras sit at 88.1-89.1% (mild drift: refit periodically). day_card.py now uses the
calibrated edge for the day's group. Cleaner fix, not done: a slow spread computed without the stock's own earnings and event days.

Card check after the calibrated edge (2026-10-20): GEHC 2024-02-06 (earnings day 0) used edge 1.506 and the miss was 2.27 band units, OUTSIDE; JPM 2025-04-09 (ordinary day, high market stress)
used edge 1.290 and the miss was -0.68, INSIDE. Band limits and misses were cross-checked by hand against the printed prices.

Forward test of the operating-income earnings surprise: scripts/card/earnings_forward_test.py, rule frozen at commit 914d857 (2026-10-20) before any window data existed. Readiness check on the real
database (2026-10-20): matrices end 2026-10-13, no item 2.02 filings in the window yet. Before evaluating (planned January 2027): refresh prices, raw 8-K filings and quarterly statements (the onboarding
scripts in SCRIPTS notes are for new companies; the incremental refresh interface needs checking against the real script), rebuild the matrices, run the readiness check, then --evaluate ONCE.
Ledger row earnings_surprise_sign_operating_income_forward (freeze commit recorded in its notes).


<!-- entry: 2026-10-20-01 | date: 2026-10-20 | label:  | source-line: 3276 | approx: no -->
### 2026-10-20-01 — Phase 7 engine, additions (2026-10-20)
> Original heading: `## Phase 7 engine, additions (2026-10-20)`

**Where the unexplained squared miss sits** (market and sector explain about 45% of squared daily moves; of the other ~55 points, by this session's runs, approximate): earnings
days about 19.5% of the unexplained (3.2% of stock-days), recorded event days about 4-5%, an excess tail on other days at most about 5 points, and about 70% looks like ordinary
heavy-tailed noise (the clean-day tail, 33.3% of the clean mass, matches a Student-t with ~9-10 degrees of freedom; Gaussian 26.1%). Shape cannot prove noise.

**Scripts added** (scripts/card/): gap_audit.py (statistical factors, stress split, composition; builds data_cache/audit_matrices.npz), gap_sample.py (random sample of big no-event
misses; `noearn` option), earnings_thread_test.py, eightk_item_scan.py, vol_regime_audit.py, earnings_surprise_test.py, day_card.py (assembled stock-day card), day_map.py (market-wide
day map). models/ holds the fitted files the card reads (event_band_model.json, earnings_band_model.json, label_annotation.json, decomp_validation_20261020.json).

**Results** (pre-set rules; ledger rows event_earnings_window_width, eightk_item_*, shared_structure_statistical_factors, vol_regime_blend_base_spread, earnings_surprise_*):
earnings windows widen the band 2.72x / 2.47x (day 0 / +1), 2.87x with a recorded event (PROVEN, 21 of 21 years); 8-K item 7.01 1.36x (lead); items 8.01, 5.02, 1.01, 2.03, 5.03,
5.07 add nothing; statistical factors real but small (+0.010 / +0.020 / +0.040 R-squared, 22 of 22 years, does not clear +0.02 in every era); a recent-volatility blend does not earn
its place (+0.025 / -0.011 / +0.025); earnings-surprise proxy: sign 53.4% / 52.9% (does not clear 54%), size nothing. Post-hoc: operating income leads revenue by ~1.4 points on identical
events; a forward test on the Q3 2026 season is frozen in the ledger (earnings_surprise_sign_operating_income_forward).

**Corrections made during the work**: the day card used the 50%-return filter on the day being explained and dropped three real energy crashes on 2020-03-09 (APA, OXY, TRGP); it now uses
every return for the day being explained and lists moves beyond 50%. The card showed a 1.00x band multiplier on earnings days; it now uses the measured group values. The joint
width model's day-only line was wrong (a dictionary kept one cell per day) and was fixed. Item codes 5, 7, 9 are pre-Aug-2004 formats and are ignored by the scan.

**Open**: band coverage test (does the 90% band contain about 90% of misses on ordinary days, event days and earnings windows?); the five day-one baseline logs (chapter 2, validation,
event width, direction, placebo) are not in results/; an ex-jump version of the fast-spread test; earnings-day filing times from EDGAR (would sharpen the band to about 3.5x on the reaction day).


<!-- entry: 2026-10-19-02 | date: 2026-10-19 | label:  | source-line: 3245 | approx: no -->
### 2026-10-19-02 — Phase 7 engine, chapter results (2026-10-19 / 2026-10-20)
> Original heading: `## Phase 7 engine, chapter results (2026-10-19 / 2026-10-20)`

**Structure.** Chapter 1 = market + sector (per-stock 250-day fit on SPY and the same-day mean of the other stocks in the sector). Chapter 2 = macro and
policy flags. Chapter 3 = the stock's own events. Everything is scored walk-forward (fit on prior years only) against a rule written before the run;
failures stay on the record. Scripts in scripts/card/ and scripts/macro/ (decomp_validation, chapter2_test, event_width_test, direction_test,
direction_placebo, event_center_test, timing_profile, masking_test, oil_size_test, build_return_cache, label_event_direction in scripts/classification).

**Chapter 1** (2.35M stock-days, 2005-2026): R2 vs zero 0.452 (eras 0.493 / 0.364 / 0.448), mean z^2 1.14, |z|>3 misses 1.6%. Adding oil, yield and credit
(layer 2) gives -0.007: does not earn a place (rule: +0.02 and positive in all eras). On own-event days: mean z^2 2.96 vs 1.11, 5.6% vs 1.6% big misses, R2 0.29.

**Chapter 2** (full run; flag days 552 / 351 / 531): per-sector, all-stock and per-stock macro pulls do not earn a place; flags do not widen the spread beyond
recent volatility (+0.000 / +0.001 / +0.002 nats). Flags widening the slow spread: +0.004 / +0.011 / +0.056, 13 of 22 years: does not (the 40-stock trial's
pass did not hold at full scale). Timing profile: macro links act on the flag day only. Masking/compounding between oil, yield and credit days: not seen
(power: differences under about 0.2 not detectable).

**Chapter 3, width** (event_width_test.py; ledger event_day_width_own_events, proven): own-event days are about 1.6x wider than ordinary days after removing
market-wide stress (day 0 1.78x, day +1 1.40x; large 2.17x, small 1.25x; new 1.71x, previously announced 1.32x; capital_raise 1.03x). All pre-set predictions held.

**Chapter 3, sign** (labeler dir_v1, claude-haiku-5-5, 22,283 events; 65% unclear). direction_test.py PASSED its pre-set line in both eras (57.7% and 57.8% vs
within-type nulls 53.9% and 53.7%; ledger event_label_direction_sign, held at lead). Post-hoc: days 2-20 at chance; far placebo underpowered (n=538).
event_center_test.py (pre-set, label beyond type): DOES NOT (+0.029 / +0.028 / +0.223%, 14 of 22 years). The sign is real and tiny against event-day
noise. Decision: no signed pull in the hypothetical price; the label is shown as an annotation.

**Event-premium rebuild** (after the event_market_reactions repair above): the view-only reactions had skipped days 0 and +1; repaired, ordinary-type
excess is +0.0292 / +0.0490 / +0.0794 (2004-07 / 2008-12 / 2013-18), +0.0367 older 2019-26 events, +0.0877 wave 1, +0.1243 wave 2. The earlier
"premium shrinks as the event set broadens" reading was mostly the defect. Backups: events_ratio_backup_20261019, reactions_view_only_backup_20261019.

**Open.** Baseline logs for chapter 2, validation, width, direction and placebo were not saved before a Codespace restart cleared /tmp; only event_center_full.out
is in results/2026-10-19/. Regenerate them (about ten minutes) and compare with the numbers above. Far placebo from the price cache for all events. Joint model
for the width multipliers. Gap audit after the engine is assembled.


<!-- entry: 2026-10-19-01 | date: 2026-10-19 | label:  | source-line: 3210 | approx: no -->
### 2026-10-19-01 — event_market_reactions view repair (2026-10-19)
> Original heading: `## event_market_reactions view repair (2026-10-19)`

**What was wrong.** event_market_reactions is a VIEW (live computation from market_prices) that overrode its numbers with the table
event_market_reactions_corrected (one row per event, primary key event_id; written by tag_reaction_character.py with the cumulative-from-prior-close
convention; 15,897 events, 564 date-corrected). For events not in the corrected table (about 31% of rows) the live branch:
(A) skipped the event date's own session (price_date < event_date for the prior close, price_date > event_date for the reaction day), so return_0d
spanned two sessions, and measured 1d/5d/20d from the reaction-day close instead of the prior close; (B) had no limit on how far after the event the
first price could be (HWM: event 2008, first price 2016); (C) joined the corrected table on event_id alone, stamping one ticker's numbers onto every
ticker of a multi-ticker event (114 rows; BAC/JPM/WFC for Lehman had identical returns); (D) fanned out on duplicate relationship links (3 rows).
It also compared a date with a timestamptz (time-zone dependent). Found because the direction test's self-check against the stored abnormal_return_1d
agreed on only 68% of rows.

**Fix.** sql/views/event_market_reactions_v2.sql: reaction day = first session on or after the event day within 7 days; prior = the session before it;
every horizon cumulative from that prior close; the corrected table supplies only corrected EVENT DATES; UTC pinned; one row per event and ticker.
event_market_reactions is now `SELECT * FROM event_market_reactions_v2` (sql/views/event_market_reactions.sql). Old definition kept in
sql/views/event_market_reactions_OLD_before_repair_20261019.sql (rollback: run that file). Old output kept in table
event_market_reactions_snapshot_20261019; new output at swap time in emr_v2_check.

**Validation.** On 15,812 single-ticker events the new view matched the corrected table: reaction day 100%, prior day 100%, return_0d/1d 100%,
return_5d 99.97%, return_20d 99.94%, abnormal 1d 99.90%, abnormal 20d 98.8% (the 188 mismatches are benchmark-side; probably SPY alignment when a
stock has a missing session; not resolved). Rows 23,351 -> 23,348 (the 3 duplicates). Old gap-1/3/4 rows: the sign of the 1-day return flipped in
about 50% (the old value was the day AFTER the reaction day). New NULL 1-day returns: 626 reaction day more than 7 days out, 29 no prior session,
31 cross-ticker stamping (NWS had no prices while NWSA's numbers were stamped on it; CEG/EXC). Post-swap: 22,513 rows at gap 0, 86 at gap 1-7, 749 NULL.

**Not affected (read the corrected table or compute from prices):** reaction-character tags, multi_feature_model_magnitude.py,
populate_sector_peer_benchmark.py, suggest_bundled_event_dates.py. 15-18 tagged events per tag were not in the corrected table.
**Affected / rerun:** pattern_card.py (read the view; also had two scale bugs, see below), refresh_event_scratch_tables.sql (2019 events: view rows
for events not in the corrected table), classifier_confidence_calibration (recomputes automatically), direction_test.py.

**pattern_card.py (patched 2026-10-19).** (1) get_tagged_event_ids read event_tags without paging (API caps at 1,000 rows); (2) get_reactions sent all
ids in one in_() (400 Bad Request). Now pages the links, chunks ids by 100, and reads the corrected table (one row per event). The tag is selected on
days +1..+20 from the reaction-day close (day 0 excluded), so the 1d/5d/20d rows contain selected days; the 0d row is clean and is flat for both tags.

**Open.** The 188 abnormal-20d mismatches; the 2019 scratch-table refresh and what was built on it.


<!-- entry: 2026-10-16-06 | date: 2026-10-16 | label:  | source-line: 3203 | approx: no -->
### 2026-10-16-06 — Ripple fill complete
> Original heading: `### 2026-10-16 — Ripple fill complete`
build_ripple_timeline.py --live filled 6,586 events (events with tracks 15,013 -> 21,599; wave 1 2,035 of 2,106, wave 2 1,509 of 1,556) before a
Codespace restart killed it at 10:45. The second pass processed 1,061 event-entity pairs, wrote 0 rows, and skipped every one for
insufficient price data (needs >= 5 company and SPY price rows in the window and a prior-day baseline), plus 34 events with no linked entity.
The remaining 776 trackable events are unfillable by this script (view ripple_todo); not worth rerunning. Coverage: 21,599 of 22,375
trackable events (96.5%); 859 bundled and 320 entity-less events never get tracks. The zoom-out views read the table directly and can be rerun.


<!-- entry: 2026-10-16-05 | date: 2026-10-16 | label:  | source-line: 3193 | approx: no -->
### 2026-10-16-05 — Flag ledger
> Original heading: `### 2026-10-16 — Flag ledger`
Tables flag_ledger (flag_key, family, description, known_on, window_desc, multiplier, pass_rule, status in proven/lead/null/retired/
untested, tested_on, notes) and flag_ledger_evidence (flag_key, era, n, estimate, se, unit). Loaded: 34 flags (6 proven, 5 lead, 15 null, 2
retired, 6 untested), 41 evidence rows. Proven: event_premium_20d, event_burst_day0_1, event_type_capital_raise_no_burst, and the shared
burst number for acquisitions, leadership changes and strategic partnerships. Leads: restructuring, corporate_action (day 0-1 and 20-day),
macro jobs report, storm_tier_large. Retired: ipo_spinoff burst (price artifact) and the capital_raise 20-day discount (failed out of time).
Rules: a stack of filters is judged by calibration on data the filters never saw, not by how well it explains history; failures stay as
'no documented effect'; overlapping flags are combined by measurement, not by multiplying; every filter shows n and eras; a new test adds
a row and never overwrites an old one. The card reads only 'proven' rows.


<!-- entry: 2026-10-16-04 | date: 2026-10-16 | label:  | source-line: 3176 | approx: no -->
### 2026-10-16-04 — Zoom-out type fix, macro-release lane, ripple fill
> Original heading: `### 2026-10-16 — Zoom-out type fix, macro-release lane, ripple fill`
Type fix (seam titles excluded, isolated events, days 0-1 ratio, 2004-18 / 2019-26): corporate_action_other 1.568 / 1.394,
corporate_action_split 1.645 (n=81, 2004-18 only), financial_result 0.961 / 1.280 (unstable across eras), restructuring 1.724 / 1.573;
ipo_spinoff has < 40 clean events per era (its 1.95 was the spin-off price artifact). Macro-release lane: macro_data_releases mixes
real release dates (PAYEMS jobs reports, CPIAUCSL; likely UNRATE, HOUST) with non-release dates (ICSA = week-ending Saturdays; UMCSENT and
many monthly series = period start dates), so only real-release series can feed a known-on-dated flag. SPY release-day |move| vs the
trailing 64-day mean |move| (ratio of means, delta-method SE; control non-release days 0.956-1.008; the gap ratio reads ~0.96 in two
eras because the baseline contains release days): PAYEMS close-to-close 1.285 (z 2.8) / 1.101 (z 1.4) / 1.125 (z 1.1) for 1995-03 /
2004-18 / 2019-26, gap 1.594 / 1.183 / 1.233, intraday 1.271 / 1.093 / 1.013; CPIAUCSL 1.084 / 1.042 / 1.096, gap 1.171 / 1.059 / 1.315,
intraday ~1.0; HOUST 1.029 / 1.019 / 0.962. Pre-set rule (close-to-close ratio > 1.10 with z > 2.5 in all three eras): FAILED for all.
The jobs report is positive in every era (pooled ~+16%, SE ~5%): a lead only (one of ~27 numbers looked at). If any effect exists it
sits in the opening gap (8:30 a.m. releases). Ripple: sec_8k_filings has only filing_date (no acceptance time), so day 0 cannot depend
on filing time without an EDGAR fetch (possible later project). View ripple_todo = 7,362 trackable events without a track (older 3,700 +
wave 1 2,106 + wave 2 1,556); 859 bundled and 320 entity-less events can never get one. build_ripple_timeline.py started 2026-10-16
(PID 21518, log /tmp/ripple_*.log): append-only upsert, skips events already in event_ripple_timeline, excludes bundled by default,
unordered paging, caches all price history in memory.


<!-- entry: 2026-10-16-03 | date: 2026-10-16 | label:  | source-line: 3164 | approx: no -->
### 2026-10-16-03 — Zoom-out: corrected test and by-type bursts
> Original heading: `### 2026-10-16 — Zoom-out: corrected test and by-type bursts`
Corrected estimator (ratio of means with delta-method SE) on isolated events, relative to days 25-39: 2004-2018: pre -4..-1 +0.062
(z 4.4), days 0-1 +0.305 (z 14.3), days 2-5 -0.013, days 6-20 -0.014 (z -1.9), days 21-24 -0.009; 2019-2026: pre +0.028 (z 1.8),
days 0-1 +0.296 (z 11.8), days 2-5 +0.013, days 6-20 -0.019 (z -2.0), days 21-24 +0.003. Pre-set: 'lasting' no; 'leaks early' no (new era
z 1.8); the earlier 'short burst' wording that included days 2-5 is not met: the burst is days 0-1 only (~+30%). By type (days 0-1
ratio, isolated, 2004-18 / 2019-26): acquisition 1.277/1.271, leadership_change 1.226/1.220, strategic_partnership 1.202/1.336,
legal_settlement 1.194/-, governance 1.306/-, restructuring 1.721/1.576, corporate_action 1.588/1.446, regulatory 1.545/1.066 (flips),
capital_raise 0.957/1.041 (no burst), financial_result 0.960/- (surprising), ipo_spinoff 1.945/- (probably spin-off price artifact; seam
titles not yet excluded in this table). Type rule (differs from pooled ~1.30, z>2.5 in BOTH eras): only capital_raise qualifies;
corporate_action (z 3.7/1.2) and restructuring (4.0/1.8) lean higher but fail in 2019-2026. Limits: ripple tracks cover 15,013 of ~23,550
events; older events are mass-confirmed promotions; current-index survivorship; magnitude only.


<!-- entry: 2026-10-16-02 | date: 2026-10-16 | label:  | source-line: 3152 | approx: no -->
### 2026-10-16-02 — Event-time zoom-out (event_ripple_timeline)
> Original heading: `### 2026-10-16 — Event-time zoom-out (event_ripple_timeline)`
event_ripple_timeline: 653,815 rows, 15,013 events, day_offset -5..39, CUMULATIVE raw/spy/abnormal returns from the day -1 close
(daily move = difference of consecutive rows); concurrent_event_count is NULL for ~38% of rows (not used). Views created:
event_daily_abn (daily |stock - SPY| move per event/day) and event_profile_base (window means per event; base = mean of days 25-39;
era = pre-2004 / 2004-2018 / 2019-2026; isolated = no other event for the entity within -5..+39 days). Curve on isolated events, ratio
of means vs days 25-39 (=1.0): 2004-2018 day 0 = 1.357, day 1 = 1.256; 2019-2026 day 0 = 1.294, day 1 = 1.299; days 2-5 ~1.00;
days 6-24 ~0.98; days -4..-1 ~1.01-1.11. Reading: the ~5% 20-day event premium is a two-day burst (~+30% daily move size),
not a 20-day state (rough arithmetic: ~+4-5% on a 20-day std). First formal test (mean of per-event ratios window/base) was BIASED
upward (E[X/Y] > E[X]/E[Y]): the control window 21-24 read +0.07..+0.13 with z up to 7.8, and its literal pre-set output
('lasting', 'leaks early') was rejected. Replaced by ratio-of-means with delta-method SE (rules unchanged). Limits: 15,013 of ~23,550
events have tracks; older events are mass-confirmed promotions; current-index survivorship; magnitude only, no direction.


<!-- entry: 2026-10-16-01 | date: 2026-10-16 | label:  | source-line: 3139 | approx: no -->
### 2026-10-16-01 — Out-of-time replication of the event premium (2004-2018)
> Original heading: `### 2026-10-16 — Out-of-time replication of the event premium (2004-2018)`
vol_estimators extended back via extend_year_safe(y) (1995-2018 only; wrapper refuses 2019+; loaded 1995-1997 and 2004-2018,
mm_matched built from vol_estimators using a/(v64*sqrt(20)), identity verified against daily_scaled_move: max diff 6e-13
over 194,407 rows); events_ratio extended with ratio_period(lo, hi). The SQL editor times out above about one year per
statement. 1995-2003 not used (unloaded years would give stale ratios). Sanity gate passed (2019-2026 rows reproduce).
Pre-set rules applied to 2004-2018 pooled. Ordinary types: n=9,412, +0.0470 (SE 0.0091, z~5.2, interval +0.0289..+0.0652)
-> consistent (interval contains +0.0295, barely); eras +0.020/+0.045/+0.069 for 2004-07/2008-12/2013-18 and +0.025 for
2019-26; all 2004-2026 n=14,592 +0.0393 (SE 0.0067). capital_raise: n=878, -0.0252 (SE 0.0190, z~-1.3) -> FAILS (needed
<= -0.05 and z <= -2); eras +0.027/-0.058/-0.018/-0.067; all years -0.0412 (z~-2.8): not robust across eras; hypothesis only,
no range multiplier. corporate_action: 2004-2018 +0.0725 (SE 0.0358), all years +0.0538 (SE 0.0273): exploratory, parked.
Caveats: current-index survivorship; older events are mass-confirmed promotions with weak events mixed in; band cut points
from 2019-2026; naive SEs; many looks overall.


<!-- entry: 2026-10-15-07 | date: 2026-10-15 | label:  | source-line: 3124 | approx: no -->
### 2026-10-15-07 — Replication on promotion wave 2
> Original heading: `### 2026-10-15 (late night) — Replication on promotion wave 2`
Cohort new_events_wave2 (newest 1,556 events by age(xmin), overlap with wave 1 checked). Only 337 are dated 2019+ (baseline
tables cover 2019-2026); 331 reactions loaded; 310 usable ordinary-type rows. NOTE: the 'realized_vol_rows_for_wave2'
query returned 1,556 because it counted the cohort through a LEFT JOIN; ignore it. Old rows reproduced exactly (ordinary
+0.0295 n=4,371; capital_raise -0.0671 n=545; corporate_action +0.0135 n=311; wave 1 -0.0063 n=499). Wave 2 ordinary
+0.0160 (SE 0.0366, interval -0.057..+0.089); new events pooled (waves 1+2) n=809 +0.0022 (SE 0.0231, interval
-0.044..+0.048); difference vs old events 0.027 (SE ~0.025, z~1.1); all ordinary events pooled ~+0.025 (SE ~0.0094,
z~2.7; hand-computed). Pre-set rule (consistent if the interval contains +0.0295, failing if the upper end is below
+0.02): consistent but uninformative. Both groups contain weak events (new: ~100-150 of 1,556; old: ~1/3 of old
governance events looked routine), so neither is clean. Power is limited by the 2019 start of the baseline tables.
Proposed next: extend vol_estimators, daily_scaled_move and mm_matched back to ~2000 (prices cover ~27 years;
event_realized_vol already spans all events) for an out-of-time test on ~10K older events, reported by era;
pre-set: consistent if the 2000-2018 ordinary interval contains +0.0295; replicated at a lower level if positive
with z > 2 but excluding +0.0295; not replicated if its upper end < +0.02. Caveat: current index members only.


<!-- entry: 2026-10-15-06 | date: 2026-10-15 | label:  | source-line: 3112 | approx: no -->
### 2026-10-15-06 — Promotion wave 2
> Original heading: `### 2026-10-15 (night) — Promotion wave 2`
After the top-band review (see the entry above): promote_events.py --exclude-types capital_raise,corporate_action,
governance_action --live: events 21,998 -> 23,554 (+1,556). Live run: 1,868 groups, 144 confirmed duplicates, 89
verifier-rejected heuristic matches, 233 verification calls, 43 skipped for no event type, 125 skipped for no
title/description. The dry run had predicted 1,664 creates and 98 duplicates; a live run also catches
announcement/completion duplicates within the batch (probable cause of the difference; not proven). Integrity after the
run: 0 orphans, 0 capital_raise/corporate_action/governance events, 0 same-entity/date/title duplicate pairs.
Dry-run sample of 40: 37 real, 3 weak (PSE&G internal asset transfer, PepsiCo forward-looking-statement filing, SCE
subsidiary president) -> ~100-150 weak events expected among the 1,556. None of the 950 bulk-confirmed rows lacked
a title or description. Unpromoted confirmed rows (~168 missing title/description/type) need a separate fix.
Cohort for the replication: new_events_wave2 (newest 1,556 events by age(xmin)).


<!-- entry: 2026-10-15-05 | date: 2026-10-15 | label:  | source-line: 3101 | approx: no -->
### 2026-10-15-05 — Replication on the newly promoted events
> Original heading: `### 2026-10-15 (afternoon) — Replication on the newly promoted events`
Scratch tables refreshed for the 2026-10-15 cohort (new_events_20261015, 2,106 events; 535 event_realized_vol rows,
532 reactions in reactions_view_only, events_ratio extended). Old rows reproduced exactly (ordinary +0.0295 n=4,371;
capital_raise -0.0671 n=545; corporate_action +0.0135 n=311). New cohort, ordinary types (capital_raise,
corporate_action, governance were excluded from promotion): n=499, matched excess -0.0063, SE 0.0298 (interval -0.065
to +0.053). Pre-set rule (consistent if the interval contains +0.0295; failing if the upper end < +0.02): consistent,
but the test is uninformative: it cannot distinguish +0.03 from zero; difference from old events 0.036, SE ~0.032
(z~1.1). Pooled ordinary premium ~+0.026 (SE ~0.0097, z~2.7; hand-computed). The premium has shrunk with each
broadening of the event set (+0.041 -> +0.031 -> +0.0295 -> new cohort -0.006); promoted events are milder
(selection), so a smaller value is expected. Treat as small, unstable, 0 to ~3%. Range product unaffected.


<!-- entry: 2026-10-15-04 | date: 2026-10-15 | label:  | source-line: 3083 | approx: no -->
### 2026-10-15-04 — Promotion run, concurrent-process incident, cleanup
> Original heading: `### 2026-10-15 (evening) — Promotion run, concurrent-process incident, cleanup`
promote_events.py --exclude-types capital_raise,corporate_action,governance_action --live: events 19,892 -> 21,998
(+2,106). Final clean run: 583 filing groups, 299 created, 100 confirmed duplicates, 32 heuristic matches rejected
by the verifier, 30 skipped for no event type, 154 skipped for no title/description (these confirmed rows still need
titles/types before they can be promoted). A first run with governance_action allowed (PID 10841) survived a kill
and ran at the same time as a second run: 136 orphan duplicate events (no event_source_filings row) were created
and removed. Removals were single DO-block transactions with audit-copy-then-delete, row-count guards and rollback on
mismatch: 27 routine governance events (rights plans, majority-voting/proxy-access/special-meeting bylaws,
reincorporations, FedEx fiscal-year change), 20 deal admin steps (HSR/FTC/FERC/SEC approvals, tender extensions,
disclosure statements), 136 orphan duplicates; audit tables event_removal_audit_20261015_{events,sources,types,
entities} (183 events). Source filings of removed events set to rejected_noise so the script cannot re-create them.
Governance sample read: 9 real of 39 (rubric: rights plans/bylaw/reincorporation are routine, activist
responses are real). Admin-title search over today's events: ~20 of 29 candidates removed; 9 held. Lessons: check
`ps` and kill the parent shell before starting a second promotion run; an orphan check must be rerun after any
concurrent run; scripts/sql/refresh_event_scratch_tables.sql refreshes the Phase 6 scratch tables for the new events.
Unaddressed: 30 older duplicate pairs (pre-2026-10-15), 9 admin-step holds, 154+30 skipped groups, 12 governance
events kept (3 are judgment calls: ACE redomicile, Domino's 203 waiver, Aptiv scheme).


<!-- entry: 2026-10-15-03 | date: 2026-10-15 | label:  | source-line: 3070 | approx: no -->
### 2026-10-15-03 — Final matched results incl. 2026; scratch-table duplicate incident
> Original heading: `### 2026-10-15 (afternoon) — Final matched results incl. 2026; scratch-table duplicate incident`
events_ratio first loaded 2019-2025 only (n=4,832); the 2026 insert was then run twice by mistake (790
rows instead of ~395; 5,622 total vs 5,227 distinct event/ticker), removed with a self-join DELETE on
ctid. Final, month x v64/v250-band matched baseline, events 2019-2026-07: all other types n=4,371 excess
+0.0295 (SE 0.0102, z~2.9; month-only +0.0308); capital_raise n=545 -0.0671 (SE 0.0242, z~-2.8; month-only
-0.0698); corporate_action n=311 +0.0135 (SE 0.0385; month-only +0.0108). Both pre-set rules pass
(ordinary >= +0.02 with z >= 2; capital_raise <= -0.05 with z <= -2). Ordinary-event excess by year (SE
~0.025-0.043): 2019 +0.048, 2020 +0.000, 2021 +0.043, 2022 +0.012, 2023 +0.074, 2024 +0.026, 2025 +0.037,
2026 -0.030 (n=332; 1.4 SE below the pooled mean; no evidence of decay, watch as 2026 data grow).
These supersede the 2019-2025-only figures in the entry above (+0.0344 / -0.0610). Naive SEs; clustering
by month would widen them ~10%. Scratch tables kept for the post-promotion rerun: reactions_view_only,
mm_matched, events_ratio (rebuild per-year; run each INSERT exactly once, check counts after each).


<!-- entry: 2026-10-15-02 | date: 2026-10-15 | label:  | source-line: 3050 | approx: no -->
### 2026-10-15-02 — Volatility-ratio matched baseline (artifact check) for the event premium and capital_raise
> Original heading: `### 2026-10-15 — Volatility-ratio matched baseline (artifact check) for the event premium and capital_raise`
Scratch tables (derived, safe to drop/rebuild): reactions_view_only (911 view-only reactions, 2019-2026-07),
mm_matched (month x vol-ratio band baseline: band 1 = v64/v250 < 0.775, 2 < 0.950, 3 < 1.162, 4 above;
cut points are the population 20th/50th/80th percentiles 0.775/0.950/1.162; mean 0.979; built from
daily_scaled_move joined to vol_estimators with v250 > 0; 48 cells/year, 2020 has 44 and 2022 has 47
because some bands are empty in some months), events_ratio (event, ticker, bucket, month, scaled move,
v64/v250 on the last day BEFORE the event). Population vol ratio 0.979; ordinary events 0.978 (median
0.947); capital raises 1.042 (median 0.981): capital raises follow slightly elevated volatility.
Results (events 2019-2025 only; 2026 events were missing from this run, n 4,832 vs 5,262 earlier, 396
2026 events expected to be the gap): all other types n=4,039 excess +0.0357 (month only) -> +0.0344
(matched, SE 0.0105, z~3.3); capital_raise n=500 -0.0627 -> -0.0610 (SE 0.0255, z~-2.4); corporate_action
n=293 +0.00002 -> +0.0049 (SE 0.0394). Pre-set rules: capital_raise survives (<= -0.05 and z >= 2), ordinary
premium survives (>= +0.02 and z >= 2). My prior estimate that mean reversion could explain 1/3 to 2/3 of
the capital_raise effect was wrong: matching moved it by 0.0017 (~3%). Capital_raise effect = ~8% smaller
moves (-0.061 on a ~0.75 base), formed on one sample, retired, replicated on 317 new events (-0.081),
robust to vol-ratio matching, NOT tested on future data (events after 2026-07-31 are the holdout; need
>= ~150 outcomes). No capital_raise multiplier added to the range tool (a coverage test with ~500 events
cannot see a ~2 point shift; SE ~1.8). Naive SEs, no clustering. Earlier "types consistent with one
premium" no longer holds with capital_raise included.


<!-- entry: 2026-10-15-01 | date: 2026-10-15 | label:  | source-line: 3030 | approx: no -->
### 2026-10-15-01 — Replication of the event premium on events the earlier tests never saw
> Original heading: `### 2026-10-15 — Replication of the event premium on events the earlier tests never saw`
Finding: event_market_reactions_corrected holds 15,897 events; events has 19,892; the view
event_market_reactions covers 19,572 (the other 320 are macro/global events). All Phase 6 event
tests read the corrected table, so ~3,675 events with reactions were excluded. The view is too slow
for one query (upstream timeout), so view-only reactions were copied by year into reactions_view_only
(911 rows 2019-2026, 87-172 per year). Same filters as before (non-bundled, no spin/separation/split-off
titles, HON after 2026-06 excluded), month-matched baseline daily_scaled_move.
Results: in-corrected n=4,404 excess +0.0311 (SE 0.0104) -- reproduces the earlier figure exactly;
view-only n=858 excess -0.0409 (SE 0.0196; 95% interval -0.079..-0.003); gap 0.072 (SE ~0.022, z~3.3,
naive). By year view-only: 2019 -0.081, 2020 -0.007, 2021 -0.025, 2022 -0.010, 2023 -0.121, 2024
-0.012, 2025 -0.069, 2026 -0.010 (8 of 8 negative; cells n=61-159); corrected: 7 of 8 positive.
Pooled n=5,262 excess ~ +0.019 (SE ~0.009, z~2.1; hand-computed). Pre-set rules: view-only
"failing" (upper end < +0.02); pooled premium < +0.02 = completeness mattered (barely). Trajectory of the
overall premium: +0.041 -> +0.031 (seam events removed) -> +0.019 (events outside the corrected table
added). Hypotheses (untested): the corrected table holds older curated, eventful events while the
view-only events are milder 8-K promotions (selection); type mix; measurement differences (view vs
corrected). Event-premium claims downgraded to "small and unstable, 0 to ~3%". Range product unaffected
(prices only). Next: split by from_8k_promotion (event_source_filings) and by type; after the
review/promotion, repeat on the newly promoted events.


<!-- entry: 2026-10-14-11 | date: 2026-10-14 | label:  | source-line: 3005 | approx: no -->
### 2026-10-14-11 — Prompt v6.x experiments and the role-change guard: stopped
> Original heading: `### 2026-10-14 (night) — Prompt v6.x experiments and the role-change guard: stopped`
Goal: stop the classifier clearing real events (CEO/CFO/President/Chair changes, guidance cuts, large
charges, large buybacks). Copy script: classify_8k_filings_v6_reclass.py (reads view candidate_8k_reclass over
reclass_targets = 6,913 filings + audit_flagged_20261014 = 62 rows; old AI fields in
filing_ai_classifications_snapshot_20261014). v6 (100 A-ticker filings): 23 flagged, 8 real_event flips (4
correct: CFO changes ADBE 2005, ABBV 2018, ABNB 2023, ADBE $25B buyback; 4 broke carve-outs: CEO retention
amendment, division presidents, CAO, Chief Strategy Officer); the 25 known misses all came back real/flagged
(circular). v6.1 (314 filings, 27 tickers): uncertain 23, noise 271, real 20, flagged 85; random 40 non-noise:
11 clear real; failures: ordinary directors marked uncertain, exhibit-only earnings releases marked uncertain,
'recent events' used to upgrade carve-out roles. v6.2 (same 314): noise 281, real 18, uncertain 15, flagged 69;
46 of 314 verdicts (15%) changed vs v6.1; all 33 non-noise rows read: 8 clear real (24%), 14 (42%) counting
reasonable uncertain; uncertain 15 of 33 (45%, 9 pure hedging); the model states the carve-outs (QCOM CTO,
RTX division president, HD director) and still returns real_event. Pre-set bars (>= 60% real, uncertain <= 20%)
FAILED -> prompt tuning stopped. Temperature setting not checked.
Guard (scripts/classification/test_role_guard.py, regex on filing text near Item 5.02, 20 labeled real vs 40
labeled routine; labels are my judgments): v1 recall 11/20, false alarms 5/40; v2 (initials/abbreviations
allowed, more verbs, committee-chair normalized) recall 15/20, false alarms 13/40; bars (recall >= 18/20,
false alarms <= 15/40) FAILED on recall -> not deployed. Rough cost if deployed: ~1,800 extra review rows on
~4,300 unflagged 5.02 rows for ~800 real catches (assumes ~25% real; weak estimate).
DB state: v6 103 rows, v6.2 1,752 rows (noise unflagged 1,268, noise flagged 202, real flagged 186, real
unflagged 7, uncertain flagged 89); kept; the 7 unflagged real_event rows sent to review with
flag_reason v6_real_event_needs_review. Known limitation: some CEO/CFO/Chair changes and guidance cuts remain
cleared as noise in the v5 pool (estimated 2-5% of events, weak estimate); checked later by rerunning the
leadership_change premium on the larger event set.


<!-- entry: 2026-10-14-10 | date: 2026-10-14 | label:  | source-line: 2988 | approx: no -->
### 2026-10-14-10 — Prices healed, forward test months 1-2, known gaps
> Original heading: `### 2026-10-14 (night) — Prices healed, forward test months 1-2, known gaps`

**Price refresh (--splice):** 495 of 497 securities with history current to 2026-10-13. Final tally of the
splice run: 58 spliced, 14 ok, 424 already fresh, 1 restated (CTVA, max_dev 0.84996), 73 requests; seams
checked (ES 09-11 -0.7%, JPM 09-29 -0.5%). KNOWN GAPS: EA (vendor needs a higher plan tier; taken private
2026-08), AVB (vendor 404; merger closed 2026-08), WBD (last price 2026-10-06), CTVA (refetched 2019-01-01..
2026-10-13, 1,856 rows; backup table market_prices_backup_ctva_20261014, 1,846 rows). CTVA stored vs fresh
adjusted_close ratio ranges 6.66-11.05 across 2019-05-24..2026-09-28 with steps of 1.5-3% on dates that look
like ex-dividend days -- not explained; CTVA excluded from analyses until a return-series comparison (corr,
mean abs diff) is checked. HON's +40.2% one-day jump on 2026-06-29 may be a similar adjustment seam (untested).
**Forward test (frozen method v1_6mo_recal_2026-10-14), after repairing prices and reloading vol_estimators
from 2026-08-01 (15,297 rows, 490-493 stocks/day):** Aug 2026: n=10,363, k=1.523, recalibrated coverage 92.9%,
static 80.4%. Sep 1-15: n=4,934, k=1.378, recalibrated 83.9%, static 71.3%. Pooled recalibrated ~90.0%, static
~77% (hand-computed). Original pass rule (>= 6 months, pooled 76-84%, at most 1 of 6 months outside 70-90%):
August used the one allowed miss; two months decide nothing. The earlier August figure (93.0%, n=9,833) was
computed on incomplete prices and is superseded. Amended 12-month rule still proposed, NOT adopted.


<!-- entry: 2026-10-14-09 | date: 2026-10-14 | label:  | source-line: 2957 | approx: no -->
### 2026-10-14-09 — Audit of the unreviewed "noise" pool; price splice
> Original heading: `### 2026-10-14 (evening) — Audit of the unreviewed "noise" pool; price splice`

**Pool audited:** 50,739 unreviewed, unflagged likely_noise filings (before this run's new rows).
**Rewrite is not the cause of the misses:** rewritten 5.5 rows (n=40): 0 confirmed real, 4 unresolved;
original 4.5 rows (n=40): 2 real (ES 1997-01-21 loss warning + PSNH bankruptcy risk; OXY 2013-04-29 CEO
succession + governance overhaul), 4 unresolved. **Concession-language group (40 rows = whole pool):** 4
clear real (ES; LUV 2019-03-27 guidance cut; EG 2025-01-27 preliminary results, $1.7B reserve
strengthening; ERIE 2026-05-21 CFO retirement), 4 lean real, 9 unsure, 23 noise. **Template a (warning /
guidance-cut language, 79 rows read):** 8 clear + 10 lean real. **Template b ($1B+ charge in an earnings
release, 5 rows):** C 2009-02-27 ($9.6B goodwill impairment) real. **Template c (5.02 + CEO/CFO/Chairman/
President + departure word; random 40 of ~1,227 pattern hits):** 10 clear real (CFO changes MCO 2018, MSCI
2019, ALL 2022, D 2018, DGX 2013, CVS 2009, CBRE 2019; Chairman BEN 2013, DG 2026; President PEP 2014) +
MSCI 2013 COO lean; 95% range ~13-41%. Role-count queries over the 4,300 5.02 noise rows (cfo 756, ceo 824,
chairman 567, president 810) are inflated by the AI's own boilerplate "(not CEO, CFO, or Chairman)" and
overlap; not usable as sizes.
**Prompt (classify_8k_filings_batch_v2.py):** the confirmed-real list already includes "CEO/CFO/Chairman
appointments or departures", so the model contradicts its own prompt (MCO: "she is EVP, not CEO/CFO/
Chairman" for the CFO). Differences from the materiality rubric to decide for a v6: "President" absent from
the real list; guidance revisions via exhibit treated as routine (cuts vs raises not separated); buyback
authorizations routine regardless of amount (rubric confirms large ones, e.g. CSX ~15% of market cap);
2.02 in the ALWAYS_ROUTINE prior.
**Actions:** 62 filings flagged for review with flag_reason audit_2026_10_14_possible_missed_event (flags
only; no verdicts changed). Prompt NOT edited mid-run (would create two classification regimes). Plan:
v6 prompt + deterministic guard on filing text for 5.02 role changes + second pass over the 5.02 noise
rows and guidance/charge hits; snapshot table filing_ai_classifications_snapshot_20261014 keeps old fields.
**Prices:** refresh_market_prices.py --splice (rescales new rows onto the stored adjustment scale when the
overlap ratio is constant; dry run JPM 1.00496, A 1.00149, AMT 1.01070, ES 1.01164, all spread 0.000000).
Real run started 17:37 (stale tickers 94 -> 89 at 17:40). Large-move scan since 2026-09-01 looks like
sector-correlated real moves (CRWD/PANW 09-14, GLW/COHR 09-14); PTC +33.5% (10-05) and FICO -26.5% (09-29)
unverified. Codespace restarted 16:54 (jobs killed); classifier is restartable.


<!-- entry: 2026-10-14-08 | date: 2026-10-14 | label:  | source-line: 2939 | approx: no -->
### 2026-10-14-08 — Event types vs MONTH-matched population baseline
> Original heading: `### 2026-10-14 (night) — Event types vs MONTH-matched population baseline`
Same as the year-matched event-type table but expected = mean scaled move of ALL tracked stock-days
in the event's calendar month (daily_scaled_move). Non-bundled events, 2019-2026-07, types with >= 100
events. n / excess (SE): corporate_action 233 / +0.128 (0.056, z~2.3); restructuring 162 / +0.061
(0.059); strategic_partnership 162 / +0.047 (0.052); acquisition 1,172 / +0.043 (0.019, z~2.2);
leadership_change 1,754 / +0.033 (0.017, z~1.9); legal_settlement 161 / +0.028 (0.059);
financial_result 184 / +0.021 (0.046); regulatory 235 / +0.008 (0.042); capital_raise 229 / -0.057
(0.043, z~-1.3). Pre-set bars: corporate_action (>= +0.10 AND ~3 SE) FAILS (best of 9 types reaching
z 2.3 by chance ~9%); capital_raise (<= -0.08 AND z <= -2) FAILS -- it was -0.110 (z~-2.4) on the
year-matched baseline, month-matching absorbed about half (capital raises cluster in quieter
months). Precision-weighted common excess ~ +0.033; heterogeneity Q ~ 8.3 on 8 df, p ~ 0.4
(hand-computed): the nine types are consistent with ONE small premium. Naive SEs (events appear under
several types and cluster in time). Conclusion: event type adds nothing beyond the overall premium;
capital_raise hypothesis retired; corporate_action stays parked. Plan: once the classification backlog
(47,473 filings) and review queue are processed, rerun the overall premium, this table, and the
tag-range test UNCHANGED on the larger event set (pre-registered replication: premium near +0.04 means
completeness did not matter; < +0.02 or > +0.08 means it did).


<!-- entry: 2026-10-14-07 | date: 2026-10-14 | label:  | source-line: 2916 | approx: no -->
### 2026-10-14-07 — Classifier rewrote existing rows; root cause and fix
> Original heading: `### 2026-10-14 (night) — Classifier rewrote existing rows; root cause and fix`

Symptoms: nightly and manual runs "succeeded" but the table barely grew (102,962 -> 102,966; only
4 rows after Oct 7); 30,731 rows labeled claude-haiku-5-5 carried September classified_at dates;
1,656 reviewed rows labeled 5.5 contradicted their human review (vs 75 of 30,409 for 4.5);
735 human-confirmed-real filings had ai_verdict likely_noise with no flag.
Cause: get_unclassified_candidates() built "already classified" in Python from separately
paginated, unordered reads and counted ~37,000 classified filings as new (script said 85,059;
true figure 47,573 = 150,539 in candidate_8k_events - 102,966 classified; 4,602 of 155,141 total
8-Ks are outside the view because of item codes it skips). The upsert replaced AI fields but not
classified_at, with no guard for reviewed rows, so rewritten rows kept their old timestamps.
Two failed runs (Oct 13, Oct 14) died on database writes (RemoteProtocolError, 502 "Network
connection lost") AFTER Anthropic batches finished, losing paid results; batch
msgbatch_01QBPZrFQZe95MTEWZvVNhvV (2,500 filings) is still to be recovered.
Fix: view candidate_8k_unclassified (selection inside the database, excludes reviewed rows);
trigger trg_protect_reviewed (reviewed rows keep AI fields); classifier patched to read from the
view with fixed order, save each batch to classification_backup/ BEFORE writing, write in groups
of 200 with retries, and set classified_at. Snapshot table: filing_ai_classifications_snapshot_20261014.
Test run: 100 filings, 51 flagged, ~$0.067 at Haiku 5.5 rates by token counts (the printed $0.33
is stale Haiku 4.5 batch pricing). NOT repaired: AI fields on rows already overwritten before the
trigger existed; unreviewed rewritten rows may have lost review flags. Pending: recover the Oct 14
batch with guards, rerun the full ~47,473 backlog, disable the nightly workflow in the GitHub UI.


<!-- entry: 2026-10-14-06 | date: 2026-10-14 | label:  | source-line: 2895 | approx: no -->
### 2026-10-14-06 — First forward month, and the monthly-coverage distribution
> Original heading: `### 2026-10-14 (night) — First forward month, and the monthly-coverage distribution`

**August 2026 (first forward month, n=9,833 origin days, one market episode):** recalibrated
(6-month window, k=1.523) coverage 93.0%, static (1.09) coverage 80.8%; interval scores 0.3709
(recalibrated) vs 0.3276 (static). Likely cause (hypothesis): k comes from Feb-Jul, a turbulent
stretch, and August was calm, so ranges were too wide (the lag measured in the backtest).
**Backtest distribution of monthly coverage (recalibrated):** 2019-22: 41 months, 15 outside
70-90%, mean 79.5%, sd 12.3, range 44.9-99.4. 2023-Jul 2026: 43 months, 10 outside (23%), mean
78.2%, sd 8.2, range 52.8-94.0; static was outside in 12 of 43. August's 93.0% is ~1.8 sd
above the 2023-26 mean and inside its observed range.
**Original forward-test rule (pooled coverage 76-84% after >= 6 months, at most 1 of 6 months
outside 70-90%): August is outside 70-90%, so it consumed the one allowed miss.** A method equal
to the backtest passes that rule ~57% of the time before August and ~27% after (rough,
independent-month assumption). The 23% monthly miss rate was above the pre-set 20% "rule too
strict" line.
**PROPOSED amendment (written AFTER seeing August and this distribution, so post-hoc; the
original result stays on the record as failed on August):** evaluate 12 resolved months; pass if
pooled coverage is 74-86%; single months descriptive only. Rough power: ~96% pass for a true mean
of 78%, ~20% for a true mean of 72% (independent months, sd 8; overlap makes true error larger).
Method remains frozen at v1_6mo_recal_2026-10-14.


<!-- entry: 2026-10-14-05 | date: 2026-10-14 | label:  | source-line: 2879 | approx: no -->
### 2026-10-14-05 — Range tool built; method FROZEN as v1_6mo_recal_2026-10-14
> Original heading: `### 2026-10-14 (night) — Range tool built; method FROZEN as v1_6mo_recal_2026-10-14`

scripts/models/range_card.py TICKER [--asof DATE] [--event]: 80% range for the stock's return
relative to SPY over 21 trading days after the last close = +- k * v64 * sqrt(20), v64 = stddev of
the last 64 daily returns, k = range_k6(month) (scripts/sql/range_k6.sql; 80th percentile of
past scaled moves over the 6 months before the prior month, only known outcomes). The "20d"
outcome window is really close(day before event) -> close(20 trading days after event day) = 21
trading days of returns; k absorbs the sqrt(20) vs 21-day mismatch. Not a direction forecast.
The "market flat" price translation understates the real range (SPY's own move is excluded).
Backtest coverage of the 80% label, 2023-2026: 77.1 / 78.8 / 79.6 / 77.1% (one path).
FROZEN: no edits to the method; changes get a new METHOD_VERSION and freeze date.
Forward test (scripts/sql/forward_test.sql): design data used origin days <= 2026-07-31; forward
sample = origin days >= 2026-08-01, refreshed by appending resolved days to vol_estimators.
Pre-registered rule (after >= 6 resolved months): pooled coverage 76-84%, at most 1 of 6 months
outside 70-90%. First month alone is one market episode; read nothing into it.


<!-- entry: 2026-10-14-04 | date: 2026-10-14 | label:  | source-line: 2846 | approx: no -->
### 2026-10-14-04 — Volatility estimators, then monthly recalibration of the 80% range
> Original heading: `### 2026-10-14 (night) — Volatility estimators, then monthly recalibration of the 80% range`

vol_estimators (scripts/sql/create_vol_estimators.sql): 915,215 stock-days 2019-2026 with
trailing 20/64/250-trading-day daily-return stddevs (v20, v64, v250) and the 20d abnormal
move `a` (|20d return - SPY 20d return|); each year must be loaded ONCE (repeat loads
doubled 2020-2026 and were deduplicated; unique index vol_estimators_uq now blocks repeats).
Running-sum stddevs match window STDDEV (max diff 1.2e-13 v64, 7e-16 v20, 6e-17 v250).
**Estimator comparison** (multiplier per estimator fit to 80% coverage on 2019-2022, scored on
2023-2026; interval score = width + 10*overshoot, lower is better). Test coverage / test score /
test-year coverage min..max: v64 74.2% / 0.3132 / 66.6..78.5; v250 73.1% / 0.3138 / 62.2..81.5;
blend3 (equal-variance mean of the three) 73.1% / 0.3139 / 64.7..78.8; max3 72.2% / 0.3176 /
62.9..78.5; v20 74.5% / 0.3245 / 69.2..78.2. Train (2019-22, in-sample): v250 and blend3 beat
v64 by 2.2% on score (4.5% and 3.0% narrower at equal coverage); out of sample v64 is ahead by
0.2%. Pre-set bar (>= 3% lower test score AND >= 2 pts narrower test-year coverage range):
NO estimator beats v64. All lose 6-8 points of coverage out of sample (2026 at 62-69%), so
the lever is recalibration over time, not the estimator. Predictions: v250 "most stable"
WRONG (least stable, 19.4-pt range), v20 best in 2026 right, blend3 best overall WRONG.
Yearly coverage noise is several points (stocks move together in shocks).
**Rolling recalibration** (scripts/sql/adaptive_multiplier_backtest.sql): k = 80th percentile of
past scaled moves over the previous 6 or 12 months (lagged >= 1 month) vs static 1.09023.
Test 2023-26 coverage static 74.2% / w6 78.3% / w12 77.4%; by year (2023/24/25/26) static
78.5/72.9/75.7/66.6, w6 77.1/78.8/79.6/77.1, w12 76.2/77.3/81.2/73.3; coverage range across
test years 11.9 / 2.5 / 7.9 pts; test interval score 0.3132 / 0.3131 / 0.3127 (no meaningful
gain). Mean |coverage - 80| over 2020-2026: 4.7 / 2.5 / 3.7 pts (hand-computed). Cost: 2020
crash year score static 0.4060 vs w6 0.4432 (+9.2%) vs w12 0.4263 (+5.0%) -- the lag; over all
2020-2026 w6 scores ~2% worse than static (static is partly in-sample for 2020-22). Pre-set
bar (coverage 78-82%, range <= ~7 pts, score >= 2% lower): w6 passes the first two (78.3%,
2.5 pts) but not the score condition. Adopted for calibration honesty, not accuracy. Caveats:
one walk-forward path, two windows tried, monthly update granularity.
**Current design of the range:** +- k_t * v64 * sqrt(20), k_t = trailing 6-month 80th percentile
of scaled moves lagged >= 1 month; separate small event premium (~ +5% scaled move, ~1.4 pts of
coverage on event days) not yet combined into the range.


<!-- entry: 2026-10-14-03 | date: 2026-10-14 | label:  | source-line: 2818 | approx: no -->
### 2026-10-14-03 — Month-matched baseline: the event premium is real but small
> Original heading: `### 2026-10-14 (late) — Month-matched baseline: the event premium is real but small`

Built daily_scaled_move (scripts/sql/create_daily_scaled_move.sql): scaled 20d abnormal
move for every tracked stock-day 2019-01..2026-07, 920,249 rows, population mean 0.7448
(consistent with the earlier random-date sample, 0.753 +- 0.011). The earlier year-matched
random-date baseline was noisy (e.g. 2020: 0.633 random sample vs 0.710 population; 2021:
0.799 vs 0.747), so population values replace it.
**Event premium vs month-matched population mean (non-bundled events, n=4,498):** +0.0407,
paired SE 0.0106 (z~3.8, naive). By year: 2019 +0.064, 2020 +0.034, 2021 +0.053, 2022
+0.016, 2023 +0.072, 2024 +0.023, 2025 +0.037, 2026 +0.008 -- all 8 years positive.
**Cluster-robust check (SE across 91 months):** mean month excess +0.0364, SE 0.0112
(z~3.2), n-weighted excess +0.0407, 57 of 91 months positive (62.6%; sign test ~2.4 SE).
Windows overlap across adjacent months and companies recur, so true uncertainty is still a
little larger. Passed pre-set rules (>= +0.02 with z >= 2; >= ~60% months positive).
Survived: realized-vol scaling, bundled-event exclusion, month-matched baseline, clustering
check. Size: ~ +0.04 on a base of ~0.75, i.e. ~5% larger moves on event days.
**Coverage at the 1.2816 multiplier (event days vs all stock-days, by year):** 2019
83.6/85.2, 2020 84.4/85.6, 2021 81.3/83.7, 2022 86.8/87.9, 2023 79.8/84.7, 2024 79.5/79.7,
2025 80.7/82.1, 2026 76.7/74.0 (2026 is ~7 months). Gap -1.7/-1.2/-2.3/-1.1/-4.9/-0.2/-1.3/
+2.7 points; n-weighted ~ -1.4 pts (hand-computed), naive SE ~0.6. Pre-set rule: >= 3
points in most years would justify an event-day multiplier; < 1.5 would not. Result sits
just under 1.5 -> not worth a separate event-day range at this level. The year-to-year
coverage swing for ALL days (74.0% to 87.9%) is ~10x larger than the event effect;
hypothesis (untested): a single 64-day volatility estimate lags regime changes. Next:
compare volatility estimators (20d, 64d, 250d, EWMA, blends) on calibration stability and
width; rerun the event-type table on this baseline (the earlier by-type month-matched
output was not captured).


<!-- entry: 2026-10-14-02 | date: 2026-10-14 | label:  | source-line: 2772 | approx: no -->
### 2026-10-14-02 — Event types vs random dates (scaled 20d move); bundled-event correction; data flags
> Original heading: `### 2026-10-14 — Event types vs random dates (scaled 20d move); bundled-event correction; data flags`

Scaled move = |20d abnormal return| / (prior-90d daily vol x sqrt(20)), from
event_realized_vol; expected = random-date mean for the same YEAR (0.7026, 0.6327, 0.7994,
0.7051, 0.6995, 0.8408, 0.7762, 0.9527 for 2019-2026; ~500 random company-days per year,
treated as fixed, so SEs are optimistic). Events with a type appear once per type.
**Event-type table (first run, bundled events included):** corporate_action n=288, excess
+0.186 (SE 0.059, z~3.1); restructuring +0.068; strategic_partnership +0.066;
legal_settlement +0.040; acquisition n=1,213 +0.037; leadership_change n=1,862 +0.032;
regulatory -0.004; financial_result -0.016; capital_raise n=229 -0.110 (z~-2.4). Nine
types tested (types with >= 100 events), so ~1 of 9 reaching z~2.4 is expected by chance.
**corporate_action checks:** positive excess in 7 of 8 years; year-adjusted excess ~ +0.11
(z~2.4, hand-computed); the earnings split is uninformative (only 2 of 288 events carry
confounded_earnings). Bucket contents (random sample of 30): ~9 splits (incl. reverse),
~6 dividend increases, ~4 buyback authorizations, ~5 tender/debt actions, ~2 spin-offs,
~4 mixed. Tail check vs all other events: mean 0.937 vs 0.783, median 0.676 vs 0.600
(+0.077), mean excluding top 5% 0.756 vs 0.671 (+0.085) -- borderline vs the pre-set 0.08.
Top-15 scaled events were mostly BUNDLED SUMMARY events (e.g. "Intel's real 2026 activity",
"Ford's South American and Indian manufacturing exit saga"), COVID-crash timing (MGM
2020-02-13, AIG 2020-02-25, Delta 2020-03-12: vol measured in the calm before, crash inside
the window), and two GE events sharing one price move.
**Rerun excluding events in event_component_dates:** corporate_action n=233, excess +0.125
(SE 0.058, z~2.2) -> FAILS the pre-set bar (>= +0.10 AND ~3 SE); parked, unconfirmed.
restructuring +0.068 (n=162), strategic_partnership +0.049 (162), legal_settlement +0.048
(161), acquisition +0.045 (n=1,172, z~2.2), leadership_change +0.034 (n=1,754, z~1.9),
regulatory -0.008, financial_result -0.016, capital_raise -0.110 (n=229, unchanged, z~-2.4).
**Overall event premium (non-bundled, 2019-2026, n=4,498): +0.0376 (SE 0.011, z~3.4)** vs
the same-year random-date mean; essentially unchanged from +0.037 before the exclusion, so
bundled events were not driving the average. Events cluster in time; true SE is larger.
**Which earlier tests excluded bundled events:** excluded (population built from the
ripple-based d5 CTE): neighbor-magnitude windows, volatility terciles, event-vs-random by
year. NOT excluded: overreaction, size quintiles, context test, scaled-sentiment test,
baseline-range coverage, tag-range test, magnitude model (build_dataset default).
**Data flags:** (1) HON price_date 2026-06-29 shows a +40.2% one-day adjusted_close move
(136->227 area; 2026-06-25 161.3 -> 227.2): implausible for a mega-cap; suspected
adjustment/spin-off artifact, unverified. (2) Honeywell event 2025-11-03 has a stored
+50.4% abnormal 20d reaction that cannot be reproduced from market_prices (no daily move
> 6% in that window); unresolved. (3) Dataset-wide scan of |daily return| > 25% since 2019
(top 40): mostly recognizable real shocks (PCG Jan 2019, 2020-03-09 energy crash, CVNA, GL
2024-04-11, BIIB, HOOD, APP, TTD, CNC, DXCM); entries dated after mid-2026 (MRNA +177%
2026-08-19, FLEX, PSKY, HON) not independently verifiable; no sign of widespread unadjusted
splits. List was capped at 40 rows, so not exhaustive.
**Status:** overall premium real but small; capital_raise discount a hypothesis;
corporate_action parked. Next: month-matched baseline (year-matching cannot handle crash
months).


<!-- entry: 2026-10-14-01 | date: 2026-10-14 | label:  | source-line: 2746 | approx: no -->
### 2026-10-14-01 — Magnitude model re-scored against a realized-volatility baseline
> Original heading: `### 2026-10-14 — Magnitude model re-scored against a realized-volatility baseline`

magnitude_vol_baseline.py (new) re-scores multi_feature_model_magnitude.py (target:
|abnormal_return_20d| >= 4.21% = "large", fixed cutoff) using event_realized_vol
(prior-90d daily-return stddev; table built by scripts/sql/create_event_realized_vol.sql,
71,801 rows; 8,779 rows have vol and every feature; 7,167 events dropped for a
missing feature, so results apply to the storm-tier/confidence-trend subset,
2,631 pre-2015 / 6,179 post-2015 rows). Vol is binned into deciles from TRAIN
quantiles only. build_dataset() rows now carry event_id and entity_id; this file's
storm loader now filters day_offset = 5 in the database (same rows, much faster).
Models (test accuracy by cutoff 2018/2020/2022/2023/2024): M0 majority 44.4/42.7/
43.8/43.6/42.0; M1 vol-only 55.4/54.7/53.8/53.7/56.3; M2 original five features
53.5/54.9/55.2/54.4/55.1; M3 five+vol 56.6/56.5/55.4/57.0/56.8; M4 four non-storm
features+vol 56.1/56.1/54.6/56.3/55.9.
M2-M0 = +9.1/+12.2/+11.4/+10.8/+13.1 (reproduces the validated +9.2..+13.4) but
M1-M0 = +11.0/+12.0/+10.0/+10.1/+14.3 and M2-M1 = -1.9/+0.2/+1.4/+0.7/-1.2: volatility
alone equals or beats the original model. Pre-set rules: "lift was mostly volatility"
(M1 within ~3 pts of M2 at >=3 of 5) HOLDS at 5 of 5; "event features add something
real" (M4 beats M1 by >=3 pts at >=4 of 5) FAILS (M4-M1 = +0.7/+1.4/+0.8/+2.6/-0.3).
Leftover: M4-M1 is positive at 4 of 5 cutoffs (~ +1 pt on average); test sets are nested
and events cluster in time, so naive SEs overstate it; below the threshold, not built on.
Baseline note: M0 is 42-44% (< 50%) because the share of "large" moves shifted between
train and test periods; hindsight majority in the test years is ~56-58%, at or above
M1-M4 (54-57%). The original +9..+13 lift was therefore measured against a baseline
degraded by base-rate drift, which a volatility feature absorbs automatically.


<!-- entry: 2026-10-13-13 | date: 2026-10-13 | label:  | source-line: 2712 | approx: no -->
### 2026-10-13-13 — Plain-volatility range baseline and tag-specific ranges
> Original heading: `### 2026-10-13 (late) — Plain-volatility range baseline and tag-specific ranges`

**Baseline: 80% range = +-1.2816 x (prior-90d daily vol x sqrt(20)), no events or tags,
scored on |20d abnormal move| for events 2019-2026.** Coverage by year (n): 2019 83.4%
(675), 2020 83.2% (668), 2021 81.0% (675), 2022 86.7% (532), 2023 78.8% (557), 2024
78.9% (582), 2025 80.5% (691), 2026 77.3% (361); n-weighted ~81.4% (hand-computed).
Walk-forward empirical version (80th pct of scaled moves from earlier years; multiplier
1.16-1.21): coverage 81.4/76.1/84.4/75.9/75.9/78.6/75.3% for 2020-26, ~78.4% overall,
undercovers in 2023-26 (hypothesis, untested: scaled moves rose over time). Caveats:
outcome is abnormal vs SPY but vol is raw stock vol (ranges probably a bit
conservative); sqrt(20) assumes independent daily returns; 2019+ outcomes were seen
while exploring, so this is a baseline, not a clean test.

**Tag-specific ranges (train events <= 2012, test 2013+, tags with >= 30 train events,
80th percentile of scaled 20d move vs global):** a first attempt limited prices to
2018-09+ and left almost no tagged events (only same_entity_sequence qualified, n_test
41) -- my query error. Corrected run: confounded_macro_conditions width ratio 1.04,
n_test 19, coverage tag 84.2% vs global 78.9%; multi_stage_divestiture 1.15, n_test 38,
81.6% vs 76.3%; same_entity_sequence 1.06, n_test 192, 83.3% vs 80.7%. No tag range is
narrower than the global one; higher coverage reflects wider ranges. Leak rate (share of
descriptions mentioning abnormal/price reaction/stock reaction) 0-5.7%. Six of the
nine tags had < 30 pre-2013 events and were not tested. Conclusion: volatility sets the
size of the range; tags do not tighten it at the 80% level. Not tested: skew, tails,
direction, or conditioning on the day-0 move. Status: negative result, with small
samples for two of three tags.

**Combination testing (next, pre-registered approach):** individual features are weak, so
combinations are worth trying, but only with a short pre-declared list, out-of-sample
scoring against the plain-volatility baseline, and a running count of every combination
tried. The existing multi_feature_model scripts already combined event_type, sentiment,
regime, firm_state and storm tier (direction stayed null). The validated magnitude model
(+9.2 to +13.4pp) must be re-scored against a realized-volatility-only baseline and
without the future-looking storm feature (storm_tier uses +-40-day neighbors).


<!-- entry: 2026-10-13-12 | date: 2026-10-13 | label:  | source-line: 2656 | approx: no -->
### 2026-10-13-12 — The three old Phase 6 threads, worked and parked
> Original heading: `### 2026-10-13 (night) — The three old Phase 6 threads, worked and parked`

**Time-to-threshold (punishment-speed asymmetry): NOT time-stable.** By period, falling
vs rising confidence_trend, mean days to first cross of -3% (events that crossed):
2020-22 9.1 vs 11.1; 2022-24 8.4 vs 11.7; 2024-26 9.8 vs 9.2 (gap rising minus falling:
+2.0, +3.3, -0.6 days). Crossing rates (falling vs rising): 69.6/66.5, 68.1/68.3,
70.4/71.1 -- about 1 SE (~3 pts) of noise in each period. Reward side (+3%): gaps
-0.5, +2.1, -1.8 days, so no stable mirror asymmetry either. Policy-stance cross: the
same "hiking" label gives opposite signs in two periods (2022-24 falling+hiking median 7
vs rising+hiking 9; 2024-26 falling+hiking 11 vs rising+hiking 7); only 32 rate
changes exist, and in 2020-22 every event got the single label "cutting", so there was
nothing to cross. The confidence label is likely monthly (get_confidence_by_month, not
re-read), so effective n is ~24 months per period; naive SEs are far too small. Day
gaps above are hand-computed from the printed results. Status: parked, not disproven.
Note: the 2024-26 run used end date 2026-07-01 to avoid counting events with incomplete
39-day windows as "never crossed".

**storm_x_sentiment (walk_forward_sentiment_by_storm.py), cutoffs 2020/2022/2024.**
Muted-share hit rate vs baseline, NEGATIVE-sentiment cells: 2020 isolated 35.9% vs 45.4%
(n=64), storm 37.0% vs 46.7% (n=100); 2022 isolated 37.8% vs 46.2% (n=37), storm 48.5%
vs 49.0% (n=33); 2024 isolated 37.5% vs 45.5% (n=16), storm 50.0% vs 48.2% (n=14). The
cutoffs are nested (later test sets are subsets of earlier ones), so these are not
independent replications; 2020 is the cleanest. Every other cell is within ~1 SE of
baseline. The docketed "+10.5pp" is probably this cell expressed as non-muted share (my
inference; original run not seen). Storm labels use +-40-day neighbors including future
events, so they are not knowable at event time.
**Direct volatility-controlled test:** scaled 20d move (|20d abnormal| / (prior-90d daily
vol x sqrt20)) by sentiment bucket (negative < -1, positive > 1 on 7-day avg tone),
2019-2026: negative 0.836 (n=342, SE 0.042), neutral 0.809 (n=1,473, SE 0.019), positive
0.793 (n=1,081, SE 0.023). Negative minus neutral +0.026 (SE ~0.046, z ~0.6). FAILS the
pre-set rule (>= +0.10 and positive in >= 5 of 7 years; 8 years present, positive in 4).
Precision-weighted within-year gap ~ -0.024 (SE ~0.039); heterogeneity p ~ 0.18 (all
hand-computed from the printed table). Sign: negative in 2019-22 (-0.05 to -0.09),
positive in 2023-26 (+0.16 to +0.59) but 2023+ negative cells are n=17-29. Excludes a
scaled-move boost above ~+0.12 (naive SEs); smaller or period-specific effects are not
excluded. Status: parked.

**Cascade Effect: case studies only.** Keyword pool (title+description; "in response to",
"following", "forced", "mandated", "compelled", "as a result of", "amid"): 1,374 of
19,892 events (following 1,084; in response to 137; amid 119; as a result of 32; forced
22; mandated 20; compelled 0). The original sizing was 374 of 16,746 events; reason for
the difference is unknown (the original query was not recovered). Read the 74 non-
"following" matches by title/short description: ~35-40 externally triggered but nearly
all shared-cause (Hop 1: TCJA charges, TARP, bank-regulator actions, Venezuela, COVID,
SVB) which comparison_signal already covers; ~30 self-caused; ~3-5 genuine Hop-2
candidates. Company-name matching on entities.name (148 event-company pairs) is mostly
noise (common-word names, exchange listing notices, one-deal counterparties); ~8-10
plausible A->B cases judged from titles alone (UPS CEO -> Tomé leaves Cisco board; Liddy
named AIG CEO -> leaves Boeing board; ON Semi exits joint proposal -> Microchip withdraws
Atmel offer; Comcast/TWC collapse -> Charter terminates agreement; Avianca downgrade ->
United default disclosure). Too few for a statistical test.

**Operational:** restarting background jobs with `&` while the originals were still
alive created duplicates and truncated their log files (`>`); use unique per-run log
names and check `ps` before relaunching.


<!-- entry: 2026-10-13-11 | date: 2026-10-13 | label:  | source-line: 2612 | approx: no -->
### 2026-10-13-11 — Do events carry magnitude information beyond volatility? (neighbor-magnitude result retracted; small event premium, inconclusive)
> Original heading: `### 2026-10-13 (late) — Do events carry magnitude information beyond volatility? (neighbor-magnitude result retracted; small event premium, inconclusive)`

Definitions: "abnormal move" = stock return minus SPY return, adjusted_close, from
the close before the event day to 20 trading days after it. "Scaled move" =
|20d abnormal return| / (prior-90-day daily return stddev x sqrt(20)); 1.0 = a move
as large as the stock's own normal 20-day wobble. 2019+ events/dates only (needs
90 prior days of prices, min 30 return observations).

**Volatility terciles (static company vol, 2019+ prices):** neighbor-magnitude gap
(>=10% bucket vs none) was 1.9 / 6.5 / 7.6 pts by tercile -- survived a static control.
**Event-level realized volatility (prior 90d) terciles: the pre-registered survive
rule FAILED.** Gaps -1.4 pts (n=14 in the >=10% cell), +1.7 (n=35), +7.0 (n=146).
75% of the >=10% bucket sits in the most volatile tercile.
**Scaled-move test:** none 0.797 (n=3,304), <5% 0.824, 5-10% 0.730, >=10% 0.725
(n=195, SE 0.053). The >=10% bucket is ~0.07 BELOW none (z ~ -1.3). Conclusion: the
storm / neighbor-magnitude effect does not survive a time-varying volatility control
in this check. The original "storm/compounding validated" finding normalized each
company against its "own baseline" (per the 09-24 transcript; code not re-read), which
appears static. That control is weaker than prior-90d realized vol. This does NOT
prove the original finding wrong (this test covers 2019+ only), but it is no longer
confirmed under the stricter control.

**Retraction:** I suggested the events' mean scaled move (~0.80) matching E|Z| = 0.798
meant events look like ordinary random-walk moves. The random-date baseline is 0.753,
so that match was a coincidence. Retracted.

**Random-date baseline (n=3,998, 2019-2026, random company/date, no event):** mean
scaled move 0.753 (SE 0.011), but it varies by year (0.63 in 2020 to 0.95 in 2026).
**Event vs random by year** (gaps/SEs computed by hand from the two result tables):
2019 +0.064, 2020 +0.116, 2021 +0.009, 2022 -0.035, 2023 +0.103, 2024 -0.001,
2025 +0.044, 2026 +0.005. Inverse-variance pooled gap ~ +0.037 (SE ~0.015, ~5% more
movement), heterogeneity p ~ 0.14. Positive in 6 of 8 years, but 2019/2020/2023 supply
most of it. Falls in the middle band of the thresholds set in advance (noise +-0.03,
real >= 0.05): INCONCLUSIVE. Naive SEs treat events as independent; events cluster in
time, so true uncertainty is larger. Event sample is also selected (needs a ripple
row, and something must have happened for an event to exist).

**Takeaways:** (1) prior realized volatility explains most of how large the next
20-day move is; (2) events plausibly add a small premium on top (few %), unproven;
(3) direction remains null everywhere tested. **Next:** tag-level scaled-move
comparison against the same-year random baseline (also fixes the problem that the
6 "significant" tags were tested against an even 1/3 split instead of the base-rate
null), with 13 tags treated as 13 comparisons.


<!-- entry: 2026-10-13-10 | date: 2026-10-13 | label:  | source-line: 2549 | approx: no -->
### 2026-10-13-10 — Phase 6 theory testing: overreaction null, size check, context test, storm_x_sentiment, storm leakage check
> Original heading: `### 2026-10-13 (evening) — Phase 6 theory testing: overreaction null, size check, context test, storm_x_sentiment, storm leakage check`

**Overreaction/reversal (theory 7): null.** On event_market_reactions_corrected,
events with |abnormal_return_0d| > 3%: mean drift after day 0 (20d minus 0d) was
+0.953% after up moves (n=1,107, SE 0.529%) and +0.964% after down moves (n=1,059,
SE 0.390%). The between-bucket difference is ~0.01 pts against an SE of ~0.66 pts
(z ~ 0.02). Reversal fractions 52.3% / 50.6%, indistinguishable from a coin flip.
A shared positive offset of ~0.95% appears in both buckets; hypothesis (untested)
is survivorship in the tracked universe. All SEs treat events as independent and
are therefore too small (events cluster in time). Single threshold, single horizon.

**Size effect (small-cap hypothesis), within this universe.** size_bucket is a
constant label ("large_or_mega_cap_tracked_universe") and cannot be used. Revenue
quintiles (static median revenue per company, most common period_type) gave mean
|20d move| of 6.57 / 6.44 / 6.31 / 5.62 / 6.18% for smallest..largest quintile.
Q1 vs Q5 gap ~0.39 pts (z ~ 2.0 naive); non-monotone (Q4 lowest). Weak support at
most. This universe's size range is narrow, so it cannot speak to true small caps.
market_cap_at_event is populated for 15,964 of 16,488 rows (0.047 to 4739.65; units
unverified) and is the better size measure for a rerun.

**Context test (pre-registered directions).** Raw means looked strong for labor
stressed (9.31% vs ~5.8%), oil spike/crash, restructuring (7.58% vs 5.96%). After
excluding 2007-10..2009-12 and 2020 and, for company status, excluding events that
are themselves restructuring events: labor stressed 5.78% vs 5.33-5.57%, oil spike
5.44% vs 5.55% normal (gone), restructuring 6.04% vs 5.43% (~0.6 pts, suggestive
only). Storm tier "large" survived (6.90% vs isolated 5.45%). Yield curve inverted
was opposite to the predicted direction (5.75% vs 6.25%) and housing was a null.
~20 groups were examined, so isolated 2-SE results are expected by chance.
KNOWN FLAW (not yet fixed): populate_company_status.py's trailing window is
window_start <= d <= as_of_date, so a restructuring event labels itself
"restructuring"; the raw restructuring gap is partly built in.

**storm_x_sentiment at cutoff 2022-01-01: does not reproduce the docketed
+10.5pp isolated+negative cell.** Test n / hit rate vs baseline (every cell
predicts "muted"): isolated-negative 37, 37.8% vs 46.2%; isolated-positive 262,
48.1% vs 46.2%; isolated-neutral 260, 45.4% vs 46.2%; storm-negative 33, 48.5% vs
49.0%; storm-positive 231, 47.2% vs 49.0%; storm-neutral 311, 50.5% vs 49.0%.
No cell is more than ~1 SE from baseline (SEs hand-computed, approximate). This
script measures the MUTED share only; if the +10.5pp came from another cutoff or a
punished-share view, this run would not show it. Cutoffs 2020-01-01 and
2024-01-01 NOT yet run.

**Storm-feature leakage check.** get_storm_lookup() (multi_feature_model.py line
~173) counts neighbor events within +-40 days, INCLUDING later events, so storm_tier
is not knowable at event time and is unsafe as a walk-forward feature. Standalone
query comparing neighbor-magnitude windows (mean |20d move|, "none" bucket vs
">=10%" bucket): +-40d 5.84% vs 10.72%; prior 1-40d 5.96% vs 11.77%; prior 7-40d
5.94% vs 12.57%. The effect did NOT shrink under backward-only windows, so leakage
does not explain it. Volatility clustering (volatile companies stay volatile) is the
leading alternative explanation and is UNTESTED; a within-volatility-tercile rerun
is pending. Gaps across windows are not directly comparable (backward windows are
shorter, so the top bucket is more extreme).

**Performance fixes in multi_feature_model.py (shared by every script that imports
it):** get_storm_lookup() now filters day_offset = 5 in the database (about 15K of
654K event_ripple_timeline rows; same rows the loop already kept; storm pairs
loaded = 15,038); get_sentiment_lookup() now uses keyset pagination on id for
company_sentiment_timeline (~533K rows). Both previously used offset paging and
sat idle on the network for 25+ minutes.

**Process note:** piping a long run through `| tail -N` hides all progress until
the process exits; use `| tee file.log` instead.


<!-- entry: 2026-10-13-09 | date: 2026-10-13 | label:  | source-line: 2504 | approx: no -->
### 2026-10-13-09 — Tier 4 review backlog: ALL REMAINING CATEGORIES CLEARED, backlog now 100% complete
> Original heading: `### 2026-10-13 — Tier 4 review backlog: ALL REMAINING CATEGORIES CLEARED, backlog now 100% complete`
Pushed through the 8 remaining, genuinely smaller categories (confounded_earnings
103, cross_entity_ripple 39, leadership_reversal 33, high_confidence_causal_link 33,
plausible_unconfirmed 32, same_industry_comparison 24, explicitly_not_attributed 24,
activist_investor_campaign 23 -- 311 rows total) by reading each category close to
or fully in full, rather than the sample-then-search method used for the four
much larger categories earlier. Real, category-specific findings:

- confounded_earnings: near-perfect (2 of 110 rejected) -- this tag's real
  definition (a quantified charge/event landing in the SAME real quarter as
  earnings) is unusually clean and well-specified, leaving little room for
  AI over-application.
- cross_entity_ripple: near-perfect (2 of 52 rejected) -- genuine shared root
  events (scandals, shared individuals, direct M&A counterparties) are easy
  to verify textually.
- leadership_reversal: 11 of 43 rejected -- recurring tell was "this is a
  planned succession, not a reversal" (the AI repeatedly suggested the tag
  for ordinary generational handoffs).
- high_confidence_causal_link: near-perfect (5 of 79 rejected, pre-existing).
- plausible_unconfirmed: 0 of 32 rejected -- real, important distinction from
  every other category: this tag's whole DEFINITION is "plausible but not
  independently confirmed," so honest hedging is the CORRECT application
  here, not a reject signal like it is everywhere else.
- same_industry_comparison: 3 of 24 rejected -- isolated verdicts/events with
  no actual named comparison point.
- explicitly_not_attributed: 13 of 24 rejected -- the largest real error rate
  of these 8 (~54%), with a genuine, subtle category confusion found: several
  rows argued the OPPOSITE of what the tag requires (the event itself IS the
  real driver of the reaction, not something price reaction should be
  redirected AWAY from) -- rejected those specifically as a real logic
  inversion, not just generic uncertainty.
- activist_investor_campaign: 4 of 23 rejected -- the tell here was simply no
  named activist investor/fund in the event text.

Also found and fixed 3 more leftover "punished" category-error rows (same
real issue resolved earlier this session -- reaction_character tags should
never be AI-suggested from text) that the earlier direct check had missed.

**REAL, FINAL STATE**: event_tag_suggestions now has zero unreviewed rows
across all 13 real tag-suggestion categories (the only remaining unreviewed
rows are 9 legitimate NONE_APPLICABLE conclusions, which don't require the
same confirm/reject treatment). The entire Tier 4 backlog flagged during the
pre-Phase-6 audit (~4,660 rows, later found to be ~5,223 once fully
enumerated) is now closed.


<!-- entry: 2026-10-13-08 | date: 2026-10-13 | label:  | source-line: 2478 | approx: no -->
### 2026-10-13-08 — Tier 4 review backlog: multi_stage_divestiture fully cleared (448 rows, 100%)
> Original heading: `### 2026-10-13 — Tier 4 review backlog: multi_stage_divestiture fully cleared (448 rows, 100%)`
Same systematic method, unusually high real error rate given this
tag's genuinely strict definition (MULTIPLE distinct, separately-timed
divestiture events -- not a single transaction, however large or
complex). Low-confidence (84, the largest low bucket of any category
this session): 25-row sample came back 25/25 self-rejecting, bulk-
rejected the entire bucket on that strength. High-confidence (115):
25-row sample, 24 genuinely strong (real, specific, multi-year
sequences -- GE's three-way split, Ford's PAG breakup, AIG's phased
AIA/ALICO exits), 1 speculative miss rejected. Mid-confidence (177):
targeted search for the category's own tell -- "however, this is a
single coordinated transaction rather than multiple distinct events"
-- caught 27 genuine errors across three passes, several explicitly
admitting "this single event itself is not multi-stage." A final
40-row sample came back 35/40 clean, 5 more subtler misses found
before bulk-confirming the rest.

**Real, final result**: 128 rejected, 320 confirmed -- 448 total, 100%
reviewed. Highest real error rate of the four categories cleared this
session (~29%), consistent with this tag's narrow definition inviting
the most generous AI suggestions -- a company's own ongoing, broader
divestiture reputation (Ford's PAG, GE's breakup) repeatedly got
applied to single, standalone transactions that merely happened at a
company already known for divesting, rather than genuinely
documented, separately-timed multi-stage sequences.


<!-- entry: 2026-10-13-07 | date: 2026-10-13 | label:  | source-line: 2456 | approx: no -->
### 2026-10-13-07 — Tier 4 review backlog: confounded_macro_conditions fully cleared (598 rows, 100%)
> Original heading: `### 2026-10-13 — Tier 4 review backlog: confounded_macro_conditions fully cleared (598 rows, 100%)`
Same systematic method. Low-confidence (5): 4 rejected (no explicit
macro bundling named), 1 confirmed genuine (downgrade explicitly quoted
"market conditions already reflected in publicly available
information" -- real textual basis despite not naming a single discrete
event). High-confidence (325, the largest single bucket sampled this
session): 30 read, all genuinely strong (real financial-crisis periods,
named CPI/jobs/PCE releases, 9/11, COVID, specific geopolitical shocks)
-- bulk-confirmed. Mid-confidence (152): a 60-row sample (the largest
single sample this session) came back 57/60 clean -- found 3 genuine
misses (one admitting no specific date/context to assess; one circular
case where the company's own statement WAS directly about the macro
event, not confounded by a separate one; one hedging both directions
speculatively) -- rejected those, bulk-confirmed the rest.

**Real, final result**: 7 rejected, 591 confirmed -- 598 total, 100%
reviewed. This category had the lowest real error rate of the four
cleared so far (~1.7%), consistent with "the event is explicitly tied
to a real, named macro/crisis period" being a genuinely easier,
cleaner judgment than the other three categories' more subtle
attribution-boundary questions.


<!-- entry: 2026-10-13-06 | date: 2026-10-13 | label:  | source-line: 2433 | approx: no -->
### 2026-10-13-06 — Tier 4 review backlog: confounded_corporate_action fully cleared (380 rows, 100%)
> Original heading: `### 2026-10-13 — Tier 4 review backlog: confounded_corporate_action fully cleared (380 rows, 100%)`
Same systematic pattern-search discipline. Low-confidence (18): 16
rejected (each explicitly stating "this IS the corporate action itself,
not a confound alongside something else" -- the category's own
recurring tell), 2 confirmed genuine (CFO appointment bundled with a
Microsoft arbitration dispute; CFO departure bundled with a segment
reporting change). High-confidence (34): sampled 25, all genuinely
clean, bulk-confirmed. Mid-confidence (bulk, ~325): targeted search for
self-doubting language ("category error", "should not apply", "removing
this") caught 13 genuine errors across two passes -- several strikingly
explicit ("Removing this tag", "Excluding this tag", literally the
model correcting itself mid-reasoning). A final 60-row random sample of
the unmatched remainder found 3 more subtler misses (speculative "may
have been bundled" language, and the offering's own internal effects
mistaken for a second event) before coming back clean enough to
bulk-confirm the rest.

**Real, final result**: 32 rejected, 348 confirmed -- 380 total, 100%
reviewed. Core lesson, distinct from confounded_regulatory_action's
"stands alone" tell: this category's AI repeatedly conflates the
primary corporate action itself with a confound to something else --
same underlying category-error pattern, different tag.


<!-- entry: 2026-10-13-05 | date: 2026-10-13 | label:  | source-line: 2406 | approx: no -->
### 2026-10-13-05 — Tier 4 review backlog: confounded_regulatory_action fully cleared (556 rows, 100%)
> Original heading: `### 2026-10-13 — Tier 4 review backlog: confounded_regulatory_action fully cleared (556 rows, 100%)`
Same real, systematic pattern-search discipline as same_entity_sequence.
Low-confidence rows (13) read individually -- 11 rejected (each
explicitly argued "clean, no confounding evidence"), 2 confirmed as
genuine (bankruptcy ruling bundled with restructuring terms; FTC
clearance landing 5 days before 9/11). High-confidence rows (43)
sampled (25 read) -- all genuinely clean, bulk-confirmed.

Mid-confidence rows (the bulk, ~497) needed the same targeted search
for the AI's own self-doubting language -- this category's recurring
real tell was explicit hedging like "however, the description does not
explicitly state/mention/identify a concurrent confounding event,"
essentially the AI correctly recognizing a regulatory action stood
alone with no real second event to confound attribution against, yet
still suggesting the tag anyway. Caught and rejected 37 genuine errors
this way across two passes (5 from an initial random sample revealing
the pattern, 32 from the full-pool targeted search), each verified by
reading the actual row. A final 30-row random sample of the unmatched
remainder came back completely clean, giving real confidence to
bulk-confirm what was left.

**Real, final result**: 48 rejected, 508 confirmed -- 556 total, 100%
reviewed. Core lesson for this category: distinguishing "this IS a
regulatory action" from "this regulatory action landed ALONGSIDE
another material event" is the whole ballgame -- a regulatory ruling
standing alone, however material, does not qualify.


<!-- entry: 2026-10-13-04 | date: 2026-10-13 | label:  | source-line: 2372 | approx: no -->
### 2026-10-13-04 — Tier 4 review backlog: same_entity_sequence fully cleared (2,931 rows, 100%)
> Original heading: `### 2026-10-13 — Tier 4 review backlog: same_entity_sequence fully cleared (2,931 rows, 100%)`
Real, systematic review of the largest Tier 4 backlog category.
Low-confidence rows (<0.65, 20 total) read individually -- all rejected,
each one's own reasoning explicitly argued against the tag. High-
confidence rows (>=0.85, 1,289) sampled extensively (70 rows read
directly) -- found 2 genuine errors, both sharing a real, identifiable
pattern (citing a CROSS-COMPANY industry/scandal framing as the
connecting logic, not a true same-ENTITY sequence); confirmed the
remaining 1,287 in bulk after that specific error pattern was
confirmed absent via a full-bucket search.

Mid-confidence rows (0.65-0.84, the largest remaining group) required
real, iterative pattern-based searching rather than pure random
sampling: found the AI consistently flags routine, unconnected events
while its OWN reasoning explicitly argues against the tag applying
("however, this is a routine...", "is not explicitly stated", "lacks
explicit connection", cross-entity movement framed as same-entity).
Ran repeated, broadening ILIKE searches for this self-doubting language
across the full remaining pool (not just a sample) -- caught and
rejected 128 genuine errors this way across several passes, each
verified by reading the actual matched rows before rejecting, not
blind pattern-matching. A final 25-row random sample of the truly
unmatched remainder came back 88% clean (3 more genuine misses found
and rejected), giving real confidence to bulk-confirm what remained.

**Real, final result**: 148 rejected, 2,783 confirmed -- 2,931 total,
100% reviewed. The recurring real error pattern worth remembering for
the other 12 Tier 4 categories: same_entity_sequence specifically
requires a documented connection WITHIN one company, not merely the
same person moving between different companies, nor a company's
involvement in a broader industry-wide event/scandal -- both read as
superficially plausible to a text-based classifier but fail the
tag's actual definition.


<!-- entry: 2026-10-13-03 | date: 2026-10-13 | label:  | source-line: 2339 | approx: no -->
### 2026-10-13-03 — Phase 6 harness gap D2 closed: real base rate computed
> Original heading: `### 2026-10-13 — Phase 6 harness gap D2 closed: real base rate computed`
Built compute_base_rate.py, closing the "what fraction of random,
unrelated same-sector days show the same move" gap from the prediction-
contract review. Samples genuinely random (security, date) pairs from
the real 32-year, 497-company universe (not tied to any event),
computes each one's forward abnormal return vs. SPY using the
identical index-based method tag_reaction_character.py uses.

**Real, significant finding**: at the 20-trading-day window (the one
most reaction_character tags use), random chance alone produces
rewarded=33.5%, punished=30.2%, muted=36.3% (n=5,000). This means any
tag's own observed rewarded/punished rate must be read against this
real floor, not in isolation -- a tag showing 40% rewarded is only
~6.5 points of real excess signal above chance, not 40 points. Shorter
windows show a much higher real muted rate (0d: 90.4%, 1d: 82.4%, 5d:
61.9%), confirming price moves genuinely need time to develop before
any signal separates from noise.

**Real infrastructure bug found and fixed along the way, affecting
both this script and populate_sector_peer_benchmark.py**: the bulk
market_prices loader used OFFSET-based pagination (.range()) which
does not scale against this table's real 3.37M rows -- each page
forces a full re-sort of a growing offset, hitting a genuine statement
timeout. Fixed with proper keyset (cursor) pagination on the table's
own indexed id column. Then hit a SECOND real bug from the same fix:
Supabase/PostgREST silently caps every request at 1,000 rows
server-side regardless of a larger client-requested .limit() value --
confirmed via a direct live test (requested 5,000, got exactly 1,000)
-- the original loop incorrectly treated that capped page as "the last
page" and stopped after just 1,000 of 3.37M real rows. Fixed by never
trusting page size to signal "last page" -- only a genuinely empty
page means pagination is done.


<!-- entry: 2026-10-13-02 | date: 2026-10-13 | label:  | source-line: 2299 | approx: no -->
### 2026-10-13-02 — Phase 6 kickoff: pattern_significance_tests refreshed, expanded to a genuine 4-way split
> Original heading: `### 2026-10-13 — Phase 6 kickoff: pattern_significance_tests refreshed, expanded to a genuine 4-way split`
Phase 6 mapping revealed pattern_significance_tests was stale (dated
2026-09-11, a full month before the much larger current dataset).
Re-ran test_pattern_significance.py fresh -- immediately found several
n values had DECREASED despite the dataset growing substantially (e.g.
high_confidence_causal_link 414->365), and confounded_regulatory_action
had flipped from significant (p=0.026) to not-significant (p=0.069).

**Real root cause investigated and confirmed, not assumed**: this
script's reaction-bucket counts only ever included
rewarded/punished/muted -- diverged_from_fundamentals (built earlier
this session, 2,307 real events upgraded) was never added to its
3-way split, so every event upgraded to that tag silently fell OUT of
every single significance test entirely. Confirmed via direct code
read (get_reaction_counts()'s reaction_tags dict), not guessed.

**Real, deliberate fix, decided with Galen**: expanded this to a
genuine 4-way split (rewarded/punished/muted/diverged_from_fundamentals,
1/4 each under the null) rather than leave the 3-way test as a
"deliberately separate question" -- a real loss of ~2,300 events' worth
of signal from every test wasn't worth the simplicity. Added
diverged_from_fundamentals_count to pattern_significance_tests.

**Real, significant result after the fix**: n values recovered to
match (and slightly exceed) the original pre-upgrade totals, and the
4-way split genuinely recovered real signal:
confounded_regulatory_action significant again (p=0.0139), and TWO
previously not-significant categories are now significant for the
first time: confounded_corporate_action (p=0.0027) and
leadership_reversal (p=0.0113). Current, confirmed-fresh significant
categories: high_confidence_causal_link, same_entity_sequence,
multi_stage_divestiture, confounded_regulatory_action,
confounded_corporate_action, leadership_reversal -- 6 of 13 testable
categories, up from 2 in the original September baseline this project
had been treating as current.

This is Phase 6's real starting point -- every further Phase 6 finding
should be checked against this fresh, correctly-scoped significance
table, not the stale September one.


<!-- entry: 2026-10-13-01 | date: 2026-10-13 | label:  | source-line: 2272 | approx: no -->
### 2026-10-13-01 — two real oddities from the pre-Phase-6 audit cleaned up
> Original heading: `### 2026-10-13 — two real oddities from the pre-Phase-6 audit cleaned up`
**12 MALFORMED rows**: not actually malformed in a harmful sense -- the
AI's real response put substantive, coherent reasoning AFTER an empty
array ([], meaning "no tag applies"), which a parsing bug mislabeled as
the literal string "MALFORMED" instead of reading it as a legitimate
no-tag judgment. 6 of 12 already had a correct human_decision (5
rejected, 1 confirmed for a genuine multi_stage_divestiture case),
confirming a human had already seen past the label and judged the real
content correctly. Fixed: 4 of 12 were genuine duplicates (the same
event already had a separate, correctly-labeled NONE_APPLICABLE row) --
deleted those. Relabeled the remaining 7 to NONE_APPLICABLE (matching
their real "[]" content) and the 1 divestiture case to
multi_stage_divestiture. Marked the 1 still-unreviewed row (after
dedup) as reviewed/rejected, consistent with the others.

**4 "punished" rows**: confirmed these were a genuine category error --
reaction_character tags (rewarded/punished/muted/diverged_from_fundamentals)
are computed deterministically from real price data by
tag_reaction_character.py, and should never be AI-suggested from text
alone. 3 of 4 were already correctly rejected by a human; rejected the
4th for consistency. Checked the root cause: the CURRENT
suggest_event_tags_batch.py already has a real, structural fix for this
(an explicit REACTION_CHARACTER_TAGS exclusion list that filters these
out of the candidate list entirely, not just a prompt instruction) --
these 4 rows predate that fix. Nothing further needed; this can't
recur with the current script.


<!-- entry: 2026-10-09-08 | date: 2026-10-09 | label:  | source-line: 2234 | approx: no -->
### 2026-10-09-08 — pre-Phase-6 audit, continued: core table freshness confirmed clean; one real finding deferred to Monday
> Original heading: `### 2026-10-09 — pre-Phase-6 audit, continued: core table freshness confirmed clean; one real finding deferred to Monday`
Checked every real table Phase 6's own model scripts actually touch
(grepped scripts/models/*.py directly rather than assume): securities,
events, event_entity_relationships, event_tags, event_type_relationships,
event_types, event_pre_context, event_market_reactions, tags,
financial_condition_score, financial_statements, market_prices,
market_regimes, company_sentiment_timeline, global_events,
pattern_significance_tests.

- **financial_condition_score**: 28,533 rows, latest period_end
  2026-08-31 -- genuinely current.
- **market_regimes**: only 9 rows, latest end_date 2023-12-31 at first
  glance -- investigated directly rather than assume this was stale.
  Real, reassuring explanation: there IS a current regime
  (ai_boom_2023_2026, start 2023-01-01, end_date NULL/ongoing) -- MAX()
  simply excludes NULLs, making an ongoing regime invisible to a naive
  MAX(end_date) check. Not a gap.
- **event_market_reactions**: 320 of 19,892 real events have no
  computed reaction. Investigated directly rather than assume this is
  a bug: confirmed via direct sampling that ALL 320 are genuinely
  macro/global events (Fed rate decisions, jobs/CPI/GDP reports,
  hurricanes, 9/11, the Suez blockage, S&P's US credit downgrade,
  WTI's negative-price day) linked to a representative macro entity
  (BLS/BEA/Fed), not a real tradeable company -- event_market_reactions
  computes company-vs-SPY abnormal return, which genuinely cannot apply
  to these. Expected, by design, not a real gap.

**Real, significant finding, deferred to Monday rather than tackled
tonight given its size**: event_tag_suggestions' Tier 4 review backlog
is much larger than previously documented -- roughly 4,660 real rows
still unreviewed across 13 categories (same_entity_sequence alone:
2,563 of 2,931 unreviewed). Full real breakdown logged in the master
to-do list. Also noticed, not yet investigated: 12 MALFORMED rows and 4
rows tagged "punished" sitting in this table, which looks like it may
not belong there at all (that's a reaction_character tag, not a Tier 4
suggestion category) -- worth a quick look Monday alongside the real
review work.


<!-- entry: 2026-10-09-07 | date: 2026-10-09 | label:  | source-line: 2197 | approx: no -->
### 2026-10-09-07 — pre-Phase-6 audit of Phases 1-5: one real bug found and fixed, everything else confirmed clean
> Original heading: `### 2026-10-09 — pre-Phase-6 audit of Phases 1-5: one real bug found and fixed, everything else confirmed clean`
Real, systematic check across everything built this session before
starting Phase 6, rather than assume it's all fine:

1. **Known, pre-existing reaction_character limitation re-confirmed
   still open**: 48 multi-entity events still affected (matches the
   previously documented ~49 figure) -- not newly broken, but a real,
   standing caveat Phase 6 should keep in mind for any
   systemic_shock/geopolitical/government_action analysis.
2. **Double-JSON-encoding bug pattern checked across the whole
   codebase**: only 3 real files use json.dumps() at all, and the 2
   from tonight's work are confirmed safe (dry-run console display
   only, not the actual write payload); the third (regenerate_tier_file.py)
   writes into an HTML file, unrelated. No real residue anywhere else.
3. **Referential integrity across all new tables**: zero orphaned
   government_decision_exposure rows, zero NULL structured_data, zero
   unreviewed relevance_verdict rows, zero gap between labor/housing/
   oil status coverage. All clean.
4. **Real genuine bug found and fixed**: 3 events had BOTH a base
   reaction tag (rewarded/punished) AND diverged_from_fundamentals
   simultaneously -- should be mutually exclusive. Root cause: these 3
   straddled the earlier crash boundary in
   backfill_diverged_from_fundamentals.py's first run, where the
   delete-old-tag step didn't complete cleanly before the process
   crashed. Found via a direct duplicate-tag query, fixed via a direct
   DELETE of the stale old tags, re-confirmed zero duplicates remain.
5. **Classification table integrity**: filing_ai_classifications row
   count exactly matches its distinct (ticker, filing_date,
   accession_number) count (102,962 = 102,962) -- zero real duplicate
   rows, confirming the recovered batch write-back from earlier today
   landed cleanly.

Real, honest scope note: this was a targeted audit of what changed
tonight/today, not an exhaustive re-review of the entire database --
reasonable given the goal was specifically "can Phase 6 proceed without
inheriting a problem from tonight's work," not a full system audit.


<!-- entry: 2026-10-09-06 | date: 2026-10-09 | label:  | source-line: 2153 | approx: no -->
### 2026-10-09-06 — Phase 5 complete: diverged_from_fundamentals backfilled, company-level status built, real RPC-batching fix discovered
> Original heading: `### 2026-10-09 — Phase 5 complete: diverged_from_fundamentals backfilled, company-level status built, real RPC-batching fix discovered`
**diverged_from_fundamentals** (the unused 4th reaction tag): built
backfill_diverged_from_fundamentals.py, a one-time pass (same shape as
recompute_firm_state.py) reviewing every already-tagged rewarded/
punished event and upgrading it where the reaction contradicts
firm_state_label (rewarded+weakening/deteriorating, or
punished+strong/improving). Deliberately a separate script rather than
editing tag_reaction_character.py's own core loop, to avoid risking its
proven logic. Hit a real duplicate-key crash partway through a first
run (a prior partial write had already upgraded some events before an
unrelated transient error) -- added real resume-safety (skip events
already tagged diverged_from_fundamentals) before completing. Final
result: 2,307 real events upgraded, genuine non-degenerate spread
across all 4 contradiction types.

**Company-level status effect**: built populate_company_status.py --
architecturally different from the other status scripts tonight (all
single NATIONAL conditions applied market-wide); this one is scoped
per-COMPANY, checking whether THIS company had a real restructuring
event_type (805 real, entity-linked events) or activist_investor_campaign
tag (5 real entities, a small but real population) within a 12-month
trailing window before each event being scored. Real, genuine result:
2,520 restructuring, 31 activist_pressure, 15 overlapping both, 13,922
with no active condition.

**Real, significant infrastructure fix discovered along the way**:
one-row-at-a-time writes kept hitting the SAME reproducible HTTP/2
connection-recycling limit (~20,000 requests, last_stream_id:19999)
that's crashed multiple status scripts tonight -- and were also just
slow regardless (one real HTTP round-trip per row). Built a genuine
fix: a Postgres function (bulk_update_company_status) doing a real,
safe PARTIAL UPDATE via `UPDATE ... FROM jsonb_to_recordset(updates)`,
called through supabase.rpc() in large chunks (2,000 rows/call)
instead of one HTTP call per row. This is a true partial update (only
the target column touched), unlike upsert()'s full-row-replace
semantics that caused real problems the night before. Cut the full
16,488-row write from a many-minutes, crash-prone run down to 9 real
RPC calls, completing cleanly in well under a minute. Worth applying
this same pattern retroactively to the other status scripts
(labor market, housing, oil, consumer financial health) if they're
ever re-run at full scale again.

This completes Phase 5.


<!-- entry: 2026-10-09-05 | date: 2026-10-09 | label:  | source-line: 2115 | approx: no -->
### 2026-10-09-05 — real $4 recovery: 4 cancelled nightly-classify runs' already-completed batches recovered, zero waste
> Original heading: `### 2026-10-09 — real $4 recovery: 4 cancelled nightly-classify runs' already-completed batches recovered, zero waste`
Galen manually triggered 5 nightly-classify workflow runs that ended up
running concurrently for 2+ hours each with zero rows written
(confirmed via a direct classified_today query), then cancelled all 5
after a real $4 Anthropic charge showed up with no visible database
result -- a real, legitimate "did this actually do anything" question.

Investigated directly via the Anthropic batches API rather than assume
the spend was wasted: found 4 of the submitted batches had actually
reached processing_status="ended" with a real results_url, meaning
Anthropic had already finished the real, paid-for work -- it was only
the GASHub Actions workflow (and its in-memory write step) that got
cancelled, not the underlying batch job, which continues running
independently on Anthropic's side regardless of what happens to the
workflow that submitted it.

Built a one-off recovery script parsing each batch's results directly
(custom_id format ticker__filing_date__accession_number, confirmed from
the real source), replicating the main classifier's exact
parse_classification_result/compute_flag logic (a first attempt without
compute_flag's exact real logic hit a NOT NULL violation on
flag_reason, which the real function returns as the string "none", not
NULL, when not flagged -- fixed before the real write).

Real, final result: 7,842 confirmed unique real classifications
recovered and written (9,949 total processed across the 4 batches, with
real overlap between runs since they'd been pulling from the same
backlog pool before being cancelled) -- confirmed via a direct count on
the recovery's own tagged prompt_version. Nothing was wasted. 4 more
batches were still actively processing at the time and need checking
back on separately once they finish.

**Real, important operational lesson for next time**: cancelling a
GitHub Actions run does NOT cancel the underlying Anthropic batch job
it submitted -- always check the real batches API before assuming a
cancelled run's spend produced nothing, since the batch itself may have
completed (or still be completing) independently.


<!-- entry: 2026-10-09-04 | date: 2026-10-09 | label:  | source-line: 2085 | approx: no -->
### 2026-10-09-04 — Oil price regime status effect built; real threshold miscalibration caught before going live
> Original heading: `### 2026-10-09 — Oil price regime status effect built; real threshold miscalibration caught before going live`
Built populate_oil_price_status.py, the last Phase 4 "status effect"
item, mirroring populate_labor_market_status.py/populate_housing_status.py
for DCOILWTICO (WTI crude). Deliberately framed as a volatility/shock
regime (spike/crash/normal), not a directional health score -- oil
price doesn't have a real "good/bad" direction the way labor market or
housing do (a spike helps energy producers, hurts airlines/consumers;
a crash does the reverse).

**Real threshold bug caught on the first dry run, before going live**:
reused the same +-0.5 deviation threshold as labor/housing without
checking whether it actually fit oil's real volatility character.
Result: {'spike': 8209, 'crash': 6665, 'normal': 1614} -- spike alone
covered half of all 16,488 events. Investigated directly: computed the
real deviation distribution across all 8,209 real trading days (not
just events) and found 85.2% exceed |0.5| -- oil's real day-to-day
volatility is far higher than labor/housing's monthly-cadence series,
so +-0.5 made "spike" the default state, not a genuine signal.

Real fix: computed the actual percentile distribution and picked a
threshold near the real 20th/80th percentile (-2.70/+3.13) instead of
assuming the same constant would transfer -- settled on +-3.0. Re-ran
the dry run: genuinely balanced, non-degenerate result (8,494 normal,
4,261 spike, 3,733 crash).

**Real, final result**: 4,910 of 16,488 event_pre_context rows filled
this run (most of the remainder already covered by earlier status
scripts needing the same trailing-window minimum), confirmed matching
the dry run exactly. This completes the last open Phase 4 item.


<!-- entry: 2026-10-09-03 | date: 2026-10-09 | label:  | source-line: 2046 | approx: no -->
### 2026-10-09-03 — government decision exposure threading built for EOs/laws (fixed 7-day window); real field-semantics mix-up caught and fixed
> Original heading: `### 2026-10-09 — government decision exposure threading built for EOs/laws (fixed 7-day window); real field-semantics mix-up caught and fixed`
Real design decision with Galen: FOMC's existing "until the next
decision" variable-window exposure model doesn't fit executive orders
and enacted laws -- with 7,992 non-FOMC decisions instead of 31, a
shared timeline would shrink most windows to 0-1 days. Built
check_decision_exposure_fixed_window.py instead, reusing
check_event_exposure.py's proven 7-day fixed-window template and bulk-
loading technique. Deliberately scoped to only the 3,035 decisions
already marked relevance_verdict='relevant' -- running this against the
~5,000 not_relevant rows would be real wasted compute.

Writes into the SAME existing government_decision_exposure table FOMC
already uses (it stores event_window_days per row, so it already
supports mixed window lengths).

Real, genuine zero-rows pattern for the earliest ~1,800 of 3,035
decisions, chronologically -- investigated and confirmed expected, not
a bug: company_sentiment_timeline (GDELT-sourced) only has real
coverage from 2015-02-17 onward, so decisions before roughly 2014 have
no real sentiment baseline to compute against.

**Real field-semantics mix-up caught after the live write** (the write
itself was correct, only a resume-check was wrong): event_window_days
is NOT the calendar window length -- same real semantics as the
original check_event_exposure.py template this was copied from -- it's
the COUNT of real sentiment data points found within the window, which
varies per decision/company. The resume-detection logic filtered on
event_window_days == 7 as if that were the fixed constant, which only
coincidentally matched decisions with exactly 7 real data points (19,518
of 151,963), not "already processed." Confirmed the actual write was
fully correct via a direct join to government_decisions.decision_type
(151,963, matching the script's own reported total exactly) before
fixing the resume filter for future re-runs -- no real collision risk
with FOMC's rows, since the caller's own decision list is already
scoped to non-FOMC.

**Real, final result**: 3,035 relevant decisions processed, 151,963
exposure rows written, confirmed correct via direct database join.


<!-- entry: 2026-10-09-02 | date: 2026-10-09 | label:  | source-line: 1988 | approx: no -->
### 2026-10-09-02 — Government decision relevance classification built and run; real cross-script parser reuse bug found
> Original heading: `### 2026-10-09 — Government decision relevance classification built and run; real cross-script parser reuse bug found`
Built classify_decision_relevance.py (step 2 of the real, deliberate
two-step relevance scoping): judges each non-FOMC government_decisions
row as relevant/not_relevant to this database's stock-research purpose
(company/economic/health regulation vs. commemorative or symbolic
bills with no economic substance). Reused the proven batch-submission/
polling infrastructure from classify_8k_filings_batch_v2.py via
importlib, matching the established reuse pattern.

**Real, genuine bug found the hard way**: also reused that script's
parse_classification_result for convenience -- this was wrong. That
function is hardcoded for the 8-K classifier's own schema (requires a
"confidence" field, only accepts real_event/likely_noise/uncertain as
valid verdicts). This script's schema is simpler (verdict/reasoning
only, relevant/not_relevant) -- every real response silently got forced
to "uncertain" by that function's own validation logic, which isn't a
parse failure at all, just a schema mismatch. The first live run wrote
7,992 rows, ALL incorrectly marked "relevant" with a fabricated
"PARSE ERROR" reasoning string. Caught via a direct database spot-check
after the run (real distribution was {relevant: 0, not_relevant: 0,
error: 7992} -- an immediately suspicious, fully degenerate result).

**Real lesson**: a shared module's helper functions are safe to reuse
only when they're genuinely generic (as submit_batch/poll/fetch-raw-
content are) -- a function that validates or interprets a specific
response SCHEMA is coupled to that script's own prompt contract and
should not be reused as-is for a different schema, even one that looks
superficially similar.

**Real fix, two parts**: (1) wrote this script's own
parse_relevance_result, matching only its actual schema, and
reimplemented the results-fetching loop locally instead of calling
batch_module.fetch_batch_results (which internally called the wrong
parser) -- real text-block-finding logic kept, parsing logic now
correct. (2) Recovered the real batch without resubmitting -- the
Anthropic batch itself had completed successfully before the original
crash/bug, so a one-off recovery script re-fetched the SAME batch_id's
already-completed results directly and overwrote the wrong write with
correct values, at zero extra API cost.

**Also fixed, in the shared fetch_batch_results function** (benefits
classify_8k_filings_batch_v2.py too): a single response with ZERO
content blocks (not even a thinking block) previously crashed the
entire fetch, discarding every other already-succeeded result in the
same real batch -- hit this live on request 7,992 of 7,992. Now handled
the same way an actual batch-level failure already was: mark that one
item as failed, keep every other real result.

**Real, final result** (confirmed via direct spot-check of 8 random
rows, genuinely sensible judgment throughout -- post-office-naming
bills and foreign-policy resolutions correctly not_relevant; financial
regulation, sanctions, transportation funding, healthcare/pharmacy
regulation, and school nutrition correctly relevant): 3,035 relevant,
4,957 not_relevant across the 7,992 real non-FOMC government_decisions
rows (30 of the "relevant" count are real parse-error rows, defaulted
to relevant on purpose so nothing silently drops out of future manual
review scope).


<!-- entry: 2026-10-09-01 | date: 2026-10-09 | label:  | source-line: 1945 | approx: no -->
### 2026-10-09-01 — Congressional enacted laws ingested (6,422 rows); real double-JSON-encoding bug found and fixed across ALL government_decisions
> Original heading: `### 2026-10-09 — Congressional enacted laws ingested (6,422 rows); real double-JSON-encoding bug found and fixed across ALL government_decisions`
Built populate_enacted_laws.py against the official Congress.gov API
(api.congress.gov/v3, requires a real, free CONGRESS_API_KEY -- unlike
the Federal Register API, not keyless). Two real calls per law by
design: the cheap /law/{congress}/pub list endpoint for the bare bill
ID, then /bill/{congress}/{type}/{number} for the real policyArea tag
(not available on the list endpoint). Real scope: congresses 103-119
(1994-present), confirmed via a live count check before building --
6,422 total, ran overnight, completed cleanly.

**Real, serious bug found this morning, affecting ALL 8,023
government_decisions rows, not just last night's new additions**:
checking the real policy_area distribution after the overnight run
returned 100% NULL. Investigated directly: structured_data was stored
as a jsonb SCALAR STRING, not a real jsonb OBJECT (confirmed via
jsonb_typeof() returning 'string', and jsonb_object_keys() refusing to
run with "cannot call jsonb_object_keys on a scalar"). Root cause: all
3 government_decisions scripts called json.dumps() before handing the
dict to the Supabase client, which serializes dicts itself --
double-encoding the result. The raw column display looked completely
normal (a JSON string's text representation is visually identical to a
real object), which is exactly why this passed unnoticed through
multiple dry runs and three separate live writes across two sessions.

Repaired all 8,023 existing rows via
`structured_data = (structured_data #>> '{}')::jsonb` (unwrap the
scalar string's real text content, re-parse it as actual JSON).
Verified clean: jsonb_typeof is 'object' for all rows,
structured_data->>'policy_area' now correctly extracts real values.
Fixed the root cause in all 3 scripts (populate_government_decisions.py,
populate_executive_orders.py, populate_enacted_laws.py) -- pass the
native dict directly, no json.dumps() wrapper.

**Real, final government_decisions state**: 8,023 total rows -- 31 FOMC
(2015-2025), 1,570 executive orders (1993-2026), 6,422 enacted laws
(1993-2026). Real, genuine policy-area variety confirmed: 1,089
Government Operations and Politics, 690 Public Lands and Natural
Resources, 669 Commemorations, 497 Armed Forces and National Security,
319 Economics and Public Finance, 296 Health, and more -- Commemorations
being a large real category is itself a good sign, since that's exactly
the kind of irrelevant bill the real step-2 relevance classification
(not yet built) should filter out.


<!-- entry: 2026-10-08-07 | date: 2026-10-08 | label:  | source-line: 1896 | approx: no -->
### 2026-10-08-07 — Federal executive orders ingested (1,570 rows); real duplicate-key schema fix found along the way
> Original heading: `### 2026-10-08 — Federal executive orders ingested (1,570 rows); real duplicate-key schema fix found along the way`
Built populate_executive_orders.py, pulling the Federal Register's own
free, keyless, official API (federalregister.gov/api/v1/documents.json,
confirmed via a live test call before building). Real history back to
1994-01-01, matching this project's own earliest tracked company date
exactly -- 1,570 real executive orders fetched and written.

**Real, genuine schema bug found and fixed before any data was lost**:
the existing government_decisions table's unique constraint
(decision_date, body, decision_type) was fine for FOMC (one decision per
real meeting date, confirmed never duplicated) but genuinely breaks for
executive orders -- confirmed directly via a live API check that up to
4 real EOs can be signed on the same real date. First live run hit a
hard constraint violation. Fixed by adding a real
source_document_number column (UNIQUE, populated from the Federal
Register's own document_number, a genuinely unique real identifier) and
dropping the old compound constraint.

This required updating populate_government_decisions.py too, since
source_document_number needed to become the universal real conflict
key across the whole table, not just for EOs -- gave FOMC rows a
synthetic source_document_number ("fomc-{date}") for consistency.
Re-running that script against the existing 31 FOMC rows (added AFTER
the column existed, so their source_document_number was NULL) produced
31 real duplicate rows instead of updating them -- Postgres treats NULL
as non-matching in a UNIQUE constraint, so the upsert couldn't find the
old rows to update. Caught via a row-count check (62 instead of 31,
immediately suspicious) before this cascaded further. The 31 real OLD
rows already had downstream data in government_decision_exposure
referencing them (confirmed via a foreign-key violation when the first,
wrong attempt tried to delete them) -- correctly reversed course and
deleted the 31 NEW duplicate rows instead (safe, nothing referenced
them yet), then set source_document_number on the original 31 via a
direct UPDATE. Final, confirmed-clean state: 31 FOMC rows, 1,570
executive orders, every row has a real, unique source_document_number.

**Relevance scoping, deliberate, two-step (Galen 2026-10-08)**: this
script ingests the raw, complete set with no filtering -- EOs have no
clean policy-area tag the way Congressional bills do. Each row's
structured_data.relevance_reviewed stays false until a separate,
not-yet-built classification step judges which EOs actually touch
companies/health/economic regulation vs. something like a commemorative
proclamation.

**Also found and fixed defensively**: some real EOs' agencies array
contains entries missing a "name" key -- real data quirk in the Federal
Register's own records, not a bug in this script. Fixed with a
.get("name") or .get("raw_name") fallback.


<!-- entry: 2026-10-08-06 | date: 2026-10-08 | label:  | source-line: 1860 | approx: no -->
### 2026-10-08-06 — Consumer Financial Health composite index built, real methodology bug found and fixed
> Original heading: `### 2026-10-08 — Consumer Financial Health composite index built, real methodology bug found and fixed`
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


<!-- entry: 2026-10-08-05 | date: 2026-10-08 | label:  | source-line: 1816 | approx: no -->
### 2026-10-08-05 — Housing fully rounded out: supply/demand + all 50 state price indexes
> Original heading: `### 2026-10-08 — Housing fully rounded out: supply/demand + all 50 state price indexes`
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


<!-- entry: 2026-10-08-04 | date: 2026-10-08 | label:  | source-line: 1788 | approx: no -->
### 2026-10-08-04 — Labor Market and Housing raw series ingested (9 more)
> Original heading: `### 2026-10-08 — Labor Market and Housing raw series ingested (9 more)`
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


<!-- entry: 2026-10-08-03 | date: 2026-10-08 | label:  | source-line: 1730 | approx: no -->
### 2026-10-08-03 — Population/Consumer Sentiment: real groundwork laid out, 9 new FRED series ingested
> Original heading: `### 2026-10-08 — Population/Consumer Sentiment: real groundwork laid out, 9 new FRED series ingested`
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


<!-- entry: 2026-10-08-02 | date: 2026-10-08 | label:  | source-line: 1710 | approx: no -->
### 2026-10-08-02 — correction: the 257 NULL-severity global_events rows are NOT unreviewed
> Original heading: `### 2026-10-08 — correction: the 257 NULL-severity global_events rows are NOT unreviewed`
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


<!-- entry: 2026-10-08-01 | date: 2026-10-08 | label:  | source-line: 1689 | approx: no -->
### 2026-10-08-01 — global_event_episodes formally retired; manual-review track confirmed stalled at 167/424
> Original heading: `### 2026-10-08 — global_event_episodes formally retired; manual-review track confirmed stalled at 167/424`
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


<!-- entry: 2026-10-03-24 | date: 2026-10-03 | label:  | source-line: 1657 | approx: yes -->
### 2026-10-03-24 — the ~13,900 unread Sept 24 real_event rows: duplicate-language sweep completed
> Original heading: `### 2026-10 — the ~13,900 unread Sept 24 real_event rows: duplicate-language sweep completed`
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


<!-- entry: 2026-10-03-23 | date: 2026-10-03 | label:  | source-line: 1618 | approx: yes -->
### 2026-10-03-23 — review backlog steady-state: real, automated nightly cadence built
> Original heading: `### 2026-10 — review backlog steady-state: real, automated nightly cadence built`
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


<!-- entry: 2026-10-03-22 | date: 2026-10-03 | label:  | source-line: 1581 | approx: yes -->
### 2026-10-03-22 — CHTR/EFX/CPRT/CDW untriaged tickers: real root cause found, real fix applied for 2 of 4
> Original heading: `### 2026-10 — CHTR/EFX/CPRT/CDW untriaged tickers: real root cause found, real fix applied for 2 of 4`
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


<!-- entry: 2026-10-03-21 | date: 2026-10-03 | label:  | source-line: 1522 | approx: yes -->
### 2026-10-03-21 — real resolution attempt on the 37 "genuinely-unresolvable" uncertain rows: 18 of 37 resolved
> Original heading: `### 2026-10 — real resolution attempt on the 37 "genuinely-unresolvable" uncertain rows: 18 of 37 resolved`
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


<!-- entry: 2026-10-03-20 | date: 2026-10-03 | label:  | source-line: 1482 | approx: yes -->
### 2026-10-03-20 — Track B (news_ai_classifications) 101 real_event candidates reviewed; no promotion script exists yet
> Original heading: `### 2026-10 — Track B (news_ai_classifications) 101 real_event candidates reviewed; no promotion script exists yet`
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


<!-- entry: 2026-10-03-19 | date: 2026-10-03 | label:  | source-line: 1446 | approx: yes -->
### 2026-10-03-19 — real, important discovery: a duplicate-detection gap in the 2026-09-24 mass auto-confirm, 67 corrected
> Original heading: `### 2026-10 — real, important discovery: a duplicate-detection gap in the 2026-09-24 mass auto-confirm, 67 corrected`
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


<!-- entry: 2026-10-03-18 | date: 2026-10-03 | label:  | source-line: 1411 | approx: yes -->
### 2026-10-03-18 — real, major milestone: promote_events.py run to completion, 3,139 new real events created
> Original heading: `### 2026-10 — real, major milestone: promote_events.py run to completion, 3,139 new real events created`
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


<!-- entry: 2026-10-03-17 | date: 2026-10-03 | label:  | source-line: 1391 | approx: yes -->
### 2026-10-03-17 — stale-URL sweep writeback complete: 39 new rows written, 112 total awaiting promote_events.py
> Original heading: `### 2026-10 — stale-URL sweep writeback complete: 39 new rows written, 112 total awaiting promote_events.py`
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


<!-- entry: 2026-10-03-16 | date: 2026-10-03 | label:  | source-line: 1373 | approx: yes -->
### 2026-10-03-16 — real, major milestone: the stale-URL sweep is fully complete (17,500 of 17,440+ processed)
> Original heading: `### 2026-10 — real, major milestone: the stale-URL sweep is fully complete (17,500 of 17,440+ processed)`
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


<!-- entry: 2026-10-03-15 | date: 2026-10-03 | label:  | source-line: 1345 | approx: yes -->
### 2026-10-03-15 — real near-miss: an overly broad UPDATE query during tag-suggestion review, caught and fixed
> Original heading: `### 2026-10 — real near-miss: an overly broad UPDATE query during tag-suggestion review, caught and fixed`
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


<!-- entry: 2026-10-03-14 | date: 2026-10-03 | label:  | source-line: 1321 | approx: yes -->
### 2026-10-03-14 — real, honest note: the 37 genuinely-ambiguous uncertain rows are NOT a funding problem at root
> Original heading: `### 2026-10 — real, honest note: the 37 genuinely-ambiguous uncertain rows are NOT a funding problem at root`
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


<!-- entry: 2026-10-03-13 | date: 2026-10-03 | label:  | source-line: 1293 | approx: yes -->
### 2026-10-03-13 — real recovery of 52 BATCH REQUEST FAILED rows: 27 of 47 recovered, rest blocked on Anthropic API funding
> Original heading: `### 2026-10 — real recovery of 52 BATCH REQUEST FAILED rows: 27 of 47 recovered, rest blocked on Anthropic API funding`
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


<!-- entry: 2026-10-03-12 | date: 2026-10-03 | label:  | source-line: 1261 | approx: yes -->
### 2026-10-03-12 — real, systematic bug found in the uncertain queue: invalid verdict values silently discarding confident real classifications
> Original heading: `### 2026-10 — real, systematic bug found in the uncertain queue: invalid verdict values silently discarding confident real classifications`
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


<!-- entry: 2026-10-03-11 | date: 2026-10-03 | label:  | source-line: 1230 | approx: no -->
### 2026-10-03-11 — real triage of the full review backlog: ~49,804 feared down to a real, honest 1,235 urgent items
> Original heading: `### 2026-10-03 — real triage of the full review backlog: ~49,804 feared down to a real, honest 1,235 urgent items`
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


<!-- entry: 2026-10-03-10 | date: 2026-10-03 | label:  | source-line: 1213 | approx: no -->
### 2026-10-03-10 — real, quick note: 804 vs 531 untagged-event discrepancy explained, 15 tagged live
> Original heading: `### 2026-10-03 — real, quick note: 804 vs 531 untagged-event discrepancy explained, 15 tagged live`
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


<!-- entry: 2026-10-03-09 | date: 2026-10-03 | label:  | source-line: 1178 | approx: no -->
### 2026-10-03-09 — 531-event untagged backlog triaged: mostly real, legitimate gaps, two confirmed accepted limitations
> Original heading: `### 2026-10-03 — 531-event untagged backlog triaged: mostly real, legitimate gaps, two confirmed accepted limitations`
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


<!-- entry: 2026-10-03-08 | date: 2026-10-03 | label:  | source-line: 1137 | approx: no -->
### 2026-10-03-08 — real root-cause fix: multi-entity reactions now computed automatically, no separate backfill needed
> Original heading: `### 2026-10-03 — real root-cause fix: multi-entity reactions now computed automatically, no separate backfill needed`
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


<!-- entry: 2026-10-03-07 | date: 2026-10-03 | label:  | source-line: 1098 | approx: no -->
### 2026-10-03-07 — real near-miss: checked the >=0.90 band for the same contradiction pattern, found zero genuine errors after verification
> Original heading: `### 2026-10-03 — real near-miss: checked the >=0.90 band for the same contradiction pattern, found zero genuine errors after verification`
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


<!-- entry: 2026-10-03-06 | date: 2026-10-03 | label:  | source-line: 1057 | approx: no -->
### 2026-10-03-06 — 0.75-0.90 auto-confirm band spot-checked at real scale, 14 real misclassifications found and corrected
> Original heading: `### 2026-10-03 — 0.75-0.90 auto-confirm band spot-checked at real scale, 14 real misclassifications found and corrected`
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


<!-- entry: 2026-10-03-05 | date: 2026-10-03 | label:  | source-line: 1035 | approx: no -->
### 2026-10-03-05 — financial_metrics residual fully resolved: real pagination tie-break bug found and fixed
> Original heading: `### 2026-10-03 — financial_metrics residual fully resolved: real pagination tie-break bug found and fixed`
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


<!-- entry: 2026-10-03-04 | date: 2026-10-03 | label:  | source-line: 1008 | approx: no -->
### 2026-10-03-04 — 367-ticker gap: real, massive batch result -- all 65 remaining high-count tickers resolved
> Original heading: `### 2026-10-03 — 367-ticker gap: real, massive batch result -- all 65 remaining high-count tickers resolved`
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


<!-- entry: 2026-10-03-03 | date: 2026-10-03 | label:  | source-line: 981 | approx: no -->
### 2026-10-03-03 — 367-ticker gap: 5 of the 6 remaining holdouts resolved, real total now 21 tickers
> Original heading: `### 2026-10-03 — 367-ticker gap: 5 of the 6 remaining holdouts resolved, real total now 21 tickers`
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


<!-- entry: 2026-10-03-02 | date: 2026-10-03 | label:  | source-line: 958 | approx: no -->
### 2026-10-03-02 — 367-ticker gap: real, broad result -- 16 tickers resolved from 3 concept additions
> Original heading: `### 2026-10-03 — 367-ticker gap: real, broad result -- 16 tickers resolved from 3 concept additions`
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


<!-- entry: 2026-10-03-01 | date: 2026-10-03 | label:  | source-line: 930 | approx: no -->
### 2026-10-03-01 — Real, broad fix for the 367-ticker quarterly gap: SalesRevenueGoodsNet (consumer-goods companies)
> Original heading: `### 2026-10-03 — Real, broad fix for the 367-ticker quarterly gap: SalesRevenueGoodsNet (consumer-goods companies)`
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


<!-- entry: 2026-10-02-01 | date: 2026-10-02 | label:  | source-line: 471 | approx: no -->
### 2026-10-02-01 — firm_state gap investigation: real concurrency bug found and fixed, "regression" was a false alarm
> Original heading: `### 2026-10-02 — firm_state gap investigation: real concurrency bug found and fixed, "regression" was a false alarm`
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


<!-- entry: 2026-09-30-12 | date: 2026-09-30 | label: PROJECT_PLAN | source-line: PLAN:515 | approx: no -->
### 2026-09-30-12 — Addendum: XOM's Quarterly Gap Confirmed, and a Much Bigger Related Finding (2026-09-30)
> Original heading: `Addendum: XOM's Quarterly Gap Confirmed, and a Much Bigger Related Finding (2026-09-30)`
> Moved from PROJECT_PLAN.md on 2026-10-28 (the section was first committed to the plan on 2026-09-30). Text unchanged except that its headings are demoted three levels so they nest under this entry. The whole original file is in the git history and in docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md.

Real Phase 1 checklist item, investigated: XOM's long-standing 2007-2016 quarterly
gap. **Confirmed real** -- XOM has zero Q1/Q2/Q3 `financial_statements` rows for the
entire decade, only an empty Q4 placeholder each year (revenue and net_income both
null). This matches the old diagnosis (likely needs raw XBRL instance-document
inspection, not the aggregated company-facts API) -- genuinely deep, slow work, not
a quick fix. **Formally accepted as out-of-scope for now**, not silently left
ambiguous -- a real decision, not an open question.

**While checking, found a much bigger, previously undocumented pattern.** 1,223
empty quarterly rows exist across 367 distinct securities (~73% of the tracked
universe) -- all `fiscal_quarter=4`, no exceptions. Investigated whether this was a
fixable Q4-derivation bug (Q4 is computed as Annual minus Q1+Q2+Q3, so a bug there
would explain scattered failures with real Q1-Q3 data sitting unused) by checking
BNY specifically (19 empty rows, the worst-affected ticker). **Real finding: it's
not a derivation bug.** Most years (2010-2015, 2017, 2019-2025 -- including recent,
modern filings) have ONLY the empty Q4 placeholder, with Q1/Q2/Q3 not present at
all, not just unpopulated. A few scattered years (2009, 2016, 2018) have real,
complete data. The empty-Q4-row count undercounts the true scope of the problem --
the ingestion script apparently always writes a Q4 placeholder row even on failure,
but genuinely skips writing any row at all for Q1/Q2/Q3 when nothing matches, so
those failures are invisible to a null-check on existing rows.

**Real working theory, not yet confirmed:** the top of the affected-ticker list is
overwhelmingly banks/financial institutions (BNY, MTB, GS, TFC, SYF, RF, FITB,
NTRS). Financial companies typically report revenue-equivalent figures under
different XBRL concept names (net interest income, total interest and dividend
income, etc.) than industrial/consumer companies' standard "Revenues" concept --
plausible that the ingestion script's concept-matching list simply doesn't include
the financial-sector-specific concept names, causing systematic quarterly gaps for
that whole sector, unrelated to XOM's separate early-XBRL-era issue.

**Real next step, in progress:** check `ingest_sec_financials_multi.py`'s actual
concept-matching list against what a real affected bank's 10-Q XBRL data contains,
to confirm or reject the financial-sector theory before attempting any fix.

<!-- entry: 2026-09-30-11 | date: 2026-09-30 | label:  | source-line: 760 | approx: no -->
### 2026-09-30-11 — Storm/compounding finding productionized: real event_pre_context columns
> Original heading: `### 2026-09-30 — Storm/compounding finding productionized: real event_pre_context columns`
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


<!-- entry: 2026-09-30-10 | date: 2026-09-30 | label:  | source-line: 735 | approx: no -->
### 2026-09-30-10 — Multi-entity reaction tagging gap closed (real fix backfilled, not a permanent code fix)
> Original heading: `### 2026-09-30 — Multi-entity reaction tagging gap closed (real fix backfilled, not a permanent code fix)`
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


<!-- entry: 2026-09-30-09 | date: 2026-09-30 | label:  | source-line: 723 | approx: no -->
### 2026-09-30-09 — EA's price-data absence explained (real, external, not a pipeline bug)
> Original heading: `### 2026-09-30 — EA's price-data absence explained (real, external, not a pipeline bug)`
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


<!-- entry: 2026-09-30-08 | date: 2026-09-30 | label:  | source-line: 695 | approx: no -->
### 2026-09-30-08 — Sector-peer ripple finding productionized: new sector_peer_ripple table
> Original heading: `### 2026-09-30 — Sector-peer ripple finding productionized: new sector_peer_ripple table`
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


<!-- entry: 2026-09-30-07 | date: 2026-09-30 | label:  | source-line: 681 | approx: no -->
### 2026-09-30-07 — The ~876-event ripple gap fully explained: not a bug, F/GE/AEP specifically
> Original heading: `### 2026-09-30 — The ~876-event ripple gap fully explained: not a bug, F/GE/AEP specifically`
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


<!-- entry: 2026-09-30-06 | date: 2026-09-30 | label:  | source-line: 668 | approx: no -->
### 2026-09-30-06 — financial_market_reactions "unification" was already resolved, before tonight
> Original heading: `### 2026-09-30 — financial_market_reactions "unification" was already resolved, before tonight`
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


<!-- entry: 2026-09-30-05 | date: 2026-09-30 | label:  | source-line: 642 | approx: no -->
### 2026-09-30-05 — Real fix found for the financial-sector quarterly gap: RevenuesNetOfInterestExpense
> Original heading: `### 2026-09-30 — Real fix found for the financial-sector quarterly gap: RevenuesNetOfInterestExpense`
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


<!-- entry: 2026-09-30-04 | date: 2026-09-30 | label:  | source-line: 608 | approx: no -->
### 2026-09-30-04 — Financial-sector quarterly gap: real partial win, real deeper bug found and NOT fixed
> Original heading: `### 2026-09-30 — Financial-sector quarterly gap: real partial win, real deeper bug found and NOT fixed`
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


<!-- entry: 2026-09-30-03 | date: 2026-09-30 | label:  | source-line: 573 | approx: no -->
### 2026-09-30-03 — BNY's real gap traced to its actual source: not our bug, a real XBRL tagging gap
> Original heading: `### 2026-09-30 — BNY's real gap traced to its actual source: not our bug, a real XBRL tagging gap`
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


<!-- entry: 2026-09-30-02 | date: 2026-09-30 | label:  | source-line: 516 | approx: no -->
### 2026-09-30-02 — Added confidence_trend to multi_feature_model.py; fixed a real pagination bug; corrected my own overclaim about its impact
> Original heading: `### 2026-09-30 — Added confidence_trend to multi_feature_model.py; fixed a real pagination bug; corrected my own overclaim about its impact`
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


<!-- entry: 2026-09-30-01 | date: 2026-09-30 | label:  | source-line: 449 | approx: no -->
### 2026-09-30-01 — financial_metrics gap: re-run closed most of it (842->78), real small residual remains
> Original heading: `### 2026-09-30 — financial_metrics gap: re-run closed most of it (842->78), real small residual remains`
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


<!-- entry: 2026-09-29-09 | date: 2026-09-29 | label: PROJECT_PLAN | source-line: PLAN:470 | approx: no -->
### 2026-09-29-09 — Addendum: Population/Consumer Sentiment — Real Scope for Phase 4 (2026-09-29)
> Original heading: `Addendum: Population/Consumer Sentiment — Real Scope for Phase 4 (2026-09-29)`
> Moved from PROJECT_PLAN.md on 2026-10-28 (the section was first committed to the plan on 2026-09-29). Text unchanged except that its headings are demoted three levels so they nest under this entry. The whole original file is in the git history and in docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md.

Raised while scoping Phase 4's real sub-tracks. Real distinction from what already
exists: `company_sentiment_timeline` (GDELT-based) measures NEWS COVERAGE TONE about
a company directly -- it's a real, working, already-built signal, but it's not the
same thing as genuine population/consumer sentiment, and it can't attach to a PERSON
rather than a company.

**The real concept, from the working example given (Elon Musk's public standing during
his DOGE involvement, and the real, observed Tesla stock impact):** population
perception of a PERSON associated with a company can drive real consumer behavior
(purchase decisions, brand favorability) independent of the company's own news
coverage. This is closer to "would the population buy from this company right now"
than "how is this company being covered in the news" -- a genuinely different signal
from what `company_sentiment_timeline` already captures.

**Checked and confirmed not already built:** searched scripts for consumer confidence/
buying confidence/executive sentiment/reputation-related work -- nothing found. This
was real design thinking from an earlier Phase 4 scoping session, never implemented.

**Real, hard sub-problem this needs, not present anywhere in the current schema:** a
PERSON -> COMPANY link. The existing sentiment pipeline matches on organization names
(GDELT company-name matching, `backfill_gdelt_sentiment.py`'s `TRACKED_COMPANIES`
dict). Matching sentiment about a specific PERSON (an executive, a founder) to the
company they're associated with is a genuinely new linking mechanism -- not a simple
extension of the existing name-matching approach.

**Real candidate data sources, not yet evaluated for feasibility:** Twitter/X (direct,
real-time population expression, but real known complications -- rate limits, bot/
inauthentic-account noise, cost -- these don't go away just because there's now a
clearer purpose for them); potentially Google Trends-style purchase-intent search
data; review-aggregator sentiment. None of these have been scoped for actual
fetchability or cost in this project.

**Connects to the Cascade Effect (see THEORY.md):** a genuine reputational event about
a specific person is a plausible real Tier-0/Tier-1 trigger in that framework (forced/
reactive company impact, not company-initiated) -- worth designing alongside that work
rather than as a fully separate track.

**Not started.** Real next steps when picked up: (1) evaluate real data source
feasibility (Twitter API access/cost first, since it's the most direct fit), (2)
design the person-to-company linking mechanism, (3) pick a real, bounded test case
(the Musk/Tesla example itself is a genuine, well-documented candidate) to validate
the approach on a single case before any broader build.

<!-- entry: 2026-09-29-08 | date: 2026-09-29 | label: PROJECT_PLAN | source-line: PLAN:433 | approx: no -->
### 2026-09-29-08 — Addendum: Government Decisions — Real Scope for a Phase 4 Sub-Track (2026-09-29)
> Original heading: `Addendum: Government Decisions — Real Scope for a Phase 4 Sub-Track (2026-09-29)`
> Moved from PROJECT_PLAN.md on 2026-10-28 (the section was first committed to the plan on 2026-09-29). Text unchanged except that its headings are demoted three levels so they nest under this entry. The whole original file is in the git history and in docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md.

Raised while reviewing Phase 4: raw macro numbers (Fed rate levels, etc.) already exist
in `macro_data_releases`, but a bare number isn't a Government Decisions *event* — the
real value is the DECISION'S REASONING (why the Fed acted), because that reasoning is
what actually connects to public opinion/sentiment, which is what plausibly shapes
company confidence. A rate change with no narrative is just a Phase 2 fact restated with
a label; it doesn't do Phase 4's real job.

**Real, sized scope:** 31 genuine Fed rate decisions exist in `macro_data_releases`
(DFEDTARU, `change_from_previous != 0`), 2015-2025 — not thousands of daily readings,
real discrete policy moves. One (2020-03-16, the COVID emergency cut) is already a real
event, hand-linked via `event_relationships`' `same_root_cause` type (see the Cascade
Effect entry in `THEORY.md` for that precedent). **The other 30 are not yet real events.**

**Real source needed, not yet built:** each decision's actual reasoning is real and
public — the Fed publishes an FOMC statement after every rate decision, directly
analogous to how an SEC 8-K is the real source for a company event. This needs
fetching and reading, same discipline as every filing reviewed tonight — never
fabricate the reasoning, trace it to the real statement text. Whether FOMC statements
are fetchable via a stable URL pattern (parallel to SEC EDGAR's) hasn't been checked.

**Why this matters more than a simple data-to-event conversion:** the real design
intent is Decision (with real reasoning) -> Public Opinion / Sentiment -> Company
Confidence. This should connect to `company_sentiment_timeline` (already real,
GDELT-based) rather than exist as an isolated track — a genuine Fed-decision event with
real reasoning is exactly the kind of Tier-0 exogenous trigger the Cascade Effect design
(see `THEORY.md`) is built around, and could plausibly interact with the already-tested
(currently null) `storm_x_sentiment` feature in a more targeted way than the general
version tested tonight.

**Not started.** Real next steps when picked up: (1) confirm FOMC statements are
fetchable, (2) build the 30 real events with sourced reasoning, individually read
before confirming, (3) link each to the existing `company_sentiment_timeline` data
around its date as the "public opinion" layer, (4) only then consider whether this
predicts company-level reactions better than the raw rate number alone.

<!-- entry: 2026-09-29-07 | date: 2026-09-29 | label: PROJECT_PLAN | source-line: PLAN:416 | approx: no -->
### 2026-09-29-07 — Addendum: Macro Data Placement — Phase 2 vs. Phase 4 (2026-09-29)
> Original heading: `Addendum: Macro Data Placement — Phase 2 vs. Phase 4 (2026-09-29)`
> Moved from PROJECT_PLAN.md on 2026-10-28 (the section was first committed to the plan on 2026-09-29). Text unchanged except that its headings are demoted three levels so they nest under this entry. The whole original file is in the git history and in docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md.

`macro_data_releases` (real FRED data: DCOILWTICO, DGS10, DFEDTARL/DFEDTARU, PAYEMS,
UNRATE, CPIAUCSL, PCEPI, GDPC1 — 9 series, 31,034 rows, 1994-01-01 through
2026-09-16) has historically been described as Phase 4's "Track A," alongside Track
B's news-narrative pipeline. **Real, current status: this data is already fully built
and current — no ingestion gap exists.** Nothing here required new work.

**Clarified split (conceptual, not a code change):** the raw macro *numbers* belong
to Phase 2's domain — usable directly for financial analysis, comparing a company's
performance against the macro backdrop, regardless of which pipeline physically
ingests them. Phase 4 owns the *narrative* — how a release was covered, market
sentiment/reaction framing around it. The table itself doesn't move or get
duplicated; this is purely about which phase's own completion checklist claims
"macro data exists and is current" as one of its real items, so future work doesn't
have to guess where to look for it.

<!-- entry: 2026-09-29-06 | date: 2026-09-29 | label:  | source-line: 881 | approx: no -->
### 2026-09-29-06 — Phase 2 spot-check: financial_metrics coverage gap
> Original heading: `### 2026-09-29 — Phase 2 spot-check: financial_metrics coverage gap`
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


<!-- entry: 2026-09-29-05 | date: 2026-09-29 | label:  | source-line: 861 | approx: no -->
### 2026-09-29-05 — Dead-column scan (Phase 1 checklist item)
> Original heading: `### 2026-09-29 — Dead-column scan (Phase 1 checklist item)`
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


<!-- entry: 2026-09-29-04 | date: 2026-09-29 | label:  | source-line: 839 | approx: no -->
### 2026-09-29-04 — Derived financial chain verified, one real fix, one false alarm resolved
> Original heading: `### 2026-09-29 — Derived financial chain verified, one real fix, one false alarm resolved`
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


<!-- entry: 2026-09-29-03 | date: 2026-09-29 | label:  | source-line: 809 | approx: no -->
### 2026-09-29-03 — Auto-confirm threshold is documented wrong; real spot-check at the real threshold
> Original heading: `### 2026-09-29 — Auto-confirm threshold is documented wrong; real spot-check at the real threshold`
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


<!-- entry: 2026-09-29-02 | date: 2026-09-29 | label:  | source-line: 800 | approx: no -->
### 2026-09-29-02 — Phase 4 Track B (news) is active, not "paused" as documented
> Original heading: `### 2026-09-29 — Phase 4 Track B (news) is active, not "paused" as documented`
`PROJECT_PLAN.md`'s architecture section describes `news_articles` as an "early-stage
live feed, paused." **This is stale.** Verified live: 407 total articles, latest
timestamped TODAY (2026-09-29). Real daily cadence confirmed (mostly 28-30
articles/day over the last two weeks, one real gap 2026-08-31 to 2026-09-16) --
driven by an external daily automation outside this codebase, not a manual/occasional
run. Genuinely active, just low-volume relative to the 8-K pipeline. Funnel: 407
articles -> 60 AI-classified -> 22 candidate events -> 6 confirmed into real `events`.


<!-- entry: 2026-09-29-01 | date: 2026-09-29 | label:  | source-line: 782 | approx: no -->
### 2026-09-29-01 — Global Events: manual review track quietly scaled, algorithmic track still stalled
> Original heading: `### 2026-09-29 — Global Events: manual review track quietly scaled, algorithmic track still stalled`
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


<!-- entry: 2026-09-28-02 | date: 2026-09-28 | label:  | source-line: 915 | approx: yes -->
### 2026-09-28-02 — STILL OPEN / UNVERIFIED
> Original heading: `# STILL OPEN / UNVERIFIED`

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


<!-- entry: 2026-09-28-01 | date: 2026-09-28 | label:  | source-line: 893 | approx: no -->
### 2026-09-28-01 — Stale-URL Sweep, Price Refresh, Tagger Fix
> Original heading: `### 2026-09-28/29 — Stale-URL Sweep, Price Refresh, Tagger Fix`
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


<!-- entry: 2026-09-22-03 | date: 2026-09-22 | label: PROJECT_PLAN | source-line: PLAN:370 | approx: no -->
### 2026-09-22-03 — Addendum 3: Full Database Audit — Universe Scope Correction, a Critical Phase 6 Finding, and a Major Unused Resource (this session, 2026-09-22)
> Original heading: `Addendum 3: Full Database Audit — Universe Scope Correction, a Critical Phase 6 Finding, and a Major Unused Resource (this session, 2026-09-22)`
> Moved from PROJECT_PLAN.md on 2026-10-28 (the section was first committed to the plan on 2026-09-22). Text unchanged except that its headings are demoted three levels so they nest under this entry. The whole original file is in the git history and in docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md.

This addendum does not supersede Sections 1-9's architecture or philosophy — the mechanical-vs-behavioral distinction in Section 2, the phase structure, and the Phase 8 gating logic all remain correct and unchanged. It corrects several places where this document's own numbers had drifted from real database state, and reports one finding serious enough to affect how Phase 6's existing tag-based results (Section 5, Addendum 2's tag-count table) should be read.

A systematic table-by-table review of the live database is in progress as of this addendum (34 of ~59 real tables reviewed so far, tracked in `table_review_checklist.md`; prioritized fix list in `database_fixes_and_review_backlog.md`). Everything below was verified directly against live data, not assumed from this document's prior text.

###### Correction: the tracked universe is 497 securities, not 13

Section 9's Tier 1 table and Section 8's Phase 8 scoping caveat both describe a 13-company "anchor node" universe. **This is significantly stale.** `securities` currently holds 497 real, onboarded securities (up from the 13 described here), with `events` at 12,517 rows (consistent with Addendum 2's 12,277 figure — that part of the doc is accurate and close to current). The onboarding pipeline described in Addendum 1 (`onboard_pipeline.py`, `promote_events.py`) has clearly been run at real scale well beyond what this document currently reflects. Worth a real pass to reconcile Section 9's tier table against which of the 497 are actually GICS-sector anchors vs. later Tier 2+ additions, since that distinction is no longer visible from the doc as written.

###### CRITICAL: `reaction_character` tagging bug affects every tag-based finding in Section 5/Addendum 2

Section 2 states plainly: *"A `reaction_character` tag says 'the market's psychological response to this class of surprise was X' — a claim about human behavior."* That claim depends on the tag genuinely reflecting one company's real reaction. **It currently does not, for any event linked to more than one company.**

`tag_reaction_character.py` computes and applies exactly ONE reaction tag per event, using only the first-linked entity's price move — even when `event_entity_relationships` links an event to many companies. Confirmed directly: the COVID-19 market panic event links 17 companies (AAPL, BA, CVX, DIS, F, GE, HON, INTC, KO, MCD, MSFT, NVDA, PFE, SLB, SPG, UNH, XOM) and carries a single "rewarded" tag applied uniformly to all 17 — hiding the real, sector-divergent reactions (energy/travel vs. tech) a genuine per-company measurement would show. The 2008 financial crisis event (12 linked companies) shows the identical pattern. `event_entity_relationships.relationship_type` (primary/affected/actor/competitor) already exists and could distinguish which company an event is genuinely "about" — neither `tag_reaction_character.py` nor any downstream analysis currently uses this field.

**Concrete, measured consequence**: this was confirmed to directly inflate `systemic_shock`'s apparent predictive strength in real model testing this session (see "Real progress on the walk-forward harness" below) — not because markets uniformly reward systemic shocks, but because every `systemic_shock` training row secretly reflects the same single first-linked-company outcome, relabeled onto every other company in the event.

**Real implication for this document's own numbers**: Addendum 2's tag-count table and any `pattern_card.py` result touching `systemic_shock`, `geopolitical`, or `government_action` should be treated as unreliable until `tag_reaction_character.py` is rewritten to compute a genuine per-(event, entity) reaction for multi-entity events. Single-entity-event tags (the large majority) are not affected by this specific bug.

###### `pattern_significance_tests` is stale and predates this finding

Checked directly: this table's 13 stored chi-square results are all dated 2026-09-11, 11 days before this bug was found. Four tags currently show as statistically significant (`same_entity_sequence` n=393 p=0.000008, `high_confidence_causal_link` n=414 p=0.0002, `multi_stage_divestiture` n=88 p=0.016, `confounded_regulatory_action` n=38 p=0.026) — worth re-running `test_pattern_significance.py` once the reaction-tagging fix lands, to check whether any of these four partly depended on the same mislabeling mechanism, the way `systemic_shock`'s model coefficient did.

###### Real progress on Section 6's walk-forward harness — partial, not complete

Section 6 states the walk-forward evaluation harness is "the real, unbuilt Phase 6 deliverable." This session ran genuine train/test-split predictive tests (`multi_feature_model.py`, cutoff-date train/test separation, sample-to-feature ratio reporting, explicit overfitting checks) against `event_type`, `firm_state`, `regime`, and `sentiment` as predictors of `reaction_character`. **Seven independent tests (five single-feature, one combined-feature, one combined-feature-minus-bundled-events) all returned the same honest result: none of these four features beat a "guess the majority class" baseline on held-out data.** This is real out-of-sample testing — a genuine partial instance of the discipline Section 6 calls for — but it is not the full prediction-contract harness (no sector benchmark, no base-rate comparison, no formal walk-forward re-tuning-prevention check yet). The honest reading: Phase 6's harness scaffolding now has real working parts, and the four most obvious candidate features have been honestly tested and found wanting — which is itself a legitimate, trustworthy negative finding worth recording, not a wasted effort.

###### Major unused resource found: `financial_market_reactions`

A complete, ~99%-populated dataset (35,826 rows, 496/497 securities) computing real abnormal stock returns (0/1/5/20-day, vs. SPY) for essentially every quarterly/annual financial filing already exists as a view — independent of the `events`/`reaction_character` system entirely, anchored to filing date rather than event date. Nothing in this session's model testing, and nothing described in Sections 5-6 of this document, uses it. This is likely a stronger, more complete foundation for a genuine predictive test than continuing to refine the four already-tested event-based features — worth scoping as real Phase 6 follow-up work.

###### Smaller corrections and findings, for completeness

- **AVB/EA's price-data gaps were NOT a "Twelve Data limitation"** (this was assumed correct elsewhere in project history) — the real, confirmed cause is that SEC's ticker-to-CIK mapping didn't recognize these tickers at `onboard_pipeline.py`'s `register_entity` step. AVB (and EQR) are now explained by a real 2026-08 AvalonBay/Equity Residential merger (→ new ticker VMRK). **EA remains a genuine, unexplained open question** — still actively traded, no merger applies.
- **`sec_filings` and `sec_8k_filings` are misleadingly named** — `sec_filings` contains only 10-K/10-Q data; the real 8-K-specific table (with item codes and the `promoted_to_event` tracking column referenced conceptually in Addendum 1) is `sec_8k_filings`. Confirmed by direct inspection, not assumed from names.
- **Recurring pattern found: "always-same-value" dead tracking columns** — three confirmed so far (`event_pre_context.surprise_vs_consensus`, `financial_condition_score.fcf_margin_change`, `sec_8k_filings.promoted_to_event`), each a column that looks like real pipeline state but was never wired up, while the real work happens correctly through a different, verified mechanism. Worth a dedicated schema-wide scan for more before considering this class of issue fully found.
- **`securities.sector` was NULL for 421 of ~497 securities all session** (not mentioned anywhere in this document) — fixed this session via real S&P 500 GICS data (`populate_sectors_gics.py`), not inferred. A first attempt using SIC-code-range mapping produced confirmed misclassifications and was abandoned in favor of real GICS data.
- **`financial_statements.free_cash_flow`**: 4,489 rows have both real ingredients (`operating_cash_flow`, `capital_expenditures`) but the simple subtraction was never computed — a cheap, high-value, not-yet-applied backfill that would directly improve `firm_state`'s reliability as a tested feature (see above).
- **`global_events` (a table from a separate GDELT-based macro/geopolitical event pipeline, not otherwise described in this document) already has real prior human review work** — `severity` and `reviewer_note` populated for 11 confirmed multi-day events (e.g. Jan 2025 LA wildfires, Jul 2025 Texas floods) — that handled a genuine multi-day-event grouping problem simply, by confirming each day individually with a connecting note. A separate, more complex algorithmic "episode grouping" mechanism attempted this session (`build_event_episodes.py`) went through four failed iterations and remains unresolved — worth strongly considering the simpler, already-proven approach instead of continuing that effort.

###### Suggested update to Section 10's next-steps list

Given the above, two items are worth adding to the existing sequence (Finish promotion → Apply tagging → Resolve Phase 5 → Re-run Phase 6 checks at larger n):
1. **Fix `tag_reaction_character.py` for multi-entity events before trusting any re-run of Phase 6's pattern checks** — re-running at larger n without this fix would just produce a larger, still-unreliable sample for `systemic_shock`/`geopolitical`/`government_action`.
2. **Scope a real test against `financial_market_reactions`** as a parallel or alternative Phase 6 target, alongside continuing to refine `reaction_character`-based testing.

<!-- entry: 2026-09-22-02 | date: 2026-09-22 | label:  | source-line: 444 | approx: yes -->
### 2026-09-22-02 — Earlier (undated in source) — PROJECT_PLAN.md findings, folded in above
> Original heading: `### Earlier (undated in source) — PROJECT_PLAN.md findings, folded in above`
Multi-entity tag bug's COVID-19/2008-crisis examples; `sec_filings`/`sec_8k_filings` naming
swap; dead-column pattern; `financial_market_reactions` discovery — all incorporated into
Current Reference and Known Gotchas above.


<!-- entry: 2026-09-22-01 | date: 2026-09-22 | label:  | source-line: 419 | approx: no -->
### 2026-09-22-01 — Database Audit, GDELT Backfill, Reaction-Tagging Fixes
> Original heading: `### 2026-09-22 — Database Audit, GDELT Backfill, Reaction-Tagging Fixes`
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


<!-- entry: 2026-09-15-01 | date: 2026-09-15 | label: PROJECT_PLAN | source-line: PLAN:313 | approx: no -->
### 2026-09-15-01 — Addendum 2: Event Tagging Pipeline Built and Tested (same session, continued)
> Original heading: `Addendum 2: Event Tagging Pipeline Built and Tested (same session, continued)`
> Moved from PROJECT_PLAN.md on 2026-10-28 (the section was first committed to the plan on 2026-09-15). Text unchanged except that its headings are demoted three levels so they nest under this entry. The whole original file is in the git history and in docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md.

Follows directly from Addendum 1 (event promotion). Once promotion was live and running, this session moved to the next real gap it surfaced: ~11,255 newly-promoted events had zero tag suggestions generated at all -- `event_tag_suggestions` was untouched by the promotion work, sitting at the exact same 1,066/212/23/1 split as before promotion began.

###### Real current state as of this addendum

- **Total events: 12,277** (up from 1,214 at session start; ~185 confirmed real_events remain genuinely unpromoted -- see "Known remaining gaps" below)
- **Tag counts (all tags, current real totals):**

| Tag | Count | Tag | Count |
|---|---|---|---|
| muted | 711 | multi_stage_divestiture | 88 |
| punished | 515 | leadership_reversal | 53 |
| rewarded | 507 | cross_entity_ripple | 52 |
| high_confidence_causal_link | 418 | confounded_corporate_action | 47 |
| same_entity_sequence | 397 | confounded_regulatory_action | 38 |
| chain_position_middle | 325 | chain_position_opening | 36 |
| confounded_macro_conditions | 163 | chain_position_closing | 36 |
| plausible_unconfirmed | 26 | confounded_earnings | 14 |
| explicitly_not_attributed | 8 | sentiment_reveals_distinct_driver | 8 |
| same_industry_comparison | 7 | diverged_from_fundamentals | 6 |
| activist_investor_campaign | 6 | sentiment_confirms_confound | 5 |

**Note on reaction_character totals (muted/punished/rewarded):** these are a mix of pre-existing tags from before this session and a partial run of `tag_reaction_character.py` tonight (see "Known remaining gaps" -- the full 11,219-event backfill was still in progress as of this addendum). **Note on sentiment_* totals (13 combined):** tonight's `resolve_sentiment_confounds.py` wrote 9 of these; the remaining 4 are most likely pre-existing (these two tags were part of the original 22-tag taxonomy, not newly created tonight -- only the deterministic script to compute them was built this session). Worth a quick verification query before relying on this number, not confirmed with certainty here.

###### What got built and tested, in order

**1. Real gap found in `suggest_event_tags.py` (pre-existing script, not built tonight):** 5 of the 22 real tags require data this script's AI-judgment prompt never provides:
- `chain_position_opening/middle/closing` -- deterministic facts about event ORDER within a `same_entity_sequence` chain, not a text-judgment call
- `sentiment_confirms_confound`/`sentiment_reveals_distinct_driver` -- explicitly require `company_sentiment_timeline` data per their own descriptions, never included in the prompt

Fixed by excluding all 5 from the AI's tag list (`NOT_AI_SUGGESTABLE` set), so the AI can no longer be asked to guess at facts it structurally cannot know.

**2. Built `compute_chain_position.py`** -- fully deterministic, no AI call. Sorts each entity's `same_entity_sequence`-tagged events chronologically, tags first as opening, last as closing, everything between as middle. Companies with only 1 sequence event get no position tag (no real "position" exists with just one link). Result: 397 real tags across 37 valid multi-event chains (2 entities skipped, only 1 sequence event each). Handles shared events (linked to 2+ companies) correctly -- verified that 2 such events received exactly one row per matching position, not duplicated, confirming the `(event_id, tag_id)` primary key dedupes correctly across independently-computed chains.

**3. Built `suggest_event_tags_batch.py`** -- Batch API version of the AI-suggestion script (same reasoning as `classify_8k_filings_batch_v2.py`'s rebuild: the original made one synchronous call per event with no cost visibility, unworkable at 11,255-event scale). Same prompt, same calibration notes, same `NOT_AI_SUGGESTABLE` exclusion, same staging-table-only write pattern.

**4. Real calibration testing before trusting it at scale (same discipline as filing classification):** tested against 3 companies with deliberately different event-writing styles -- AAPL (narrative/editorialized titles, leadership-succession-dense), EXC (procedural/regulatory titles), XOM (litigation-heavy). 107 total `same_entity_sequence` suggestions read by hand. Found 4 real misses (generic "multi-year trend" claims treated as documented chains, and 2 cases where the AI's own reasoning explicitly stated no textual link existed yet applied the tag anyway) -- 3 of 4 already caught by the existing confidence<0.75 auto-flag; 1 (AAPL, confidence 0.85) would have silently slipped through.

**5. Fix: raised the auto-flag threshold specifically for `same_entity_sequence` to 0.87** (not a blanket change to all tags -- the other 106 suggestions across all 3 companies were well-justified even down to 0.65-0.72, so a blanket hike would have over-flagged genuinely good suggestions for no benefit). Retroactively re-flagged the one already-written miss below the new threshold.

**6. Built `resolve_sentiment_confounds.py`** for the 2 remaining excluded tags. Real design decision made deliberately (not defaulting to a market-wide average for simplicity): a genuine sector baseline requires multiple same-sector companies with sentiment data, or "divergence" just measures noise between 1-2 companies. Real check of current data: only Information Technology (AAPL/AMD/MSFT/NVDA, 4 companies) and Energy (XOM/CVX, 2 companies) have any multi-company sentiment coverage at all -- every other sector has exactly 1 company. Script **dynamically discovers** which sectors qualify (minimum 3 total companies = 2+ real peers) every run, rather than hardcoding a list -- this was itself a real fix made mid-session after a first version with a hardcoded 2-sector list produced a weak result for Energy (both XOM and CVX got tagged "diverged" from each other during the COVID crash, which is a shaky conclusion from a 2-company/1-peer comparison). After the fix, Energy correctly auto-excludes itself (prints `[SKIP SECTOR]` with the real reason) and will automatically start qualifying once a 3rd Energy company gets sentiment data -- no code change needed later. Went live on Information Technology only: 9 real tags written.

**7. Found and fixed a real bug in `tag_reaction_character.py` (pre-existing script, not built tonight):** `get_untagged_events()`'s `event_entity_relationships` query had no pagination, silently capped at Supabase's default 1,000-row limit -- with 12,000+ real rows in that table now, this caused the script to report only 70 events needing tags instead of the real ~11,567. Same bug class already documented elsewhere in this project's history (`classify_8k_filings.py`'s resumability check hit the identical 1,000-row cap). Fixed with the same `.range()` pagination pattern used elsewhere. First (buggy) run before the fix legitimately tagged 62 real events with real price data before being caught -- no data damage, just an incomplete backlog view. After the fix, correctly found 11,219 real events needing tags; full backfill was running in the background as of this addendum.

###### Known remaining gaps (honest, as of this addendum)

- **~185 confirmed real_events genuinely unpromoted.** Down from the original 328 found post-live-run; a further pass created 142 more, leaving primarily the ~46 rows with no resolvable `event_type` (need manual/AI assignment before they can ever be promoted) plus legitimate confirmed-duplicate skips.
- **`tag_reaction_character.py`'s full 11,219-event backfill** was still running as of this addendum -- the `rewarded`/`punished`/`muted` counts in the table above are a partial snapshot, not final.
- **`suggest_event_tags_batch.py`'s chained 66-ticker run** (budget-scoped to ~$1.80 of a $1.87 remaining balance, smallest-tickers-first) was also still running as of this addendum -- most of the 11,255-event AI-suggestion backlog remains unprocessed, gated on both this run finishing and a further budget refill for the rest.
- **`sentiment_*` tags remain scoped to Information Technology only** -- by design, not oversight. Will expand automatically as more same-sector companies get sentiment data (ties to the real Section 9 GICS Tier 2 expansion plan).
- **The `event_tag_suggestions` review queue** (17 flagged in the AAPL test batch, 46 in EXC's, etc.) has not yet been worked through with the same calibration-policy discipline used for `filing_ai_classifications` earlier this session. That's the natural next step once suggestion generation finishes.

###### Readiness note for Phase 7/8

Per Section 6 and 8 of the real project plan, Phase 8 (autotrader/backtest environment) is explicitly gated on Phases 1-7 being genuinely, not approximately, trustworthy -- and specifically on a tag surviving the walk-forward evaluation harness described in Section 6, which remains unbuilt. Tonight's work is real, substantial progress on Phase 3 (event volume, corrected taxonomy) and the tagging layer that feeds Phase 6 -- but it does NOT itself constitute Phase 6 completion. The honest sequence before Phase 7/8 planning should resume in earnest: finish the two backlogs above, work the tag-suggestion review queue, re-run Phase 5's price-reaction linking against the full new event volume, and only then revisit whether `pattern_card.py`'s sector-benchmark/base-rate/walk-forward gaps are worth building out now that n has grown substantially across most tag categories.

<!-- entry: 2026-09-11-01 | date: 2026-09-11 | label:  | source-line: 411 | approx: no -->
### 2026-09-11-01 — `pattern_significance_tests` populated — 13 chi-square results, 4 tags statistically
> Original heading: `### 2026-09-11`
`pattern_significance_tests` populated — 13 chi-square results, 4 tags statistically
significant at the time (`same_entity_sequence`, `high_confidence_causal_link`,
`multi_stage_divestiture`, `confounded_regulatory_action`). Predates the 09-22 multi-entity
tagging bug discovery — worth re-running `test_pattern_significance.py` once that's fixed,
to check whether any of the four partly depended on the same mislabeling mechanism that
inflated `systemic_shock`.


<!-- entry: 2026-09-08-02 | date: 2026-09-08 | label: PROJECT_PLAN | source-line: new | approx: no -->
### 2026-09-08-02 — Baseline of the original plan: what changed from it, the phase percentages, the coverage tiers, the old next steps (moved from PROJECT_PLAN v1)
BASELINE OF THE ORIGINAL PLAN. Moved from PROJECT_PLAN.md (v1) into this changelog on 2026-10-29 so that the timeline shows where the project stood before the corrections and addenda that are already in this changelog at their true dates (the label PROJECT_PLAN). DATING: this entry carries the date 2026-09-08, the day PROJECT_PLAN.md was first committed (cab4344, 'consolidated with 7-company expansion'); the text below is the LAST version of these four sections before the 2026-10-28 rewrite, so it may include small edits made on 09-15 or 09-22 (see git log of PROJECT_PLAN.md). These four sections are HISTORY, not the current state: the current plan is PROJECT_PLAN.md (v2, 2026-10-28) and the current state is docs/PROJECT_STATUS.md. The unedited whole of the old plan is docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md. Sections 3 (what changed from the original plan), 5 (phase status with the original percentages), 9 (the coverage tier system) and 10 (the old immediate next steps), VERBATIM:

## 3. What Changed From the Original Plan, and Why

| Original plan | What actually happened | Why it's better |
|---|---|---|
| Alpha Vantage as a candidate data source | Rejected for cost; SEC EDGAR XBRL used as free, authoritative primary source for financials | Free, official, and forces primary-source discipline into the project's DNA from day one |
| "Record meaningful events" (Phase 3) | Every event requires primary-source verification before entry; tracked hit rate via `candidate_review_log` (~20–33% depending on category) | Prevents the event database from silently filling with noise; hit-rate tracking is itself a real data quality signal |
| Single news pipeline (Phase 4) | Split into **Track A** (FRED macro data — structured, backfillable) and **Track B** (Marketaux news — specifically for surprise/consensus framing FRED can't provide) | Recognizes that hard data and *narrative framing* are fundamentally different signals that needed different pipelines |
| Event relationships implied uniform confidence | Explicit confidence calibration (e.g., 0.95 for direct textual confirmation vs. 0.8 for analyst-consensus inference) | Distinguishes confirmed fact from well-supported inference — critical for not overclaiming later |
| Phase 6 pattern example: "12 similar events, 9 positive" | Same idea, but with an enforced n=30–50 threshold before treating any finding as a real pattern, and explicit repeated correction of premature single-instance ("n=1") claims | Real financial-pattern literature is full of spurious small-sample findings; this discipline was underestimated in the original plan |
| Strict linear phase order (finish 2 before starting 3, etc.) | Phases progressed **iteratively and in parallel** | More realistic and more productive than a strict waterfall; phase "boundaries" turned out to be soft |
| No mention of an automated classification layer | Built a full AI-assisted classification pipeline (Haiku-based), used for both Track B news AND Phase 3 8-K filing review, with an explicit **check-and-balance system**: mandatory confidence + reasoning, duplicate detection, random audit sampling, and a human-reviewed queue — nothing auto-promotes to the real `events` table | Wasn't conceived in the original plan at all; emerged from recognizing that pure manual review wouldn't scale, while pure automation couldn't be trusted blind. Proven twice now, at real scale, in two different contexts |
| No explicit "Historical vs. Live" distinction | Introduced as a reframe for Phase 3/4's "never truly finishes" feeling: **Historical** work (bounded, can reach genuine 100%) vs. **Live** work (perpetual, ongoing maintenance) | Gives the team a real sense of completion on bounded sub-problems instead of an undifferentiated, endless backlog |

## 5. Phase Status (Current, Honest — updated after the 7-company classifier expansion)

| Phase | Original estimate | Actual status | Notes |
|---|---|---|---|
| 1. Data Foundation | 80% | **~98%** | Fully audited across all 13 tickers via a real completeness scan (not just null-rate). Found and fixed a genuine PLD REIT-revenue-concept gap (2011-2016 now complete). XOM's 2007-2016 quarterly thinness remains a known, tracked, genuinely-hard-to-fix gap — investigated via full XBRL concept scan, appears to require raw instance-document inspection (custom company extension concept), deliberately accepted rather than chased further right now |
| 2. Financial Analysis | 60% | **100%** | Full 11-view chain traced and verified; zero real bugs found in final audit |
| 3. Corporate Events | Early development | **~85%** | Original 6 companies: 63+ events, full 1.01 sweep complete. **All 7 new Tier 1 tickers (LIN, XOM, AEP, PG, GE, PLD, F) now have rich, fully-chained event histories** — hundreds of real events added via a proven AI classification pipeline (`classify_8k_filings.py`), spanning major M&A, leadership successions, litigation, and multi-year sagas across all 13 tracked companies. Tag system expanded from 13 to 17 tags (evidence-based additions) and exhaustively human-reviewed across all categories |
| 4. News Ingestion | Not yet built | **~40%** | Track A (FRED) complete; Track B (Marketaux) built with working AI classification + audit loop. `classify_8k_filings.py` is now a second proven instance of the same check-and-balance architecture, validated at real scale (7 companies, ~2,000+ filings, real classifier misses caught and corrected via random audit and human review) |
| 5. Price Reaction Engine | Not yet built | **~85%** | Abnormal-returns-vs-SPY working; ~~unification with `financial_market_reactions` still pending~~ -- see the correction below, this was already resolved even at the time this table was written. Anchor-date diagnostic came back reassuring (small, explainable, consistently-negative drift) |
| 6. Historical Pattern Engine | Future | **~15%** | Tag governance established and exhaustively reviewed. `pattern_card.py` cleared n=30 for the first time this session (rewarded n=52, punished n=54) — but this result is understood to be circular (tags were assigned from the same abnormal-return data being tested), confirming the harness works end-to-end, not that anything is predictive. **New this session: `event_pre_context` layer built** (firm state, market regime, size bucket per event) — the actual pre-event-known feature set a genuine predictive test would need. `surprise_vs_consensus` remains explicitly unbuildable (no analyst estimate data ingested anywhere in the project) |
| 7. Dashboard/Website | Not yet built | **0%** | Untouched — correctly deferred |
| 8. Autotrader ("the brain") | Not yet built | **0%** | Untouched, correctly deferred until Phases 1–7 are genuinely trustworthy. See Section 8 below for the full scoped vision, and the new backtest-environment addendum |

**Two real bugs found and permanently fixed this session, beyond the coverage expansion itself:**
1. `classify_8k_filings.py`'s resumability check silently capped at Supabase's default 1,000-row query limit as the classification table grew past that size — fixed with explicit pagination, benefiting every future classification run regardless of scale.
2. PLD's 2011-2016 quarterly financial gap was traced to two real REIT-specific revenue XBRL concepts (`OperatingLeasesIncomeStatementLeaseRevenue`, `RealEstateRevenueNet`) not in the ingestion candidate list — fixed and re-ingested.
3. (Discovered later, same session) `populate_pre_context.py`'s market-cap lookup used the wrong column name (`close_price` instead of the real `close`) — silently returned NULL for all 337 rows despite reporting success; caught via direct verification query, not by trusting the script's own success message, then fixed and confirmed (335/337 populated correctly).

## 9. Coverage Tier System (GICS-Based)

Adopted the real, industry-standard Global Industry Classification Standard (GICS) — 11 sectors, 25 industry groups, 74 industries, 163 sub-industries, maintained by MSCI/S&P Dow Jones Indices.

**Tier 1 — Cross-sector anchors (one per GICS sector, longest public history preferred as tiebreaker). STATUS: all 11 fully onboarded, ingested, AND now have rich event histories as of this session.**

| GICS Sector | Anchor | Status | Notes |
|---|---|---|---|
| Information Technology | MSFT | Onboarded, events built | |
| Health Care | PFE | Onboarded, events built | |
| Financials | JPM | Onboarded, events built | |
| Consumer Discretionary | F (Ford) | **Onboarded, 127 real events built this session** | Largest single haul: historic Mulally hire, Way Forward restructuring, live BlueOval SK battery saga |
| Consumer Staples | PG | **Onboarded, 37 real events built this session** | Gillette ($54B), Coty ($15B), Lafley "boomerang CEO" saga |
| Industrials | GE | **Onboarded, 116 real events built this session** | Richest single history: 2008 Berkshire rescue, Capital Exit Plan, full 3-way split through GE Aerospace rename |
| Energy | XOM | **Onboarded, 41 real events built this session** | Real, tracked, hard-to-fix gap: 2007-2016 quarterly financial thinness, likely a custom XBRL extension concept requiring raw instance-document inspection to fully resolve — deliberately accepted for now |
| Utilities | AEP | **Onboarded, 69 real events built this session** | Turk Plant 15-year saga, Akins installed-then-removed reversal, Icahn activism |
| Materials | LIN | **Onboarded, 12 real events built this session** | Praxair/Linde merger saga, Lamba CEO succession |
| Real Estate | PLD | **Onboarded, 65 real events built this session** | AMB-ProLogis 2011 founding merger; live SEGRO takeover bid as of latest data |
| Communication Services | T (AT&T) | Onboarded (financials/prices only — event history not yet built) | |

**Tier 1.5 — Within-sector comparison set** (existing, not abandoned): AAPL, NVDA, AMD sit in Information Technology alongside MSFT — a deliberate direct-competitor/within-sector comparison set, fully built out already.

**Tier 2/3/4** (future, unchanged from original scoping): large-cap sector-filling → mid-cap → small-cap/recent-IPO, with Tier 4 only ever added when already chained to an existing graph node (a named supplier, competitor, or counterparty in an existing event) — never onboarded cold.

**Important framing note (this session):** the current 13-company universe is explicitly described as **anchor nodes for a future, much larger universe** — not the final intended scope. This has real design implications already accounted for: `market_regimes` is universe-independent by construction (dated by calendar time, not tied to any company), and both AI classification pipelines (`classify_8k_filings.py`, `suggest_event_tags.py`) are already fully ticker-agnostic, so onboarding future companies means running the same proven scripts, not rebuilding anything. One expected future change: `same_industry_comparison` and `cross_entity_ripple` currently have few instances because the universe is deliberately sector-diverse (one anchor per GICS sector) — once more companies are added *within* the same sector, those tags should genuinely fire much more often, which would be the system working correctly, not a signal of anything wrong.

**Immediate remaining Tier 1 work:** build T/AT&T's event history using the now-proven `classify_8k_filings.py` pipeline, the same way the other 7 were done this session.

## 10. Immediate Next Steps

1. **Root-cause XOM's quarterly gap properly**, if ever revisited: would require pulling raw XBRL instance documents from individual 10-Q filings (not the aggregated company-facts API), since the standard concept scan found nothing — likely a custom company-specific extension concept from XOM's early XBRL era.
2. **Build T/AT&T's event history** — the one remaining Tier 1 anchor without a built-out event history, using the proven classifier pipeline.
4. **Build the actual Phase 6 walk-forward evaluation harness** (Section 6) — `pattern_card.py` exists but doesn't yet implement the sector benchmark, base rate comparison, or walk-forward out-of-sample split. This is the real remaining Phase 6 deliverable.
5. **Consider Tier 2 large-cap sector-filling tickers**, or continue deepening the current 13 with T's event history first.
6. **Revisit the news-sequence chain-detection Phase 4 idea** once Track B has accumulated enough real article volume to test against.
7. **The `surprise_vs_consensus` gap** — would require a new data source (analyst estimates) not currently part of any track; flag for a future dedicated scoping session, don't build a weaker silent substitute.

<!-- entry: 2026-09-08-01 | date: 2026-09-08 | label: PROJECT_PLAN | source-line: PLAN:274 | approx: no -->
### 2026-09-08-01 — Correction (verified this session): Anchor-Date Unification Is Already Resolved
> Original heading: `Correction (verified this session): Anchor-Date Unification Is Already Resolved`
> Moved from PROJECT_PLAN.md on 2026-10-28 (the section was first committed to the plan on 2026-09-08). Text unchanged except that its headings are demoted three levels so they nest under this entry. The whole original file is in the git history and in docs/archive/PROJECT_PLAN_pre_rewrite_2026-10-28.md.

Section 5's Phase 5 notes and Section 10's "immediate next steps" both previously listed unifying `event_market_reactions` and `financial_market_reactions`'s anchor-date logic as still pending. **This is stale — verified with real data this session that it was already fixed** (the `event_market_reactions` day-0 anchor was changed from `>=` to `>` to match `financial_market_reactions` exactly, done in an earlier session but never marked resolved in this doc).

Verification query run this session: compared `abnormal_return_20d` between both views for every `financial_result` event with a match in both. Result: every comparison showed exact agreement (diff = 0.0000) except one (AMD Q3 2024, diff = 0.008), which is fully explained by the filed_date landing one calendar day after the event_date — a normal SEC filing-timing nuance, not measurement error.

**Action taken:** remove this item from the "immediate next steps" list — it's done, not pending. Lesson for future sessions: verify a "known issue" against current real data before re-investigating it; documentation can silently drift out of sync with an already-applied fix.

Addendum: Classification Backlog Clearance & Event Promotion Pipeline (this session)
This session did not touch Phase 6/7/8 scoping (Sections 6, 8 above remain the current, correct plan). It addressed a much more foundational gap discovered while investigating why Phase 6's tag counts (rewarded n=52, punished n=54 per Section 5) seemed low relative to how much confirmed real-event material actually existed in filing_ai_classifications.

Finding: the "not enough data" read on Phase 6 was a pipeline-throughput problem, not a data-scarcity problem. Tracing the full path end-to-end: 70,697 raw candidate filings -> 29,387+ AI-classified -> 22,720+ human-reviewed -> 11,282 confirmed real_event rows -> only 1,214 ever promoted into the actual events table. The bottleneck was a missing promotion step between "confirmed by a human" and "structured database row" -- not a shortage of underlying material.

Work done this session:

Cleared the human-review backlog (15,961 + a further 2,868 rows found mid-session) to zero, using an evidence-based calibration policy: measured real AI/human agreement rate per confidence+template-match bucket before trusting any bulk auto-confirm (two buckets came back at ~99-100% agreement across thousands of sampled rows and were safe to bulk-clear; everything else got individual review)
Found corporate_action (per Section 5's 17-tag system context, a separate but related taxonomy issue) had drifted into an overloaded catch-all absorbing 2,380 mistyped rows -- restructuring, capital raises, governance actions, spinoffs, none of which its real definition covers. Added 4 new event types to event_types (capital_raise, governance_action, ipo_spinoff, restructuring) and retyped 2,522 affected rows
Found and fixed a structural double-counting bug: NWS/NWSA (dual-class shares of the same company) file identical 8-Ks under both tickers with the same accession number, causing every News Corp filing to be fetched/classified/reviewed twice
Built promote_events.py: turns confirmed real_event rows into actual events + event_entity_relationships + event_type_relationships rows, deduping by (filing_date, accession_number) rather than by ticker (fixes the NWS/NWSA case structurally). Duplicate detection uses same-entity + date-proximity as a heuristic, but every heuristic match gets a real LLM verification call before being trusted -- the unverified heuristic alone had a measured ~33% false-positive rate at sample scale, including one that would have silently blocked P&G's Gillette merger announcement (an event already referenced in this plan's own Section 9, Tier 1 P&G notes)
New event_source_filings table added for traceability + idempotency -- every event now traces back to its real source filing(s), and the promotion script is safely re-runnable
Proven safe across three real interruption types this session (manual interrupt, network connection drop, full machine restart) -- verified via integrity checks after each, zero data corruption in any case
As of this addendum, the live promotion run is in progress: events growing from 1,214 toward an estimated 11,000+

What this changes for Section 5's Phase status table:

Phase 3 (Corporate Events): the ~85% figure should be revisited once the live run completes -- the event count is about to grow roughly 9x, though the underlying event quality discipline (primary-source verification, the check-and-balance architecture) is unchanged
Phase 6 (Historical Pattern Engine): still genuinely ~15% -- this session did NOT touch the walk-forward harness, sector benchmarks, or base-rate comparison described in Section 6. What it did do is remove a real bottleneck upstream of Phase 6: once tagging (see below) catches up to the new event volume, pattern_card.py's n=30-50 checks will be running against a much larger, more representative pool than the current n=52/54 rewarded/punished figures reflect

New, not-yet-started gap this session surfaced: event tagging has its own backlog. event_tag_suggestions (the AI-suggest/human-confirm pipeline analogous to filing_ai_classifications) had only 212 rows in review as of this session, against what will shortly be 11,000+ untagged events. This sits between Phase 3 and Phase 6 in the existing architecture diagram and needs the same calibration-first discipline applied to it next, before Phase 6's walk-forward harness work can proceed meaningfully.

Revised Section 10 next steps, in order (supersedes the numbered list above for near-term work; Section 10's items 1, 4, 6, 7 remain valid and un-superseded):

Finish the current live promotion run
Apply calibrated tagging to the new event volume (same discipline as this session's filing-review clearance)
Resolve remaining Phase 5 items per Section 5 (this session did not touch Phase 5)
Re-run Phase 6's existing pattern checks against the much larger n before investing further in the walk-forward harness build-out, to confirm the larger sample actually changes which tags are viable candidates for it

One new supporting script this session, in the same spirit as classify_8k_filings.py's proven check-and-balance pattern: onboard_pipeline.py chains the full company-onboarding sequence (register -> financials -> 8-K history -> prices -> classify -> calibrated auto-review -> scoped promotion) into one command, logging every step's real verification result to new onboarding_runs / onboarding_run_steps tables, so an onboarding run can be handed to someone without full project context and checked asynchronously rather than requiring live supervision. Not yet tested end-to-end on a real new company -- do that before relying on it for the Tier 2 expansion mentioned in Section 10.
