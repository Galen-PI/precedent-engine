#!/usr/bin/env python3
"""
long_history_sector_test.py -- READ-ONLY long-history replication of the oil and 10-year-yield tests using Kenneth French's
49 daily industry portfolios (1926+, cached in data_cache/french) and macro_long (FRED, same-day series). Writes nothing to the DB.

PRE-REGISTERED (written before any result was seen):
 Measure: z = |industry return| / stdev of the previous 64 daily returns (>= 50 valid); control = mean z of the other industries that day (>= 10).
 Within each month: R(group) = mean z(industry) / mean z(others) over the group's days; contrast = ln R(shock days) - ln R(ordinary days);
 a month counts only with >= 2 shock days and >= 5 ordinary days. Era amplification = exp(mean of monthly contrasts); t = mean / (stdev / sqrt(months)).
 Same-day version: the shock day itself. Next-day version: the day after a shock day.
 OIL: shock = |WTI daily change| >= 3% (prices > 5 only). Target Oil. Eras 1986-1999, 2000-2018, 2019-end.
      PASS same-day: amplification >= 1.15 and t >= 2.5 in EVERY era. PASS next-day: >= 1.05 and t >= 2.5 in every era.
 YIELD: shock = |10-year Treasury yield change| >= 0.10 percentage points. Targets Util, RlEst, Banks (each its own test). Eras 1962-1985, 1986-2007, 2008-end.
      PASS same-day: >= 1.10 and t >= 2.5 in EVERY era. PASS next-day: >= 1.05 and t >= 2.5 in every era.
 PLACEBOS (both tests): Hlth and Softw must stay below 1.10 in every era (same-day), else the contrast is contaminated.
 All other industries are descriptive only (written to data_cache/long_history_results.csv).

Usage: python3 -u scripts/macro/long_history_sector_test.py
"""
import os, sys, math, csv, zipfile
from collections import deque, defaultdict
from supabase import create_client

ZIP = "data_cache/french/49_Industry_Portfolios_daily_CSV.zip"
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
PLACEBOS = ["Hlth", "Softw"]
EXPS = [
    dict(name="OIL", series="DCOILWTICO", kind="oil", targets=["Oil"], extra=["Coal"], same_line=1.15, next_line=1.05,
         eras=[("1986-1999", "1986-01-01", "1999-12-31"), ("2000-2018", "2000-01-01", "2018-12-31"), ("2019-end", "2019-01-01", "2100-01-01")]),
    dict(name="10Y_YIELD", series="DGS10", kind="yield", targets=["Util", "RlEst", "Banks"], extra=["Insur"], same_line=1.10, next_line=1.05,
         eras=[("1962-1985", "1962-01-01", "1985-12-31"), ("1986-2007", "1986-01-01", "2007-12-31"), ("2008-end", "2008-01-01", "2100-01-01")]),
]


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


def load_macro(sid):
    rows, off = [], 0
    while True:
        page = sb.table("macro_long").select("obs_date,value").eq("series_id", sid).order("obs_date").range(off, off + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return [(r["obs_date"], r["value"]) for r in rows if r["value"] is not None]


def shock_flags(series, kind):
    out, prev = {}, None
    for d, v in series:
        if prev is not None:
            if kind == "oil":
                out[d] = (abs(v / prev - 1) >= 0.03) if (prev > 5 and v > 5) else None
            else:
                out[d] = abs(v - prev) >= 0.10 - 1e-9
        prev = v
    return out


def contrast(zi_map, tot, cnt, dates, flagmap, lo, hi):
    months = defaultdict(lambda: ([], [], [], []))
    for d in dates:
        if d < lo or d > hi:
            continue
        f, zi = flagmap.get(d), zi_map.get(d)
        if f is None or zi is None or cnt.get(d, 0) < 11:
            continue
        oth = (tot[d] - zi) / (cnt[d] - 1)
        if oth <= 0:
            continue
        m = months[d[:7]]
        if f:
            m[0].append(zi)
            m[1].append(oth)
        else:
            m[2].append(zi)
            m[3].append(oth)
    ds = []
    for sz, so, nz, no in months.values():
        if len(sz) >= 2 and len(nz) >= 5:
            rs = (sum(sz) / len(sz)) / (sum(so) / len(so))
            rn = (sum(nz) / len(nz)) / (sum(no) / len(no))
            if rs > 0 and rn > 0:
                ds.append(math.log(rs) - math.log(rn))
    n = len(ds)
    if n < 3:
        return n, None, None
    mu = sum(ds) / n
    sd = math.sqrt(sum((x - mu) ** 2 for x in ds) / (n - 1))
    return n, math.exp(mu), (mu / (sd / math.sqrt(n)) if sd > 0 else None)


def fmt(a, t):
    return "   n/a        " if a is None else "%.3f (t %5.1f)" % (a, t if t is not None else float("nan"))


def main():
    block = 1 if "--equal" in sys.argv else 0
    print("WEIGHTING:", "EQUAL-weighted (small-cap heavy)" if block else "VALUE-weighted (large-cap heavy)", flush=True)
    cols, data = load_french(ZIP, block)
    dates = sorted(data)
    print("French: %d industries, %d days, %s .. %s" % (len(cols), len(dates), dates[0], dates[-1]), flush=True)
    z = zscores(cols, dates, data)
    tot, cnt = {}, {}
    for c in cols:
        for d, v in z[c].items():
            tot[d] = tot.get(d, 0.0) + v
            cnt[d] = cnt.get(d, 0) + 1
    results = []
    for E in EXPS:
        series = load_macro(E["series"])
        flags = shock_flags(series, E["kind"])
        same, nxt, prev_d = {}, {}, None
        for d in dates:
            same[d] = flags.get(d)
            nxt[d] = flags.get(prev_d) if prev_d else None
            prev_d = d
        print("\n===== %s | %s: %d observations %s .. %s" % (E["name"], E["series"], len(series), series[0][0], series[-1][0]), flush=True)
        for en, lo, hi in E["eras"]:
            print("  era %-10s shock days: %d" % (en, sum(1 for d in dates if lo <= d <= hi and same[d])))
        res = {}
        for c in cols:
            res[c] = []
            for en, lo, hi in E["eras"]:
                n1, a1, t1 = contrast(z[c], tot, cnt, dates, same, lo, hi)
                n2, a2, t2 = contrast(z[c], tot, cnt, dates, nxt, lo, hi)
                res[c].append((en, n1, a1, t1, a2, t2))
                results.append([E["name"], c, en, n1, a1, t1, a2, t2])
        print("\n  industry  era         months   same-day amp (t)    next-day amp (t)")
        for c in E["targets"] + PLACEBOS + E["extra"]:
            tag = "TARGET" if c in E["targets"] else ("PLACEBO" if c in PLACEBOS else "descriptive")
            for en, n1, a1, t1, a2, t2 in res[c]:
                print("  %-8s  %-10s %4d    %s    %s   %s" % (c, en, n1, fmt(a1, t1), fmt(a2, t2), tag))
        print("\n  VERDICTS (pre-set lines)")
        for c in E["targets"]:
            same_ok = all(r[2] is not None and r[3] is not None and r[2] >= E["same_line"] and r[3] >= 2.5 for r in res[c])
            next_ok = all(r[4] is not None and r[5] is not None and r[4] >= E["next_line"] and r[5] >= 2.5 for r in res[c])
            print("   %-8s same-day: %s | next-day: %s" % (c, "PASS" if same_ok else "not passed", "PASS" if next_ok else "not passed"))
        for c in PLACEBOS:
            bad = any(r[2] is not None and r[2] >= 1.10 for r in res[c])
            print("   placebo %-6s %s" % (c, "CONTAMINATED (>= 1.10 in some era)" if bad else "clean (< 1.10 in every era)"))
    os.makedirs("data_cache", exist_ok=True)
    outname = "data_cache/long_history_results%s.csv" % ("_equal" if block else "")
    with open(outname, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["experiment", "industry", "era", "months", "amp_same", "t_same", "amp_next", "t_next"])
        w.writerows(results)
    print("\nwrote %s (%d rows)" % (outname, len(results)))


if __name__ == "__main__":
    main()
