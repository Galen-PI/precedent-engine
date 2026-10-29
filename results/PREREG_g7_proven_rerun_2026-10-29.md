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

(procedure, script interfaces and how each script is pointed at the cleaned set go here, after they are read and before any run)
