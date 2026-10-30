"""patch_prereg_addendum9_1030.py (2026-10-30): appends Addendum 9 (the procedure for event_label_direction_sign, scripts/card/direction_test.py)
to results/PREREG_g7_proven_rerun_2026-10-29.md. The registration must be exactly the version after Addendum 8 (sha256 cb7896cc...) and the placeholder must occur
exactly once, or nothing is changed. No registered prediction is edited: the text before PRED-TABLE-END is compared before and after.
Usage: python3 scripts/audit/patch_prereg_addendum9_1030.py [results/PREREG_g7_proven_rerun_2026-10-29.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "results/PREREG_g7_proven_rerun_2026-10-29.md"
T = open(p, encoding="utf-8").read()
assert sha(T) == "cb7896ccdc81f811e6b61a42cacb38094c5aacbb9669eca4d0bca89c5d377bef", "the registration is not the version after Addendum 8; nothing changed"
old = "(further dated addenda go here: the remaining procedures)"
assert T.count(old) == 1, "placeholder not found exactly once; nothing changed"
new = """### Addendum 9 (2026-10-30, before the run): event_label_direction_sign, scripts/card/direction_test.py

**What the script does, read from its own text and its printout.** It is read-only (console output only). It asks whether the news-direction label (good or bad, from event_direction_labels) predicts the SIGN of the stock's abnormal return over days 0 and +1, computed from the closes (stock return minus the S&P 500 return). The sample is the events labeled good or bad (mixed and unclear are left out) with usable closes, minus the type systemic_shock, thinned to the earliest event per ticker per calendar week; eras are split at 2019-01-01. A hit is label good with a positive abnormal return, or label bad with a negative one. Its pass line, written before any label existed: in BOTH eras at least 800 events, a hit rate of at least 55%, the lower end of the 95% Wilson interval above 50%, and a hit rate that beats a within-type permutation null (p of at most 0.05; labels shuffled among the events of the same type and era, 2,000 shuffles, generator seeded with 11). The labeler's prompt is frozen. Usage: python3 -u scripts/card/direction_test.py, no arguments; credentials from the environment; the environment variable REACTIONS_TABLE must be unset.

**Original printout.** results/2026-10-19/direction_test.out (36 lines), committed in 29c8cd6 (2026-10-20 16:12:19, 'Baseline logs regenerated and saved'), after the script's last commit. It is a regenerated baseline of the final version of the script; its numbers equal the once-only run seen in the session record of 2026-10-19 (22,283 labels; 57.7% on 4,212 events and 57.8% on 1,311). It has no elapsed-time line, so ARM 0 is compared with it without any normalization.

**Pin.** Commit ea2a09f (2026-10-19 19:07:30), the last of the script's three commits (5f85f42 at 18:24:22 and 9299f41 at 18:41:46 before it) and the one that makes it read the frozen reaction table. The script's imports are the standard library plus the supabase client (inside get_sb); it imports no local module, so none of the earlier ARM 1 patches applies and a new one is used (below).

**Every input, checked on 2026-10-30 from git and the database (the rule of Addendum 4a).**
1. Code: the script (232 lines) at the pin; its top level holds imports and constants (ERA_SPLIT, REACTIONS_TABLE, EXCLUDED_TYPES, MIN_N, B); its reads begin in main().
2. Database tables, read over REST (credentials in the environment): event_direction_labels (event_id, ticker, ptype, event_date, label, size, timing): 22,283 rows, 3,147 good, 2,700 bad, latest event date 2026-09-11, all identical to the original printout; event_market_reactions_v2_snapshot_20261019, a FROZEN copy of the repaired reaction view taken on 2026-10-19: 23,348 rows, so later reaction repairs and the 2026-10-29 date corrections are NOT part of this re-run by design; event_exclusions (event_id, severity) for ARM 1 only.
3. No matrices, no price cache, no model file and no file on disk are read; the permutation generator is seeded (random.Random(11)), so its p-values reproduce.
4. Output: console only; each arm is saved with the same redirect as the original (standard output and standard error together) under results/g7_rerun/.

**Pre-check of ARM 1 (SQL, 2026-10-30).** 217 labeled good or bad events carry an exclude row; only 2 of them have usable stock closes in the frozen table. The number 217 equals the original printout's 'unusable closes: 217', so about 215 of them are already dropped by the script as unusable.

**Set-up.** git worktree add /tmp/g7_pin_dir ea2a09f (its commit line is printed). The script reads nothing from data_cache, so no link is made and the worktree's git status must print nothing in ARM 0. The worktree is removed afterwards.

**ARM 0** is the pinned script, unpatched. Its output must be identical, line by line, to the original printout (starting with 22,283 labels, 3,147 good, 2,700 bad; 5,626 usable; 5,523 after thinning; 57.7% on 4,212 and 57.8% on 1,311; permutation p 0.000 and 0.001; verdict PASS). If any line differs, the run STOPS and the cause (the label table, the frozen table, the environment variable, or the code) is found before ARM 1.

**ARM 1** is the same after scripts/audit/g7_patch_arm1_direction_v1.py edits ONLY the worktree's copy of direction_test.py: right after the labels are read, labels whose event_id has an exclude row in event_exclusions are removed, before the sample is built and thinned, so an excluded event cannot block a neighbour in the weekly thinning; the number of labels removed is printed. The patch refuses a second application, a path outside /tmp and a target line that does not match exactly once, and was tested on a faithful copy of load_events (an excluded event is dropped, a row whose severity is note is kept, reactions are fetched only for the labels that remain).

**Tripwires.** (1) ARM 1 prints that 1,527 excluded events are in scope and that between 217 and 1,527 of the 22,283 labels were removed (the 217 good or bad events of the pre-check are among them); the first output line must show good plus bad equal to 5,847 minus 217, that is 5,630. (2) The usable events must not rise and must fall by at most 2 (5,626 to between 5,624 and 5,626); the unusable-closes count falls by up to 215. (3) The worktree's git status must print nothing in ARM 0 and only the edited file in ARM 1; each arm's output and the patch diff are saved to results/g7_rerun/ with the arm in the name.

**Stated in advance.** (a) The registered rows p27 to p29 describe ARM 1; ARM 0 is reported beside it. (b) ARM 1 is expected to be almost identical to ARM 0: at most 2 usable events leave the sample (plus any knock-on change in the weekly thinning), so the hit rates should move by about 0.1 points or less. (c) No cell of the rule is thin: the lowest margin is the Wilson lower end of 55.1% in 2019-2026 against 50%, and the smallest era has 1,311 events against the minimum of 800. (d) The labels come from a language-model labeler with a frozen prompt and are not independent of the events they label; the test uses a frozen copy of the reaction table, so it tests the event set (ARM 1) and not any later change to prices. (e) Sealed versus non-sealed is not reported: the script has no company-set split. Nothing here re-scores or edits a prediction.

(further dated addenda go here: the remaining procedures)"""
head_before = T[:T.index("PRED-TABLE-END")]
R = T.replace(old, new)
assert R[:R.index("PRED-TABLE-END")] == head_before, "a registered prediction would change; nothing written"
open(p, "w", encoding="utf-8").write(R)
R2 = open(p, encoding="utf-8").read(); print("ok   Addendum 9 appended"); print("PREREG sha256", sha(R2), "|", R2.count("\n"), "lines")
