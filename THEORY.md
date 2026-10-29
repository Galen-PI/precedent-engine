# THEORY: what the data has said (v2, 2026-10-28)

**What this file is.** The findings log, anchored to the flag ledger (the tables `flag_ledger` and `flag_ledger_evidence`: 112 flags, with their full notes, pass rules and by-era numbers). Every claim below carries its flag key; **the ledger is the source of truth and this file is a reading of it.** Numbers are as recorded on the dates shown. **None has yet been re-run on the cleaned analysis set** (docs/PROJECT_STATUS.md, gate G7). The previous version of this file (1,166 lines, a chronological log with its corrections) is docs/archive/THEORY_pre_rewrite_2026-10-28.md.

**How to read a status.**
- **proven:** passed its pre-set rule (usually in each era, out of sample or against a placebo).
- **lead:** passed in part, only post hoc, or inside a screen; worth a pre-set test, not a claim.
- **null:** failed its registered rule. A null is *not an absence*: it means "not shown by this test at this resolution", and several nulls hold small real effects (the notes say which).
- **untested:** no verdict yet (a forward test still running, or not buildable).
- **retired:** no longer carried.

---

## 1. Where it stands

| status | flags | note |
|---|---|---|
| proven | 15 | 12 are substantive findings; 3 only say a type "uses the pooled number" (Section 3) |
| lead | 21 | |
| null | 62 | |
| untested | 12 | two are frozen forward tests, evaluated after 2027-01-05 |
| retired | 2 | |
| **total** | **112** | the five statuses agree with the database |

## 2. The picture, in five sentences

1. **The size of a stock's move is predictable around known dates:** event days run about 1.3 to 1.6 times a normal day, earnings days about 2.5 to 2.7 times, and scheduled FOMC announcements lift the whole market about 1.1 to 1.14 times.
2. **Bands built from those widths calibrate out of sample** to about 90% coverage, by group and by market-stress level.
3. **Direction is only weakly readable:** the labeler's good-or-bad reading of an event's text gets the sign of the two-day move right about 58% of the time against about 54% by chance, and it explains almost none of the squared miss; every price-side direction signal tested was null.
4. **Macro, government and law flags are mostly null at the level tested;** the exceptions are Energy on oil-shock days (proven, same day only) and a cluster of yield-shock leads (Banks up, Health Care down).
5. **Nothing here is a trading edge:** every proven result is about the size of moves or explains them after the fact, and the cost-adjusted expected-value test is a Phase 8 gate that has not been run.

---

## 3. Proven (15)

| flag | the claim | recorded evidence | tested |
|---|---|---|---|
| `event_burst_day0_1` | Isolated events: move size on the filing day and the day after, against days 25 to 39 | ratio 1.306 (n 6,871, 2004-2018) and 1.331 (n 3,836, 2019-2026); the card uses 1.3 | 10-16 |
| `event_premium_20d` | Ordinary event types move more over 20 days than volatility predicts | after the 10-19 repair, matched excess +0.055 (SE 0.009) for 2004-2018 and +0.052 for 2004-2026, positive in every era, mostly the two-day burst; caveats: current-index survivorship, naive SEs | 10-16 (repaired 10-19) |
| `event_daily_range_coverage` | A daily range from 64-day volatility under-covers on days 0 and +1 | coverage 73.9% and 72.3% on days 0-1 against 80.3% and 80.9% ordinary; a multiplier of 1.25 (frozen) restores it within 1.6 points | 10-16 |
| `event_day_width_own_events` | Own-event days are wider than ordinary days beyond what volatility and the same day's other stocks imply | band multiplier 1.60 over 41,542 own-event days (day 0 1.78, day +1 1.40); walk-forward gain positive in 22 of 22 years; by type 1.03 (capital raise) to 2.21 (accounting investigation) | 10-19 |
| `event_earnings_window_width` | Earnings releases (8-K item 2.02) widen days 0 and +1 | 2.72x (day 0) and 2.47x (day +1), gain positive in 21 of 21 years; earnings days are 3.16% of stock-days but hold 19.5% of the unexplained squared miss | 10-20 |
| `earnings_role_bands_walk_forward` | Bands set by each company's reaction-day habit beat pooled earnings bands | interval-score ratio 0.890 / 0.869 / 0.857 by era (0.868 overall, 56,176 test observations); coverage 89.9 / 88.5 / 90.1% on reaction days; shuffled-habit placebo about 1.00. Caveat: "last 4 quarters" was chosen after a test on the same years. Forward test frozen (Section 6) | 10-21 |
| `band_edge_calibration_90` | A per-group empirical 90th-percentile edge calibrates the band out of sample | all six groups inside the 88-92% rule: ordinary 90.21%, event 89.15%, earnings day 0 89.49%, day +1 88.70%, earnings plus event 88.47% (n 3,044), Regulation FD 89.83% | 10-20 |
| `band_stress_scale_median` | Scaling the band by the median squared miss, with one edge, holds coverage across stress levels | 89.63% to 91.08% in all 12 era-by-bin cells (2,187,937 ordinary stock-days); the card still uses the mean-based scale, and the all-groups version was not adopted (`band_median_scale_all_groups`, null) | 10-20 |
| `event_label_direction_sign` | The labeler's good-or-bad reading of an event's text predicts the sign of the day 0-1 abnormal return beyond event type | hit rate 57.7% [56.2, 59.2] (n 4,212, 2004-2018) and 57.8% (n 1,311, 2019-2026) against within-type nulls of about 53.9% and 53.7%; far placebo clean (days 26-39: 49.8% against 50.2%). Small: it explains almost none of the squared miss (`event_label_signed_pull_center`, null) | 10-19, promoted 10-20 |
| `fomc_announcement_day_market_move` | The whole market moves more on scheduled FOMC announcement days (size, not direction) | 1.140 [1.067, 1.218] (2004-2014, n 88) and 1.112 [1.044, 1.186] (2015-2026, n 92); day +1 is larger (1.215 and 1.199, exploratory); placebos 0.974 and 0.945 | 10-23 |
| `macro_oil_shock_energy_same_day` | Energy stocks move more than the rest on days WTI moves 3% or more | 1.293 (t 9.2) and 1.319 (t 8.2); placebo sectors 0.94 to 1.01. Same day only, not knowable in advance; at industry level the effect is weak or absent before 2000; the older estimator reads about 4-6% low | 10-16 |
| `event_type_capital_raise_no_burst` | Capital-raise filings show no day 0-1 burst | 1.024 (n 505) and 1.098 (n 355) against about 1.31 and 1.33 pooled (z -7.1 and -3.2); explains the retired 20-day discount | 10-16 |
| `event_type_acquisition` | *(uses the pooled number)* acquisition burst is not distinct from pooled | 1.277 (n 2,127) and 1.319 (n 936) | 10-16 |
| `event_type_leadership_change` | *(uses the pooled number)* | 1.250 (n 1,699) and 1.276 (n 1,442) | 10-16 |
| `event_type_strategic_partnership` | *(uses the pooled number)* | 1.252 (n 300) and 1.381 (n 131) | 10-16 |

## 4. Leads (21)

| flag | the claim | recorded evidence | why only a lead |
|---|---|---|---|
| `eightk_item_7_01_width` | Regulation FD 8-K filings widen days 0 and +1 | 1.36x over 34,283 flagged days; gain +0.098 / +0.082 / +0.093; 20 of 21 years | passed inside a screen of 10 item codes; mixes routine materials with guidance; the card uses 1.36x with a weak-lead label |
| `guidance_type_filing_day_width` | 8.01 and 7.01 filings with guidance language widen more than other filings | 2.37x [1.83, 2.86] (n 50); ratio to the others 1.94 [1.48, 2.37] | crude keyword class (about 54% precision on a read of 50); small n |
| `event_corporate_action_20d` | Corporate-action filings: 20-day move | all years +0.080 (SE 0.027) after repair | heterogeneous type, many looks |
| `event_type_restructuring` | Restructuring burst | 1.712 (n 339) and 1.671 (n 163); z against pooled 4.2 and 2.3 | misses the 2.5 bar in 2019-2026 by 0.2; the eras agree |
| `event_type_corporate_action` | Non-split corporate-action burst | 1.634 and 1.424; z 3.9 and 0.75 | fails in 2019-2026 |
| `event_type_accounting_investigation` | Restatement and non-reliance burst | 1.419 (n 113, 2004-2018 only) | not distinct from pooled |
| `event_type_governance_action` | Governance burst | 1.323 (n 144) and 1.492 (n 72) | not distinct from pooled; older events are routine |
| `event_type_legal_settlement` | Settlement burst | 1.198 (n 571) and 1.341 (n 173) | within about 2 SE of pooled |
| `event_utility_commission_burst_smaller` | Utility-commission matters burst 23-30% less than other events | pooled -0.266 (t -3.22, 138 events); second era only 27 events | post hoc; needs forward data |
| `ipo_spinoff_band_multiplier_walkforward` | A fitted multiplier of about 1.9 would restore coverage for spin-off event days (the card uses 1.0, about 71% coverage) | walk-forward coverage 83.9% and 90.7% against an 86-94% window; interval-score ratio 0.881 and 0.797 | PARTIAL; not adopted (about 2.3% of event days) |
| `labeler_size_timing_validity` | The labeler's size and timing hints order event-day width correctly | size large 2.17, moderate 1.59, small 1.25; timing new 1.71, previously announced 1.32 | a validity check against a descriptive prediction, not a finding |
| `longhist_oil_shock_oil_industry` | Oil industry on oil-shock days, 1986-2026 | calibrated 1.085 (1986-1999, beats 39 of 40 shifted copies), 1.185, 1.524: rising by era | the pre-set every-era line (1.15) is missed in the first era |
| `longhist_yield_shock_banks` | Banks on yield days of 10bp or more | calibrated 1.059 / 1.189 / 1.187; pooled 1.139, beating all 40 shifted copies | 1962-1985 is only about +6%, below the 1.10 line |
| `longhist_yield_shock_banks_equal_weighted` | Equal-weighted Banks, same days | 1.100 / 1.059 / 1.108 | post hoc; the line is not met in 1986-2007 |
| `longhist_yield_shock_health_dampening` | Health Care moves LESS on yield days | calibrated 0.938 / 0.958 / 0.908; pooled 0.936, below all 40 shifted copies | post-hoc origin; needs its own pre-set test |
| `macro_yield_shock_financials` | Financials on yield days of 10bp or more | 1.059 (t 2.7) and 1.100 (t 3.6) | misses the 1.10 line in 2004-2018 |
| `macro_yield_shock_real_estate` | Real Estate, same days | 1.057 (t 1.8) and 1.076 (t 1.9) | below the line and below t 2.5 |
| `macro_yield_shock_defensives_post_hoc` | Staples and Health Care move less on big-yield days | Staples 0.927 and 0.901; Health Care 0.950 and 0.917 | observed after the fact, not pre-registered |
| `macro_jobs_report_payems` | Jobs-report days move the market more | 1.285 (z 2.8), 1.101, 1.125; pooled about +16% (SE about 5%) | rule failed; one of about 27 numbers looked at; sits in the opening gap |
| `unrecorded_sector_theme` | A big ordinary miss with a volume spike often comes with same-sector misses (a narrow sector theme) | 10.9% against 3.5% placebo: +7.4 points [+6.3, +8.6] (n 6,730) | below the 10-point rule, above the 2-point reading guide; two post-hoc fixes after the first run |
| `storm_tier_large` | A large prior reaction (storm tier) and the next event's reaction | 6.90% against 5.45%, isolated events | **the weakest lead:** not re-tested since 10-13, its evidence unit is inferred, and the original result file was not found |

## 5. Nulls (62), by what they ruled out

*A null failed its registered rule; it is not proof of zero. The notes in the ledger give the resolution (the smallest effect each test could have seen).*

- **An event's own reaction: direction and dynamics (10).** `direction_overreaction_reversal` (reversal fractions 52.3% against 50.6%), `time_to_threshold_asymmetry` (not stable across periods), `event_lasting_days_6_20`, `event_pre_days_m4_m1`, `event_date_lag` (no general lag; only Regulatory is a lead), `magnitude_model_features` (the +9 to +13 point lift was entirely volatility), `tag_specific_ranges` (tags give wider, not narrower, ranges), `storm_x_sentiment`, `size_effect_in_universe`, `volatility_estimator_variants` (nothing beats the 64-day estimate).
- **Event types with no stable number (2).** `event_type_financial_result` and `event_type_regulatory` flip between eras.
- **Government-direct events (3).** `event_gov_direct_burst`, `event_gov_direct_enforcement_burst`, `event_gov_direct_size_split`: no burst difference (up to about +17% not excluded for enforcement).
- **Earnings surprise (2).** `earnings_surprise_sign_revenue`: hit rate 53.4% (2009-2018) and 52.9% (2019-2026), permutation p under 0.001, so real but under the 54% bar; operating income reads about 1.4 points higher on the same events (post hoc, and its forward test is frozen). `earnings_surprise_size_revenue`: high-to-low 1.02x, no relation.
- **8-K items (4).** `eightk_item_1_01_width` (1.06x), `eightk_item_5_02_width` (1.01x), `eightk_item_8_01_width` (1.17x, fading after the first era), `eightk_items_2_03_5_03_5_07_width` (about 1.0x). Item 7.01 is a lead.
- **Band mechanics (8).** `band_coverage_fixed_edge_1_645` (over-covers: ordinary 93.3%), `band_median_scale_all_groups` (fails earnings groups in 2013-2019), `event_band_class_calibration_audit` (no class flagged; spin-off event days cover about 71%), `spread_exjump_window`, `vol_regime_blend_base_spread`, `shared_structure_statistical_factors` (real but small, about 4.3% of the unexplained miss), `unrecorded_group_move_peers` (group moves 4.6% against 0.1% placebo, not material), `guidance_type_filing_ordinary_variance` (0.36% of the ordinary pool, not material).
- **The label's signed pull (1).** `event_label_signed_pull_center`: the sign is real but explains almost none of the squared miss.
- **News attention and tone (2).** `gdelt_article_spike_next_day_width` (matched shortfall +0.6 and +0.5 points, negligible), `gdelt_tone_shock_next_day_direction` (matched lift -0.7 and -0.7, so any effect above about 1 point is excluded; same-day tone correlates only about 0.01 with the same-day miss).
- **Macro (6).** `macro_cpi`, `macro_housing_starts`, `macro_oil_shock_energy_next_day`, `macro_yield_shock_utilities`, `context_labor_stress` (9.31% fell to 5.78% once crises were excluded), `context_oil_spike_crash`.
- **Long history, 1962-2026 (7).** `longhist_credit_widening_banks`, `longhist_equal_weight_size_transfer`, `longhist_masking_oil_alone_vs_with_other`, `longhist_masking_yield_banks_alone_vs_with_other`, `longhist_oil_size_gradient` (era-specific), `longhist_yield_shock_real_estate`, `longhist_yield_shock_utilities`.
- **The Federal Reserve (4).** `fed_change_day_banks_amplification` (1.078, interval 0.994 to 1.168), `fed_change_day_financials_amplification` (1.065 and 1.038, placebos clean), `fomc_rate_sensitive_sector_contrast` (1.044 and 1.001: the FOMC-day effect is market-wide, with no sector leader), and `fomc_pre_announcement_drift`, which **replicated historically** (+0.449% over two days, t 3.03, 1994-2011) **and faded** (+0.118%, t 0.92, 2012-2026); its null status reflects the persistence part of the rule.
- **Executive orders (2).** `eo_relevant_signing_day_market_move` (0.969 in 2004-2014, 1.009 in 2015-2026) and `eo_relevant_signing_market_wide_amplification` (0.994 pooled). **Watch item, post hoc:** 2025-2026 day +1 reads 1.158 (t +3.98); trade and tariff days (n 26) read 1.321 and 1.453 against 1.016 and 1.079 for the other orders; tariff orders are themselves market news, so this is descriptive only.
- **Laws (9).** `law_introduction_sector_move` (1.016), `law_first_passage_sector_move` (0.992), `law_final_passage_sector_move` (0.977), `law_signing_sector_move` (1.005), `law_final_passage_tail_ge3`, `law_signing_tail_ge3`, `law_company_persistence_same_area`, `law_events_after_gov_direct`, `law_events_after_reg_legal_restructuring`.
- **Human patterns (2).** `round_number_clustering_whole_dollar`: **the verdict is null only because the registered flat null model failed its calibration.** Whole-dollar closes land 3.19 times (2001-2013) and 1.71 times (2014-2026) as often as plain cents, a described fact. `round_number_threshold_move_size`: +1.07% and +1.25% in move size near round thresholds (t 2.18 and 2.47), unconfirmed, about 1% of a range.

## 6. Untested (12)

| flag | why |
|---|---|
| `earnings_role_bands_forward_test` | **frozen** 2026-10-22; evaluate once after prices exist through about 2027-01-05 |
| `earnings_surprise_sign_operating_income_forward` | **frozen** 2026-10-20; evaluate once after the season; a non-pass with fewer than 500 events is inconclusive, not null |
| `fed_state` | the pre-set sector-contrast test has not run; only four independent episodes |
| `company_state_filing_dated` | needs filing dates; closely tied to gate G6 |
| `flag_overlap_storm_testability` | counting step closed: the storm idea cannot be tested at the pair level on this universe (2 of 28 pairs testable, one of them mechanical) |
| `cascade_effect` | only about 8 to 10 plausible chained cases |
| `government_decisions_day_level` | partly tested (laws null, FOMC proven, executive orders null); its note was updated 2026-10-29 |
| `law_driven_charge_events_titles`, `law_named_charge_event_reaction` | counting steps; 13 distinct charge events attributed to a law drew about 40 to 50% of the burst of contemporaneous events (descriptive, post hoc, clustered) |
| `macro_other_series` | needs a real release calendar |
| `news_sentiment_gdelt` | its note now points to the two GDELT tests of 2026-10-22 (both null) |
| `local_flags` | not built |

## 7. Retired, and corrected

**Retired in the ledger (2).** `event_capital_raise_20d_discount` (fails the out-of-time rule; after the 10-19 repair 2004-2018 is about -0.019; explained by `event_type_capital_raise_no_burst`) and `event_type_ipo_spinoff` (the 1.95 reading was a spin-off price artifact; fewer than 40 clean events per era remain).

**Claims retired or downgraded from the earlier log of this file:**
- **2026-10-03, retracted:** the "validated magnitude prediction" (+9.2 to +13.4 points over baseline at five cutoffs) was measured against the training period's majority class instead of the test period's; against the honest baseline the model had no lift. Ledger row: `magnitude_model_features` (null).
- **2026-10-03, retracted:** "the effect emerges slowly" (multi-horizon) was a mechanical artifact.
- **2026-10-02, corrected:** the claim that sentiment excludes pre-2015 events was wrong.
- **Downgraded:** the storm / compounding effect ("validated, standing", neighbours within 40 days) survives only as the lead `storm_tier_large`.
- **Unconfirmed, never in the ledger:** the sector-peer ripple effect (z 17.49, n 1,215 peers) and the COVID-era factor attribution (R-squared 0.138, 8 events by 15 companies, n 120). Neither has been tested against the volatility confound that sank the magnitude model.
- **2026-10-19, repaired:** the reactions view had skipped days 0 and +1 for 4,971 events, which had made the event premium look as if it shrank as the event set grew; that reading was mostly this defect (`event_premium_20d`).
- **2026-10-22, scoring corrections:** several predictions recorded as "missed" were within sampling noise of their ranges; the ranges had been narrower than one standard error.
- **Tag-level significance:** the first-reported "6 of 13 tags significant" was tested against the wrong null and is retracted (docs/PROJECT_STATUS.md, section 5.3). It has no ledger row.

## 8. Where the ledger is stale or disagrees

**Repaired 2026-10-29** (append-only notes, no status changed; backup table flag_ledger_backup_20261029, to be dropped after 2026-11-28; see CHANGELOG): `fed_state` (the Fed raised the target range on 2026-09-16 and the view correctly reads tightening), `news_sentiment_gdelt` (its note now points to the two GDELT tests of 2026-10-22 and the table sizes; it stays untested), `government_decisions_day_level` (FOMC days and executive orders have since been tested), the three "uses the pooled number" rows (rerun numbers added; each note now says what proven means there), and the three rows that cited the retired SCRIPTS.md.

**Still open:**
1. **"proven" for a type that only "uses the pooled number"** (`event_type_acquisition`, `event_type_leadership_change`, `event_type_strategic_partnership`) is a different claim from the substantive findings. Each note now says so, but the status vocabulary still hides it inside the count of 15. Changing it may affect code that reads the status values, so the decision waits for gate G7.
2. **`fomc_pre_announcement_drift`** is null although the historical effect replicated; its note already says "REPLICATES, FADED", so no edit was needed.
3. **`storm_tier_large`:** the evidence unit is inferred and the original result file was not found (stated in its evidence row).
4. **Duplicated sentences** remain in the notes of `earnings_surprise_sign_operating_income_forward` (a frozen forward-test row, left untouched on purpose) and `longhist_oil_shock_oil_industry` (cosmetic).
5. **The tag-significance audit has no ledger row.** Adding one needs the audit's primary numbers, which have not been re-read (gate G7).

## 9. What would change this picture

- **The two frozen forward tests** (both "untested" above), evaluated once after 2027-01-05, each against its pre-set rule.
- **Re-running the 12 substantive proven findings on the cleaned analysis set** (excluded events removed, independent clusters reported): gate G7. A finding that survives has earned the word; one that does not is a finding about the data.
- **Pre-set tests for the yield-shock leads** (Banks up, Health Care down), which pass their nulls from 1986 on but have only a post-hoc origin.
- **A point-in-time firm state** (gate G6): until then no label that depends on firm state, including `diverged`, can be tested.
- **The 2025-2026 executive-order watch item,** which needs its own pre-set forward test.

## 10. The standard

A claim is a pattern only when it declares universe, horizon, benchmark, base rate, similarity keys, magnitude with an interval, and an out-of-sample window; the sample size is stated as rows **and** independent clusters (a company's events within 28 days count once). See PROJECT_PLAN.md, section 3. A null is recorded with the same weight as a positive result: it says where not to spend time and prevents finding the same null twice.
