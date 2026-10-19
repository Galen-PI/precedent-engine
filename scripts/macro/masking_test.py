#!/usr/bin/env python3
"""
masking_test.py -- READ-ONLY. Does a link get weaker (masking) or stronger (compounding) on days when OTHER daily markers are also active?
Reads the cached French 49-industry daily file and macro_long (DCOILWTICO, DGS10, DAAA, DBAA). Writes nothing.

PRE-REGISTERED 2026-10-19 (before any real-data result; the null was revised twice after synthetic calibration checks, see CHANGE LOG):
 Daily markers: oil move (|WTI change| >= 3%, both prices > 5), yield move (|DGS10 change| >= 0.10 points), credit widening
   (change in DBAA - DAAA >= 0.03 points). A day is usable only when all three markers can be computed.
 Primary pairs (only two, to keep the number of looks small): trigger OIL with target Oil industry; trigger YIELD with target Banks.
 For a trigger T: "alone" = T on and both other markers off; "with other" = T on and at least one other marker on;
   ordinary days = all three markers off. Days with any other combination are excluded.
 Measure: z = |r| / stdev of the previous 64 returns (>= 50 valid); o = mean z of the other industries that day (>= 10).
 DESIGN (within month): only MIXED months are used: a calendar month with >= 5 ordinary days and at least one "alone" and at least one
   "with other" trigger day. For each such month R = (sum of target z on ordinary days) / (sum of o on ordinary days); predicted
   trigger-day z = R x o. A(alone) = sum of actual z on alone days / sum of predicted, pooled over the mixed months of the era;
   A(with) likewise. M = A(alone) - A(with).
 NULL: within each mixed month the labels "alone" and "with other" are shuffled among that month's trigger days (the counts per month stay
   fixed); 1,000 shuffles (fixed seed). This holds each month's composition fixed, so it is exact for "the label does not matter within a
   month". k_mask = shuffles with M >= the real M; k_comp = shuffles with M <= the real M.
 MASKING (a primary pair): both 2000-2012 and 2013-2026 have >= 25 mixed months, M >= 0.10 and k_mask <= 49 (one-sided p <= 0.05) in BOTH.
   COMPOUNDING is the mirror image (-M >= 0.10 and k_comp <= 49 in both). A pair with fewer than 25 mixed months in an era is "too thin".
 1986-1999 and pooled 2000-2026 are descriptive. Placebo industries Hlth and Softw are reported for both triggers (not in the verdict).
 CHANGE LOG: (1) the circular-shift null of the credit and oil-size tests was miscalibrated for comparing two subsets of one trigger (|z| >= 2 in
   21% of oil cells and 12% of yield cells with no interaction); (2) a quarter-block label permutation had an off-center null because shuffling
   changes which months qualify; (3) the within-month design above. Synthetic calibration of (3), 20 seeds each: no interaction: standardized M
   sd 1.07 (oil) and 1.12 (yield), a false both-era verdict in 1 of 40 pairs; built-in masking (1.4 vs 1.05) found in 11 of 20 (oil) and 9 of 20
   (yield) pairs; built-in compounding (1.4 vs 1.9) in 13 of 20 and 10 of 20.
 Stated in advance: masking is expected in 2000-2012 (2008-09 overlap) and little or nothing in 2013-2026; this could be wrong. With about
   25-45 mixed months per era the power is moderate: an interaction smaller than about 0.3 may not pass.

Usage: python3 -u scripts/macro/masking_test.py
"""
import os, sys, math, bisect, zipfile
from collections import deque, defaultdict

ZIP = "data_cache/french/49_Industry_Portfolios_daily_CSV.zip"
ERAS = [("1986-1999", "1986-01-01", "1999-12-31"), ("2000-2012", "2000-01-01", "2012-12-31"), ("2013-2026", "2013-01-01", "2100-01-01")]
SHIFTS = [s * m for m in range(21, 212, 10) for s in (1, -1)]
PAIRS = [("oil", "Oil"), ("yield", "Banks")]
PLAC = ["Hlth", "Softw"]
MIN_MONTHS = 25
PERM_B = 1000
PERM_K = 49


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


def marker_maps(sb):
    oil = load_macro(sb, "DCOILWTICO")
    y10 = load_macro(sb, "DGS10")
    aaa = dict(load_macro(sb, "DAAA"))
    baa = dict(load_macro(sb, "DBAA"))
    assert oil and y10 and aaa and baa, "a macro series is missing from macro_long"
    omap, ymap, cmap = {}, {}, {}
    for i in range(1, len(oil)):
        d, v = oil[i]
        pv = oil[i - 1][1]
        if pv > 5 and v > 5:
            omap[d] = abs(v / pv - 1) >= 0.03
    for i in range(1, len(y10)):
        ymap[y10[i][0]] = abs(y10[i][1] - y10[i - 1][1]) >= 0.10 - 1e-9
    sp = sorted((d, baa[d] - aaa[d]) for d in aaa if d in baa)
    for i in range(1, len(sp)):
        cmap[sp[i][0]] = sp[i][1] - sp[i - 1][1] >= 0.03 - 1e-9
    return omap, ymap, cmap


def trig_arrays(dates, omap, ymap, cmap, trig):
    alone, withoth = [], []
    for d in dates:
        o, y, c = omap.get(d), ymap.get(d), cmap.get(d)
        if o is None or y is None or c is None:
            alone.append(None)
            withoth.append(None)
            continue
        flags = {"oil": o, "yield": y, "credit": c}
        t = flags[trig]
        anyother = any(v for k, v in flags.items() if k != trig)
        if t and not anyother:
            alone.append(True)
            withoth.append(None)
        elif t and anyother:
            alone.append(None)
            withoth.append(True)
        elif not t and not anyother:
            alone.append(False)
            withoth.append(False)
        else:
            alone.append(None)
            withoth.append(None)
    return alone, withoth


def month_groups(zc, tot, cnt, alone, withoth, dates, i0, i1):
    """Mixed months only: >= 5 ordinary days (all three markers off) and at least one 'alone' AND one 'with other' trigger day.
    Returns [(R, [(z, o, label), ...])] with R = ordinary-day sum z / sum o and label 0 = alone, 1 = with other."""
    by = defaultdict(lambda: {"oz": 0.0, "oo": 0.0, "no": 0, "trig": []})
    for k in range(i0, i1):
        zz = zc[k]
        if zz is None or cnt[k] < 11:
            continue
        o = (tot[k] - zz) / (cnt[k] - 1)
        if o <= 0:
            continue
        m = by[dates[k][:7]]
        if alone[k] is False:
            m["oz"] += zz
            m["oo"] += o
            m["no"] += 1
        elif alone[k] is True:
            m["trig"].append((zz, o, 0))
        elif withoth[k] is True:
            m["trig"].append((zz, o, 1))
    months = []
    for mk, m in by.items():
        if m["no"] >= 5 and m["oo"] > 0:
            labs = set(t[2] for t in m["trig"])
            if 0 in labs and 1 in labs:
                months.append((m["oz"] / m["oo"], m["trig"]))
    return months


def pooled(months, labels=None):
    za = pa = zw = pw = 0.0
    for mi, (R, trig) in enumerate(months):
        labs = labels[mi] if labels is not None else [t[2] for t in trig]
        for (z, o, _), lab in zip(trig, labs):
            if lab == 0:
                za += z
                pa += R * o
            else:
                zw += z
                pw += R * o
    if pa <= 0 or pw <= 0:
        return None, None, None
    return za / pa - zw / pw, za / pa, zw / pw


def within_month_null(months, B, seed=7):
    import random
    rng = random.Random(seed)
    base = [[t[2] for t in trig] for R, trig in months]
    out = []
    for _ in range(B):
        labels = []
        for labs in base:
            l2 = list(labs)
            rng.shuffle(l2)
            labels.append(l2)
        out.append(pooled(months, labels)[0])
    return [v for v in out if v is not None]


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
    for trig, tgt in PAIRS:
        assert tgt in zarr, "industry not found: " + tgt
    for c in PLAC:
        assert c in zarr, "industry not found: " + c

    omap, ymap, cmap = marker_maps(sb)
    ranges = [(en, bisect.bisect_left(dates, lo), bisect.bisect_right(dates, hi)) for en, lo, hi in ERAS]
    ranges.append(("2000-2026 (desc.)", ranges[1][1], nd))
    verdicts = {}
    for trig, tgt in PAIRS:
        alone, withoth = trig_arrays(dates, omap, ymap, cmap, trig)
        print("\n===== TRIGGER %s: days alone %d, with another marker %d, ordinary %d" % (
            trig.upper(), sum(1 for f in alone if f), sum(1 for f in withoth if f), sum(1 for f in alone if f is False)), flush=True)
        print("  industry  era                mixed months (days alone/with) | A alone  A with | M = alone - with   null mean (sd)   masking beats   compounding beats")
        for c in [tgt] + PLAC:
            tag = "TARGET" if c == tgt else "PLACEBO"
            for en, i0, i1 in ranges:
                months = month_groups(zarr[c], tot, cnt, alone, withoth, dates, i0, i1)
                nA = sum(1 for R, tr in months for t in tr if t[2] == 0)
                nW = sum(1 for R, tr in months for t in tr if t[2] == 1)
                M, aa, aw = pooled(months)
                if M is None or len(months) < 6:
                    print("  %-8s  %-18s    %3d (%d/%d)                  | n/a (too thin)   %s" % (c, en, len(months), nA, nW, tag), flush=True)
                    if c == tgt:
                        verdicts[(trig, en)] = ("thin", len(months))
                    continue
                null = within_month_null(months, PERM_B)
                mm, ms = msd(null)
                km = sum(1 for v in null if v >= M)
                kc = sum(1 for v in null if v <= M)
                print("  %-8s  %-18s    %3d (%d/%d)                  | %.3f   %.3f | %+.3f   %+.3f (%.3f)   %4d/%d   %4d/%d   %s" % (
                    c, en, len(months), nA, nW, aa, aw, M, mm, ms, len(null) - km, len(null), len(null) - kc, len(null), tag), flush=True)
                if c == tgt:
                    verdicts[(trig, en)] = ("ok", len(months), M, km, kc, len(null))
    print("\nVERDICTS (pre-set: both 2000-2012 and 2013-2026, >= %d mixed months, |M| >= 0.10 and within-month permutation p <= 0.05)" % MIN_MONTHS)
    for trig, tgt in PAIRS:
        cells = [verdicts.get((trig, e)) for e in ("2000-2012", "2013-2026")]
        if any(c is None for c in cells):
            res = "no conclusion (an era could not be computed)"
        elif any(c[0] == "thin" or c[1] < MIN_MONTHS for c in cells):
            mon = ", ".join("%s: %s" % (e, c[1]) for e, c in zip(("2000-2012", "2013-2026"), cells))
            res = "too thin (mixed months: %s)" % mon
        elif all(c[2] >= 0.10 and c[3] <= PERM_K for c in cells):
            res = "MASKING"
        elif all(-c[2] >= 0.10 and c[4] <= PERM_K for c in cells):
            res = "COMPOUNDING"
        else:
            res = "not passed (no consistent masking or compounding)"
        print("  trigger %-5s target %-6s : %s" % (trig, tgt, res))


if __name__ == "__main__":
    main()
