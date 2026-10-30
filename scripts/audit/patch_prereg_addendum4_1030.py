"""patch_prereg_addendum4_1030.py (2026-10-30): appends Addendum 4 (band_edge_calibration_90 via scripts/card/band_calibrate.py) to
results/PREREG_g7_proven_rerun_2026-10-29.md BEFORE the run. Text only; no prediction is edited. Gated on the exact committed hash (after Addenda 2 and 3).
Usage: python3 scripts/audit/patch_prereg_addendum4_1030.py [results/PREREG_g7_proven_rerun_2026-10-29.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "results/PREREG_g7_proven_rerun_2026-10-29.md"
T = open(p, encoding="utf-8").read()
assert sha(T) == "a237e3d05abb669fb883c82f7043976a8aaa1bfb4d93e69fda716d4aa711182d", "the registration is not the version after Addenda 2 and 3; nothing changed"
old = "(further dated addenda go here: the role-band pin, the remaining procedures)"
assert T.count(old) == 1, "placeholder not found exactly once; nothing changed"
new = """### Addendum 4 (2026-10-30, before the run): band_edge_calibration_90, scripts/card/band_calibrate.py

**What the script does, read from its own text.** It is read-only on the database but WRITES models/band_calibration.json, a live model the card uses, so it runs only inside a pinned git worktree: its ROOT is computed from the script's own location, which puts the write inside the worktree and leaves the live file untouched. It reads data_cache/audit_matrices.npz (built 2026-10-20), models/event_band_model.json and models/earnings_band_model.json (as at the pin), the database table sec_8k_filings (earnings windows and Regulation FD filings) and, through event_width_test.load_event_info, the tables event_direction_labels and ev_ent (event_id, entity_id, d, ptype), which supply the recorded event days. Usage: python3 -u scripts/card/band_calibrate.py, no arguments; credentials from the environment. Its original printout is results/2026-10-19/band_calibrate.out (31 lines, 43 seconds).

**Pin.** Commit 22a26ff (2026-10-20 16:22:44, the script's only commit), the earliest faithful state of the code and of its two imported modules (event_width_test.py as of ea2a09f; day_card.py as of the pin; later commits to day_card.py are not included). The printout is filed under 2026-10-19 but the script's commit is 2026-10-20, so the printout may come from an earlier uncommitted version; ARM 0 tests that.

**Set-up (the same commands will be run):** git worktree add /tmp/g7_pin_band 22a26ff, then a symbolic link /tmp/g7_pin_band/data_cache to the repository's data_cache. The worktree is removed afterwards.

**ARM 0** is the pinned script, unpatched. It must reproduce the original printout: the matrices line (496 stocks x 8250 days); ordinary coverage 90.21% within 0.05 points; every other group within 0.20 points of its printed coverage in each era; every group CALIBRATED; fitted edges within 0.01 band units. If it does not, the run STOPS and the cause (database drift in ev_ent or event_direction_labels since 2026-10-20, or code) is found before ARM 1.

**ARM 1** is the same after scripts/audit/g7_patch_arm1_event_width.py edits ONLY the worktree's copy of event_width_test.py: rows of ev_ent whose event_id has an exclude row in event_exclusions are skipped, so their days stop being recorded event days. The patch is hash-checked, refuses a second application and any path outside /tmp, and the run prints how many ev_ent rows it removed. The registered rows p30 to p32 describe ARM 1.

**Pre-check (SQL, before ARM 0):** the latest ev_ent day, the ev_ent row count, the number of ev_ent rows the filter removes, and the latest 8-K filing date.

**Tripwires.** (1) The removed-rows count printed by ARM 1 equals the pre-check's number. (2) In ARM 1 the group 'recorded event, no earnings' (25,485 days in the original) and 'earnings window + recorded event' (3,044) must shrink; identical group sizes in ARM 0 and ARM 1 mean the filter did nothing. (3) Each arm's console output and the model file it wrote are copied to results/g7_rerun/ with the arm in the name, and the patch diff is saved.

**Stated in advance.** Group sizes change in ARM 1 because the days of excluded events move out of the 'recorded event' groups into 'ordinary' or 'earnings, no event': a composition effect, not noise. The registered rule is unchanged (coverage within 88% to 92% in each judged era with at least 1,000 scored days). The thin margins in the original printout are: earnings day +1 88.14% in 2013-2019 (0.14 above the line), earnings + event 88.46% in 2020-2026 (0.46), earnings day 0 88.53% in 2013-2019 (0.53), earnings + event 88.57% in 2013-2019, recorded event 88.72% in 2013-2019; any of them can fail on a shift of 0.1 to 0.5 points, which is what p32 prices.

(further dated addenda go here: the remaining procedures)"""
open(p, "w", encoding="utf-8").write(T.replace(old, new))
R = open(p, encoding="utf-8").read(); print("ok   Addendum 4 appended"); print("PREREG sha256", sha(R), "|", R.count("\n"), "lines")