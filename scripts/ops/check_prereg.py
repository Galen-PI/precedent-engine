#!/usr/bin/env python3
"""
check_prereg.py FILE -- checks a NEW pre-registration against results/TEMPLATE_PREREG.md before it can be committed (scripts/hooks/pre-commit runs it on every newly added results/PREREG_*.md; run it by hand any time). Exit status 0 = every requirement met.
REQUIRED LABELS (a line starting with the label and a colon): ANCHOR, TRIALS, HURDLE, DECAY, STANDARD TEST, FORWARD CHECK, PLACEBO, PREDICTIONS, WHAT WOULD CHANGE THE PLAN, LIMITS.
CONTENT RULES: TRIALS carries confirmatory=N descriptive=N ledger_before=N; HURDLE carries 't>=' a number and mentions the 3.0 reference (results/ANCHORS.md item 3); DECAY carries forward_fraction=X with 0 < X <= 1 (results/ANCHORS.md item 5); ANCHOR names DATA, LITERATURE or NONE. A PRED-TABLE block (between PRED-TABLE-BEGIN and PRED-TABLE-END) has rows   id | type | statement | point | lo | hi | level | anchor   with type ratio, pct, diff or prob; numeric rows need lo <= point <= hi and level 80 or 95; an anchor starts with DATA (and names its source), LITERATURE (and names ANCHORS#N, an item that exists in results/ANCHORS.md) or NONE; a NONE ratio row needs lo <= point/2 and hi >= 2 point (SCRIPTS.md addendum 24); a prob row needs 0 <= point <= 1.
"""
import re, sys, os

REQUIRED = ["ANCHOR", "TRIALS", "HURDLE", "DECAY", "STANDARD TEST", "FORWARD CHECK", "PLACEBO", "PREDICTIONS", "WHAT WOULD CHANGE THE PLAN", "LIMITS"]
TYPES = ("ratio", "pct", "diff", "prob")


def block(text, begin, end):
    m = re.search(r"^\s*%s\s*$(.*?)^\s*%s\s*$" % (re.escape(begin), re.escape(end)), text, re.M | re.S)
    if not m:
        return None
    return [l.strip() for l in m.group(1).splitlines() if l.strip() and not l.strip().startswith("#")]


def anchor_items(path):
    try:
        return {int(m.group(1)) for m in re.finditer(r"^(\d+)\. ", open(path).read(), re.M)}
    except OSError:
        return set()


def line_of(text, label):
    m = re.search(r"^\s*(?:#+\s*)?%s\s*:(.*)$" % re.escape(label), text, re.M)
    return m.group(1) if m else None


def num(s):
    try:
        return float(s)
    except ValueError:
        return None


def check(path, anchors_path=None):
    text = open(path).read()
    problems = []
    for lab in REQUIRED:
        if line_of(text, lab) is None:
            problems.append("missing label '%s:' (see results/TEMPLATE_PREREG.md)" % lab)
    t = line_of(text, "TRIALS")
    if t is not None:
        for key in ("confirmatory", "descriptive", "ledger_before"):
            if not re.search(r"\b%s\s*=\s*\d+" % key, t):
                problems.append("TRIALS needs %s=<integer>" % key)
    h = line_of(text, "HURDLE")
    if h is not None and not (re.search(r"t\s*>=\s*\d", h) and "3.0" in h):
        problems.append("HURDLE must state the pass line as 't>=<number>' and mention the 3.0 reference (ANCHORS.md item 3)")
    d = line_of(text, "DECAY")
    if d is not None:
        m = re.search(r"forward_fraction\s*=\s*([0-9.]+)", d)
        if not m or not (0 < float(m.group(1)) <= 1):
            problems.append("DECAY needs forward_fraction=<number above 0 and at most 1> (ANCHORS.md item 5)")
    a = line_of(text, "ANCHOR")
    if a is not None and not re.search(r"\b(DATA|LITERATURE|NONE)\b", a):
        problems.append("ANCHOR must name DATA, LITERATURE or NONE")
    rows = block(text, "PRED-TABLE-BEGIN", "PRED-TABLE-END")
    if rows is None:
        problems.append("no PRED-TABLE-BEGIN ... PRED-TABLE-END block")
    elif not rows:
        problems.append("the PRED-TABLE block has no rows")
    else:
        items = anchor_items(anchors_path or os.path.join(os.path.dirname(os.path.abspath(path)), "ANCHORS.md"))
        for r in rows:
            f = [x.strip() for x in r.split("|")]
            if len(f) != 8:
                problems.append("PRED row needs 8 fields (id | type | statement | point | lo | hi | level | anchor), has %d: %s" % (len(f), r[:60])); continue
            pid, typ, stmt, point, lo, hi, level, anc = f
            if typ not in TYPES:
                problems.append("%s: type must be one of %s" % (pid, ", ".join(TYPES))); continue
            p, l, hh = num(point), num(lo), num(hi)
            if p is None:
                problems.append("%s: point is not a number" % pid); continue
            if typ == "prob":
                if not 0 <= p <= 1:
                    problems.append("%s: a prob row needs 0 <= point <= 1" % pid)
            else:
                if l is None or hh is None or not (l <= p <= hh):
                    problems.append("%s: needs numeric lo <= point <= hi" % pid)
                if num(level) not in (80, 95):
                    problems.append("%s: level must be 80 or 95" % pid)
            au = anc.split()[0] if anc.split() else ""
            if au not in ("DATA", "LITERATURE", "NONE"):
                problems.append("%s: anchor must start with DATA, LITERATURE or NONE" % pid)
            elif au == "DATA" and len(anc.split()) < 2:
                problems.append("%s: a DATA anchor must name its source (a file, an addendum or a table)" % pid)
            elif au == "LITERATURE":
                m = re.search(r"ANCHORS#(\d+)", anc)
                if not m or int(m.group(1)) not in items:
                    problems.append("%s: a LITERATURE anchor must cite ANCHORS#N with N an item in results/ANCHORS.md (items: %s)" % (pid, sorted(items)))
            elif au == "NONE" and typ == "ratio" and None not in (l, hh) and p > 0 and not (l <= p / 2.0 and hh >= 2.0 * p):
                problems.append("%s: with anchor NONE a ratio range must run from at most point/2 to at least 2 x point (point %s, range %s to %s)" % (pid, point, lo, hi))
    return problems


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_prereg.py results/PREREG_x.md")
    pr = check(sys.argv[1])
    if pr:
        print("PREREG CHECK FAILED for %s:" % sys.argv[1]); [print("   - " + p) for p in pr]; sys.exit(1)
    print("PREREG CHECK OK: %s" % sys.argv[1])
