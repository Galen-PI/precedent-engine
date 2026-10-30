"""patch_prereg_addendum5_1030.py (2026-10-30): appends Addendum 5 (event_day_width_own_events via scripts/card/event_width_test.py) to
results/PREREG_g7_proven_rerun_2026-10-29.md BEFORE the run. Text only; no prediction is edited. Gated on the exact committed hash after Addendum 4a.
Usage: python3 scripts/audit/patch_prereg_addendum5_1030.py [results/PREREG_g7_proven_rerun_2026-10-29.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "results/PREREG_g7_proven_rerun_2026-10-29.md"
T = open(p, encoding="utf-8").read()
assert sha(T) == "6eb95c259a332ce7a99f20173ed1b57aa5849714a4d5c541e7a3673dbc1db9c9", "the registration is not the version after Addendum 4a; nothing changed"
old = "(further dated addenda go here: the remaining procedures)"
assert T.count(old) == 1, "placeholder not found exactly once; nothing changed"
new = """### Addendum 5 (2026-10-30, before the run): event_day_width_own_events, scripts/card/event_width_test.py

**Every input the procedure reads (the rule of Addendum 4a).**
- **Code:** scripts/card/event_width_test.py and scripts/card/decomp_validation.py (imported as dv), both exactly as at commit 798e1e7f (2026-10-20 16:06:22, the last commit before the original run, which is stamped 16:11). Neither module changed between ea2a09f (the ledger's date pin) and 798e1e7f. Both use only the standard library (decomp_validation imports os, sys, pickle, glob, math, json, time, bisect); no model files are read.
- **Cache:** data_cache/returns, 500 files (one per security plus _macro.pkl), read through the relative path "data_cache/returns", so the run must start at the worktree root; none of its files is newer than the original run (checked: 0), and the worktree links the repository's data_cache.
- **Database tables:** securities, event_direction_labels (22,283 labels at the original run) and ev_ent (event_id, entity_id, d, ptype).
- **Writes:** none by event_width_test.py. decomp_validation writes scripts/card/out/decomp_validation.json only in its own main, which is not run.
- **Original output:** results/2026-10-19/event_width_full.log (57 lines, 108 seconds, file time 2026-10-20 16:11; first line: 498 securities, 8,250 trading days 1994-01-03 to 2026-10-13, events mapped for 491 securities, direction labels 22,283; verdict lines: E1 - W0, E3 - W2 and E5 each EARNS ITS PLACE, claim SUPPORTED).

**Set-up.** git worktree add /tmp/g7_pin_ew 798e1e7f, a symbolic link /tmp/g7_pin_ew/data_cache to the repository's data_cache, runs from /tmp/g7_pin_ew. The worktree is removed afterwards.

**ARM 0** is the pinned script, unpatched, no arguments (the full run). It must reproduce the original log: the first line's counts, the three gains per era within 0.005 nats, the years-positive counts identical (E5 22 of 22) and the verdict lines identical. The tables that use the direction labels may differ if the labels table has changed since 2026-10-20 (the first line prints its count); a difference there is recorded and does not stop the run, a difference in the three registered gains does.

**ARM 1** is the same after scripts/audit/g7_patch_arm1_event_width.py edits the worktree's copy of event_width_test.py (the same exact-match edit as for band_calibrate.py: rows of ev_ent whose event has an exclude row are skipped, and the run prints how many; the loader is the same code at line 83). The patch is hash-checked, refuses a second application and any path outside /tmp.

**Tripwires.** ARM 1 prints "1527 excluded events; 716 of 22338 ev_ent rows removed" (the pre-check of 2026-10-30, since the table has not changed); the three gains differ at least in the last digit between the arms; each arm's console output is saved in results/g7_rerun/ with the arm in the name, and the patch diff is saved.

**Registered rows.** p24 to p26 (the band multiplier against an ordinary day, the E3 - W2 gain in 2013-2019, and the pass) describe ARM 1.

**Stated in advance.** The filter removes 3.2 percent of the ev_ent rows, but its effect on the three gains should be small: the days of an excluded event become ordinary days, and where an excluded event shared a day with a kept event the rule 'the first event by event_id supplies the type, size and timing' now picks the kept one. The tables by type and by size or timing can move more than the three gains. The effective sample is smaller than the row count (event days are about 1.5 percent of stock-days and are not independent of the market around them).

(further dated addenda go here: the remaining procedures)"""
open(p, "w", encoding="utf-8").write(T.replace(old, new))
R = open(p, encoding="utf-8").read(); print("ok   Addendum 5 appended"); print("PREREG sha256", sha(R), "|", R.count("\n"), "lines")
