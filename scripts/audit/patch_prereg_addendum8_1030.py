"""patch_prereg_addendum8_1030.py (2026-10-30): appends Addendum 8 (the procedure for event_earnings_window_width, scripts/card/earnings_thread_test.py)
to results/PREREG_g7_proven_rerun_2026-10-29.md. The registration must be exactly the version after Addendum 7a (sha256 1ce898e3...) and the placeholder must occur
exactly once, or nothing is changed. No registered prediction is edited: the text before PRED-TABLE-END is compared before and after.
Usage: python3 scripts/audit/patch_prereg_addendum8_1030.py [results/PREREG_g7_proven_rerun_2026-10-29.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "results/PREREG_g7_proven_rerun_2026-10-29.md"
T = open(p, encoding="utf-8").read()
assert sha(T) == "1ce898e369295db136abf7e328acf23c7b408939df4b7c7cb27c8b6c5accd683", "the registration is not the version after Addendum 7a; nothing changed"
old = "(further dated addenda go here: the remaining procedures)"
assert T.count(old) == 1, "placeholder not found exactly once; nothing changed"
new = """### Addendum 8 (2026-10-30, before the run): event_earnings_window_width, scripts/card/earnings_thread_test.py

**What the script does, read from its own text and its printout.** It is read-only (console output only). Over every stock and year it asks whether earnings-release days (8-K item 2.02; day 0 is the first trading day on or after the filing date, day +1 the day after) widen the miss beyond an ordinary day, how much more often big misses with no recorded event fall on earnings days, and how much of the unexplained squared miss sits on them. Its rule, written before its first run: it EARNS ITS PLACE if the walk-forward gain in Gaussian log score is at least 0.005 nats per earnings stock-day in each of 2006-2012, 2013-2019 and 2020-2026 and positive in at least 70% of test years; the PRIMARY group is earnings days with no recorded event, day 0 and day +1 together. Usage: python3 -u scripts/card/earnings_thread_test.py, no arguments; credentials from the environment. Original printout: results/2026-10-19/earnings_thread_full.out (26 lines, 19 seconds), made by python3 -u scripts/card/earnings_thread_test.py > results/2026-10-19/earnings_thread_full.out 2>&1 and committed together with the script in 10cd146 (2026-10-20 14:34:17); the folder name 2026-10-19 is not the date of the run.

**Units, checked.** The printout labels the gain in nats and its values (+1.3260, +2.0072, +1.7741 per earnings stock-day) are consistent with a multiplier near 2.7: the log-score gain of using the right scale instead of the ordinary one is half of (m squared minus 1 minus the natural log of m squared), about 2.2 nats at m = 2.7. The registered rows p15 and p16 are in these units. The rule's margin is very wide (a gain of at least 0.005 against 1.33 to 2.01), so no verdict risk comes from the rule itself; the narrow registered intervals (plus or minus 0.05 on the gain, plus or minus 0.03 on the multiplier) are what p15 and p16 price.

**Pin.** Commit 10cd146, the script's only commit and the earliest faithful state of the code. The script's only local import is event_width_test.py, which has one commit (ea2a09f, 2026-10-19 19:07:30, before the pin), so it is identical at the pin and at HEAD; the two target lines of the ARM 1 patch matched exactly once in that file earlier today.

**Every input, checked on 2026-10-30 from git, the file system and the database (the rule of Addendum 4a).**
1. Code: the script (196 lines) and event_width_test.py, from the worktree at the pin. The script's top level holds imports, constants (CACHE_FILE, TEST_START, MIN_PRIOR, ERAS) and function definitions; its reads begin in main(). The import-time statements of event_width_test.py were read earlier today: constants only.
2. data_cache/audit_matrices.npz: sha256 7bd617a487a40d8949ecbad3cbb7481b9f1ae61df4b9eac76edb2255023963e6, written 2026-10-20 14:16, 18 minutes before the script's commit; 496 stocks by 8,250 days, 1994-01-03 to 2026-10-13; supplied by a symbolic link to the repository's data_cache; its hash is printed again before ARM 0 and must match.
3. Database tables, read over REST (credentials in the environment): sec_8k_filings (security_id, filing_date, rows whose item_codes contain 2.02): 41,459 filings, the same number as in the original printout, 41,046 distinct stock-dates in it; securities; event_direction_labels (read by event_width_test.load_event_info and unused by this script's result); ev_ent (22,338 rows, latest day 2026-09-11), the recorded event days (41,579 in the original printout). ARM 1 also reads event_exclusions (event_id, severity).
4. No price cache, no model file and no random generator are used.
5. Output: console only; each arm is saved with the same redirect as the original run (standard output and standard error together) under results/g7_rerun/.

**Latest dates compared with the original run (the rule of Addendum 2).** The matrices end 2026-10-13 and were written before the original run; sec_8k_filings has 155,141 rows through 2026-09-18 with 41,459 item-2.02 filings, the number the original printout shows; ev_ent has latest day 2026-09-11. The first line of the printout (matrices, filings, flagged days, recorded event days) is compared line by line in ARM 0.

**Set-up (the same commands will be run).** git worktree add /tmp/g7_pin_earn 10cd146 (its commit line is printed), then a symbolic link /tmp/g7_pin_earn/data_cache to the repository's data_cache. The worktree is removed afterwards.

**ARM 0** is the pinned script, unpatched. After removing the two elapsed-time items (the last field of the first line and the line that starts with total) its output must be identical, line by line, to the original printout, starting with 41,459 filings, 41,046 distinct stock-dates, 40,157 and 39,872 flagged days and 41,579 recorded event days. If any line differs, the run STOPS and the cause (database drift in sec_8k_filings, ev_ent or securities since 2026-10-20, the matrices, or the code) is found before ARM 1.

**ARM 1** is the same after scripts/audit/g7_patch_arm1_event_width_v2.py edits ONLY the worktree's copy of event_width_test.py: rows of ev_ent whose event_id has an exclude row in event_exclusions are skipped, and the number skipped is printed.

**Tripwires.** (1) ARM 1 prints that 716 ev_ent rows were skipped. (2) The recorded event days printed on the first line must be LOWER in ARM 1 than the 41,579 of ARM 0; an equal count would mean the exclusions did not reach this script. (3) The pinned worktree's git status must list only the untracked data_cache link in ARM 0, and the edited file plus the link in ARM 1; each arm's output and the patch diff are saved to results/g7_rerun/ with the arm in the name.

**Stated in advance.** (a) The registered rows p15 to p17 describe ARM 1; ARM 0 is reported beside it. (b) In ARM 1 the PRIMARY group (earnings days with no recorded event) can only gain days, from days freed in the groups 'event only' and 'event plus earnings', so its scales and gains may move slightly; the narrow intervals of p15 and p16 are what is at risk, not the verdict. (c) The script's own note stands: the 8-K table has no filing time (now measured in event_timing; day 0 stays the filing date by the decision of 2026-10-30), the test treats day 0 and day +1 as one window, and it does not know the sign. (d) Sealed versus non-sealed is not reported: the script has no company-set split. Nothing here re-scores or edits a prediction.

(further dated addenda go here: the remaining procedures)"""
head_before = T[:T.index("PRED-TABLE-END")]
R = T.replace(old, new)
assert R[:R.index("PRED-TABLE-END")] == head_before, "a registered prediction would change; nothing written"
open(p, "w", encoding="utf-8").write(R)
R2 = open(p, encoding="utf-8").read(); print("ok   Addendum 8 appended"); print("PREREG sha256", sha(R2), "|", R2.count("\n"), "lines")
