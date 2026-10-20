#!/usr/bin/env python3
"""
eo_market_test.py -- READ-ONLY. Is the market-wide move size larger than usual around executive-order signing days?
Reads sector_day_z (the average |return| / own 64-day volatility across all stocks, by sector and day) and
government_decisions (executive_order rows, structured_data keys signing_date and relevance_verdict). Writes nothing.

PRE-REGISTERED 2026-10-19 (before any result was seen):
 Measure: M(day) = sum(n * mean_z) / sum(n) over all sector rows of that day (all sectors incl. Unclassified), days with >= 150 stocks.
 Event dates: distinct signing dates (structured_data.signing_date; orders without one are dropped) of orders whose
   relevance_verdict = 'relevant', 2004-01-01..2026-07-31. A weekend or holiday date moves to the next trading day.
 Window: the signing day plus the next trading day (2 days).
 Baseline: the same 2-day window at +-63, +-126, +-189, +-252 trading days, minus any baseline window touching a window of the SAME group;
   >= 4 baseline windows needed.
 Amplification = [sum of window M] / [sum of baseline per-window mean M] pooled over the dates in the era (ratio of sums);
   t = ln(amplification) / SE with SE from a CLUSTER bootstrap that resamples whole calendar quarters (2,000 resamples, fixed seed);
   95% interval from bootstrap percentiles. (On synthetic no-effect data with clustered signing dates, a bootstrap over single dates
   flagged |t| >= 2 in 17% of runs and the quarter-cluster version in 7%, so the single-date version was dropped before any real result.)
 Placebos: the whole window shifted by +21 and -21 trading days (shifted windows touching real windows dropped).
 Eras: 2004-2012 and 2013-2026.
 PASS: amplification >= 1.05 with t >= 2.5 in BOTH eras, and all four placebo cells (2 shifts x 2 eras) with |t| < 2.5.
 LEAD: pooled t >= 2.0 and amplification >= 1.00 in both eras, placebos clean.
 If any placebo cell fails (|t| >= 2.5) the answer is NO CONCLUSION.
 Descriptive only (not in the verdict): dates with only non-relevant orders, same machinery.
 Limits stated in advance: a signing day often shares its date with other news (jobs reports, Fed days, tariffs), and this design cannot
 separate them; a pass would be an association, not an effect of the order.

Usage: python3 -u scripts/macro/eo_market_test.py
"""
import os, sys, math, bisect, random

OFFS = [63, -63, 126, -126, 189, -189, 252, -252]
ERAS = [("2004-2012", "2004-01-01", "2012-12-31"), ("2013-2026", "2013-01-01", "2026-07-31")]
START, END = "2004-01-01", "2026-07-31"


def get_sb():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def fetch_all(sb, table, cols, orders, eq=None):
    rows, off = [], 0
    while True:
        q = sb.table(table).select(cols)
        if eq:
            q = q.eq(eq[0], eq[1])
        for o in orders:
            q = q.order(o)
        page = q.range(off, off + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return rows


def contrasts(M, nd, firsts, shift, blocked):
    def zo(j):
        return M[j] if 0 <= j < nd else None
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
        sz, nb = 0.0, 0
        for off in OFFS:
            j = k + off
            if j in blocked or j + 1 in blocked:
                continue
            p, q = zo(j), zo(j + 1)
            if p is None or q is None:
                continue
            sz += p + q
            nb += 1
        if nb < 4:
            out.append(None)
            continue
        out.append((a + b, 2.0, sz / nb, 2.0))
    return out


def qkey(d):
    return d[:4] + "Q" + str((int(d[5:7]) - 1) // 3)


def summarize(pairs, B=2000, seed=12345):
    """pairs = [(item, date)]; item = (window sum, window n, baseline mean sum, baseline n). Ratio of sums; bootstrap over calendar quarters."""
    n = len(pairs)
    cl = {}
    for it, d in pairs:
        c = cl.setdefault(qkey(d), [0.0, 0.0, 0.0, 0.0])
        for j in range(4):
            c[j] += it[j]
    cs = list(cl.values())
    G = len(cs)
    if n < 3 or G < 8:
        return n, None, None, None, None

    def amp(sel):
        zw = sum(c[0] for c in sel)
        ow = sum(c[1] for c in sel)
        zb = sum(c[2] for c in sel)
        ob = sum(c[3] for c in sel)
        return (zw / ow) / (zb / ob)
    a = amp(cs)
    rng = random.Random(seed)
    la = sorted(math.log(amp([cs[rng.randrange(G)] for _ in range(G)])) for _ in range(B))
    m = sum(la) / B
    se = math.sqrt(sum((x - m) ** 2 for x in la) / (B - 1))
    return n, a, (math.log(a) / se if se > 0 else None), math.exp(la[int(0.025 * B)]), math.exp(la[int(0.975 * B)])


def fmt(a, t):
    return "  n/a        " if a is None else "%.3f (t %5.1f)" % (a, t if t is not None else float("nan"))


def pick(rows, era):
    if era == "POOLED":
        return [(v, d) for d, v in rows]
    lo, hi = next((a, b) for n, a, b in ERAS if n == era)
    return [(v, d) for d, v in rows if lo <= d <= hi]


def main():
    sb = get_sb()
    sd = fetch_all(sb, "sector_day_z", "day,n,mean_z", ["day", "sector"])
    agg = {}
    for r in sd:
        if r["n"] is None or r["mean_z"] is None:
            continue
        if str(r["day"])[:10] > "2026-07-31":      # the pre-registered window ends 2026-07-31; sector_day_z was extended past it on 2026-10-20
            continue
        a = agg.setdefault(str(r["day"])[:10], [0.0, 0])
        a[0] += r["n"] * r["mean_z"]
        a[1] += r["n"]
    days = sorted(agg)
    nd = len(days)
    M = [(agg[d][0] / agg[d][1]) if agg[d][1] >= 150 else None for d in days]
    print("sector_day_z: %d rows, %d trading days %s .. %s, %d with >= 150 stocks; mean M %.3f" % (
        len(sd), nd, days[0], days[-1], sum(1 for m in M if m is not None), sum(m for m in M if m is not None) / max(1, sum(1 for m in M if m is not None))), flush=True)

    eo = fetch_all(sb, "government_decisions", "decision_date,structured_data", ["decision_date", "id"], eq=("decision_type", "executive_order"))
    rel, nonrel, nosign = set(), set(), 0
    for r in eo:
        s = r.get("structured_data") or {}
        sdte = str(s.get("signing_date") or "")[:10]
        if len(sdte) != 10:
            nosign += 1
            continue
        if not (START <= sdte <= END):
            continue
        (rel if s.get("relevance_verdict") == "relevant" else nonrel).add(sdte)
    nonrel -= rel
    print("executive orders read: %d (no signing_date: %d); distinct dates: relevant %d, only-non-relevant %d" % (len(eo), nosign, len(rel), len(nonrel)))
    for en, lo, hi in ERAS:
        print("   %-10s relevant dates %d | only-non-relevant dates %d" % (en, sum(1 for d in rel if lo <= d <= hi), sum(1 for d in nonrel if lo <= d <= hi)))

    def build(dset):
        evs = sorted(dset)
        firsts, keep = [], []
        for d in evs:
            i = bisect.bisect_left(days, d)
            if i < nd - 1:
                firsts.append(i)
                keep.append(d)
        blocked = set()
        for k in firsts:
            blocked.update((k, k + 1))
        return keep, firsts, blocked

    out = {}
    for name, dset in (("RELEVANT", rel), ("non-relevant", nonrel)):
        keep, firsts, blocked = build(dset)
        for sh in (0, 21, -21):
            vals = contrasts(M, nd, firsts, sh, blocked)
            out[(name, sh)] = [(keep[m], v) for m, v in enumerate(vals) if v is not None]
    print("\n  group         era         real windows              shift +21                 shift -21")
    for name in ("RELEVANT", "non-relevant"):
        tag = "PRIMARY" if name == "RELEVANT" else "descriptive"
        for en in [e[0] for e in ERAS] + ["POOLED"]:
            line = "  %-12s  %-10s" % (name, en)
            for sh in (0, 21, -21):
                n, a, t, lo, hi = summarize(pick(out[(name, sh)], en))
                line += "  n=%3d %s |" % (n, fmt(a, t))
            print(line + "  " + tag)

    cells = {}
    for en in [e[0] for e in ERAS] + ["POOLED"]:
        cells[en] = {sh: summarize(pick(out[("RELEVANT", sh)], en)) for sh in (0, 21, -21)}
    plac_ok = all(cells[en][sh][2] is not None and abs(cells[en][sh][2]) < 2.5 for en in [e[0] for e in ERAS] for sh in (21, -21))
    amps = [cells[e[0]][0][1] for e in ERAS]
    ts = [cells[e[0]][0][2] for e in ERAS]
    p = cells["POOLED"][0]
    if not plac_ok:
        verdict = "NO CONCLUSION (a placebo cell failed calibration)"
    elif all(a is not None and a >= 1.05 for a in amps) and all(t is not None and t >= 2.5 for t in ts):
        verdict = "PASS"
    elif p[2] is not None and p[2] >= 2.0 and all(a is not None and a >= 1.0 for a in amps):
        verdict = "LEAD"
    else:
        verdict = "not passed"
    print("\nRELEVANT pooled: %d dates, amplification %s, 95%% interval %s .. %s" % (
        p[0], "n/a" if p[1] is None else "%.3f" % p[1], "n/a" if p[3] is None else "%.3f" % p[3], "n/a" if p[4] is None else "%.3f" % p[4]))
    print("placebo cells clean: %s | VERDICT (pre-set lines): %s" % (plac_ok, verdict))

    def lr(v):
        return math.log((v[0] / v[1]) / (v[2] / v[3]))
    big = sorted(out[("RELEVANT", 0)], key=lambda r: -abs(lr(r[1])))[:8]
    print("\nlargest per-date contrasts, ln(window / baseline) (a few dates should not drive the result):")
    print("  " + ", ".join("%s %+.2f" % (r[0], lr(r[1])) for r in big))

    # descriptive robustness block (added after the first real run; NOT part of the verdict)
    ls = sorted(lr(r[1]) for r in out[("RELEVANT", 0)])
    q = lambda f: ls[int(f * (len(ls) - 1))]
    print("\nper-date ln contrast percentiles (descriptive): 5%% %+.2f | 25%% %+.2f | median %+.2f | 75%% %+.2f | 95%% %+.2f | mean of per-date logs %+.3f" % (
        q(0.05), q(0.25), q(0.5), q(0.75), q(0.95), sum(ls) / len(ls)))
    top = set(r[0] for r in sorted(out[("RELEVANT", 0)], key=lambda r: -abs(lr(r[1])))[:8])
    rest = [(r[1], r[0]) for r in out[("RELEVANT", 0)] if r[0] not in top]
    n2, a2, t2, lo2, hi2 = summarize(rest)
    print("pooled without the 8 largest-|contrast| dates (descriptive): n=%d %s, interval %.3f .. %.3f" % (n2, fmt(a2, t2), lo2, hi2))


if __name__ == "__main__":
    main()
