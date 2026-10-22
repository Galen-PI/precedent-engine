# Prediction tally, 2026-10-22 session (numeric range predictions visible in the conversation)

Scored two ways. **Strict** = the old bare tick: every component of the actual value inside the stated range. **Within noise** = inside, or outside by no more than about 1.5 standard errors (for deterministic counts: about 3% of the range edge). **MISS** = outside by more than about 2 standard errors, or a conceptual miss. The NEAR boundary is my judgment; deterministic counts have no sampling error. Earlier sessions are in SCRIPTS.md and are not included.

| ID | Test | Prediction (point and range) | Actual | Strict | Class | Distance / note |
|---|---|---|---|---|---|---|
| A1 | Overlap counts | EVT single-flag volume 35,000-45,000 stock-days | 37,175 | yes | IN | - |
| A2 | Overlap counts | ERN volume 75,000-90,000 | 80,029 | yes | IN | - |
| A3 | Overlap counts | FD volume 60,000-90,000 | 43,747 | no | MISS | 16,253 below the floor (27%); a count |
| A4 | Overlap counts | JOB volume 100,000-140,000 | 119,685 | yes | IN | - |
| A5 | Overlap counts | testable pairs at most 6 of 28 | 4 | yes | IN | - |
| A6 | Overlap counts | JOB x ERN 300-3,000 stock-days per era | 2,432 / 1,754 | yes | IN | - |
| A7 | Overlap counts | YLD_F x ERN 300-3,000 | 620 / 419 | yes | IN | - |
| A8 | Overlap counts | YLD_F x EVT 300-3,000 | 435 / 114 | no | MISS | era B 186 below the floor |
| A9 | Overlap counts | OIL_E pairs under 300 per era (EVT possibly more) | OIL_E x JOB 302 / 430; five others under 300 | no | MISS | one of six pairs; era B 130 over the line |
| A10 | Overlap counts | macro x JOB pairs under 40 distinct days per era | 39 / 16 (yield), 18 / 21 (oil) | yes | IN | - |
| A11 | Overlap counts | JOB x ERN distinct days 170-185 and 90-100 | 169 / 87 | no | NEAR | 1 and 3 days under; a count |
| A12 | Overlap counts | own-source share of the EVT x FD overlap 40-65% | 83.8% / 92.5% | no | MISS | 24 and 46 SE above the top |
| B1 | Fed change days | change days about 58 (27 + 31) | 59 (27 + 32; 31 scorable) | yes | IN | - |
| B2 | Fed change days | Financials amplification 1.00-1.12, both eras | 1.065 / 1.038 | yes | IN | - |
| B3 | Fed change days | Real Estate and Utilities 1.00-1.10 | RE 1.025 / 1.044; Utilities 0.986 / 0.991 | no | NEAR | Utilities 0.2 and 0.1 SE below the floor |
| B4 | Fed change days | Health Care 0.93-1.05 | 1.051 / 0.978 | no | NEAR | 0.02 SE over (rounding) |
| B5 | Fed change days | crisis-excluded Financials within 0.05 of the full estimate | 0.011 and 0.009 apart | yes | IN | - |
| B6 | Fed change days | one era resolves 10-12% at t 2.5 | 12.8% / 12.7% | no | NEAR | about 0.5 SE |
| B7 | Fed change days | per-event log-ratio spread 0.2-0.25 | 0.25 / 0.27 (implied) | no | NEAR | 0.02 over in era B; about 0.5 SE |
| C1 | Executive-order days | 2004-2014 amplification 1.00-1.04 | 0.967 | no | NEAR | 1.3 SE below; the interval overlaps |
| C2 | Executive-order days | 2015-2024 amplification 1.00-1.05 | 0.977 | no | NEAR | 0.9 SE below; the interval overlaps |
| C3 | Executive-order days | 2025-2026 amplification 1.03-1.20 | 1.081 | yes | IN | - |
| C4 | Executive-order days | per-day spread 0.25-0.35 | 0.34 / 0.41 | no | MISS | era B about 3.9 SE of an sd; resolution only 4.9 -> 5.6% |
| C5 | Executive-order days | resolution 4-7% at t 2.5 | 6.7% / 5.6% | yes | IN | - |
| C6 | Executive-order days | cleaned era A 0.970 (0.968-0.973) | 0.969 | yes | IN | - |
| C7 | Executive-order days | cleaned era B 1.008 (1.006-1.010) | 1.009 | yes | IN | - |
| C8 | Executive-order days | cleaned 2025-2026 1.081 (1.079-1.083) | 1.081 | yes | IN | - |
| C9 | Executive-order days | Fed Financials unchanged within 0.002 | identical | yes | IN | - |
| D1 | Law-driven charges | title matches 150 (90-260) | 32 | no | MISS | about 10 SE below the floor (a count); conceptual |
| D2 | Law-driven charges | Affordable Care Act group 25 (10-50) | 9 | no | NEAR | 1 below the floor (0.3 SE) |
| D3 | Law-driven charges | Tax Cuts and Jobs group 20 (8-40) | 10 | yes | IN | - |
| D4 | Law-driven charges | charge-word share 45% (30-60) | 50% | yes | IN | - |
| D5 | Law-driven charges | all-isolated burst ratio 1.30 (1.28-1.33) | 1.304 | yes | IN | - |
| D6 | Law-driven charges | law-group burst ratio 0.95 (0.70-1.25) | 0.364 | no | MISS | 5.4 SE below the floor |
| D7 | Law-driven charges | 2010 control burst 0.95 (0.75-1.20) | 0.738 | no | NEAR | 0.1 SE below the floor |
| D8 | Law-driven charges | 2017-18 control burst 1.10 (0.85-1.35) | 0.952 | yes | IN | - |
| D9 | Law-driven charges | law-group events counted 8 (5-12) | 9 | yes | IN | - |
| D10 | Law-driven charges | law-group burst SE 0.15-0.30 | 0.062 | no | MISS | my SE guess was 2.4x too large |
| E1 | Labeler counts | law events labeled new 7 of 9 (4-9) | 13 of 13 (all) | yes | IN | top of the range, scaled |
| E2 | Labeler counts | law events labeled large 5 of 9 (3-8) | 5 of 13 | yes | IN | scaled range 4-11 |
| E3 | Labeler counts | share new 70% (60-80) | 72.5% | yes | IN | - |
| E4 | Labeler counts | share previously_announced 15% (8-25) | 25.2% | no | NEAR | 0.2 over; about 0.5 SE |
| E5 | Labeler counts | previously_announced that are acquisitions 55% (35-75) | 54.0% | yes | IN | - |
| E6 | Labeler counts | labeled isolated events 11,000 (9,000-12,500) | 10,877 (eras A and B) | yes | IN | - |
| E7 | Labeler counts | duplicate labels none | none | yes | IN | - |
| F1 | Event band audit | overall coverage 89.2% (88.0-90.5) in each era | 91.1 / 89.8 / 89.6 | no | MISS | era 1: 2.3 SE above the top |
| F2 | Event band audit | classes testable 18 (10-30) | 31 | no | NEAR | 1 above the top |
| F3 | Event band audit | classes miscalibrated 2 (0-5) | 0 | yes | IN | - |
| F4 | Event band audit | previously_announced x acquisition coverage 93 (90-96) | 90.7 / 89.4 / 89.4 | no | NEAR | 0.7-0.8 SE below the floor |
| F5 | Event band audit | size large coverage 88 (85-91) | 92.2 / 88.0 / 90.4 | no | NEAR | era 1: 1.3 SE above the top |
| G1 | ipo_spinoff walk-forward | in-sample multipliers 1.4 (1.2-1.7), 1.7 (1.4-2.0), 1.9 (1.5-2.3) | 1.57, 2.06, 1.87 | no | NEAR | middle one 0.06 above the top (0.3 SE) |
| G2 | ipo_spinoff walk-forward | training multipliers 1.4 (1.2-1.7) and 1.6 (1.4-1.9) | 1.57, 1.90 | yes | IN | - |
| G3 | ipo_spinoff walk-forward | test coverage 88% (84-92) | 83.9 / 90.7 | no | NEAR | 0.05 SE below the floor |
| G4 | ipo_spinoff walk-forward | interval-score ratio 0.88 (0.75-0.97) | 0.881 / 0.797 | yes | IN | - |

## Summary (54 range predictions)

| | Count | Share |
|---|---|---|
| inside the stated range (strict hit rate; target for well-set 80% ranges: about 80%) | 30 | 56% |
| outside, but within noise (NEAR) | 15 | 28% |
| inside or within noise | 45 | 83% |
| real misses (MISS) | 9 | 17% |

By test (strict inside / within noise / miss): Overlap counts 7 / 1 / 4; Fed change days 3 / 4 / 0; Executive-order days 6 / 2 / 1; Law-driven charges 5 / 2 / 3; Labeler counts 6 / 1 / 0; Event band audit 1 / 3 / 1; ipo_spinoff walk-forward 2 / 2 / 0.

## Probability calls (7)

| Call | Forecast | Happened |
|---|---|---|
| Fed Financials PASS | 15% | no |
| Executive-order PASS | 12% | no |
| Fed placebos clean | 90% | yes |
| Executive-order placebos clean | 85% | yes |
| a testable law group (T4) | 35% | no |
| at least one class flagged (audit) | 55% | no |
| ipo_spinoff PASS | 55% | no |

Mean Brier score 0.114 (always saying 50% scores 0.250; lower is better). Five calls were that something NEW would work (15, 12, 35, 55, 55%): none did. If those probabilities were right, the chance of zero successes is about 10%: mild evidence of over-optimism about new things working, or chance (n = 5).

## What the tally says

1. **My ranges were too narrow.** Strict hit rate 56% against about 80% for ranges set to be 80% intervals. The +-1 SE convention is the right fix; the within-noise rate of 83% is partly by construction (it counts near-misses as consistent), so the strict rate is the calibration number to improve.
2. **The misses cluster in how often a feature appears in the data** (A3, A8, A9, A12, D1: FD volume, an overlap count, the own-source share, title matches), not in effect sizes. Effect-size predictions mostly held (B2, C3, C5, D5, G4). Where they missed, they missed the same way: I predicted amplification above 1.00 and got values at or below it (C1, C2, B3 Utilities, D6, D7), a mild optimism bias.
3. **Rule going forward:** do not predict a count that a single COUNT query answers; predict effects and outcomes, and keep probability calls for pass/fail. Log each prediction in results/prediction_log.csv when it is made (id, test, point, low, high, actual, class), so no tally has to be reconstructed from a conversation.
