"""patch_prereg_addendum1_1029.py (2026-10-29): appends Addendum 1 to results/PREREG_g7_proven_rerun_2026-10-29.md, BEFORE any run.
Text only: the PRED-TABLE and every prediction are untouched. Gated on the exact committed hash; the placeholder must match once.
Usage: python3 scripts/audit/patch_prereg_addendum1_1029.py [results/PREREG_g7_proven_rerun_2026-10-29.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "results/PREREG_g7_proven_rerun_2026-10-29.md"
T = open(p, encoding="utf-8").read()
assert sha(T) == "c821bf5b36f9522d2fdfbf3d5ec693c777e7ff05d395893a0c9047f62c9a87e6", "the registration is not the committed version; nothing changed"
old = "(procedure, script interfaces and how each script is pointed at the cleaned set go here, after they are read and before any run)"
assert T.count(old) == 1, "placeholder not found exactly once; nothing changed"
new = """### Addendum 1 (2026-10-29, written before any run): the corrected design, what is known about each procedure, and the controls

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

(further dated addenda go here: the by-type SQL, the role-band pin, the remaining procedures)"""
open(p, "w", encoding="utf-8").write(T.replace(old, new))
R = open(p, encoding="utf-8").read(); print("ok   Addendum 1 appended"); print("PREREG sha256", sha(R), "|", R.count("\n"), "lines")