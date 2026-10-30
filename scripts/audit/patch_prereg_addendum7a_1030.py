"""patch_prereg_addendum7a_1030.py (2026-10-30): appends Addendum 7a (a correction to the description of the earlier ARM 1 patch) to
results/PREREG_g7_proven_rerun_2026-10-29.md. The registration must be exactly the version after Addendum 7 (sha256 a8d53a1e...) and the placeholder must occur
exactly once, or nothing is changed. No registered prediction is edited: the text before PRED-TABLE-END is compared before and after.
Usage: python3 scripts/audit/patch_prereg_addendum7a_1030.py [results/PREREG_g7_proven_rerun_2026-10-29.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "results/PREREG_g7_proven_rerun_2026-10-29.md"
T = open(p, encoding="utf-8").read()
assert sha(T) == "a8d53a1eb55f92bb747114a9be8f3cad4012e57e39839919ea451ff0e6794a6d", "the registration is not the version after Addendum 7; nothing changed"
old = "(further dated addenda go here: the remaining procedures)"
assert T.count(old) == 1, "placeholder not found exactly once; nothing changed"
new = """### Addendum 7a (2026-10-30, before the run): a correction to the description of the earlier ARM 1 patch

Addendum 7 described scripts/audit/g7_patch_arm1_event_width.py from the copy printed in the 2026-10-30 session record and left open whether the committed copy differs. The check was made, read-only, in the save block of Addendum 7 (a grep of the committed file). The committed copy DOES refuse a second application (its line 12 asserts that the filter is not already present) and DOES print how many ev_ent rows it removed (it collects the rows, keeps those whose event_id is not in the exclusion set, and prints the number removed). The copy in the session record was therefore an earlier draft, and the two reasons Addendum 7 gives for writing v2 (the count is not printed; a second application is not refused) are wrong for the committed patch; Addendum 4's statement that the earlier patch refuses a second application was right.

The procedure does not change. ARM 1 uses scripts/audit/g7_patch_arm1_event_width_v2.py as registered in Addendum 7, because it is committed, was tested on a faithful copy of load_event_info, and removes the same rows (those whose event_id has an exclude row in event_exclusions), skipping them inside the loop instead of collecting the rows first. The tripwires are unchanged (716 skipped rows expected). Nothing in this correction edits a prediction.

(further dated addenda go here: the remaining procedures)"""
head_before = T[:T.index("PRED-TABLE-END")]
R = T.replace(old, new)
assert R[:R.index("PRED-TABLE-END")] == head_before, "a registered prediction would change; nothing written"
open(p, "w", encoding="utf-8").write(R)
R2 = open(p, encoding="utf-8").read(); print("ok   Addendum 7a appended"); print("PREREG sha256", sha(R2), "|", R2.count("\n"), "lines")
