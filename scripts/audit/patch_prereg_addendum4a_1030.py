"""patch_prereg_addendum4a_1030.py (2026-10-30): appends Addendum 4a (a failed first attempt of the band_calibrate Arm 0, its cause and its fix, plus a new
rule for procedure addenda) to results/PREREG_g7_proven_rerun_2026-10-29.md BEFORE the retry. Text only; no prediction is edited. Gated on the exact committed
hash after Addendum 4. Usage: python3 scripts/audit/patch_prereg_addendum4a_1030.py [results/PREREG_g7_proven_rerun_2026-10-29.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "results/PREREG_g7_proven_rerun_2026-10-29.md"
T = open(p, encoding="utf-8").read()
assert sha(T) == "c1f4dcb2e821372d855e43d847941498731b6638d236ce3a8b34433debf4d452", "the registration is not the version after Addendum 4; nothing changed"
old = "(further dated addenda go here: the remaining procedures)"
assert T.count(old) == 1, "placeholder not found exactly once; nothing changed"
new = """### Addendum 4a (2026-10-30, before the retry): the first Arm 0 attempt of band_calibrate.py failed; cause, fix, and a new rule

**What happened.** The first attempt (pinned worktree at 22a26ff, after the pre-check and the registration commit 52550ee) stopped at the script's first input check: "models/earnings_band_model.json not found." Nothing was computed and no model file was written. Its console output is kept as results/g7_rerun/band_calibrate_arm0_attempt1_FAILED_missing_model_2026-10-30.out; the model-file copy that the command had made (a copy of the file as committed at the pin, not a product of any run) was deleted.

**Cause.** Addendum 4 said the two model files come "as at the pin" without checking that both are tracked at the pin. models/earnings_band_model.json is not in commit 22a26ff: it was first committed in 4e06a3c (2026-10-20 18:17:06), almost two hours after the pin (16:22:44). The copy on disk was written at 15:26, before the original printout (16:20:25 on 2026-10-20), so it is the file the original run read. models/event_band_model.json is at the pin (last commit 39015c4, 2026-10-20 13:43:31).

**Fix.** The file is taken from git, not from the disk: git show 4e06a3c:models/earnings_band_model.json is written into the worktree's models/ folder, and only after its sha256 is shown to equal the sha256 of the file on disk (which proves that the file the original run read and the committed file are the same bytes). The pin plus that one file is then the original run's input set. Nothing else in Addendum 4 changes: ARM 0, ARM 1, the tolerances, the tripwires and the registered rows p30 to p32 stand.

**New rule for every procedure addendum from here on.** The addendum lists EVERY input the procedure reads (code and imported modules, model files, caches, database tables) and states, from git or the file system, that each exists at the pin or how it is supplied and verified, before the registration is committed. The registration commit is not evidence that the procedure runs.

**One more fact recorded before the retry.** The pre-check gave ev_ent 22,338 rows, 716 of which ARM 1 removes (3.2 percent), latest day 2026-09-11, latest 8-K 2026-09-18: of the 1,527 excluded events only 716 have rows in ev_ent, so the exclusion filter here is smaller than in the by-type run.

(further dated addenda go here: the remaining procedures)"""
open(p, "w", encoding="utf-8").write(T.replace(old, new))
R = open(p, encoding="utf-8").read(); print("ok   Addendum 4a appended"); print("PREREG sha256", sha(R), "|", R.count("\n"), "lines")