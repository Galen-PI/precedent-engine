# PREREG 2026-10-29: re-running the 15 proven flags on the cleaned data (gate G7)   (written BEFORE any outcome was computed)
# Registered by the assistant for Galen Pike on the template results/TEMPLATE_PREREG.md. The first version of this file did not follow the template and was refused by the pre-commit check; it was rewritten before any commit and before any result existed.
DATA AND USE RULE: the same universe and eras as the original tests (2026-10-13 to 2026-10-23): the exploration tickers only, the 160 sealed tickers are not touched in this pass. The cleaned event selection (event_analysis_set, 21,670 events, with the repaired ripple table) replaces the old one; every other input is unchanged. No price levels are used (every statistic is a return, a ratio, a coverage or a score), so the as-quoted levels addendum does not apply. This file covers the 15 PROVEN flags; the 21 leads and the Tier 1 nulls get their own registration.
ANCHOR: DATA. The old numbers and registered rules in flag_ledger and flag_ledger_evidence (the results of 2026-10-13 to 2026-10-23); the change in the data is stated below. Each predicted magnitude is the old one shifted by the expected effect of the cleaning (about 2.3% of events removed and 1.4% added, so an estimate should move by about a fifth of its standard error, plus a known direction: removing misdated duplicates tends to sharpen event effects); market-wide flags are predicted not to move at all.
TRIALS: confirmatory=15 descriptive=15 ledger_before=112    (15 flags re-run under their own rules; 15 descriptive looks are the with-and-without-the-508-exclusions reruns used to attribute any change; ledger_before = SELECT COUNT(*) FROM flag_ledger)
HURDLE: each flag passes by its OWN registered rule, unchanged (for example t>=2.5 in both eras with clean placebos for the FOMC flag; the multiplier, coverage and score lines stay as written in flag_ledger.pass_rule). The reference hurdle for a newly discovered effect is 3.0 (ANCHORS.md item 3); it does not apply, because this re-tests registered rules on cleaned data and discovers nothing. A flag that fails is a recommendation to demote it to lead, which is Galen's decision.
DECAY: forward_fraction=1.0 because the re-run uses the same sample period, so no out-of-sample decay is expected from the cleaning itself; decay belongs to the forward checks (the frozen forward tests, evaluated once after 2027-01-05), not to this re-run.
STANDARD TEST: each flag keeps its original method (event study against a matched baseline, interval-forecast coverage, walk-forward log score); this re-run changes the data, not the method. Three flags on market-wide data are POSITIVE CONTROLS (band_stress_scale_median, fomc_announcement_day_market_move, macro_oil_shock_energy_same_day): they must reproduce within the stated tolerance before any event-level result is read. Independent clusters (company, date) are reported beside rows. No new significance machinery is added.
PLACEBO: the registered placebos stay (the FOMC plus and minus 21-day placebo, the oil-shock sector placebos, the far-day placebo, the shuffled-habit placebo), plus a process placebo: the three controls, and an attribution run for every flag that moves by more than its predicted range, once with and once without the 508 exclusions, so a cleaning effect can be told from noise.
FORWARD CHECK: the January 2027 data (the runbook's ingestion steps) and the two frozen forward tests (evaluated once at runbook step 7); any flag that fails here is re-checked on the January data before its status changes.
PREDICTIONS: ranges are 80% intervals (33 numeric rows, so about 6.6 are expected to miss); the probability rows state whether a flag still passes its registered rule; scoring uses scripts/ops/score_predictions.py after the results. The last three rows are overall calls: all 15 pass 43% (the product of the per-flag probabilities), a control misses 9%, and 10 or more numeric rows miss 25% (a calibration check on my own intervals).
PRED-TABLE-BEGIN
# id | type | statement | point | lo | hi | level | anchor      (type: ratio, pct, diff or prob; level 80 or 95; anchor DATA <source>, LITERATURE ANCHORS#N, or NONE)
p1 | pct | band_stress_scale_median: lowest of the 12 era-by-bin coverage cells (old 89.63) | 89.63 | 89.55 | 89.71 | 80 | DATA flag_ledger_evidence
p2 | pct | band_stress_scale_median: highest of the 12 coverage cells (old 91.08) | 91.08 | 91.00 | 91.16 | 80 | DATA flag_ledger_evidence
p3 | ratio | band_stress_scale_median: interval score ratio C over B in 2020-2026 (old 0.983) | 0.983 | 0.981 | 0.985 | 80 | DATA flag_ledger_evidence
p4 | prob | band_stress_scale_median reproduces within tolerance and still passes (CONTROL) | 0.97 |  |  |  | DATA flag_ledger
p5 | ratio | fomc_announcement_day_market_move: day 0 ratio 2004-2014 (old 1.140) | 1.140 | 1.138 | 1.142 | 80 | DATA flag_ledger_evidence
p6 | ratio | fomc_announcement_day_market_move: day 0 ratio 2015-2026 (old 1.112) | 1.112 | 1.110 | 1.114 | 80 | DATA flag_ledger_evidence
p7 | prob | fomc_announcement_day_market_move reproduces within tolerance and still passes (CONTROL) | 0.97 |  |  |  | DATA flag_ledger
p8 | ratio | macro_oil_shock_energy_same_day: Energy amplification 2004-2018 (old 1.293) | 1.293 | 1.290 | 1.296 | 80 | DATA flag_ledger_evidence
p9 | ratio | macro_oil_shock_energy_same_day: Energy amplification 2019-2026 (old 1.319) | 1.319 | 1.316 | 1.322 | 80 | DATA flag_ledger_evidence
p10 | prob | macro_oil_shock_energy_same_day reproduces within tolerance and still passes (CONTROL) | 0.97 |  |  |  | DATA flag_ledger
p11 | ratio | earnings_role_bands_walk_forward: interval score ratio role over pooled 2013-2019 (old 0.869) | 0.869 | 0.855 | 0.883 | 80 | DATA flag_ledger_evidence
p12 | ratio | earnings_role_bands_walk_forward: interval score ratio role over pooled 2020-2026 (old 0.857) | 0.857 | 0.843 | 0.871 | 80 | DATA flag_ledger_evidence
p13 | pct | earnings_role_bands_walk_forward: tightest role-band coverage cell (old 88.5) | 88.5 | 88.3 | 88.9 | 80 | DATA flag_ledger_evidence
p14 | prob | earnings_role_bands_walk_forward still passes its registered rule | 0.90 |  |  |  | DATA flag_ledger
p15 | diff | event_earnings_window_width: gain per earnings stock-day 2013-2019 in nats (old 2.01) | 2.01 | 1.96 | 2.06 | 80 | DATA flag_ledger_evidence
p16 | ratio | event_earnings_window_width: day 0 band multiplier (old 2.72) | 2.72 | 2.69 | 2.75 | 80 | DATA flag_ledger_evidence
p17 | prob | event_earnings_window_width still passes its registered rule | 0.99 |  |  |  | DATA flag_ledger
p18 | ratio | event_burst_day0_1: days 0 to 1 ratio 2004-2018 (old 1.306) | 1.31 | 1.29 | 1.34 | 80 | DATA flag_ledger_evidence
p19 | ratio | event_burst_day0_1: days 0 to 1 ratio 2019-2026 (old 1.331) | 1.335 | 1.31 | 1.36 | 80 | DATA flag_ledger_evidence
p20 | prob | event_burst_day0_1 still passes its registered rule | 0.99 |  |  |  | DATA flag_ledger
p21 | diff | event_daily_range_coverage: shortfall versus control in points 2004-2018 (old 6.7) | 6.8 | 6.0 | 7.6 | 80 | DATA flag_ledger_evidence
p22 | diff | event_daily_range_coverage: shortfall versus control in points 2019-2026 (old 9.2) | 9.3 | 8.3 | 10.3 | 80 | DATA flag_ledger_evidence
p23 | prob | event_daily_range_coverage still passes its registered rule | 0.97 |  |  |  | DATA flag_ledger
p24 | ratio | event_day_width_own_events: band multiplier versus an ordinary day (old 1.60) | 1.60 | 1.57 | 1.63 | 80 | DATA flag_ledger_evidence
p25 | diff | event_day_width_own_events: gain per event stock-day E3-W2 in 2013-2019 in nats (old 0.541) | 0.541 | 0.51 | 0.57 | 80 | DATA flag_ledger_evidence
p26 | prob | event_day_width_own_events still passes its registered rule | 0.99 |  |  |  | DATA flag_ledger
p27 | pct | event_label_direction_sign: hit rate 2004-2018 (old 57.7) | 57.5 | 56.6 | 58.5 | 80 | DATA flag_ledger_evidence
p28 | pct | event_label_direction_sign: hit rate 2019-2026 (old 57.8) | 57.6 | 56.0 | 59.2 | 80 | DATA flag_ledger_evidence
p29 | prob | event_label_direction_sign still passes its registered rule in both eras | 0.94 |  |  |  | DATA flag_ledger
p30 | pct | band_edge_calibration_90: coverage of the earnings plus event group (old 88.47) | 88.4 | 88.1 | 88.8 | 80 | DATA flag_ledger_evidence
p31 | pct | band_edge_calibration_90: coverage of the earnings day +1 group in 2013-2019 (old 88.14) | 88.1 | 87.95 | 88.3 | 80 | DATA flag_ledger_evidence
p32 | prob | band_edge_calibration_90 still passes in every group and every judged era | 0.85 |  |  |  | DATA flag_ledger
p33 | diff | event_premium_20d: pooled 2004-2018 premium (old repaired 0.0548) | 0.054 | 0.040 | 0.068 | 80 | DATA flag_ledger_evidence
p34 | diff | event_premium_20d: 2019-2026 older events premium (old repaired 0.037) | 0.035 | 0.015 | 0.055 | 80 | DATA flag_ledger_evidence
p35 | prob | event_premium_20d still passes its registered rule | 0.85 |  |  |  | DATA flag_ledger
p36 | prob | event_premium_20d keeps the same rule category (consistent, replicated lower or not replicated) | 0.70 |  |  |  | DATA flag_ledger
p37 | ratio | event_type_capital_raise_no_burst: burst ratio 2004-2018 (old 1.024) | 1.03 | 0.98 | 1.09 | 80 | DATA flag_ledger_evidence
p38 | ratio | event_type_capital_raise_no_burst: burst ratio 2019-2026 (old 1.098) | 1.10 | 1.03 | 1.17 | 80 | DATA flag_ledger_evidence
p39 | diff | event_type_capital_raise_no_burst: z versus the pooled burst in 2019-2026 (old -3.2) | -3.2 | -4.0 | -2.4 | 80 | DATA flag_ledger_evidence
p40 | prob | event_type_capital_raise_no_burst still differs from pooled with z above 2.5 in both eras | 0.90 |  |  |  | DATA flag_ledger
p41 | ratio | event_type_acquisition: burst ratio 2004-2018 (old 1.277) | 1.28 | 1.24 | 1.32 | 80 | DATA flag_ledger_evidence
p42 | ratio | event_type_acquisition: burst ratio 2019-2026 (old 1.319) | 1.32 | 1.28 | 1.36 | 80 | DATA flag_ledger_evidence
p43 | prob | event_type_acquisition still uses the pooled number | 0.97 |  |  |  | DATA flag_ledger
p44 | ratio | event_type_leadership_change: burst ratio 2004-2018 (old 1.250) | 1.25 | 1.21 | 1.29 | 80 | DATA flag_ledger_evidence
p45 | ratio | event_type_leadership_change: burst ratio 2019-2026 (old 1.276) | 1.28 | 1.24 | 1.32 | 80 | DATA flag_ledger_evidence
p46 | prob | event_type_leadership_change still uses the pooled number | 0.96 |  |  |  | DATA flag_ledger
p47 | ratio | event_type_strategic_partnership: burst ratio 2004-2018 (old 1.252) | 1.25 | 1.17 | 1.33 | 80 | DATA flag_ledger_evidence
p48 | ratio | event_type_strategic_partnership: burst ratio 2019-2026 (old 1.381) | 1.38 | 1.27 | 1.49 | 80 | DATA flag_ledger_evidence
p49 | prob | event_type_strategic_partnership still uses the pooled number | 0.98 |  |  |  | DATA flag_ledger
p50 | prob | all 15 proven flags pass their registered rules | 0.43 |  |  |  | DATA flag_ledger
p51 | prob | at least one control misses its tolerance and the re-run stops | 0.09 |  |  |  | DATA flag_ledger
p52 | prob | at least 10 of the 33 numeric rows land outside their 80 percent intervals (my intervals are too narrow) | 0.25 |  |  |  | DATA flag_ledger
PRED-TABLE-END
WHAT WOULD CHANGE THE PLAN: (1) A control outside its tolerance: STOP, diagnose the re-run process (script version, window, defaults) and read no event-level result until the control reproduces. (2) A flag outside its predicted range: record it as a SURPRISE, run the with-and-without-508-exclusions attribution, and report both. (3) A flag that fails its registered rule: an append-only ledger note and a recommendation to demote; the status change is Galen's, after the January check. (4) A flag that comes back STRONGER than predicted is recorded as plainly as one that weakens. (5) If 10 or more numeric rows miss their intervals, my intervals were too narrow and every later registration of mine widens by that factor.
LIMITS: the re-run script for each flag is not yet confirmed, and none has been shown to read the cleaned set; that goes in a dated addendum BEFORE any run. Whether the original tests used the exploration universe only is assumed, not verified. event_premium_20d was repaired once already (2026-10-19) and its rule uses naive standard errors, so its pass is the weakest evidence here; the verdict stays on the registered rule and a clustered SE is reported beside it. The sample is 2004 to 2026 on a current-index universe (survivorship), as in the original tests. Probabilities are my judgement from margins and sample sizes, not a model.
NOT IN THIS NOTE: the 21 leads, the Tier 1 nulls (event_lasting_days_6_20, event_pre_days_m4_m1, time_to_threshold_asymmetry, direction_overreaction_reversal, tag_specific_ranges, event_type_financial_result, event_type_regulatory) and Tier 2, the new state-dependent hypotheses, and any change to a registered rule.
# AFTER THE RESULTS: append a block   ACTUAL-TABLE-BEGIN / id | actual | se / ACTUAL-TABLE-END   (prob rows: actual 1 or 0) and run   python3 scripts/ops/score_predictions.py results/PREREG_g7_proven_rerun_2026-10-29.md

## Old numbers and registered rules, for reference (the predictions are ONLY in the table above)

1. band_stress_scale_median (CONTROL, 2,187,937 ordinary stock-days): coverage 89.63% to 91.08% in 12 cells; score ratio 0.986 / 0.986 / 0.983. Rule: each era, every bin with 1,000+ days covers 88% to 92%, mean score within 1%.
2. fomc_announcement_day_market_move (CONTROL): day 0 1.140 (n 88), 1.112 (n 92), 1.121 without 2020 (n 85); placebos 0.974, 0.945. Rule: t>=2.5 both eras, clean placebos, t>=2.0 without 2020.
3. macro_oil_shock_energy_same_day (CONTROL): 1.293 (115 months), 1.319 (64 months); placebos 0.967 / 0.942 and 0.986 / 1.006. Rule: amplification 1.15 or more, t>=2.5 both eras, placebo sectors about 1.10 or less.
4. earnings_role_bands_walk_forward: ratios 0.890 / 0.869 / 0.857 (56,176 observations); coverage cells 88.5% to 91.9%. Rule: each era ratio 0.98 or less, coverage 88% to 92%, shuffled placebo 0.99 or more.
5. event_earnings_window_width: gain 1.33 / 2.01 / 1.77 nats; multipliers 2.72 (day 0), 2.47 (day +1); n 41,046. Rule: 0.005 nats or more each era, positive in 70% of years.
6. event_burst_day0_1: 1.306 (SE 0.018, n 6,871); 1.331 (SE 0.023, n 3,836). Rule: days 0 to 1 elevated with z above 2 in both eras.
7. event_daily_range_coverage: shortfall versus control 6.7 and 9.2 points (n 22,410 and 10,827). Rule: 5 points or more in both eras.
8. event_day_width_own_events: gain 0.22 to 0.54 nats; multiplier 1.60; n 41,542. Rule: 0.005 nats or more each era, positive in 70% of years.
9. event_label_direction_sign: 57.7% (n 4,212); 57.8% (n 1,311). Rule: hit rate 55% or more, Wilson lower end above 50%, permutation p of 0.05 or less, both eras.
10. band_edge_calibration_90: six groups; tightest: earnings + event 88.47% (n 3,044), earnings day +1 88.14% in 2013-19. Rule: coverage 88% to 92% in each judged era.
11. event_premium_20d: repaired eras 0.029, 0.049, 0.079, 0.037 (2019-26 older events), waves 0.088 and 0.124; n 14,592. Rule: 2004-2018 pooled interval contains +0.0295 (consistent), or positive with z above 2 excluding it (replicated lower), or upper end below 0.02 (not replicated).
12. event_type_capital_raise_no_burst: 1.024 (n 505), 1.098 (n 355); z versus pooled -7.1 and -3.2. Rule: differs from the pooled burst with z above 2.5 in both eras.
13 to 15. event_type_acquisition 1.277 / 1.319 (n 2,127 / 936); event_type_leadership_change 1.250 / 1.276 (n 1,699 / 1,442); event_type_strategic_partnership 1.252 / 1.381 (n 300 / 131). Rule: uses the pooled number (1.306 / 1.331) unless it differs with z above 2.5 in both eras; these pass by staying indistinguishable.

## Addendum (dated; the predictions above are not edited)

### Addendum 1 (2026-10-29, written before any run): the corrected design, what is known about each procedure, and the controls

**A correction to my own plan.** I wrote that an "Arm 0" would reproduce the ledger's numbers. For the event-level flags that is wrong: the database itself changed since the original runs (tags, reactions, ripple rows) and cannot be restored, so only the controls, and flags that read frozen or market-wide inputs, can be reproduced. The design is:

- **Controls:** one run each; they must reproduce the ledger's numbers within the tolerances in the PRED-TABLE.
- **Event-level flags:** two runs on the current database. **Arm 0** is the original procedure, unchanged, no exclusions. **Arm 1** is the same procedure restricted to the cleaned set (events without an `exclude` row in event_exclusions, equivalently event_analysis_set) and, wherever the procedure tests whether an event is isolated, with excluded events removed from the neighbour test as well. Old ledger number against Arm 0 is the effect of all the data fixes together; Arm 1 minus Arm 0 is the effect of the exclusions.
- **Code is pinned:** scripts run from a checkout of the commit as of the flag's tested_on date (git worktree, data_cache linked), unless the script's last commit is on or before that date and no module it imports changed after it.

**What is known** (from the repository, the ledger notes and the earlier transcripts; "ready" means the procedure is identified, not that it has run):

| flag | procedure | how identified | status |
|---|---|---|---|
| band_stress_scale_median | scripts/card/robust_stress_test.py, no arguments; reads data_cache/audit_matrices.npz (2026-10-20) and the database for 8-K filings and recorded event days; last commit 97eb587 (2026-10-20) | ledger note; its docstring quotes 89.63% to 91.08% | CONTROL, ready |
| fomc_announcement_day_market_move | scripts/card/fomc_day_test.py, no arguments (17d2f0d, 2026-10-23); helper fed_change_day_test.py (ed51e0a, 2026-10-22); reads fomc_meetings, macro_long, sector_day_z | ledger note | CONTROL, ready; the calendar table was reloaded on 2026-10-28, so n for 2015-2026 may change if a meeting after the last price date is counted |
| macro_oil_shock_energy_same_day | the SQL in scripts/sql/g7_control_oil_shock_energy_2026-10-16.sql; reads spy_cal, macro_data_releases (DCOILWTICO) and sector_day_z | recovered from the 2026-10-16 20:30 session; it prints the ledger numbers (Energy 1.293 t 9.2 over 115 months; 1.319 t 8.2 over 64 months) | CONTROL, ready; pre-check the last dates of the three tables first |
| band_edge_calibration_90 | scripts/card/band_calibrate.py (22a26ff, 2026-10-20) | ledger note | pin to 9f16aad4; not yet read |
| earnings_role_bands_walk_forward | scripts/card/earnings_role_band_test.py (2f031f2, 2026-10-21); imports day_card, event_width_test, unrecorded_candidates, earnings_timing_check | inferred from names and imports (the ledger note names build_ohlc_cache.py, a cache builder) | MUST be pinned to 63e08d84: commit b68b1b1 on 2026-10-22 refit the role model and changed day_card.py |
| event_day_width_own_events | scripts/card/event_width_test.py (ea2a09f, 2026-10-19) | ledger note | pin ea2a09f4; not yet read |
| event_earnings_window_width | scripts/card/earnings_thread_test.py; earlier output results/2026-10-19/earnings_thread_full.out | ledger note | not yet read |
| event_label_direction_sign | scripts/card/direction_test.py (ea2a09f, 2026-10-19), which reads the FROZEN reaction snapshot and the labels, one event per ticker per week | inferred (the note names no script; direction_far_placebo.py says it uses the same sample) | insulated from reaction-table fixes by design; Arm 1 still applies to the event set |
| event_burst_day0_1; event_type_acquisition; event_type_capital_raise_no_burst; event_type_leadership_change; event_type_strategic_partnership | SQL on the view event_profile_base (created 2026-10-16: baseline days 25 to 39, windows 0 to 1, an `isolated` flag), the by-type query with the seam exclusion and the corporate-action split | recovered from the 2026-10-16 16:27 session; its numbers equal the ledger rows (ALL_POOLED 6,871 and 3,836) | the exact query is saved and committed in its own addendum before it runs; Arm 1 changes the sample AND the isolation test |
| event_premium_20d | the database function ratio_period(date, date) called per period, plus a combining query | seen in the 2026-10-16 16:27 session | definition not yet recovered |
| event_daily_range_coverage | a query over market_prices, vol_estimators and events; only its ledger INSERT text is known | not located | not located |

`stock_card.py` and `day_card.py` are DISPLAY scripts that read the ledger; they are not tests and are never run as one. `median_scale_adoption_check.py` writes models/band_median_calibration.json and is never run in this exercise.

**Order and rules of the run**

1. This addendum and the recovered oil SQL are committed before anything runs.
2. Controls first, in this order: C3 (the SQL, after a last-date pre-check), C2 (fomc_day_test.py), C1 (robust_stress_test.py). Every output is saved under results/g7_rerun/ with the date in its name and is never edited.
3. A control outside its tolerance stops the run (rule 1 of section 3); the same-day commits of that script are checked first.
4. No event-level flag runs until its own procedure is committed in a further dated addendum.
5. TRIPWIRES: every run prints how many events, rows or days it read and the latest date in each table it reads. The Arm 1 count must be below the Arm 0 count by about the number of excluded events in scope (508 overall); equal counts mean the exclusions were not applied.

**Known risks, stated in advance:** a script whose last commit falls on its tested_on date may have changed after the run; the 2015-2026 FOMC n may differ if the reloaded calendar adds a meeting; the oil control's 2019-2026 month count could be 65 if sector_day_z was extended after 2026-10-16 (the pre-check answers that). These addenda do not change any prediction above.

### Addendum 2 (2026-10-29, after the three controls, before any event-level run): outcomes, one stated deviation, and a new rule

Provenance: Addendum 1 was committed at 16:01:25 UTC (a1125ea); the C2 and C1 output files are dated 16:02:09 and 16:03:34 (results/g7_rerun/). The C3 query ran in the SQL editor and has no timestamp.

**Outcomes against the registered rows** (the ACTUAL-TABLE at the end of the exercise will carry these values):

| id | registered | actual | result |
|---|---|---|---|
| p1 lowest coverage cell, band_stress_scale_median | 89.63 [89.55, 89.71] | 89.63 | hit |
| p2 highest coverage cell | 91.08 [91.00, 91.16] | 91.08 | hit |
| p3 score ratio C over B, 2020-2026 | 0.983 [0.981, 0.985] | 0.9834 | hit |
| p4 control reproduces and passes | 0.97 | yes (ordinary stock-days 2,187,937; ratios 0.9862, 0.9857, 0.9834; verdict "earns its place") | 1 |
| p5 FOMC day 0, 2004-2014 | 1.140 [1.138, 1.142] | 1.140 (n 88, t +3.90) | hit |
| p6 FOMC day 0, 2015-2026 | 1.112 [1.110, 1.114] | 1.112 (n 92, t +3.27) | hit |
| p7 FOMC control reproduces and passes | 0.97 | yes (n 85 without 2020, placebos 0.974 and 0.945, verdict PASS) | 1 |
| p8 Energy amplification 2004-2018 | 1.293 [1.290, 1.296] | 1.293 (t 9.2, 115 months) | hit |
| p9 Energy amplification 2019-2026 | 1.319 [1.316, 1.322] | 1.324 (t 8.5, 66 months) | MISS |
| p10 oil control reproduces within tolerance and passes | 0.97 | recorded 0: the tolerance as registered was not met on today's data (the rule itself is met) | 0 |
| p51 a control misses its tolerance and the run stops | 0.09 | recorded 1: the run was halted until the cause was found | 1 |

**The deviation (C3, era 2019-2026) and its attribution.** The pre-check showed sector_day_z now ends on 2026-09-15 (macro_data_releases for DCOILWTICO on 2026-10-06, spy_cal on 2026-10-13). The control returned 66 qualifying Energy months where the ledger has 64. The monthly values were listed and the statistic recomputed with the last months dropped: through 2026-09, 66 months, 1.324, t 8.5; through 2026-08, 65 months, 1.317, t 8.3; through 2026-07, 64 months, 1.319, t 8.2; through 2026-06, 63 months, 1.318, t 8.1. Only the cut through July 2026 reproduces the ledger exactly. **The control reproduces on its original window; the difference is two months (August and September 2026) added to sector_day_z after 2026-10-16.** Addendum 1 had named this risk but expected 65 months. The registered rule for the flag is met on the current data: Energy 1.293 and 1.324 with t 9.2 and 8.5; placebos Health Care 0.967 and 0.944, Information Technology 0.986 and 1.002; no other sector above 1.042. The values on the current data are this flag's values for the exercise.

**Scoring record.** p9 is scored as a miss and p10 as 0 even though the cause is benign and was anticipated as a risk: the tolerance I registered assumed the tables had not grown, and that was my error, not the data's. Nothing is re-scored afterwards.

**New rule for every procedure addendum that follows.** Each run prints the latest date in every table it reads and compares it with the window of the original run (the ledger's tested_on date and its sample sizes), so that a result that moves because a table was extended is attributed to the extension and not to the cleaning. For event-level flags this is checked in Arm 0 first.


### Addendum 3 (2026-10-29, before any event-level run): the by-type burst procedure (event_burst_day0_1 and the four event_type flags)

**What is measured.** For isolated events (no other event of the same company within -5 to +39 days), by era and event type: ratio = SUM(mean of days 0 to 1) / SUM(mean of days 25 to 39), seam events (titles with spin, separation, split-off) excluded, corporate actions split by title, an ALL_POOLED row, cells of 60 events or more; SE by the ratio estimator; **z for a type = (type ratio - pooled ratio) / SE of the type, the pooled value treated as known** (this reproduces the ledger's -7.1 and -3.2). The query is recovered from the 2026-10-16 16:27 session, where its output became the ledger rows; the view event_profile_base it reads was created in that session and does not appear again in any later session.

**Files (committed before any run):** scripts/sql/g7_bytype_burst_arm0_2026-10-16.sql (the original, byte for byte), scripts/sql/g7_bytype_burst_arm1_cleaned.sql (the view rebuilt inline, with excluded events removed from the sample AND from the isolation test) and scripts/sql/g7_bytype_burst_arm1_null.sql (the Arm 1 form with an empty exclusion list). Arm 1 and Arm 1-null differ in one line; the tail of both is identical to Arm 0's.

**Order.** (1) Pre-check of the data window: the latest event date, the rows and isolated rows of event_profile_base, the events in event_daily_abn and the number of excluded events. (2) ARM 0. Its ALL_POOLED n is compared with the ledger's 6,871 and 3,836; a higher n is expected (314 events were added to the ripple table on 2026-10-28 and fewer events fail isolation than the duplicates allowed), and the direction and size are recorded. (3) ARM 1-NULL must equal ARM 0 in every row (n, ratio, SE); if any row differs, the rebuild of the view is wrong and ARM 1 is not run. (4) ARM 1.

**Which arm the predictions describe.** The registered rows for these flags (p18 to p20 for the burst, p37 to p40 for capital raise, p41 to p49 for acquisition, leadership change and strategic partnership) describe ARM 1, the cleaned data. ARM 0 is reported beside it; ARM 1 minus ARM 0 is the effect of the exclusions, and the ledger value minus ARM 0 is the effect of every other data change since 2026-10-16.

**Tripwires.** Arm 1 and Arm 0 must not be identical in every row (identical would mean the exclusions did not apply). Arm 1's isolated count in a cell can be HIGHER than Arm 0's (removing duplicates frees neighbours) while its event count is lower; both are reported. The latest date and counts from the pre-check are compared with the ledger's window.

**Limits, stated in advance.** The view's isolation test counts every other event for the company in event_entity_relationships, multi-entity events included, and Arm 1 does the same; the type is the first by name when an event has several; none of this is changed. Nothing here re-scores or edits a prediction.

### Addendum 4 (2026-10-30, before the run): band_edge_calibration_90, scripts/card/band_calibrate.py

**What the script does, read from its own text.** It is read-only on the database but WRITES models/band_calibration.json, a live model the card uses, so it runs only inside a pinned git worktree: its ROOT is computed from the script's own location, which puts the write inside the worktree and leaves the live file untouched. It reads data_cache/audit_matrices.npz (built 2026-10-20), models/event_band_model.json and models/earnings_band_model.json (as at the pin), the database table sec_8k_filings (earnings windows and Regulation FD filings) and, through event_width_test.load_event_info, the tables event_direction_labels and ev_ent (event_id, entity_id, d, ptype), which supply the recorded event days. Usage: python3 -u scripts/card/band_calibrate.py, no arguments; credentials from the environment. Its original printout is results/2026-10-19/band_calibrate.out (31 lines, 43 seconds).

**Pin.** Commit 22a26ff (2026-10-20 16:22:44, the script's only commit), the earliest faithful state of the code and of its two imported modules (event_width_test.py as of ea2a09f; day_card.py as of the pin; later commits to day_card.py are not included). The printout is filed under 2026-10-19 but the script's commit is 2026-10-20, so the printout may come from an earlier uncommitted version; ARM 0 tests that.

**Set-up (the same commands will be run):** git worktree add /tmp/g7_pin_band 22a26ff, then a symbolic link /tmp/g7_pin_band/data_cache to the repository's data_cache. The worktree is removed afterwards.

**ARM 0** is the pinned script, unpatched. It must reproduce the original printout: the matrices line (496 stocks x 8250 days); ordinary coverage 90.21% within 0.05 points; every other group within 0.20 points of its printed coverage in each era; every group CALIBRATED; fitted edges within 0.01 band units. If it does not, the run STOPS and the cause (database drift in ev_ent or event_direction_labels since 2026-10-20, or code) is found before ARM 1.

**ARM 1** is the same after scripts/audit/g7_patch_arm1_event_width.py edits ONLY the worktree's copy of event_width_test.py: rows of ev_ent whose event_id has an exclude row in event_exclusions are skipped, so their days stop being recorded event days. The patch is hash-checked, refuses a second application and any path outside /tmp, and the run prints how many ev_ent rows it removed. The registered rows p30 to p32 describe ARM 1.

**Pre-check (SQL, before ARM 0):** the latest ev_ent day, the ev_ent row count, the number of ev_ent rows the filter removes, and the latest 8-K filing date.

**Tripwires.** (1) The removed-rows count printed by ARM 1 equals the pre-check's number. (2) In ARM 1 the group 'recorded event, no earnings' (25,485 days in the original) and 'earnings window + recorded event' (3,044) must shrink; identical group sizes in ARM 0 and ARM 1 mean the filter did nothing. (3) Each arm's console output and the model file it wrote are copied to results/g7_rerun/ with the arm in the name, and the patch diff is saved.

**Stated in advance.** Group sizes change in ARM 1 because the days of excluded events move out of the 'recorded event' groups into 'ordinary' or 'earnings, no event': a composition effect, not noise. The registered rule is unchanged (coverage within 88% to 92% in each judged era with at least 1,000 scored days). The thin margins in the original printout are: earnings day +1 88.14% in 2013-2019 (0.14 above the line), earnings + event 88.46% in 2020-2026 (0.46), earnings day 0 88.53% in 2013-2019 (0.53), earnings + event 88.57% in 2013-2019, recorded event 88.72% in 2013-2019; any of them can fail on a shift of 0.1 to 0.5 points, which is what p32 prices.

### Addendum 4a (2026-10-30, before the retry): the first Arm 0 attempt of band_calibrate.py failed; cause, fix, and a new rule

**What happened.** The first attempt (pinned worktree at 22a26ff, after the pre-check and the registration commit 52550ee) stopped at the script's first input check: "models/earnings_band_model.json not found." Nothing was computed and no model file was written. Its console output is kept as results/g7_rerun/band_calibrate_arm0_attempt1_FAILED_missing_model_2026-10-30.out; the model-file copy that the command had made (a copy of the file as committed at the pin, not a product of any run) was deleted.

**Cause.** Addendum 4 said the two model files come "as at the pin" without checking that both are tracked at the pin. models/earnings_band_model.json is not in commit 22a26ff: it was first committed in 4e06a3c (2026-10-20 18:17:06), almost two hours after the pin (16:22:44). The copy on disk was written at 15:26, before the original printout (16:20:25 on 2026-10-20), so it is the file the original run read. models/event_band_model.json is at the pin (last commit 39015c4, 2026-10-20 13:43:31).

**Fix.** The file is taken from git, not from the disk: git show 4e06a3c:models/earnings_band_model.json is written into the worktree's models/ folder, and only after its sha256 is shown to equal the sha256 of the file on disk (which proves that the file the original run read and the committed file are the same bytes). The pin plus that one file is then the original run's input set. Nothing else in Addendum 4 changes: ARM 0, ARM 1, the tolerances, the tripwires and the registered rows p30 to p32 stand.

**New rule for every procedure addendum from here on.** The addendum lists EVERY input the procedure reads (code and imported modules, model files, caches, database tables) and states, from git or the file system, that each exists at the pin or how it is supplied and verified, before the registration is committed. The registration commit is not evidence that the procedure runs.

**One more fact recorded before the retry.** The pre-check gave ev_ent 22,338 rows, 716 of which ARM 1 removes (3.2 percent), latest day 2026-09-11, latest 8-K 2026-09-18: of the 1,527 excluded events only 716 have rows in ev_ent, so the exclusion filter here is smaller than in the by-type run.

### Addendum 5 (2026-10-30, before the run): event_day_width_own_events, scripts/card/event_width_test.py

**Every input the procedure reads (the rule of Addendum 4a).**
- **Code:** scripts/card/event_width_test.py and scripts/card/decomp_validation.py (imported as dv), both exactly as at commit 798e1e7f (2026-10-20 16:06:22, the last commit before the original run, which is stamped 16:11). Neither module changed between ea2a09f (the ledger's date pin) and 798e1e7f. Both use only the standard library (decomp_validation imports os, sys, pickle, glob, math, json, time, bisect); no model files are read.
- **Cache:** data_cache/returns, 500 files (one per security plus _macro.pkl), read through the relative path "data_cache/returns", so the run must start at the worktree root; none of its files is newer than the original run (checked: 0), and the worktree links the repository's data_cache.
- **Database tables:** securities, event_direction_labels (22,283 labels at the original run) and ev_ent (event_id, entity_id, d, ptype).
- **Writes:** none by event_width_test.py. decomp_validation writes scripts/card/out/decomp_validation.json only in its own main, which is not run.
- **Original output:** results/2026-10-19/event_width_full.log (57 lines, 108 seconds, file time 2026-10-20 16:11; first line: 498 securities, 8,250 trading days 1994-01-03 to 2026-10-13, events mapped for 491 securities, direction labels 22,283; verdict lines: E1 - W0, E3 - W2 and E5 each EARNS ITS PLACE, claim SUPPORTED).

**Set-up.** git worktree add /tmp/g7_pin_ew 798e1e7f, a symbolic link /tmp/g7_pin_ew/data_cache to the repository's data_cache, runs from /tmp/g7_pin_ew. The worktree is removed afterwards.

**ARM 0** is the pinned script, unpatched, no arguments (the full run). It must reproduce the original log: the first line's counts, the three gains per era within 0.005 nats, the years-positive counts identical (E5 22 of 22) and the verdict lines identical. The tables that use the direction labels may differ if the labels table has changed since 2026-10-20 (the first line prints its count); a difference there is recorded and does not stop the run, a difference in the three registered gains does.

**ARM 1** is the same after scripts/audit/g7_patch_arm1_event_width.py edits the worktree's copy of event_width_test.py (the same exact-match edit as for band_calibrate.py: rows of ev_ent whose event has an exclude row are skipped, and the run prints how many; the loader is the same code at line 83). The patch is hash-checked, refuses a second application and any path outside /tmp.

**Tripwires.** ARM 1 prints "1527 excluded events; 716 of 22338 ev_ent rows removed" (the pre-check of 2026-10-30, since the table has not changed); the three gains differ at least in the last digit between the arms; each arm's console output is saved in results/g7_rerun/ with the arm in the name, and the patch diff is saved.

**Registered rows.** p24 to p26 (the band multiplier against an ordinary day, the E3 - W2 gain in 2013-2019, and the pass) describe ARM 1.

**Stated in advance.** The filter removes 3.2 percent of the ev_ent rows, but its effect on the three gains should be small: the days of an excluded event become ordinary days, and where an excluded event shared a day with a kept event the rule 'the first event by event_id supplies the type, size and timing' now picks the kept one. The tables by type and by size or timing can move more than the three gains. The effective sample is smaller than the row count (event days are about 1.5 percent of stock-days and are not independent of the market around them).

### Addendum 6 (2026-10-30): a correction to the registration's universe statement

The DATA AND USE RULE of this registration says the re-runs use "the exploration tickers only" and that "the 160 sealed tickers are not touched in this pass". The limits section called this assumed, not verified. It is WRONG for the runs so far: the by-type SQL has no sealed filter and its ARM 0 reproduced the ledger's counts on ALL companies (ALL_POOLED n 6,914 against the ledger's 6,871, where excluding the sealed third of events would give about 4,600); band_calibrate.py and event_width_test.py read all 498 securities. The original tests of these flags used all companies too, so the re-runs compare like with like and no result of this exercise is invalidated, but the sealed tickers have been part of every one of these tests since they were first run.

Consequences. (1) The sealed set is NOT an independent confirmation for any of the 15 flags, nor for the Tier 1 nulls registered in results/PREREG_g7_tier1_window_nulls_2026-10-30.md; any claim that would need confirmation is confirmed on forward data (January 2027), and sealed and non-sealed results are reported side by side as a consistency check between two disjoint company sets. (2) The multiplicity rule of this exercise ("a flip holds once on the sealed tickers") is replaced, for these flags, by: a flip passes its registered rule, clears a pre-stated minimum effect, holds with the same sign in both company sets, and is re-tested on forward data before any status change. (3) Standing rule 13 of the status file (tests read the analysis set, adopted 2026-10-28) is respected in ARM 1 in substance, not in form: ARM 1 removes events with an exclude reason, as event_analysis_set does, but does not require a reaction row. No prediction above is changed.

(further dated addenda go here: the remaining procedures)
