#!/usr/bin/env python3
"""
credit_spread_circular_test.py -- READ-ONLY. Calibrated re-run of the credit-spread x Banks test (and of the 10-year-yield bridge)
using an EMPIRICAL NULL: the same shock flags, circularly shifted by 40 amounts. Reads the cached French 49-industry daily file and
macro_long (DAAA, DBAA, DGS10). Writes nothing.

PRE-REGISTERED 2026-10-19 (before any result of this version was seen). Flags, threshold, eras and measure are UNCHANGED from
credit_spread_test.py, whose placebo cells failed calibration (shifted flags +21 days read 1.131, t 2.9, in 1986-1999):
 Flags: widening shock = daily change in DBAA - DAAA >= max(95th percentile of daily changes, 0.03 pp). (The 2026-10-19 run gave 0.030 pp, 724 days.)
 Measure: z = |r| / stdev of the previous 64 returns (>= 50 valid); o = mean z of the other industries that day (>= 10).
   Within each calendar month with >= 2 shock days and >= 5 ordinary days: predicted shock-day z for the target =
   (sum of o on shock days) x (sum of target z on ordinary days / sum of o on ordinary days).
   Amplification A = (sum of actual target z on shock days) / (sum of predicted) over the qualifying months of the era.
 Null: the flag series is shifted circularly (wrapping inside the span where flags exist) by each of +-21, +-31, ..., +-211 trading days
   (40 shifts). A is recomputed for every shifted copy exactly the same way. This keeps the clustering of the flags and the persistence of returns.
 For each industry and era: A (real), mean and sd of the shifted A, k = how many shifted A are >= the real A, and p = (1 + k) / (1 + number of copies).
   "Beats at least 39 of 40" means k <= 1 (p <= 0.049).
 PASS (same-day, Banks): in EVERY era (1986-1999, 2000-2012, 2013-2026) A >= 1.10 and k <= 1.
 LEAD: pooled A >= 1.05 and pooled k <= 1, and A >= 1.00 in every era.
 Next-day line (usable forward): A >= 1.05 and k <= 1 in every era (flags moved one day later, same circular null).
 Industries other than Banks are reported, not in the verdict. The 40 shifted copies overlap in time and are not independent, so p is approximate.
 BRIDGE (descriptive, no verdict): the 10-year-yield shock (|change in DGS10| >= 0.10 points) for Banks, Hlth, Softw in eras 1962-1985,
   1986-2007, 2008-end with the same null.
 Stated in advance: expectation is that the credit result stays flat and the Banks yield effect survives.

Usage: python3 -u scripts/macro/credit_spread_circular_test.py
"""
import os, sys, math, bisect, zipfile
from collections import deque, defaultdict

ZIP = "data_cache/french/49_Industry_Portfolios_daily_CSV.zip"
TARGET, DESCR, PLAC = "Banks", ["Fin", "Insur", "RlEst"], ["Hlth", "Softw"]
CREDIT_ERAS = [("1986-1999", "1986-01-01", "1999-12-31"), ("2000-2012", "2000-01-01", "2012-12-31"), ("2013-2026", "2013-01-01", "2100-01-01")]
YIELD_ERAS = [("1962-1985", "1962-01-01", "1985-12-31"), ("1986-2007", "1986-01-01", "2007-12-31"), ("2008-end", "2008-01-01", "2100-01-01")]
MIN_THR = 0.03
SHIFTS = [s * m for m in range(21, 212, 10) for s in (1, -1)]


def get_sb():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def load_french(path, block=0):
    z = zipfile.ZipFile(path)
    lines = z.read(z.namelist()[0]).decode("latin-1").splitlines()
    heads = [k for k, l in enumerate(lines) if l.startswith(",") and "Agric" in l]
    i = heads[block]
    cols = [c.strip() for c in lines[i].split(",")[1:] if c.strip()]
    data = {}
    for l in lines[i + 1:]:
        if not l.strip():
            break
        parts = [p.strip() for p in l.split(",")]
        if len(parts[0]) != 8 or not parts[0].isdigit():
            break
        vals = []
        for p in parts[1:1 + len(cols)]:
            try:
                v = float(p)
            except ValueError:
                v = None
            vals.append(None if v is None or v <= -99.0 else v / 100.0)
        vals += [None] * (len(cols) - len(vals))
        d = parts[0]
        data[d[:4] + "-" + d[4:6] + "-" + d[6:]] = vals
    return cols, data


def zscores(cols, dates, data):
    z = {c: {} for c in cols}
    for j, c in enumerate(cols):
        win, s1, s2, k = deque(), 0.0, 0.0, 0
        for d in dates:
            r = data[d][j]
            if k >= 50:
                var = (s2 - s1 * s1 / k) / (k - 1)
                if r is not None and var > 0:
                    z[c][d] = abs(r) / math.sqrt(var)
            win.append(r)
            if r is not None:
                s1 += r
                s2 += r * r
                k += 1
            if len(win) > 64:
                old = win.popleft()
                if old is not None:
                    s1 -= old
                    s2 -= old * old
                    k -= 1
    return z


def load_macro(sb, sid):
    rows, off = [], 0
    while True:
        page = sb.table("macro_long").select("obs_date,value").eq("series_id", sid).order("obs_date").range(off, off + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return [(r["obs_date"], float(r["value"])) for r in rows if r["value"] is not None]


def credit_flags(sb):
    a = dict(load_macro(sb, "DAAA"))
    b = dict(load_macro(sb, "DBAA"))
    assert a and b, "DAAA or DBAA not found in macro_long (series_id mismatch?)"
    sp = sorted((d, b[d] - a[d]) for d in a if d in b)
    ch = [(sp[i][0], sp[i][1] - sp[i - 1][1]) for i in range(1, len(sp))]
    allc = sorted(c for d, c in ch)
    q95 = allc[int(0.95 * (len(allc) - 1))]
    thr = max(q95, MIN_THR)
    return {d: (c >= thr - 1e-9) for d, c in ch}, thr, q95, len(sp)


def yield_flags(sb):
    s = load_macro(sb, "DGS10")
    assert s, "DGS10 not found in macro_long"
    return {s[i][0]: abs(s[i][1] - s[i - 1][1]) >= 0.10 - 1e-9 for i in range(1, len(s))}


def to_array(flagmap, dates):
    return [flagmap.get(d) for d in dates]


def circ_shift(arr, s):
    """circular shift inside the span where flags exist; flag at day k becomes the flag of day k - s (wrapping)."""
    idx = [k for k, f in enumerate(arr) if f is not None]
    if not idx:
        return list(arr)
    lo, hi = idx[0], idx[-1]
    span = hi - lo + 1
    out = [None] * len(arr)
    for k in range(lo, hi + 1):
        out[k] = arr[lo + ((k - lo - s) % span)]
    return out


def amp_point(zc, tot, cnt, flags, dates, i0, i1):
    """returns (months, amplification) over day indices [i0, i1)."""
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
        if len(sz) >= 2 and len(nz) >= 5:
            num += sum(sz)
            den += sum(so) * (sum(nz) / sum(no))
            n += 1
    if n < 6 or den <= 0:
        return n, None
    return n, num / den


def era_index_ranges(dates, eras):
    out = []
    for en, lo, hi in eras:
        out.append((en, bisect.bisect_left(dates, lo), bisect.bisect_right(dates, hi)))
    out.append(("POOLED", out[0][1], len(dates)))
    return out


def run_experiment(name, F0, eras, inds, zarr, tot, cnt, dates):
    ranges = era_index_ranges(dates, eras)
    real = {"same": F0, "next": circ_shift(F0, 1)}
    nulls = {"same": [circ_shift(F0, s) for s in SHIFTS], "next": [circ_shift(F0, s + 1) for s in SHIFTS]}
    res = {}
    print("\n===== %s  (%d shifted copies per variant)" % (name, len(SHIFTS)))
    print("  industry  era        months | same-day: A      null mean (sd)    beats  p      | next-day: A      null mean (sd)    beats  p")
    for c in inds:
        tag = "TARGET" if c == TARGET else ("PLACEBO" if c in PLAC else "descriptive")
        for en, i0, i1 in ranges:
            line = "  %-8s  %-10s" % (c, en)
            for vn in ("same", "next"):
                n, a0 = amp_point(zarr[c], tot, cnt, real[vn], dates, i0, i1)
                vals = [amp_point(zarr[c], tot, cnt, fl, dates, i0, i1)[1] for fl in nulls[vn]]
                vals = [v for v in vals if v is not None]
                if a0 is None or len(vals) < 20:
                    res[(c, en, vn)] = (n, a0, None, None, None, len(vals))
                    line += "  %3d | n/a" % n if vn == "same" else " | n/a"
                    continue
                mu = sum(vals) / len(vals)
                sd = math.sqrt(sum((v - mu) ** 2 for v in vals) / (len(vals) - 1))
                k = sum(1 for v in vals if v >= a0)
                p = (1 + k) / (1 + len(vals))
                res[(c, en, vn)] = (n, a0, mu, sd, k, len(vals))
                if vn == "same":
                    line += "  %3d |" % n
                else:
                    line += " |"
                line += "  %.3f   %.3f (%.3f)   %2d/%d  %.3f " % (a0, mu, sd, len(vals) - k, len(vals), p)
            print(line + " " + tag, flush=True)
    return res


def main():
    sb = get_sb()
    cols, data = load_french(ZIP)
    dates = sorted(data)
    nd = len(dates)
    z = zscores(cols, dates, data)
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
    for c in [TARGET] + DESCR + PLAC:
        assert c in zarr, "industry not found: " + c

    cf, thr, q95, nsp = credit_flags(sb)
    F0 = to_array(cf, dates)
    print("credit flags: threshold %.3f pp (95th percentile %.3f, floor %.2f); shock days on French trading days: %d; shifts: %d (%d .. %d)" % (
        thr, q95, MIN_THR, sum(1 for f in F0 if f), len(SHIFTS), min(SHIFTS), max(SHIFTS)), flush=True)

    inds = [TARGET] + DESCR + PLAC
    R = run_experiment("CREDIT WIDENING (Baa - Aaa), same flags and threshold as the 2026-10-19 run", F0, CREDIT_ERAS, inds, zarr, tot, cnt, dates)

    eras = [e[0] for e in CREDIT_ERAS]
    same = [R[(TARGET, en, "same")] for en in eras]
    pooled = R[(TARGET, "POOLED", "same")]
    nxt = [R[(TARGET, en, "next")] for en in eras]
    ok = lambda r, line: r[1] is not None and r[4] is not None and r[1] >= line and r[4] <= 1
    if all(ok(r, 1.10) for r in same):
        verdict = "PASS"
    elif ok(pooled, 1.05) and all(r[1] is not None and r[1] >= 1.0 for r in same):
        verdict = "LEAD"
    else:
        verdict = "not passed"
    next_ok = all(ok(r, 1.05) for r in nxt)
    print("\nBANKS credit: pooled A %s, empirical-null sd %s (the earlier cluster-bootstrap SE of the log was 0.026), beats %s of %s"
          % ("n/a" if pooled[1] is None else "%.3f" % pooled[1], "n/a" if pooled[3] is None else "%.3f" % pooled[3],
             "n/a" if pooled[4] is None else str(pooled[5] - pooled[4]), pooled[5]))
    print("VERDICT same-day (pre-set lines): %s | next-day line (A >= 1.05 and k <= 1 in every era): %s" % (verdict, "PASS" if next_ok else "not passed"))

    BR = run_experiment("BRIDGE: 10-YEAR YIELD SHOCK (descriptive)", to_array(yield_flags(sb), dates), YIELD_ERAS, [TARGET] + PLAC, zarr, tot, cnt, dates)
    print("\n(the earlier bridge read Banks 1.059 / 1.189 / 1.187, pooled 1.139, with the calibrated estimator; the older harness read 1.018 / 1.137 / 1.124)")


if __name__ == "__main__":
    main()
