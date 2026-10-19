#!/usr/bin/env python3
"""
oil_size_test.py -- READ-ONLY. Does the Oil industry's extra movement on oil-shock days grow with the SIZE of the oil move?
Reads the cached French 49-industry daily file and macro_long (DCOILWTICO). Writes nothing.

PRE-REGISTERED 2026-10-19 (before any result was seen):
 Oil move size c = |WTI daily change|, only for days with both prices > 5. Buckets: B1 = 3% <= c < 5%, B2 = 5% <= c < 10%, B3 = c >= 10%.
 Ordinary days = c < 3%. For bucket k the flag series is True on bucket-k days, False on ordinary days, and EXCLUDED (None) on days in
 the other buckets, so larger-move days do not contaminate the comparison.
 Measure (same as the credit test): z = |r| / stdev of the previous 64 returns (>= 50 valid); o = mean z of the other industries that day (>= 10).
   Within each calendar month with >= 2 shock days and >= 5 ordinary days: predicted shock-day z = (sum of o on shock days) x
   (sum of target z on ordinary days / sum of o on ordinary days). Amplification A = sum of actual / sum of predicted over the qualifying months.
 Null: each flag series shifted circularly by +-21, +-31, ..., +-211 trading days (40 shifts); A recomputed for every shifted copy.
   k = number of shifted copies >= the real value; "beats at least 39 of 40" means k <= 1.
 Target: Oil industry. Descriptive: Coal. Placebo industries: Hlth, Softw. Eras: 1986-1999 (the effect is absent there: control),
   2000-2012, 2013-2026. A bucket-era with fewer than 25 qualifying months is "too thin" and gets no pass or fail.
 DOSE-RESPONSE: D = A(B2) - A(B1), with the null D computed from both flag series shifted by the SAME amount.
 PASS: in BOTH 2000-2012 and 2013-2026: both buckets have >= 25 qualifying months, D >= 0.10 and D beats at least 39 of 40 shifted D.
 B3 (>= 10%): amplification and null reported, descriptive only (too thin by the 25-month rule when it is).
 Stated in advance: a gradient is expected but its size is not known.
 ADDED AFTER THE FIRST RUN (descriptive, not part of the verdict): bucket "all 3%+" = every day with c >= 3% (the pre-set measure of the earlier
 long-history oil test, re-run with the calibrated estimator and the circular null), because the 1986-1999 control era showed a borderline effect.

Usage: python3 -u scripts/macro/oil_size_test.py
"""
import os, sys, math, bisect, zipfile
from collections import deque, defaultdict

ZIP = "data_cache/french/49_Industry_Portfolios_daily_CSV.zip"
TARGET, DESCR, PLAC = "Oil", ["Coal"], ["Hlth", "Softw"]
ERAS = [("1986-1999", "1986-01-01", "1999-12-31"), ("2000-2012", "2000-01-01", "2012-12-31"), ("2013-2026", "2013-01-01", "2100-01-01")]
SHIFTS = [s * m for m in range(21, 212, 10) for s in (1, -1)]
BUCKETS = {1: "3-5%", 2: "5-10%", 3: "10%+", 4: "all 3%+"}
MIN_MONTHS = 25


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


def oil_bucket_map(sb):
    s = load_macro(sb, "DCOILWTICO")
    assert s, "DCOILWTICO not found in macro_long"
    out = {}
    for i in range(1, len(s)):
        d, v = s[i]
        pv = s[i - 1][1]
        if pv > 5 and v > 5:
            c = abs(v / pv - 1)
            out[d] = 0 if c < 0.03 else (1 if c < 0.05 else (2 if c < 0.10 else 3))
    return out


def bucket_array(bmap, dates, k):
    out = []
    for d in dates:
        b = bmap.get(d)
        if k == 4:
            out.append(None if b is None else (b > 0))
        else:
            out.append(None if b is None or b not in (0, k) else (b == k))
    return out


def circ_shift(arr, s):
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


def msd(vals):
    mu = sum(vals) / len(vals)
    return mu, math.sqrt(sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)) if len(vals) > 1 else 0.0


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

    bmap = oil_bucket_map(sb)
    farr = {k: bucket_array(bmap, dates, k) for k in (1, 2, 3, 4)}
    fnull = {k: [circ_shift(farr[k], s) for s in SHIFTS] for k in (1, 2, 3, 4)}
    ranges = [(en, bisect.bisect_left(dates, lo), bisect.bisect_right(dates, hi)) for en, lo, hi in ERAS]
    ranges.append(("2000-2026 (desc.)", ranges[1][1], nd))
    for k in (1, 2, 3, 4):
        print("bucket %s: %d days on French trading days; shifted copies: %d" % (BUCKETS[k], sum(1 for f in farr[k] if f), len(SHIFTS)), flush=True)

    allres = {}
    print("\n  industry  era                bucket  months | A       null mean (sd)    beats   p")
    for c in [TARGET] + DESCR + PLAC:
        tag = "TARGET" if c == TARGET else ("PLACEBO" if c in PLAC else "descriptive")
        for en, i0, i1 in ranges:
            for k in (1, 2, 3, 4):
                n, a0 = amp_point(zarr[c], tot, cnt, farr[k], dates, i0, i1)
                vals = [amp_point(zarr[c], tot, cnt, fl_, dates, i0, i1)[1] for fl_ in fnull[k]]
                allres[(c, en, k)] = (n, a0, vals)
                ok = [v for v in vals if v is not None]
                if a0 is None or len(ok) < 20:
                    print("  %-8s  %-18s %-6s  %3d   | n/a (too thin)   %s" % (c, en, BUCKETS[k], n, tag))
                    continue
                mu, sd = msd(ok)
                kk = sum(1 for v in ok if v >= a0)
                print("  %-8s  %-18s %-6s  %3d   | %.3f   %.3f (%.3f)   %2d/%d  %.3f   %s" % (c, en, BUCKETS[k], n, a0, mu, sd, len(ok) - kk, len(ok), (1 + kk) / (1 + len(ok)), tag), flush=True)

    print("\nDOSE-RESPONSE D = A(5-10%) - A(3-5%), null from both flag series shifted by the same amount")
    print("  industry  era                months (B1/B2) | D        null mean (sd)    beats   p")
    verdict_cells = {}
    for c in [TARGET] + DESCR + PLAC:
        for en, i0, i1 in ranges:
            n1, a1, v1 = allres[(c, en, 1)]
            n2, a2, v2 = allres[(c, en, 2)]
            if a1 is None or a2 is None:
                print("  %-8s  %-18s   %3d/%3d       | n/a" % (c, en, n1, n2))
                continue
            d0 = a2 - a1
            ds = [b - a for a, b in zip(v1, v2) if a is not None and b is not None]
            mu, sd = msd(ds)
            kk = sum(1 for v in ds if v >= d0)
            verdict_cells[(c, en)] = (n1, n2, d0, kk, len(ds))
            print("  %-8s  %-18s   %3d/%3d       | %+.3f   %+.3f (%.3f)   %2d/%d  %.3f" % (c, en, n1, n2, d0, mu, sd, len(ds) - kk, len(ds), (1 + kk) / (1 + len(ds))), flush=True)

    cells = [verdict_cells.get((TARGET, e)) for e in ("2000-2012", "2013-2026")]
    if any(c is None for c in cells):
        verdict = "no conclusion (a tested era could not be computed)"
    elif any(c[0] < MIN_MONTHS or c[1] < MIN_MONTHS for c in cells):
        verdict = "too thin (fewer than %d qualifying months in a bucket-era)" % MIN_MONTHS
    elif all(c[2] >= 0.10 and c[3] <= 1 for c in cells):
        verdict = "PASS"
    else:
        verdict = "not passed"
    print("\nOIL dose-response in 2000-2012 and 2013-2026 (pre-set line: D >= 0.10 and beats >= 39 of 40 in BOTH): %s" % verdict)
    c1 = verdict_cells.get((TARGET, "1986-1999"))
    if c1:
        print("control era 1986-1999 (effect expected absent): D %+.3f, beats %d of %d" % (c1[2], c1[4] - c1[3], c1[4]))


if __name__ == "__main__":
    main()
