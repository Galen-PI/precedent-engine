#!/usr/bin/env python3
"""
earnings_surprise_test.py -- READ-ONLY (local matrices; the database is read for quarterly statements, 8-K item 2.02 filings and recorded event days).
Earnings windows hold about 19.5% of all unexplained squared miss on about 3% of stock-days. The band now widens on them, but the SIGN and the SIZE of the reaction are
unknown. There is no analyst consensus in the database, so this uses the standard proxy for a surprise: the year-over-year change in a quarterly figure against that
company's OWN recent trend (a seasonal random walk with drift, standardized).

Usage:   python3 -u scripts/card/earnings_surprise_test.py
Needs:   data_cache/audit_matrices.npz (gap_audit.py builds it). Database: financial_statements (period_type = quarterly), sec_8k_filings, the event tables.

DATA FACTS (from your query results): quarterly rows cover 497 securities from 2006; fiscal Q4 rows carry revenue and net income but NO EPS, so EPS is not used; filed_date is the
10-Q/10-K filing date, which can trail the earnings release by weeks, so each statement is MATCHED to the first 8-K item 2.02 filing after its period end (+3 days) and no later
than 3 days after its filed date.
SURPRISE. For each measure (revenue is the PRIMARY; operating income and net income are reported without a verdict): delta = this quarter minus the same fiscal quarter a year
earlier; surprise = (delta - mean of the previous 8 quarters' deltas) / their standard deviation (at least 6 needed, spread > 0).
OUTCOME. The two-day cumulative chapter-1 miss over day 0 (the first trading day on or after the 2.02 filing date) and day +1, so the unknown filing time does not matter.
Earnings windows that overlap a recorded event day are excluded, as in the earnings test.

PRE-SET RULES (written before the first run).
 SIGN TEST: the sign of the revenue surprise against the sign of the two-day miss. PASSES if, in BOTH 2009-2018 and 2019-2026: >= 800 events, hit rate >= 54%, the 95% Wilson
   interval's lower end > 50%, and a permutation test (surprise signs shuffled within each calendar quarter, 2,000 shuffles) gives p <= 0.05.
 SIZE TEST: earnings windows split into terciles of |revenue surprise| within each calendar quarter. EARNS A PLACE as a band modifier if three tercile scales beat one pooled
   earnings scale (all fit on years BEFORE the test year, a group needs >= 200 prior days) by >= 0.005 nats per earnings stock-day in EACH of 2010-2014, 2015-2019, 2020-2026
   AND the gain is positive in >= 70% of test years.
PREDICTIONS (before the run): the sign hit rate is 51-53% (below the 54% line, so the sign test does not pass); the size test passes, with the high-|surprise| tercile's band
 multiplier at least 1.3x the low tercile's.
"""
import os, sys, math, time, bisect, datetime, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
MEAS = ("revenue", "operating_income", "net_income")
PRIMARY = "revenue"
SIGN_ERAS = [("2009-2018", 2009, 2018), ("2019-2026", 2019, 2100)]
SIZE_ERAS = [("2010-2014", 2010, 2014), ("2015-2019", 2015, 2019), ("2020-2026", 2020, 2100)]
MIN_EVENTS_ERA = 800
SIGN_BAR = 0.54
MIN_PRIOR = 200
MIN_GROUP_QUARTER = 9
PERMS = 2000


def paged(make_query):
    rows, off = [], 0
    while True:
        page = make_query().range(off, off + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return rows


def add_days(d, k):
    return (datetime.date.fromisoformat(str(d)[:10]) + datetime.timedelta(days=k)).isoformat()


def surprises(stmts):
    """For one security's quarterly rows: [(period_end, filed_date, {measure: surprise or None})] in period order."""
    by_fq = {(r["fiscal_year"], r["fiscal_quarter"]): r for r in stmts if r.get("fiscal_year") is not None and r.get("fiscal_quarter") is not None}
    rows = sorted(stmts, key=lambda r: str(r["period_end"]))
    hist = {m: [] for m in MEAS}
    out = []
    for r in rows:
        prev = by_fq.get((r.get("fiscal_year") - 1, r.get("fiscal_quarter"))) if r.get("fiscal_year") is not None and r.get("fiscal_quarter") is not None else None
        sues = {}
        for m in MEAS:
            cur, pv = r.get(m), (prev.get(m) if prev else None)
            if cur is None or pv is None:
                sues[m] = None
                continue
            delta = float(cur) - float(pv)
            h = hist[m][-8:]
            if len(h) >= 6:
                mu = sum(h) / len(h)
                sd = math.sqrt(sum((x - mu) ** 2 for x in h) / (len(h) - 1))
                sues[m] = (delta - mu) / sd if sd > 0 else None
            else:
                sues[m] = None
            hist[m].append(delta)
        out.append((str(r["period_end"])[:10], str(r["filed_date"])[:10], sues))
    return out


def wilson(h, n, z=1.96):
    if n == 0:
        return 0.0, 1.0
    p = h / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    w = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - w, c + w


def main():
    t0 = time.time()
    if not os.path.exists(CACHE_FILE):
        sys.exit("Run gap_audit.py first: it builds %s." % CACHE_FILE)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E, SD = d["dates"], d["ids"], d["E"], d["SD"]
    N, n = E.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = E / SD
    Zsq = Z.astype(np.float64) ** 2
    valid = ~np.isnan(Zsq)
    S = np.nansum(Zsq, axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        Z5 = Zsq / qo
    ok = valid & np.isfinite(Z5) & (qo > 0) & (cnt[None, :] > 20)

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids.tolist())}
    f202 = defaultdict(set)
    EA = np.zeros((N, n), dtype=bool)
    for r in paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").like("item_codes", "%2.02%").order("id")):
        f = str(r["filing_date"])[:10]
        f202[r["security_id"]].add(f)
        k = idx.get(r["security_id"])
        i = bisect.bisect_left(dl, f)
        if k is not None and i < n:
            EA[k, i] = True
            if i + 1 < n:
                EA[k, i + 1] = True
    stm = paged(lambda: sb.table("financial_statements").select("security_id,period_end,fiscal_year,fiscal_quarter,filed_date,revenue,operating_income,net_income")
                .eq("period_type", "quarterly").order("id"))
    by_sec = defaultdict(list)
    for r in stm:
        if r.get("period_end") and r.get("filed_date"):
            by_sec[r["security_id"]].append(r)
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids.tolist()))
    EV = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                EV[k, t] = True

    # match each statement to its earnings release (the first 8-K item 2.02 after the period end) and build the outcome
    used, events = set(), []
    n_stm = n_match = n_out = 0
    for sid, rows in by_sec.items():
        k = idx.get(sid)
        if k is None:
            continue
        flist = sorted(f202.get(sid, []))
        for pe, fd, sues in surprises(rows):
            n_stm += 1
            lo, hi = add_days(pe, 3), add_days(fd, 3)
            cand = [f for f in flist if lo < f <= hi and (sid, f) not in used]
            if not cand:
                continue
            f = cand[0]
            used.add((sid, f))
            n_match += 1
            i = bisect.bisect_left(dl, f)
            if i + 1 >= n or not (ok[k, i] and ok[k, i + 1]) or EV[k, i] or EV[k, i + 1]:
                continue
            C = float(E[k, i]) + float(E[k, i + 1])
            sc = math.sqrt(float(SD[k, i]) ** 2 + float(SD[k, i + 1]) ** 2)
            yr = int(f[:4])
            events.append({"year": yr, "yq": (yr, (int(f[5:7]) - 1) // 3 + 1), "sue": sues, "C": C, "zc": C / sc, "z5": float(Z5[k, i]) + float(Z5[k, i + 1]), "n": 2})
            n_out += 1
    print("statements: %d quarterly rows | matched to an item 2.02 filing: %d (%.0f%%) | with a usable two-day outcome and no recorded event: %d | %.0fs" % (
        n_stm, n_match, 100.0 * n_match / max(n_stm, 1), n_out, time.time() - t0), flush=True)
    for m in MEAS:
        print("  events with a %s surprise: %d" % (m, sum(1 for e in events if e["sue"].get(m) is not None)))

    # ------------------------------------------------------------------ SIGN TEST
    rng = np.random.RandomState(11)
    print("\nSIGN TEST: does the sign of the surprise predict the sign of the two-day miss? (chance-adjusted by shuffling surprises within each calendar quarter)")
    print("  %-18s %-10s %7s %9s %20s %10s %9s" % ("measure", "era", "events", "hit rate", "95% interval", "null mean", "p"))
    sign_pass = {}
    for m in MEAS:
        for era in SIGN_ERAS:
            sel = [e for e in events if era[1] <= e["year"] <= era[2] and e["sue"].get(m) not in (None, 0.0)]
            if len(sel) < 30:
                print("  %-18s %-10s %7d  (too few)" % (m, era[0], len(sel)))
                continue
            pred = np.array([1 if e["sue"][m] > 0 else -1 for e in sel])
            act = np.array([1 if e["C"] > 0 else -1 for e in sel])
            groups = defaultdict(list)
            for j, e in enumerate(sel):
                groups[e["yq"]].append(j)
            gl = [np.array(v) for v in groups.values()]
            hits = int((pred == act).sum())
            nperm = []
            for _ in range(PERMS):
                c = 0
                for g in gl:
                    c += int((rng.permutation(pred[g]) == act[g]).sum())
                nperm.append(c)
            nperm = np.array(nperm)
            pval = float(((nperm >= hits).sum() + 1) / (PERMS + 1))
            lo, hi = wilson(hits, len(sel))
            print("  %-18s %-10s %7d %8.1f%% %9.1f%% - %5.1f%% %9.1f%% %9.3f" % (m + (" *" if m == PRIMARY else ""), era[0], len(sel), 100.0 * hits / len(sel), 100 * lo, 100 * hi,
                                                                              100.0 * nperm.mean() / len(sel), pval))
            if m == PRIMARY:
                sign_pass[era[0]] = (len(sel) >= MIN_EVENTS_ERA and hits / len(sel) >= SIGN_BAR and lo > 0.5 and pval <= 0.05)
    sv = "PASSES" if len(sign_pass) == len(SIGN_ERAS) and all(sign_pass.values()) else "does not pass"
    print("VERDICT, sign test under the pre-set rule (revenue surprise; both eras: >= %d events, hit rate >= %.0f%%, interval lower end > 50%%, p <= 0.05): %s" % (MIN_EVENTS_ERA, 100 * SIGN_BAR, sv))
    print("  CONTROL, like with like: all three surprises scored on the SAME events (those that have all three); post-hoc, no verdict")
    for era in SIGN_ERAS:
        sel = [e for e in events if era[1] <= e["year"] <= era[2] and all(e["sue"].get(x) not in (None, 0.0) for x in MEAS)]
        if len(sel) < 30:
            continue
        act = np.array([1 if e["C"] > 0 else -1 for e in sel])
        groups = defaultdict(list)
        for j, e in enumerate(sel):
            groups[e["yq"]].append(j)
        gl = [np.array(v) for v in groups.values()]
        for m in MEAS:
            pred = np.array([1 if e["sue"][m] > 0 else -1 for e in sel])
            hits = int((pred == act).sum())
            nperm = np.array([sum(int((rng.permutation(pred[g]) == act[g]).sum()) for g in gl) for _ in range(500)])
            pval = float(((nperm >= hits).sum() + 1) / 501)
            lo, hi = wilson(hits, len(sel))
            print("  %-18s %-10s %7d %8.1f%% %9.1f%% - %5.1f%% %9.1f%% %9.3f" % ("same events: " + m[:9], era[0], len(sel), 100.0 * hits / len(sel), 100 * lo, 100 * hi, 100.0 * nperm.mean() / len(sel), pval))
    up = [e["C"] for e in events if (e["sue"].get(PRIMARY) or 0) > 0]
    dn = [e["C"] for e in events if (e["sue"].get(PRIMARY) or 0) < 0]
    if up and dn:
        print("  mean two-day miss when the revenue surprise is positive: %+.2f%% (n=%d); negative: %+.2f%% (n=%d)" % (100 * np.mean(up), len(up), 100 * np.mean(dn), len(dn)))

    # ------------------------------------------------------------------ SIZE TEST
    byq = defaultdict(list)
    for j, e in enumerate(events):
        if e["sue"].get(PRIMARY) is not None:
            byq[e["yq"]].append(j)
    for e in events:
        e["grp"] = None
    for yq, js in byq.items():
        if len(js) < MIN_GROUP_QUARTER:
            continue
        order = sorted(js, key=lambda j: abs(events[j]["sue"][PRIMARY]))
        for r, j in enumerate(order):
            events[j]["grp"] = min(2, int(3 * r / len(order)))
    yrs = sorted({e["year"] for e in events})
    stats = {g: {y: [0.0, 0.0] for y in yrs} for g in (0, 1, 2)}
    for e in events:
        if e["grp"] is not None:
            stats[e["grp"]][e["year"]][0] += e["n"]
            stats[e["grp"]][e["year"]][1] += e["z5"]
    ordinary = ok & ~EA & ~EV
    ord_mean = float(Z5[ordinary].mean())

    def pooled(g, ys):
        nn = sum(stats[g][y][0] for y in ys)
        ss = sum(stats[g][y][1] for y in ys)
        return (ss / nn if nn > 0 else float("nan")), nn

    print("\nSIZE TEST: terciles of |revenue surprise| within each calendar quarter (low / middle / high)")
    print("  calibrated band multiplier vs an ordinary day (all years):  " + "   ".join("%s %.2fx (%d days)" % (nm, math.sqrt(pooled(g, yrs)[0] / ord_mean), pooled(g, yrs)[1]) for g, nm in ((0, "low"), (1, "middle"), (2, "high"))))
    lo_m, hi_m = math.sqrt(pooled(0, yrs)[0] / ord_mean), math.sqrt(pooled(2, yrs)[0] / ord_mean)
    print("  high / low ratio: %.2fx" % (hi_m / lo_m))
    print("  %-34s %10s %10s %10s | years positive" % ("", SIZE_ERAS[0][0], SIZE_ERAS[1][0], SIZE_ERAS[2][0]))
    per_year, era_g, era_n = {}, defaultdict(float), defaultdict(float)
    for Y in [y for y in yrs if y >= SIZE_ERAS[0][1]]:
        pr = [y for y in yrs if y < Y]
        sg = {}
        for g in (0, 1, 2):
            s_, n_ = pooled(g, pr)
            if n_ < MIN_PRIOR or not (s_ > 0):
                sg = None
                break
            sg[g] = s_
        if sg is None:
            continue
        tot_n = sum(pooled(g, pr)[1] for g in (0, 1, 2))
        s_all = sum(pooled(g, pr)[0] * pooled(g, pr)[1] for g in (0, 1, 2)) / tot_n
        gain, nn = 0.0, 0.0
        for g in (0, 1, 2):
            n_t, s_t = stats[g][Y]
            if n_t == 0:
                continue
            gain += (-0.5 * n_t * math.log(sg[g]) - 0.5 * s_t / sg[g]) - (-0.5 * n_t * math.log(s_all) - 0.5 * s_t / s_all)
            nn += n_t
        if nn > 0:
            per_year[Y] = gain / nn
            for era in SIZE_ERAS:
                if era[1] <= Y <= era[2]:
                    era_g[era[0]] += gain
                    era_n[era[0]] += nn
    vals = [(era_g[e[0]] / era_n[e[0]]) if era_n[e[0]] > 0 else None for e in SIZE_ERAS]
    npos = sum(1 for v in per_year.values() if v > 0)
    print("  %-34s %10s %10s %10s | %d of %d" % ("PRIMARY three scales vs one pooled", *["%+.4f" % v if v is not None else "n/a" for v in vals], npos, len(per_year)))
    zv = "EARNS A PLACE" if (len(per_year) >= 8 and all(v is not None and v >= 0.005 for v in vals) and npos / len(per_year) >= 0.70) else "does not earn a place"
    print("VERDICT, size test under the pre-set rule (>= 0.005 nats in each era and >= 70%% of years): %s" % zv)
    print("\nNOTE: a revenue trend surprise is a crude stand-in for the surprise against analyst consensus, which is not in the database; a weak result here does not rule out a consensus surprise.")
    print("      Net income and operating income are reported for shape only (they carry one-off items). The filing time is unknown, which is why the outcome is the two-day sum.")
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
