"""patch_prereg_addenda23_1029.py (2026-10-29): appends Addendum 2 (the three controls) and Addendum 3 (the by-type burst procedure) to results/PREREG_g7_proven_rerun_2026-10-29.md,
AFTER the controls ran and BEFORE any event-level run (Addendum 3 is the procedure for the next flags). Text only; no prediction is edited. Gated on the exact committed hash of the file
after Addendum 1. Usage: python3 scripts/audit/patch_prereg_addenda23_1029.py [results/PREREG_g7_proven_rerun_2026-10-29.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "results/PREREG_g7_proven_rerun_2026-10-29.md"
T = open(p, encoding="utf-8").read()
assert sha(T) == "2ebef592289e4b514971ba2e76c514ef8d395a331027f210f5b5d07a5982617e", "the registration is not the version after Addendum 1; nothing changed"
old = "(further dated addenda go here: the by-type SQL, the role-band pin, the remaining procedures)"
assert T.count(old) == 1, "placeholder not found exactly once; nothing changed"
new = """### Addendum 2 (2026-10-29, after the three controls, before any event-level run): outcomes, one stated deviation, and a new rule

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

(further dated addenda go here: the role-band pin, the remaining procedures)"""
open(p, "w", encoding="utf-8").write(T.replace(old, new))
R = open(p, encoding="utf-8").read(); print("ok   Addenda 2 and 3 appended"); print("PREREG sha256", sha(R), "|", R.count("\n"), "lines")