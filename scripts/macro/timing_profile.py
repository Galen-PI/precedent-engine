#!/usr/bin/env python3
"""
timing_profile.py -- READ-ONLY. When does each macro link act: the day before, the same day, or the days after?

Reads the cached French 49-industry daily file and macro_long (DCOILWTICO, DGS10, DAAA, DBAA). Writes nothing. Imports its loaders from
oil_size_test.py (same folder).

Usage:   python3 -u scripts/macro/timing_profile.py

DESIGN (an event study with a clean baseline):
  Flags (the ledger's lines): oil |WTI move| >= 3% (both prices > 5); yield |DGS10 change| >= 0.10 pp; credit widening (Baa - Aaa) >= 0.03 pp.
  ISOLATED flag = no other flag of the same kind within 3 trading days either side. CLEAN ordinary day = no flag within 3 trading days either side.
  For each offset k in -3..+3 the 'shock days' are the days k trading days after an isolated flag (k = -1 is the day BEFORE the flag, k = 0 the
  flag day itself); the baseline is the clean ordinary days. So no shock day sits in another flag's neighborhood, and the baseline is not
  contaminated by volatility left over from a flag.
  Measure (as in the earlier tests): z = |r| / stdev of the previous 64 returns (>= 50 valid); o = mean z of the other industries that day (>= 10).
  Within each calendar month with >= 1 shock day and >= 5 clean ordinary days: predicted shock-day z = (sum of o on shock days) x (sum of target z on
  ordinary days / sum of o on ordinary days). Amplification A = sum of actual / sum of predicted over the qualifying months.
  Null: the isolated/clean structure is shifted circularly by +-21, +-31, ..., +-211 trading days (40 shifts) and A recomputed at the same offset.
  'High beats' = number of shifted copies below the real A; 'low beats' = number above it. A cell is FLAGGED when high beats >= 39 (marked ^) or
  low beats >= 39 (marked v).
LINKS: oil -> Oil industry; yield -> Banks; yield -> Hlth (the defensive-dampening thread); credit -> Banks (a null link, as a control).
Eras: 1986-1999, 2000-2012, 2013-2026 (effects depend on the era).
READING IT. Cells at k != 0 are NOT tests of anything pre-registered: with 4 links x 3 eras x 6 offsets = 72 cells, about 7 are expected to be
  flagged by chance alone (each cell has a 4/41 chance). The script prints that expectation next to the count. A pattern is worth a closer look only
  if it recurs: the same offset and direction for the same link in at least two eras. But that is itself loose: on null data it appears for about
  8% of links, i.e. roughly a 30% chance of at least one such entry somewhere across 4 links. The strict tier (all three eras) has well under a 1% chance
  of appearing by chance anywhere. Nothing here changes the ledger; a candidate needs its own pre-registered test.
"""
import os, sys, math, bisect
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oil_size_test as ot

OFFS = [-3, -2, -1, 0, 1, 2, 3]
SHIFTS = ot.SHIFTS
ERAS = ot.ERAS
LINKS = [("oil", "Oil", "oil shock -> Oil industry"), ("yield", "Banks", "yield shock -> Banks"),
         ("yield", "Hlth", "yield shock -> Health (dampening)"), ("credit", "Banks", "credit widening -> Banks (control)")]


def marker_flags(sb):
    oil, y10 = ot.load_macro(sb, "DCOILWTICO"), ot.load_macro(sb, "DGS10")
    aaa, baa = dict(ot.load_macro(sb, "DAAA")), dict(ot.load_macro(sb, "DBAA"))
    assert oil and y10 and aaa and baa, "a macro series is missing from macro_long"
    fo, fy, fc = {}, {}, {}
    for i in range(1, len(oil)):
        d, v = oil[i]
        pv = oil[i - 1][1]
        if pv > 5 and v > 5:
            fo[d] = abs(v / pv - 1) >= 0.03
    for i in range(1, len(y10)):
        fy[y10[i][0]] = abs(y10[i][1] - y10[i - 1][1]) >= 0.10 - 1e-9
    sp = sorted((d, baa[d] - aaa[d]) for d in aaa if d in baa)
    for i in range(1, len(sp)):
        fc[sp[i][0]] = sp[i][1] - sp[i - 1][1] >= 0.03 - 1e-9
    return {"oil": fo, "yield": fy, "credit": fc}


def structure(F):
    """code array: 1 = isolated flag, 0 = clean ordinary day, None otherwise."""
    n = len(F)
    code = [None] * n
    for i in range(n):
        if F[i] is None:
            continue
        near = [F[j] for j in range(max(0, i - 3), min(n, i + 4)) if j != i]
        quiet = not any(v for v in near if v is not None)
        if F[i]:
            if quiet:
                code[i] = 1
        elif quiet:
            code[i] = 0
    return code


def offset_array(code, k):
    n = len(code)
    out = [None] * n
    for i in range(n):
        if code[i] == 0:
            out[i] = False
    for t in range(n):
        if code[t] == 1 and 0 <= t + k < n:
            out[t + k] = True
    return out


def amp(zc, tot, cnt, flags, dates, i0, i1, min_shock=1):
    by = defaultdict(lambda: [[], [], [], []])
    for k in range(i0, i1):
        f, zz = flags[k], zc[k]
        if f is None or zz is None or cnt[k] < 11:
            continue
        o = (tot[k] - zz) / (cnt[k] - 1)
        if o <= 0:
            continue
        m = by[dates[k][:7]]
        if f:
            m[0].append(zz)
            m[1].append(o)
        else:
            m[2].append(zz)
            m[3].append(o)
    num = den = 0.0
    n = 0
    for sz, so, nz, no in by.values():
        if len(sz) >= min_shock and len(nz) >= 5:
            num += sum(sz)
            den += sum(so) * (sum(nz) / sum(no))
            n += 1
    if n < 6 or den <= 0:
        return n, None
    return n, num / den


def main():
    sb = ot.get_sb()
    cols, data = ot.load_french(ot.ZIP)
    dates = sorted(data)
    nd = len(dates)
    z = ot.zscores(cols, dates, data)
    pos = {d: k for k, d in enumerate(dates)}
    tot, cnt, zarr = [0.0] * nd, [0] * nd, {}
    for c in cols:
        arr = [None] * nd
        for d, v in z[c].items():
            k = pos[d]
            arr[k] = v
            tot[k] += v
            cnt[k] += 1
        zarr[c] = arr
    print("French: %d industries, %d days, %s .. %s" % (len(cols), nd, dates[0], dates[-1]), flush=True)
    for _, tgt, _ in LINKS:
        assert tgt in zarr, "industry not found: " + tgt
    flags = marker_flags(sb)
    ranges = [(en, bisect.bisect_left(dates, lo), bisect.bisect_right(dates, hi)) for en, lo, hi in ERAS]

    cells = {}      # (link index, era, k) -> (months, A, high_beats, low_beats, n_null)
    structs = {}
    for li, (mk, tgt, title) in enumerate(LINKS):
        if mk not in structs:
            F = [flags[mk].get(d) for d in dates]
            code = structure(F)
            structs[mk] = (code, [ot.circ_shift(code, s) for s in SHIFTS])
            print("%s: %d flagged days, %d isolated (no flag within 3 days either side), %d clean ordinary days" % (
                mk, sum(1 for v in F if v), sum(1 for c in code if c == 1), sum(1 for c in code if c == 0)), flush=True)
        code, shifted = structs[mk]
        for en, i0, i1 in ranges:
            for k in OFFS:
                n, a0 = amp(zarr[tgt], tot, cnt, offset_array(code, k), dates, i0, i1)
                if a0 is None:
                    cells[(li, en, k)] = (n, None, 0, 0, 0)
                    continue
                vals = []
                for cs in shifted:
                    nn, av = amp(zarr[tgt], tot, cnt, offset_array(cs, k), dates, i0, i1)
                    if av is not None:
                        vals.append(av)
                if len(vals) < 20:
                    cells[(li, en, k)] = (n, a0, 0, 0, len(vals))
                    continue
                hi = sum(1 for v in vals if v < a0)
                lo = sum(1 for v in vals if v > a0)
                cells[(li, en, k)] = (n, a0, hi, lo, len(vals))
        print("  done: %s" % title, flush=True)

    print("\nPROFILE: amplification A at each offset (k = trading days after an isolated flag; k = 0 is the flag day). ^ = beats >= 39 of 40 shifted copies above, v = below")
    for li, (mk, tgt, title) in enumerate(LINKS):
        print("\n" + title)
        print("  %-10s" % "era" + "".join("%11s" % ("k=%+d" % k) for k in OFFS) + "     months at k=0")
        for en, _, _ in ranges:
            row = "  %-10s" % en
            for k in OFFS:
                n, a, hi, lo, nn = cells[(li, en, k)]
                if a is None:
                    row += "%11s" % "n/a"
                else:
                    mark = "^" if hi >= 39 else ("v" if lo >= 39 else " ")
                    row += "%10.3f%s" % (a, mark)
            print(row + "     %d" % cells[(li, en, 0)][0])

    flagged, total = 0, 0
    recur = defaultdict(list)
    for (li, en, k), (n, a, hi, lo, nn) in cells.items():
        if k == 0 or a is None or nn < 20:
            continue
        total += 1
        if hi >= 39 or lo >= 39:
            flagged += 1
            recur[(li, k, "above" if hi >= 39 else "below")].append(en)
    print("\nOFFSETS OTHER THAN 0: %d cells computed, %d flagged (^ or v). Expected by chance alone: about %.1f (each cell has a 4/41 chance)." % (total, flagged, total * 4.0 / 41))
    rec = [(LINKS[li][2], k, d, ens) for (li, k, d), ens in recur.items() if len(ens) >= 2]
    rec3 = [r for r in rec if len(r[3]) >= 3]
    print("RECURRING in >= 2 eras (loose: by chance alone this appears for about 8%% of links, about 30%% of the time somewhere across %d links): %s" % (len(LINKS), "none" if not rec else ""))
    for title, k, d, ens in rec:
        print("   %s at k=%+d, %s the null, in %s" % (title, k, d, ", ".join(ens)))
    print("RECURRING in all 3 eras (strict: well under 1%% chance anywhere by chance): %s" % ("none" if not rec3 else ""))
    for title, k, d, ens in rec3:
        print("   %s at k=%+d, %s the null, in %s" % (title, k, d, ", ".join(ens)))
    k0 = [(LINKS[li][2], en, a, hi, lo) for (li, en, k), (n, a, hi, lo, nn) in sorted(cells.items()) if k == 0 and a is not None]
    print("\nSAME-DAY (k = 0) for reference, this design vs the ledger's all-flags design:")
    for title, en, a, hi, lo in k0:
        print("   %-40s %-10s A = %.3f  (above %d of 40 shifted copies, below %d)" % (title, en, a, hi, lo))


if __name__ == "__main__":
    main()
