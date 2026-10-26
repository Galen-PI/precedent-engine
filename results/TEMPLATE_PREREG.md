# PREREG <date>: <title>   (written BEFORE any outcome was computed; copy this file to results/PREREG_<name>_<date>.md)
# Every label below must appear at the start of a line, followed by a colon: scripts/ops/check_prereg.py (run by the pre-commit hook on every NEW registration) refuses a file that lacks one.
DATA AND USE RULE: <data, eras, exclusions; price levels follow results/PREREG_asquoted_levels_valid_from_2026-10-26.md addendum 6 (closes from 2001-06-01, valid tickers, from valid_from)>
ANCHOR: <DATA, LITERATURE or NONE>. <what earlier results (name the file or addendum) or a published magnitude (results/ANCHORS.md item N) say about the quantity tested; if NONE, say so: every ratio range below is then at least half to double its point (SCRIPTS.md addendum 24). A cheap anchor slice (about 5% of tickers, seeded, excluded from the confirmatory run) is run first when one exists.>
TRIALS: confirmatory=<N> descriptive=<N> ledger_before=<N>    (ledger_before = SELECT COUNT(*) FROM flag_ledger; a descriptive look is any statistic printed but not part of a pass line)
HURDLE: pass needs t>=<x> in BOTH eras <with a clean placebo>; reference hurdle for a newly discovered effect 3.0 (ANCHORS.md item 3; 2.78 in the replication literature, item 4). <say whether the pass line is below the reference and what that means for how a pass is described: a pass between 2.5 and 3.0 is a lead until it holds forward>
DECAY: forward_fraction=<0.4 to 0.75 typical>. <the share of the in-sample magnitude expected to survive out of sample (ANCHORS.md item 5: 26% lower out of sample, 58% lower after publication); the forward check is judged against this, not against the in-sample size>
STANDARD TEST: <the standard method for this kind of object and whether this test follows it: event study (market model or matched baseline, cross-sectional dependence), interval forecast (Kupiec coverage, Christoffersen independence and conditional coverage, ANCHORS.md item 7), predictive regression (out of sample, deflation for trials, ANCHORS.md item 6)>
PLACEBO: <the calibration or placebo that must be clean before any pass, set from the noise, not from the effect>
FORWARD CHECK: <what data after this sample will confirm or retire the result, and when (a dated runbook step)>
PREDICTIONS: <one line: ranges are 80% or 95% intervals; scoring uses scripts/ops/score_predictions.py after the results>
PRED-TABLE-BEGIN
# id | type | statement | point | lo | hi | level | anchor      (type: ratio, pct, diff or prob; level 80 or 95; anchor DATA <source>, LITERATURE ANCHORS#N, or NONE)
p1 | ratio | <statement> | <point> | <lo> | <hi> | 95 | NONE
p2 | prob | <verdict or event statement> | <probability 0 to 1> |  |  |  | DATA <source>
PRED-TABLE-END
WHAT WOULD CHANGE THE PLAN: <stop rules and what each failure means, fixed in advance>
LIMITS: <written in advance>
NOT IN THIS NOTE: <what is deliberately out of scope>
# AFTER THE RESULTS: append a block   ACTUAL-TABLE-BEGIN / id | actual | se / ACTUAL-TABLE-END   (prob rows: actual 1 or 0) and run   python3 scripts/ops/score_predictions.py results/PREREG_<name>_<date>.md
