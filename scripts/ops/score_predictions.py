#!/usr/bin/env python3
"""
score_predictions.py FILE [--all] -- scores the PRED-TABLE of a registration against the ACTUAL-TABLE written after its results (rows   id | actual | se   between ACTUAL-TABLE-BEGIN and ACTUAL-TABLE-END; for a prob row the actual is 1 or 0). Per numeric row: INSIDE the stated range, the distance in standard errors from the point, whether actual +- 1.96 se overlaps the range. Per prob row: the Brier term (p - outcome)^2. SUMMARY by nominal level: the share inside against the nominal 80 / 95, which is the calibration the project asked for (are the ranges systematically too narrow?). --all aggregates every results/PREREG_*.md that has both tables.
"""
import re, sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_prereg import block


def load(path):
    t = open(path).read()
    pr, ac = block(t, "PRED-TABLE-BEGIN", "PRED-TABLE-END"), block(t, "ACTUAL-TABLE-BEGIN", "ACTUAL-TABLE-END")
    P = {}
    for r in pr or []:
        f = [x.strip() for x in r.split("|")]
        if len(f) == 8:
            P[f[0]] = f
    A = {}
    for r in ac or []:
        f = [x.strip() for x in r.split("|")]
        if len(f) >= 2:
            A[f[0]] = (float(f[1]), float(f[2]) if len(f) > 2 and f[2] else None)
    return P, A


def score(P, A, out=print, tag=""):
    num_rows, brier = [], []
    for pid, f in P.items():
        if pid not in A:
            continue
        _, typ, stmt, point, lo, hi, level, anc = f
        act, se = A[pid]
        if typ == "prob":
            brier.append((float(point) - act) ** 2)
            out("   %s%-8s prob %.2f -> outcome %d  (Brier term %.3f)  %s" % (tag, pid, float(point), act, (float(point) - act) ** 2, stmt[:60])); continue
        p, l, h = float(point), float(lo), float(hi)
        inside = l <= act <= h
        z = (act - p) / se if se else None
        ov = (act - 1.96 * se <= h and act + 1.96 * se >= l) if se else None
        num_rows.append((int(float(level)), inside))
        out("   %s%-8s %-5s point %g range [%g, %g] (%s%%) actual %g%s | %s | %s | %s" % (tag, pid, typ, p, l, h, level, act, " se %g" % se if se else "", "INSIDE" if inside else "OUTSIDE", "%.1f SE from the point" % z if z is not None else "no se", "overlap" if ov else ("no overlap" if ov is not None else "")))
    return num_rows, brier


def summary(num_rows, brier, out=print):
    for lev in (80, 95):
        rs = [i for l, i in num_rows if l == lev]
        if rs:
            out("CALIBRATION at the nominal %d%%: %d of %d ranges contain the actual (%.0f%%)%s" % (lev, sum(rs), len(rs), 100.0 * sum(rs) / len(rs), "  <- too narrow if well below %d%%" % lev))
    if brier:
        out("BRIER (probability rows): %d rows, mean %.3f (0.25 = always saying 50%%)" % (len(brier), sum(brier) / len(brier)))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--all" in sys.argv:
        rows, br = [], []
        for f in sorted(glob.glob("results/PREREG_*.md")):
            P, A = load(f)
            if P and A:
                print(f); r, b = score(P, A); rows += r; br += b
        summary(rows, br)
    elif args:
        P, A = load(args[0]); r, b = score(P, A); summary(r, b)
    else:
        raise SystemExit("usage: score_predictions.py results/PREREG_x.md | --all")
