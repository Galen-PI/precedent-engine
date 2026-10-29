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

(further dated addenda go here: the role-band pin, the remaining procedures)
