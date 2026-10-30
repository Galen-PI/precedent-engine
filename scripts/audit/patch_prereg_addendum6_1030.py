"""patch_prereg_addendum6_1030.py (2026-10-30): appends Addendum 6 (a correction of the registration's universe statement) to
results/PREREG_g7_proven_rerun_2026-10-29.md. Text only; no prediction is edited. Gated on the exact committed hash after Addendum 5.
Usage: python3 scripts/audit/patch_prereg_addendum6_1030.py [results/PREREG_g7_proven_rerun_2026-10-29.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "results/PREREG_g7_proven_rerun_2026-10-29.md"
T = open(p, encoding="utf-8").read()
assert sha(T) == "63ca3099912722a58acceff78a848ac0e13d34c343373a111c3f2569485d9e02", "the registration is not the version after Addendum 5; nothing changed"
old = "(further dated addenda go here: the remaining procedures)"
assert T.count(old) == 1, "placeholder not found exactly once; nothing changed"
new = """### Addendum 6 (2026-10-30): a correction to the registration's universe statement

The DATA AND USE RULE of this registration says the re-runs use "the exploration tickers only" and that "the 160 sealed tickers are not touched in this pass". The limits section called this assumed, not verified. It is WRONG for the runs so far: the by-type SQL has no sealed filter and its ARM 0 reproduced the ledger's counts on ALL companies (ALL_POOLED n 6,914 against the ledger's 6,871, where excluding the sealed third of events would give about 4,600); band_calibrate.py and event_width_test.py read all 498 securities. The original tests of these flags used all companies too, so the re-runs compare like with like and no result of this exercise is invalidated, but the sealed tickers have been part of every one of these tests since they were first run.

Consequences. (1) The sealed set is NOT an independent confirmation for any of the 15 flags, nor for the Tier 1 nulls registered in results/PREREG_g7_tier1_window_nulls_2026-10-30.md; any claim that would need confirmation is confirmed on forward data (January 2027), and sealed and non-sealed results are reported side by side as a consistency check between two disjoint company sets. (2) The multiplicity rule of this exercise ("a flip holds once on the sealed tickers") is replaced, for these flags, by: a flip passes its registered rule, clears a pre-stated minimum effect, holds with the same sign in both company sets, and is re-tested on forward data before any status change. (3) Standing rule 13 of the status file (tests read the analysis set, adopted 2026-10-28) is respected in ARM 1 in substance, not in form: ARM 1 removes events with an exclude reason, as event_analysis_set does, but does not require a reaction row. No prediction above is changed.

(further dated addenda go here: the remaining procedures)"""
open(p, "w", encoding="utf-8").write(T.replace(old, new))
R = open(p, encoding="utf-8").read(); print("ok   Addendum 6 appended"); print("PREREG sha256", sha(R), "|", R.count("\n"), "lines")
