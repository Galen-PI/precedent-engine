#!/usr/bin/env python3
"""
credit_spread_test.py -- READ-ONLY. Do Banks move more than the other industries on days when the Baa-minus-Aaa corporate
yield spread widens sharply? Reads the cached French 49-industry daily file and macro_long (DAAA, DBAA, DGS10). Writes nothing.

PRE-REGISTERED 2026-10-19 (before any result was seen):
 Spread = DBAA - DAAA on days where both exist (from 1986-01-02). Daily change = spread minus the previous available spread.
 WIDENING SHOCK day = daily change >= max(95th percentile of all daily changes, 0.03 percentage points). Both numbers are printed.
 Measure: z = |r| / stdev of the previous 64 returns (>= 50 valid); o = mean z of the other industries that day (>= 10).
 Within each calendar month with >= 2 shock days and >= 5 ordinary days:
     predicted shock-day z for the target = (sum of o on shock days) x (sum of target z on ordinary days / sum of o on ordinary days)
 Amplification (era or pooled) = (sum of actual target z on shock days) / (sum of predicted), pooled over the qualifying months
   (ratio of sums: the older harness took the log of a ratio over few days, which reads low; see the bridge below).
   t = ln(amplification) / SE, SE from a CLUSTER bootstrap over calendar quarters (2,000 resamples, fixed seed).
 Variants: same-day; next-day (the day after a shock); placebo = shock flags shifted by +21 and by -21 trading days.
 Target: Banks (primary). Descriptive: Fin, Insur, RlEst. Placebo industries: Hlth, Softw (reported, not in the verdict).
 Eras: 1986-1999, 2000-2012, 2013-2026.
 PASS (same-day, Banks): amplification >= 1.10 with t >= 2.5 in EVERY era, and all six placebo cells (2 shifts x 3 eras) with |t| < 2.5.
 LEAD: pooled amplification >= 1.05 with t >= 2.5, amplification >= 1.00 in every era, placebo cells clean.
 If any placebo cell fails (|t| >= 2.5) the answer is NO CONCLUSION.
 Next-day line (usable forward): >= 1.05 with t >= 2.5 in every era.
 Same-day effects are explanation only (the spread is known after the close).
 BRIDGE (descriptive, no verdict): the old 10-year-yield test (shock = |change in DGS10| >= 0.10 points; eras 1962-1985, 1986-2007, 2008-end)
   for Banks and the two placebo industries with THIS estimator, to compare with the older harness (Banks 1.018 / 1.137 / 1.124).
 Also printed: how many credit shock days are also 10-year-yield shock days.

Usage: python3 -u scripts/macro/credit_spread_test.py
"""
import os, sys, math, random, zipfile
from collections import deque, defaultdict

ZIP = "data_cache/french/49_Industry_Portfolios_daily_CSV.zip"
TARGET, DESCR, PLAC = "Banks", ["Fin", "Insur", "RlEst"], ["Hlth", "Softw"]
CREDIT_ERAS = [("1986-1999", "1986-01-01", "1999-12-31"), ("2000-2012", "2000-01-01", "2012-12-31"), ("2013-2026", "2013-01-01", "2100-01-01")]
YIELD_ERAS = [("1962-1985", "1962-01-01", "1985-12-31"), ("1986-2007", "1986-01-01", "2007-12-31"), ("2008-end", "2008-01-01", "2100-01-01")]
MIN_THR = 0.03


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
    return {d: (c >= thr - 1e-9) for d, c in ch}, thr, q95, len(sp), sp[0][0], sp[-1][0]


def yield_flags(sb):
    s = load_macro(sb, "DGS10")
    assert s, "DGS10 not found in macro_long"
    return {s[i][0]: abs(s[i][1] - s[i - 1][1]) >= 0.10 - 1e-9 for i in range(1, len(s))}


def to_array(flagmap, dates):
    return [flagmap.get(d) for d in dates]


def shifted(arr, s):
    n = len(arr)
    return [arr[k - s] if 0 <= k - s < n else None for k in range(n)]


def month_items(zc, tot, cnt, nd, flags, dates, lo, hi):
    by = defaultdict(lambda: ([], [], [], []))
    for k in range(nd):
        d = dates[k]
        if d < lo or d > hi:
            continue
        f, zz = flags[k], zc[k]
        if f is None or zz is None or cnt[k] < 11:
            continue
        o = (tot[k] - zz) / (cnt[k] - 1)
        if o <= 0:
            continue
        m = by[d[:7]]
        if f:
            m[0].append(zz)
            m[1].append(o)
        else:
            m[2].append(zz)
            m[3].append(o)
    items = []
    for mk, (sz, so, nz, no) in by.items():
        if len(sz) >= 2 and len(nz) >= 5:
            items.append((mk, sum(sz), sum(so) * (sum(nz) / sum(no)), len(sz)))
    return items


def summarize(items, B=2000, seed=12345):
    """returns (months, shock days, amplification, t, lo, hi, se_log)."""
    n = len(items)
    nsd = sum(i[3] for i in items)
    cl = {}
    for mk, zs, pred, ns in items:
        q = mk[:4] + "Q" + str((int(mk[5:7]) - 1) // 3)
        c = cl.setdefault(q, [0.0, 0.0])
        c[0] += zs
        c[1] += pred
    cs = list(cl.values())
    G = len(cs)
    if n < 6 or G < 4:
        return n, nsd, None, None, None, None, None

    def amp(sel):
        return sum(c[0] for c in sel) / sum(c[1] for c in sel)
    a = amp(cs)
    rng = random.Random(seed)
    la = sorted(math.log(amp([cs[rng.randrange(G)] for _ in range(G)])) for _ in range(B))
    m = sum(la) / B
    se = math.sqrt(sum((x - m) ** 2 for x in la) / (B - 1))
    return n, nsd, a, (math.log(a) / se if se > 0 else None), math.exp(la[int(0.025 * B)]), math.exp(la[int(0.975 * B)]), se


def fmt(r):
    return "  n/a        " if r[2] is None else "%.3f (t %5.1f)" % (r[2], r[3] if r[3] is not None else float("nan"))


def run_experiment(name, flags0, eras, inds, zarr, tot, cnt, nd, dates, show_next=True):
    variants = {"same": flags0, "+21": shifted(flags0, 21), "-21": shifted(flags0, -21), "next": shifted(flags0, 1)}
    res = {}
    print("\n===== %s" % name)
    print("  industry  era         months/shock days   same-day              shift +21             shift -21             next-day")
    for c in inds:
        tag = "TARGET" if c == TARGET else ("PLACEBO" if c in PLAC else "descriptive")
        for en, lo, hi in eras + [("POOLED", eras[0][1], "2100-01-01")]:
            line = "  %-8s  %-10s" % (c, en)
            for vn in ("same", "+21", "-21", "next"):
                r = summarize(month_items(zarr[c], tot, cnt, nd, variants[vn], dates, lo, hi))
                res[(c, en, vn)] = r
                if vn == "same":
                    line += " %3d / %4d       " % (r[0], r[1])
                line += " %s |" % fmt(r)
            print(line + " " + tag)
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

    cf, thr, q95, nsp, sp0, sp1 = credit_flags(sb)
    print("spread observations: %d, %s .. %s | 95th percentile of daily change %.3f pp | threshold used %.3f pp (floor %.2f)" % (nsp, sp0, sp1, q95, thr, MIN_THR))
    F0 = to_array(cf, dates)
    ndays = sum(1 for f in F0 if f)
    print("credit widening shock days on French trading days: %d of %d with a flag" % (ndays, sum(1 for f in F0 if f is not None)))
    yf = yield_flags(sb)
    both = sum(1 for k, f in enumerate(F0) if f and yf.get(dates[k]))
    print("of those, also a 10-year-yield shock day (|change| >= 0.10): %d" % both, flush=True)

    inds = [TARGET] + DESCR + PLAC
    R = run_experiment("CREDIT WIDENING (Baa - Aaa)", F0, CREDIT_ERAS, inds, zarr, tot, cnt, nd, dates)

    eras = [e[0] for e in CREDIT_ERAS]
    cells = [R[(TARGET, en, "same")] for en in eras]
    plac = [R[(TARGET, en, vn)] for en in eras for vn in ("+21", "-21")]
    plac_ok = all(p[3] is not None and abs(p[3]) < 2.5 for p in plac)
    pooled = R[(TARGET, "POOLED", "same")]
    all110 = all(c[2] is not None and c[3] is not None and c[2] >= 1.10 and c[3] >= 2.5 for c in cells)
    all100 = all(c[2] is not None and c[2] >= 1.0 for c in cells)
    if not plac_ok:
        verdict = "NO CONCLUSION (a placebo cell failed calibration)"
    elif all110:
        verdict = "PASS"
    elif pooled[2] is not None and pooled[3] is not None and pooled[2] >= 1.05 and pooled[3] >= 2.5 and all100:
        verdict = "LEAD"
    else:
        verdict = "not passed"
    nxt = [R[(TARGET, en, "next")] for en in eras]
    next_ok = all(c[2] is not None and c[3] is not None and c[2] >= 1.05 and c[3] >= 2.5 for c in nxt)
    print("\nBANKS pooled 1986-2026: %d months, %d shock days, amplification %s, 95%% interval %s .. %s" % (
        pooled[0], pooled[1], "n/a" if pooled[2] is None else "%.3f" % pooled[2],
        "n/a" if pooled[4] is None else "%.3f" % pooled[4], "n/a" if pooled[5] is None else "%.3f" % pooled[5]))
    if pooled[6]:
        print("resolution: t >= 2.5 needs about +%.0f%% pooled (SE of the log %.3f)" % (100 * (math.exp(2.5 * pooled[6]) - 1), pooled[6]))
    print("placebo cells clean: %s | VERDICT same-day (pre-set lines): %s | next-day line (>= 1.05, t >= 2.5 every era): %s" % (plac_ok, verdict, "PASS" if next_ok else "not passed"))

    BR = run_experiment("BRIDGE: 10-YEAR YIELD SHOCK (descriptive; old harness read Banks 1.018 / 1.137 / 1.124)", to_array(yf, dates), YIELD_ERAS, [TARGET] + PLAC, zarr, tot, cnt, nd, dates)


if __name__ == "__main__":
    main()
