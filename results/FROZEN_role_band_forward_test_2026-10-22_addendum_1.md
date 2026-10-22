# ADDENDUM 1 to the frozen role-band forward rule
Written 2026-10-22, before any outcome exists. The frozen file (commit fdac0a2) is UNCHANGED; this addendum records how the rule is implemented and corrects one PREDICTION. The rule itself is not altered.

1. IMPLEMENTATION CHOICES where the frozen text is silent (also in the script header): verdict precedence TOO FEW > VOID > NOT SHOWN > PARTIAL > PASS; the window is by filing date, inclusive; an event is evaluable only if day i+1 exists in the matrices with finite band units on both days, and --evaluate refuses to run before the matrices reach 2027-01-04; 'isolated' is the walk-forward's definition; habits and ties come from earnings_roles.habit_at and is_tie (first_year 2006); --evaluate refuses to run if any file hashed in the frozen file has changed.

2. THE PLACEBO. The walk-forward placebo refits each group's edge on shuffled habits, so it behaves like the pooled model (ratios 1.003-1.005). A frozen forward model has nothing to refit: the deployed half-widths (5.322 and 1.904) are applied to shuffled assignments, which mis-size most days, so the placebo ratio is expected to be well ABOVE 1 (synthetic worlds with the real half-widths gave 1.12-1.24). Consequences: (a) criterion (c) (mean placebo ratio >= 0.99) cannot realistically fail forward, so it is inert; the criteria that carry the verdict are (a) the interval-score improvement and (b) coverage, both genuinely out-of-sample for a frozen model; (b) the frozen PREDICTION for the placebo (1.004, range 0.998-1.012) was wrong in expectation and is corrected here, before any outcome: placebo mean ratio 1.15 (1.08-1.25). Both will be scored; the rule text is not changed.

3. FROZEN SCRIPT (scripts/card/earnings_role_forward_test.py, committed before any refresh); its hash follows.

```
11dedd8cee0dd02d6ad18ff9d94f1d51078feea27670058bb2fe6c89a8bf064e  scripts/card/earnings_role_forward_test.py
```
