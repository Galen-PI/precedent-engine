"""fix_changelog_order.py (2026-10-29): the changelog tool's add --date put the entry 2026-09-08-02 at the TOP of the index and of the
entries. This moves the index line and the entry block to sit directly above their 2026-09-08-01 neighbours (newest first). Every position
is asserted; nothing is written unless all hold. Usage: python3 scripts/audit/fix_changelog_order.py [CHANGELOG.md]"""
import sys
p = sys.argv[1] if len(sys.argv) > 1 else "CHANGELOG.md"
L = open(p, encoding="utf-8").read().splitlines(keepends=True)
def find(prefix):
    hits = [i for i, l in enumerate(L) if l.startswith(prefix)]
    assert len(hits) == 1, "%r: expected exactly 1 line, found %d; nothing written" % (prefix, len(hits))
    return hits[0]
i_new, i_old = find("| 2026-09-08-02 |"), find("| 2026-09-08-01 |")
e_new, e_old = find("<!-- entry: 2026-09-08-02 |"), find("<!-- entry: 2026-09-08-01 |")
e_end = next(i for i in range(e_new + 1, len(L)) if L[i].startswith("<!-- entry:"))
assert i_new < i_old and e_new < e_old and e_end <= e_old, "the entry is not above its neighbour as expected; nothing written"
before = (len(L), sum(1 for l in L if l.startswith("<!-- entry:")), sum(1 for l in L if l.startswith("| 20")))
index_line = L[i_new]; block = L[e_new:e_end]
rest = L[:e_new] + L[e_end:]                       # remove the entry block first (it is below the index)
del rest[i_new]                                    # then the index line
j_idx = next(i for i, l in enumerate(rest) if l.startswith("| 2026-09-08-01 |"))
rest.insert(j_idx, index_line)
j_ent = next(i for i, l in enumerate(rest) if l.startswith("<!-- entry: 2026-09-08-01 |"))
rest[j_ent:j_ent] = block
after = (len(rest), sum(1 for l in rest if l.startswith("<!-- entry:")), sum(1 for l in rest if l.startswith("| 20")))
assert before == after, "line or entry counts changed: %s vs %s; nothing written" % (before, after)
open(p, "w", encoding="utf-8").write("".join(rest))
print("moved: index line from line %d to line %d; entry (%d lines) from line %d to line %d; counts unchanged %s" % (i_new + 1, j_idx + 1, len(block), e_new + 1, j_ent + 1, after))