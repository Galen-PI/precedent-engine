import re, sys
TAG = re.compile(r"\$([A-Za-z_][A-Za-z_0-9]*)?\$")
def lint(sql, recurse=("do",), line0=1):
    problems, i, depth, line, stmts = [], 0, 0, line0, 0
    while i < len(sql):
        ch = sql[i]
        if ch == "\n": line += 1; i += 1; continue
        if sql.startswith("--", i):
            j = sql.find("\n", i); i = len(sql) if j < 0 else j; continue
        if ch == "'":
            j = i + 1
            while j < len(sql):
                if sql[j] == "'" and sql[j + 1:j + 2] == "'": j += 2; continue
                if sql[j] == "'": break
                j += 1
            line += sql[i:j].count("\n"); i = j + 1; continue
        m = TAG.match(sql, i)
        if m:
            tag = m.group(0); j = sql.find(tag, m.end())
            if j < 0: problems.append("line %d: dollar quote %s is never closed" % (line, tag)); return problems, stmts
            inner = sql[m.end():j]
            if m.group(1) in recurse:
                p, _ = lint(inner, recurse, line); problems += p
            line += sql[i:j + len(tag)].count("\n"); i = j + len(tag); continue
        if ch == "(": depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0: problems.append("line %d: unbalanced ')'" % line); depth = 0
        elif ch == ";" and depth == 0: stmts += 1
        i += 1
    if depth != 0: problems.append("line %d: %d unclosed '('" % (line, depth))
    return problems, stmts
if __name__ == "__main__":
    s = open(sys.argv[1]).read(); p, n = lint(s)
    print("statements ending in ';' at top level:", n); print("PROBLEMS:" if p else "NO PROBLEMS FOUND", *p, sep="\n  ")
