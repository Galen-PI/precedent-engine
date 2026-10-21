#!/usr/bin/env bash
# prepare_review_session.sh -- one command that refreshes the human-review files, safely.
# 1. refuses to run unless SEC_USER_AGENT holds a real contact (the SEC blocks made-up ones)
# 2. applies the 'trial runs write a separate file' patch if it is not applied yet
# 3. runs the FULL exhibit-excerpt fetch (rows already cached are not refetched; failures are retried)
# 4. prints the tally of what came back, rebuilds the priority file, and commits both
# Usage:   export SEC_USER_AGENT="stock-research1 you@yourdomain.com"; bash scripts/card/prepare_review_session.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ -z "${SEC_USER_AGENT:-}" || "$SEC_USER_AGENT" != *@* || "$SEC_USER_AGENT" == *example.com* || "$SEC_USER_AGENT" == *YOUR_REAL* || "$SEC_USER_AGENT" == *your* ]]; then
  echo 'STOP: set a real contact first, in this same shell, for example:'
  echo '  export SEC_USER_AGENT="stock-research1 you@yourdomain.com"'
  exit 1
fi
echo "== 1/4 safety patch"
python3 - << 'PY'
p = "scripts/card/add_exhibit_excerpts.py"
s = open(p).read()
if "_trial.csv" in s:
    print("   already applied")
else:
    old = '    path = os.path.join(RESULTS, "human_review_queue_with_excerpts.csv")\n'
    assert s.count(old) == 1, "anchor not found exactly once: nothing written"
    s = s.replace(old, '    # a run with a row limit is a TRIAL: it must never overwrite the full file\n    name = "human_review_queue_with_excerpts.csv" if len(sys.argv) <= 2 else "human_review_queue_with_excerpts_trial.csv"\n    path = os.path.join(RESULTS, name)\n')
    open(p, "w").write(s)
    print("   patched")
PY
echo "== 2/4 full excerpt run (about 3 minutes the first time)"
python3 -u scripts/card/add_exhibit_excerpts.py A
echo "== 3/4 what came back"
python3 - << 'PY'
import csv, re
from collections import Counter
rows = list(csv.DictReader(open("results/human_review_queue_with_excerpts.csv")))
c = Counter()
for r in rows:
    e = r["exhibit_excerpt"]
    c["has an exhibit excerpt" if not e.startswith("(") else re.sub(r"\d{3,}", "N", e[:60])] += 1
print("   rows:", len(rows))
for k, v in c.most_common():
    print("   %4d  %s" % (v, k))
L = sorted(len(r["exhibit_excerpt"]) for r in rows if not r["exhibit_excerpt"].startswith("("))
print("   excerpt length: longest %d, median %d | keyword hints: %d" % (L[-1], L[len(L) // 2], sum(1 for r in rows if r["keyword_hint"])))
PY
python3 -u scripts/card/build_review_priority.py
echo "== 4/4 commit"
git add scripts/card/add_exhibit_excerpts.py scripts/card/prepare_review_session.sh results/human_review_queue_with_excerpts.csv results/human_review_priority.csv
git commit -m "Refresh review files (full excerpt run with a real contact)" || echo "   nothing new to commit"
git push origin main || echo "   push failed: run git push origin main later"
echo "done"
