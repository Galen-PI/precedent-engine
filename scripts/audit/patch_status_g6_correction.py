"""patch_status_g6_correction.py (2026-10-29): corrects the G6 row of docs/PROJECT_STATUS.md after the Q4 and direction reads.
The earlier text said 2006 and 2007 (181 rows) had no filing record and that Q4 rows were untested; both were wrong. Gated on the exact
installed hash; the replacement must match exactly once. Usage: python3 scripts/audit/patch_status_g6_correction.py [docs/PROJECT_STATUS.md]"""
import hashlib, sys
def sha(s): return hashlib.sha256((s if s.endswith("\n") else s + "\n").encode("utf-8")).hexdigest()
p = sys.argv[1] if len(sys.argv) > 1 else "docs/PROJECT_STATUS.md"
S = open(p, encoding="utf-8").read()
assert sha(S) == "4f60c559dd642adce16434238d4018b4d8da5e2ff073bfe2a6c7f558802631fa", "PROJECT_STATUS is not the expected v1.3; nothing changed"
old = ("**New 10-29:** sec_filings holds the real 10-Q filing date for each quarterly row, and the stored filed_date is retroactive for periods ending 2008 to 2010 "
       "(a real 10-Q more than 30 days earlier exists for 358 of 638 rows in 2008, 435 of 1,119 in 2009, 217 of 1,342 in 2010): a join can move the usable point-in-time state "
       "from about 2011 back to about 2008; 2006 and 2007 (181 rows) have no filing record and keep the cap; Q4 rows were not tested against 10-Ks | open |")
new = ("**New 10-29 (corrected the same afternoon):** sec_filings holds the real filing date for 27,909 of the 28,533 quarterly rows (97.8 percent; the 10-Q for fiscal quarters 1 to 3, the 10-K for quarter 4). "
       "The stored filed_date is NEVER earlier than the real date (0 rows), is within 3 days of it for 26,119 rows, and is more than 30 days LATER for 1,790 rows (retroactive: 1 in 2006, 173 in 2007, 620 in 2008, 547 in 2009, 261 in 2010, 49 in 2011, 139 in 2012 to 2024); none lie between 4 and 30 days. "
       "A join on (security, period_end, form) fixes all 1,790 and moves the usable point-in-time state back to about 2007; 624 rows (93 of them in 2007 to 2010) have no real date and keep the cap LEAST(filed_date, period_end + 90 days). "
       "An earlier version of this row said 2006 and 2007 had no filing record and that Q4 rows were untested: both were wrong (the 10-Q-only test missed the Q4 rows, which 10-Ks cover). "
       "The values in the early rows still come from later filings and may reflect restatements | open |")
assert S.count(old) == 1, "G6 text: expected exactly 1 match, found %d; nothing was written" % S.count(old)
S = S.replace(old, new); open(p, "w", encoding="utf-8").write(S)
print("ok   G6 row corrected"); print("STATUS sha256", sha(S), "|", S.count("\n"), "lines")