#!/usr/bin/env python3
"""
fed_change_days_test.py -- READ-ONLY. Do rate-sensitive French industries move more than the other industries
on Fed target-rate change days? Reads the cached French 49-industry daily file, macro_long (DFEDTAR/DFEDTARU)
and government_decisions (interest_rate rows). Writes nothing to the database.

PRE-REGISTERED 2026-10-19 (before any result was seen; replaces the window proposed on 2026-10-18):
 Event days: Fed target changes. 1994-02-01..2014-12-31: the macro_long series date (weekday pattern Tue/Wed = announcement day).
   2015 on: the announcement date in government_decisions (decision_type interest_rate); the series is dated the day AFTER for 29 of 31.
   A date that is not a French trading day moves to the next trading day. Data end 2026-08-31 (the 2026-09-16 hike is outside).
   1982-1993 is descriptive only (changes were not announced then).
 Window: the announcement day plus the next trading day (2 days).
 Measure: z = |r| / stdev of the previous 64 returns (>= 50 valid); o = mean z of the other industries that day (>= 10).
   Each date contributes its window sums (z, o over the 2 days) and its baseline per-window means (z, o).
   Baseline = the same 2-day window at +-63, +-126, +-189, +-252 trading days, minus any baseline window touching a real event window;
   >= 4 baseline windows needed.
   Amplification (era or pooled) = [sum window z / sum window o] / [sum baseline z / sum baseline o] over the dates (ratio of sums;
   the first version, a mean of per-date log ratios, was biased 8-17% LOW on synthetic no-effect data and was dropped before any real result).
   t = ln(amplification) / SE, SE from a bootstrap over dates (2,000 resamples, fixed seed); 95% interval from the bootstrap percentiles.
 Placebos: the whole event window shifted by +21 and -21 trading days (same machinery; shifted windows touching real windows dropped).
 Targets: Banks (primary). Descriptive: Insur, Util, RlEst. Placebo industries: Hlth, Softw.
 Eras: 1994-2003, 2004-2014, 2015-2026.
 PASS (Banks): pooled 1994-2026 amplification >= 1.05 and t >= 2.5, amplification >= 1.00 in every era,
   and both pooled placebo shifts with |t| < 2.5 (a fixed 0.90-1.10 band was dropped: with ~90 dates the sampling error alone is about +-0.12,
   so that band would have declared 'no conclusion' by chance roughly one run in five).
 LEAD: pooled t >= 2.0, pooled amplification >= 1.00 in at least 2 of 3 eras, placebos clean.
 If a placebo shift fails (|t| >= 2.5) the answer is NO CONCLUSION.
 Hlth and Softw (placebo industries) are reported, not part of the verdict.
 Reported but not part of the verdict: (A) the older window (day before the series date + series date) for all dates;
   (B) without the two March 2020 emergency days (announced 2020-03-03 and 2020-03-15); (C) hikes only, cuts only.

Usage: python3 -u scripts/macro/fed_change_days_test.py
"""
import os, sys, math, bisect, random, zipfile
from collections import deque
from datetime import date, timedelta

ZIP = "data_cache/french/49_Industry_Portfolios_daily_CSV.zip"
TARGETS, DESCR, PLAC = ["Banks"], ["Insur", "Util", "RlEst"], ["Hlth", "Softw"]
ERAS = [("1994-2003", "1994-02-01", "2003-12-31"), ("2004-2014", "2004-01-01", "2014-12-31"), ("2015-2026", "2015-01-01", "2100-01-01")]
OFFS = [63, -63, 126, -126, 189, -189, 252, -252]
FIRST_ANNOUNCED = "1994-02-01"


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


def fed_changes(sb):
    rows = sorted(load_macro(sb, "DFEDTAR") + load_macro(sb, "DFEDTARU"))
    out, prev = {}, None
    for d, v in rows:
        if prev is not None and v != prev:
            out[d] = 1 if v > prev else -1
        prev = v
    return out


def announce_dates(sb):
    rows = sb.table("government_decisions").select("decision_date").eq("decision_type", "interest_rate").execute().data
    return sorted(str(r["decision_date"])[:10] for r in rows)


def contrasts(zc, tot, cnt, nd, firsts, shift, blocked):
    """per-event window/baseline sums (None if not computable). Window = days (k, k+1) with k = first + shift."""
    def zo(j):
        if j < 0 or j >= nd:
            return None
        zz = zc[j]
        if zz is None or cnt[j] < 11:
            return None
        o = (tot[j] - zz) / (cnt[j] - 1)
        return (zz, o) if o > 0 else None
    out = []
    for k0 in firsts:
        k = k0 + shift
        if shift and (k in blocked or k + 1 in blocked):
            out.append(None)
            continue
        a, b = zo(k), zo(k + 1)
        if a is None or b is None:
            out.append(None)
            continue
        sz, so, nb = 0.0, 0.0, 0
        for off in OFFS:
            j = k + off
            if j in blocked or j + 1 in blocked:
                continue
            p, q = zo(j), zo(j + 1)
            if p is None or q is None:
                continue
            sz += p[0] + q[0]
            so += p[1] + q[1]
            nb += 1
        if nb < 4:
            out.append(None)
            continue
        out.append((a[0] + b[0], a[1] + b[1], sz / nb, so / nb))
    return out


def summarize(items, B=2000, seed=12345):
    """items = [(window z sum, window o sum, baseline z mean, baseline o mean)]; ratio-of-sums amplification + bootstrap."""
    n = len(items)
    if n < 3:
        return n, None, None, None, None

    def amp(idx):
        zw = sum(items[i][0] for i in idx)
        ow = sum(items[i][1] for i in idx)
        zb = sum(items[i][2] for i in idx)
        ob = sum(items[i][3] for i in idx)
        return (zw / ow) / (zb / ob)
    a = amp(range(n))
    rng = random.Random(seed)
    la = sorted(math.log(amp([rng.randrange(n) for _ in range(n)])) for _ in range(B))
    m = sum(la) / B
    se = math.sqrt(sum((x - m) ** 2 for x in la) / (B - 1))
    return n, a, (math.log(a) / se if se > 0 else None), math.exp(la[int(0.025 * B)]), math.exp(la[int(0.975 * B)])


def fmt(a, t):
    return "  n/a        " if a is None else "%.3f (t %5.1f)" % (a, t if t is not None else float("nan"))


def pick(rows, era, drop=(), direction=None):
    out = []
    for d, dirn, v in rows:
        if d in drop or (direction is not None and dirn != direction):
            continue
        if era == "POOLED":
            ok = d >= FIRST_ANNOUNCED
        elif era == "1982-1993":
            ok = d < FIRST_ANNOUNCED
        else:
            lo, hi = next((a, b) for n, a, b in ERAS if n == era)
            ok = lo <= d <= hi
        if ok:
            out.append(v)
    return out


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
    for c in TARGETS + DESCR + PLAC:
        assert c in zarr, "industry not found: " + c

    chg = fed_changes(sb)
    sdates = sorted(chg)
    ann = announce_dates(sb)
    ev = []   # (announcement day, direction, series date)
    for d in sdates:
        if "1982-01-01" <= d < "2015-01-01":
            ev.append((d, chg[d], d))
    for a in ann:
        if a < "2015-01-01":
            continue
        lim = (date.fromisoformat(a) + timedelta(days=2)).isoformat()
        s = next((x for x in sdates if a <= x <= lim), None)
        ev.append((a, chg[s] if s else 0, s if s else a))
    ev = [e for e in ev if bisect.bisect_left(dates, e[0]) < nd]
    print("events: %d (announcement dates; %d from government_decisions)" % (len(ev), sum(1 for e in ev if e[0] >= "2015-01-01")))
    for en in ["1982-1993"] + [e[0] for e in ERAS]:
        print("   %-10s %d dates" % (en, len(pick([(e[0], e[1], 0.0) for e in ev], en))))

    firsts = [bisect.bisect_left(dates, e[0]) for e in ev]
    blocked = set()
    for k in firsts:
        blocked.update((k, k + 1))
    firstsA = [max(bisect.bisect_left(dates, e[2]) - 1, 0) for e in ev]
    blockedA = set()
    for k in firstsA:
        blockedA.update((k, k + 1))

    res, resA = {}, {}
    for c in TARGETS + DESCR + PLAC:
        for sh in (0, 21, -21):
            vals = contrasts(zarr[c], tot, cnt, nd, firsts, sh, blocked)
            res[(c, sh)] = [(ev[m][0], ev[m][1], v) for m, v in enumerate(vals) if v is not None]
        valsA = contrasts(zarr[c], tot, cnt, nd, firstsA, 0, blockedA)
        resA[c] = [(ev[m][0], ev[m][1], v) for m, v in enumerate(valsA) if v is not None]

    eras = [e[0] for e in ERAS]
    print("\n  industry  era         real windows              shift +21                 shift -21")
    for c in TARGETS + DESCR + PLAC:
        tag = "TARGET" if c in TARGETS else ("PLACEBO" if c in PLAC else "descriptive")
        for en in eras + ["POOLED", "1982-1993"]:
            line = "  %-8s  %-10s" % (c, en)
            for sh in (0, 21, -21):
                n, a, t, lo, hi = summarize(pick(res[(c, sh)], en))
                line += "  n=%3d %s |" % (n, fmt(a, t))
            print(line + "  " + tag)

    n0, a0, t0, lo0, hi0 = summarize(pick(res[("Banks", 0)], "POOLED"))
    print("\nBANKS pooled 1994-2026: %d dates, amplification %s, 95%% interval %s .. %s" % (
        n0, "n/a" if a0 is None else "%.3f" % a0, "n/a" if lo0 is None else "%.3f" % lo0, "n/a" if hi0 is None else "%.3f" % hi0))
    era_amps = [summarize(pick(res[("Banks", 0)], en))[1] for en in eras]
    pl = [summarize(pick(res[("Banks", s)], "POOLED")) for s in (21, -21)]
    plac_ok = all(p[2] is not None and abs(p[2]) < 2.5 for p in pl)
    n_ge = sum(1 for a in era_amps if a is not None and a >= 1.0)
    if not plac_ok:
        verdict = "NO CONCLUSION (placebo shifts failed calibration)"
    elif a0 is not None and t0 is not None and a0 >= 1.05 and t0 >= 2.5 and n_ge == 3:
        verdict = "PASS"
    elif a0 is not None and t0 is not None and t0 >= 2.0 and a0 >= 1.0 and n_ge >= 2:
        verdict = "LEAD"
    else:
        verdict = "not passed"
    print("placebos clean: %s | eras with amplification >= 1.00: %d of 3 | VERDICT (pre-set lines): %s" % (plac_ok, n_ge, verdict))

    print("\nSENSITIVITIES (Banks, pooled 1994-2026; not part of the verdict)")
    n, a, t, lo, hi = summarize(pick(resA["Banks"], "POOLED"))
    print("  A older window (day before series date + series date): n=%d %s" % (n, fmt(a, t)))
    n, a, t, lo, hi = summarize(pick(res[("Banks", 0)], "POOLED", drop=("2020-03-03", "2020-03-15")))
    print("  B without March 2020 emergency days:                  n=%d %s" % (n, fmt(a, t)))
    for nm, dr in (("hikes only", 1), ("cuts only", -1)):
        n, a, t, lo, hi = summarize(pick(res[("Banks", 0)], "POOLED", direction=dr))
        print("  C %-10s                                       n=%d %s" % (nm, n, fmt(a, t)))
    def lr(v):
        return math.log((v[0] / v[1]) / (v[2] / v[3]))
    big = sorted(res[("Banks", 0)], key=lambda r: -abs(lr(r[2])))[:6]
    print("\nlargest per-date contrasts for Banks, ln(window ratio / baseline ratio) (a few dates should not drive the result):")
    print("  " + ", ".join("%s %+.2f" % (r[0], lr(r[2])) for r in big))


if __name__ == "__main__":
    main()
