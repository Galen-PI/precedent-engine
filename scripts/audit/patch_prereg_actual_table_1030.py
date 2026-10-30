"""patch_prereg_actual_table_1030.py (2026-10-30): appends Addendum 12 (G7 complete: the actual values of all 52 registered rows and what they do and do not say)
and the ACTUAL-TABLE block to results/PREREG_g7_proven_rerun_2026-10-29.md. The registration must be exactly the version after Addendum 11 (sha256 e5980272...) and the placeholder
must occur exactly once, or nothing is changed. No registered prediction is edited: the text before PRED-TABLE-END is compared before and after.
Usage: python3 scripts/audit/patch_prereg_actual_table_1030.py [results/PREREG_g7_proven_rerun_2026-10-29.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "results/PREREG_g7_proven_rerun_2026-10-29.md"
T = open(p, encoding="utf-8").read()
assert sha(T) == "e5980272862263af0efa7975e6b29410bd8821942632654ba44032e2408707be", "the registration is not the version after Addendum 11; nothing changed"
old = "(further dated addenda go here: the remaining procedures)"
assert T.count(old) == 1, "placeholder not found exactly once; nothing changed"
new = """### Addendum 12 (2026-10-30, G7 complete): the actual values of all 52 registered rows, and what they do and do not say

**Sources of the values.** p1 to p10 and p51: the outcome table of Addendum 2 (the three controls). p11 to p17, p21 to p32: the actuals files results/g7_rerun/actuals_role_band_2026-10-30.txt, actuals_earn_width_2026-10-30.txt, actuals_range_2026-10-30.txt, actuals_event_width_2026-10-30.txt, actuals_direction_2026-10-30.txt and actuals_band_calibrate_2026-10-30.txt. p18 to p20 and p37 to p49: the by-type results file results/g7_rerun/bytype_all_steps_2026-10-29.out. p33 to p36: results/g7_rerun/actuals_premium_2026-10-30.txt (the values are in its reading; the standard errors are the naive ones of its ARM 1 de-duplicated rows). p50 and p52 are derived from the other rows. The values of p11 to p23, p27 to p29, p33 to p36 and p37 to p49 describe ARM 1 (checked against their files and the by-type results); for p24 to p26 and p30 to p32 the arm is the one their actuals files record, which was not re-checked when this addendum was written; the controls have no arm.

**What the table says.** All 15 flags were re-run, each by its own registered rule, and all 15 pass it (p50 = 1); the oil control passes its rule but missed the tolerance registered for it (p10 = 0, Addendum 2). Of the 33 numeric rows, 32 land inside their 80 percent intervals and 1 outside: p9, the energy amplification of 2019-2026 (1.324 against 1.316 to 1.322), which Addendum 2 attributes to two months (2026-08 and 2026-09) added to sector_day_z after the ledger's window. The registered trigger for widening later intervals (10 or more numeric rows outside, item 5 of WHAT WOULD CHANGE THE PLAN) did not fire (p52 = 0). Of the 19 probability rows, 17 are true; the two false ones are p10 and p52. Item 1 of the same list happened: a control missed its registered tolerance and the run stopped until the cause was found (p51 = 1, registered at 0.09). The 32 of 33 is a hit rate of 97 percent against a nominal 80 percent; many of the rows are near-mechanical reproductions (the controls, with intervals of a few thousandths), so this is NOT evidence that intervals can be narrower, and no change to later intervals is drawn from it.

**Recorded plainly, as the registration requires (items 2 and 4).** (1) event_premium_20d came back WEAKER than the ledger: +0.0433 for the pooled 2004-2018 premium against the ledger's +0.0550, inside the registered interval (0.040 to 0.068) but close to its lower end (12 percent of the interval width from it), because four price-artifact events carrying an exclude row were removed; its rule category is B (above the registered range) by the naive SE, by a margin of 0.0004, and A by the clustered SE (actuals_premium_2026-10-30.txt). (2) event_daily_range_coverage and event_label_direction_sign came back unchanged by the cleaning (6.71 and 9.22 points; 57.7 and 57.8 percent). (3) For event_daily_range_coverage only part (3) of the ledger's three-part rule was rebuilt; parts (1) and (2) stand as recorded, and the frozen forward test is untouched.

**What has NOT been done.** The flag_ledger table is not updated (evidence rows and notes are an append-only batch that needs Galen's approval of the wording); no status was changed (a change of status is Galen's, after the January check, as registered); the frozen forward tests and the January data checks are pending (evaluated once after 2027-01-05); G4, G8, G9 and G10 are open. The new tables of the rebuilds (events_ratio_g7_arm0, events_ratio_g7_arm1, flag_days_g7_arm0, flag_days_g7_arm1, ctrl_days_g7_arm0, ctrl_days_g7_arm1) and the functions ratio_period_g7_arm0 and ratio_period_g7_arm1 are to be dropped after 2026-11-28.

(further dated addenda go here: none planned)

ACTUAL-TABLE-BEGIN
p1 | 89.63 |
p2 | 91.08 |
p3 | 0.9834 |
p4 | 1 |
p5 | 1.14 |
p6 | 1.112 |
p7 | 1 |
p8 | 1.293 |
p9 | 1.324 |
p10 | 0 |
p11 | 0.869 |
p12 | 0.857 |
p13 | 88.5 |
p14 | 1 |
p15 | 2.0071 |
p16 | 2.72 |
p17 | 1 |
p18 | 1.298 | 0.018
p19 | 1.331 | 0.022
p20 | 1 |
p21 | 6.71 |
p22 | 9.22 |
p23 | 1 |
p24 | 1.6 |
p25 | 0.5410 |
p26 | 1 |
p27 | 57.7 |
p28 | 57.8 |
p29 | 1 |
p30 | 88.47 |
p31 | 88.14 |
p32 | 1 |
p33 | 0.0433 | 0.0067
p34 | 0.0368 | 0.0104
p35 | 1 |
p36 | 1 |
p37 | 1.03 | 0.040
p38 | 1.098 | 0.072
p39 | -3.24 |
p40 | 1 |
p41 | 1.272 | 0.031
p42 | 1.333 | 0.043
p43 | 1 |
p44 | 1.24 | 0.031
p45 | 1.262 | 0.030
p46 | 1 |
p47 | 1.237 | 0.076
p48 | 1.381 | 0.108
p49 | 1 |
p50 | 1 |
p51 | 1 |
p52 | 0 |
ACTUAL-TABLE-END
"""
head_before = T[:T.index("PRED-TABLE-END")]
R = T.replace(old, new)
assert R[:R.index("PRED-TABLE-END")] == head_before, "a registered prediction would change; nothing written"
open(p, "w", encoding="utf-8").write(R)
R2 = open(p, encoding="utf-8").read(); print("ok   Addendum 12 and the ACTUAL-TABLE appended"); print("PREREG sha256", sha(R2), "|", R2.count("\n"), "lines")
