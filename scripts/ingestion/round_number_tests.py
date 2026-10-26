#!/usr/bin/env python3
"""
round_number_tests.py -- the TWO REGISTERED round-number tests (results/PREREG_round_number_2026-10-26.md): (1) clustering of closes: the whole-dollar ratio against the 80 cents values that are not multiples of 5; (2) behaviour near round thresholds: next-day z (stock_day_z) after a close within 1% of a round threshold k x 10 (k = 2..9, previous close $10 to $100) against the two placebo neighbours at +-27% of the spacing. READ-ONLY. Every rule below is the registered one.
USE RULE: closes from 2001-06-01, tickers with status valid (rule_version since_2001-06-01), each from its valid_from. ERAS: A before 2014-01-01, B from 2014-01-01; test 2 uses only outcome days from 2004-01-01 (stock_day_z starts there) and drops the days in BAD_DAYS (the days with fewer than 100 stocks; a PRE-FLIGHT check asks the database and stops if any of them has 100 stocks or more).
STOPS (registered): if the cents filter drops more than 3% of the closes of $10 and above in an era, nothing is reported; the share of test-2 zone-days with no z value (after 2004, not a bad day) is printed first.
INFERENCE: bootstrap over TICKERS (whole tickers resampled), --boot resamples (2,000 registered; secondary statistics 500). SAFE TO INTERRUPT: each ticker's counts go to data_cache/round_tests_cache.jsonl and a rerun resumes (--fresh ignores the cache).
Usage:   scripts/ops/bg.sh roundtests python3 -u scripts/ingestion/round_number_tests.py
"""
import os, sys, math, json, argparse, collections, random, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_asquoted_accuracy as C
import round_number_counts as RC

BAD_DAYS = {"2009-07-26", "2016-02-27", "2024-05-27", "2025-12-25"}
ZSTART = "2004-01-01"
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data_cache", "round_tests_cache.jsonl")
BASE = [c for c in range(100) if c % 5]
OTHER5 = [c for c in range(0, 100, 5) if c not in (0, 25, 50, 75)]
CBUCKETS = [(5, 10, "$5-10"), (10, 20, "$10-20"), (20, 50, "$20-50"), (50, 100, "$50-100"), (100, 250, "$100-250"), (250, 1e12, "$250-up")]
KS = list(range(2, 10))
KINDS = RC.KINDS
POS = {}
for _e in ("A", "B"):
    for _k in KS:
        for _kind in KINDS:
            POS[(_e, _k, _kind)] = len(POS) * 2
VLEN = len(POS) * 2


def cbucket(p):
    for lo, hi, name in CBUCKETS:
        if lo <= p < hi:
            return name
    return None


def process_ticker(sb, sec, valid_from):
    stored = [(str(r["price_date"])[:10], float(r["adjusted_close"])) for r in C.paged(sb, "market_prices", "price_date,adjusted_close", "price_date", lambda q: q.eq("security_id", sec["id"])) if r.get("adjusted_close")]
    fac = [(str(r["effective_date"])[:10], float(r["ratio"])) for r in C.paged(sb, "price_adjustment_factors", "effective_date,ratio", "effective_date", lambda q: q.eq("security_id", sec["id"]))]
    allc = C.asquoted(stored, fac)
    start = max(RC.SINCE, str(valid_from)[:10]) if valid_from else RC.SINCE
    closes = [(d, p) for d, p in allc if d >= start and p >= 1.0]
    zrows = {str(r["day"])[:10]: float(r["z"]) for r in C.paged(sb, "stock_day_z", "day,z", "day", lambda q: q.eq("security_id", sec["id"])) if r.get("z") is not None}
    rec = {"ticker": sec["ticker"], "cents": {"A": [0] * 100, "B": [0] * 100}, "n10": {"A": 0, "B": 0}, "drop10": {"A": 0, "B": 0}, "bk": {}, "z": {}, "zy": {}, "zdays": {"A": 0, "B": 0}, "zbad": 0, "zmiss": 0}
    for d, p in closes:
        e = RC.era(d)
        b = cbucket(p)
        if b is None:
            continue
        ok = C.dpenny(p) <= C.TOLC
        if p >= 10:
            rec["n10"][e] += 1
            if not ok:
                rec["drop10"][e] += 1
        if not ok:
            continue
        c = int(round(p * 100)) % 100
        if p >= 10:
            rec["cents"][e][c] += 1
        cell = rec["bk"].setdefault(e + "|" + b, [0, 0, 0, 0, 0])
        if c == 0: cell[0] += 1
        elif c == 50: cell[1] += 1
        elif c in (25, 75): cell[2] += 1
        elif c % 5 == 0: cell[3] += 1
        else: cell[4] += 1
    for i in range(1, len(closes)):
        P = closes[i - 1][1]
        t = closes[i][0]
        if not (10 <= P < 100) or t < ZSTART:
            continue
        zs = [(kind, k) for kind, k in RC.zones(P) if 2 <= k <= 9]
        if not zs:
            continue
        e = RC.era(t)
        rec["zdays"][e] += 1
        if t in BAD_DAYS:
            rec["zbad"] += 1
            continue
        z = zrows.get(t)
        if z is None:
            rec["zmiss"] += 1
            continue
        for kind, k in zs:
            for key, dct in (("%s|%d|%s" % (e, k, kind), rec["z"]), ("%s|%d|%s" % (t[:4], k, kind), rec["zy"])):
                v = dct.setdefault(key, [0, 0.0]); v[0] += 1; v[1] += z
    return rec


def cents_ratios(v):
    nb = sum(v[c] for c in BASE)
    if nb == 0:
        return None
    m = nb / 80.0
    return {"c0": v[0] / m, "c50": v[50] / m, "c2575": (v[25] + v[75]) / 2.0 / m, "other5": sum(v[c] for c in OTHER5) / 16.0 / m, "n": sum(v), "base": nb}


def bucket_ratios(cell):
    nb = cell[4]
    if nb == 0:
        return None
    m = nb / 80.0
    return {"c0": cell[0] / m, "c50": cell[1] / m, "c2575": cell[2] / 2.0 / m, "other5": cell[3] / 16.0 / m}


def pct(sorted_vals, q):
    return sorted_vals[min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))]


def boot_vectors(vectors, B, rng):
    n = len(vectors); L = len(vectors[0])
    for _ in range(B):
        acc = [0] * L
        for _ in range(n):
            acc = [a + b for a, b in zip(acc, vectors[rng.randrange(n)])]
        yield acc


def zvec(rec):
    v = [0.0] * VLEN
    for key, (n, s) in rec["z"].items():
        e, k, kind = key.split("|"); i = POS.get((e, int(k), kind))
        if i is not None:
            v[i] += n; v[i + 1] += s
    return v


def zget(vec, e, k, kind):
    i = POS[(e, k, kind)]
    return vec[i], vec[i + 1]


def mean_of(vec, e, k, kinds):
    n = sum(zget(vec, e, k, kk)[0] for kk in kinds); s = sum(zget(vec, e, k, kk)[1] for kk in kinds)
    return (s / n) if n else None


def estimates(vec, e, w, side=None):
    """pooled ln RHO and pooled placebo contrast for one era from a summed vector; w = weights by k (fixed); side None, 'below' or 'above'"""
    Rk = ["R_" + side] if side else ["R_below", "R_above"]
    P27 = ["P27_" + side] if side else ["P27_below", "P27_above"]
    P73 = ["P73_" + side] if side else ["P73_below", "P73_above"]
    num = den = cnum = cden = 0.0
    for k in KS:
        r, a, b = mean_of(vec, e, k, Rk), mean_of(vec, e, k, P27), mean_of(vec, e, k, P73)
        if r is None or a is None or b is None or r <= 0 or a <= 0 or b <= 0:
            continue
        num += w[k] * math.log(r / ((a + b) / 2.0)); den += w[k]
        cnum += w[k] * math.log(a / b); cden += w[k]
    return (num / den if den else None), (cnum / cden if cden else None)


def run_tests(recs, boot, seed, out=print):
    rng = random.Random(seed)
    res = {}
    for e in ("A", "B"):
        n10 = sum(r["n10"][e] for r in recs); d10 = sum(r["drop10"][e] for r in recs)
        if n10 and d10 / float(n10) > 0.03:
            raise SystemExit("STOP: the cents filter drops %.1f%% of the era %s closes of $10 and above (registered limit 3%%); read the loss first" % (100.0 * d10 / n10, e))
    zd = {e: sum(r["zdays"][e] for r in recs) for e in ("A", "B")}
    zm = sum(r["zmiss"] for r in recs); zb = sum(r["zbad"] for r in recs)
    out("TEST-2 DATA CHECK: zone-days (outcome day from 2004, class s10, k 2..9): era A %d, era B %d; dropped on bad days %d; no z value %d (%.2f%% of all)" % (zd["A"], zd["B"], zb, zm, 100.0 * zm / max(1, zd["A"] + zd["B"])))
    out("CENTS FILTER: closes of $10 and above dropped as not cent-exact: era A %.2f%%, era B %.2f%%" % tuple(100.0 * sum(r["drop10"][e] for r in recs) / max(1, sum(r["n10"][e] for r in recs)) for e in ("A", "B")))
    looked = 0
    out("\n=== TEST 1: CLUSTERING OF CLOSES (closes of $10 and above, cent-exact) ===")
    per_era = {}
    for e in ("A", "B"):
        vecs = [r["cents"][e] for r in recs]
        tot = [sum(col) for col in zip(*vecs)]
        pt = cents_ratios(tot)
        boots = [cents_ratios(v) for v in boot_vectors(vecs, boot, rng)]
        boots = [b for b in boots if b]
        se = {k: statistics.pstdev([b[k] for b in boots]) for k in ("c0", "c50", "c2575", "other5")}
        iv = {k: (pct(sorted(b[k] for b in boots), 0.025), pct(sorted(b[k] for b in boots), 0.975)) for k in ("c0", "c50", "c2575", "other5")}
        m = pt["base"] / 80.0
        cov, absz = 0, []
        cb = {}
        for v in boot_vectors(vecs, max(200, boot // 4), rng):
            nb = sum(v[c] for c in BASE)
            if nb:
                for c in BASE:
                    cb.setdefault(c, []).append(v[c] / (nb / 80.0))
        for c in BASE:
            r = tot[c] / m; xs = sorted(cb[c]); lo, hi = pct(xs, 0.025), pct(xs, 0.975); s = statistics.pstdev(xs)
            cov += (lo <= 1.0 <= hi); absz.append(abs(r - 1.0) / s if s else 0.0)
        share = cov / 80.0
        omega = max(1.0, pct(sorted(absz), 0.95) / 1.96) if share < 0.90 else 1.0
        per_era[e] = (pt, se, iv, share, omega)
        looked += 4 + 80
        out("ERA %s: closes %d | CALIBRATION: %.0f%% of the 80 plain cents have an interval containing 1.0%s" % (e, pt["n"], 100 * share, "" if omega == 1.0 else " -> every interval widened by x%.2f" % omega))
        for k, nm in (("c0", "whole dollars (c=00)  PRIMARY"), ("c50", "halves (c=50)"), ("c2575", "quarters (c=25, 75)"), ("other5", "other multiples of 5")):
            lo, hi = iv[k]; wlo = pt[k] - omega * (pt[k] - lo); whi = pt[k] + omega * (hi - pt[k])
            out("   %-30s ratio %.3f  SE %.3f  95%% [%.3f, %.3f]%s" % (nm, pt[k], se[k], wlo, whi, "" if omega == 1.0 else " (widened)"))
    ok_pass = all(per_era[e][0]["c0"] >= 1.05 and per_era[e][0]["c0"] - per_era[e][4] * (per_era[e][0]["c0"] - per_era[e][2]["c0"][0]) >= 1.03 for e in ("A", "B"))
    ok_lead = all(per_era[e][0]["c0"] - per_era[e][4] * (per_era[e][0]["c0"] - per_era[e][2]["c0"][0]) > 1.00 for e in ("A", "B"))
    res["test1"] = "PASS" if ok_pass else "LEAD" if ok_lead else "NULL"
    out("TEST 1 VERDICT: %s (pass needs ratio >= 1.05 with a lower bound >= 1.03 in BOTH eras; lead = lower bound above 1.00 in both)" % res["test1"])
    out("   secondary, by price bucket (descriptive; %d resamples): whole-dollar ratio and 95%% interval" % min(boot, 500))
    for e in ("A", "B"):
        for lo_, hi_, nm in CBUCKETS:
            cells = [r["bk"].get(e + "|" + nm, [0, 0, 0, 0, 0]) for r in recs]
            tot = [sum(col) for col in zip(*cells)]; pr = bucket_ratios(tot)
            if not pr or tot[4] < 400:
                continue
            bs = [bucket_ratios(v) for v in boot_vectors(cells, min(boot, 500), rng)]; xs = sorted(b["c0"] for b in bs if b)
            looked += 1
            out("   era %s %-9s c0 ratio %.3f [%.3f, %.3f]  c50 %.3f  c25/75 %.3f  (baseline closes %d)" % (e, nm, pr["c0"], pct(xs, 0.025), pct(xs, 0.975), pr["c50"], pr["c2575"], tot[4]))
    out("\n=== TEST 2: BEHAVIOUR NEAR ROUND THRESHOLDS (previous close $10-$100, k = 2..9, outcome z on the next day) ===")
    vecs = [zvec(r) for r in recs]
    tot = [sum(col) for col in zip(*vecs)]
    summary = {}
    for e in ("A", "B"):
        w = {k: sum(zget(tot, e, k, kk)[0] for kk in ("R_below", "R_above")) for k in KS}
        est, con = estimates(tot, e, w)
        be = []
        for v in boot_vectors(vecs, boot, rng):
            a, b = estimates(v, e, w)
            if a is not None and b is not None:
                be.append((a, b))
        sa = statistics.pstdev([a for a, _ in be]); sb_ = statistics.pstdev([b for _, b in be])
        xs = sorted(a for a, _ in be)
        ys = collections.defaultdict(lambda: [0.0] * VLEN)
        for r in recs:
            for key, (n, s) in r["zy"].items():
                yr, k, kind = key.split("|")
                if (yr < "2014") == (e == "A"):
                    i = POS[(e, int(k), kind)]
                    ys[yr][i] += n; ys[yr][i + 1] += s
        signs = []
        for yr, v in sorted(ys.items()):
            a, _ = estimates(v, e, w)
            if a is not None:
                signs.append(1 if a > 0 else -1 if a < 0 else 0)
        cons = (sum(1 for s in signs if s == (1 if est > 0 else -1)) / float(len(signs))) if signs else 0.0
        summary[e] = {"est": est, "t": est / sa if sa else 0.0, "con": con, "tcon": con / sb_ if sb_ else 0.0, "cons": cons}
        looked += 8
        out("ERA %s: round zone-days %d | ESTIMATE ln RHO %+.4f (SE %.4f, t %+.2f) = %+.2f%% in mean z, 95%% [%+.2f%%, %+.2f%%] | PLACEBO contrast ln(P27/P73) %+.4f (t %+.2f) | year consistency %.0f%% of %d years" % (e, sum(w.values()), est, sa, summary[e]["t"], 100 * (math.exp(est) - 1), 100 * (math.exp(pct(xs, 0.025)) - 1), 100 * (math.exp(pct(xs, 0.975)) - 1), con, summary[e]["tcon"], 100 * cons, len(signs)))
        for side in ("below", "above"):
            a, c = estimates(tot, e, w, side)
            looked += 1
            out("   descriptive, %s zones only: ln RHO %s" % (side, "n/a" if a is None else "%+.4f" % a))
    sg = (summary["A"]["est"] > 0) == (summary["B"]["est"] > 0)
    clean = all(abs(summary[e]["tcon"]) < 2.5 for e in ("A", "B"))
    cons_ok = all(summary[e]["cons"] >= 0.70 for e in ("A", "B"))
    pass_ = sg and all(abs(summary[e]["t"]) >= 2.5 for e in ("A", "B")) and clean and cons_ok
    lead = sg and all(abs(summary[e]["t"]) >= 2.0 for e in ("A", "B")) and clean
    res["test2"] = "PASS" if pass_ else "LEAD" if lead else "NULL"
    out("TEST 2 VERDICT: %s (pass needs the same sign in both eras with |t| >= 2.5, a clean placebo contrast |t| < 2.5, and the era's sign in at least 70%% of years; lead = |t| >= 2.0 in both with a clean placebo)" % res["test2"])
    out("\nDESCRIPTIVE STATISTICS LOOKED AT (for the ledger): %d" % looked)
    return res


def main(argv=None, sb=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261026)
    a = ap.parse_args(argv)
    if sb is None:
        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    vf = C.paged(sb, "asquoted_levels_valid_from", "security_id,ticker,status,valid_from,rule_version", "ticker", lambda q: q.eq("rule_version", "since_2001-06-01"))
    usable = [r for r in vf if r["status"] == "valid"]
    secs = {s["id"]: s for s in C.paged(sb, "securities", "id,ticker", "ticker", lambda q: q)}
    cache = {}
    if not a.fresh and os.path.exists(CACHE_FILE):
        for line in open(CACHE_FILE):
            try:
                r = json.loads(line); cache[r["ticker"]] = r
            except ValueError:
                pass
    for d in sorted(BAD_DAYS):
        n = len(C.paged(sb, "stock_day_z", "day", "day", lambda q: q.eq("day", d)))
        print("PRE-FLIGHT guard day %s: %d stocks in stock_day_z (a stray day has fewer than 100)" % (d, n), flush=True)
        if n >= 100:
            raise SystemExit("STOP: %s has %d stocks in stock_day_z, so it is not a stray day; the BAD_DAYS list is wrong (fix it before any run: the cache would be poisoned)" % (d, n))
    todo = [r for r in usable if r["ticker"] not in cache]
    print("usable tickers %d | already processed %d | to process %d" % (len(usable), len(usable) - len(todo), len(todo)), flush=True)
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "a") as fh:
        for i, r in enumerate(todo):
            if i % 10 == 0:
                print("PROGRESS %d/%d" % (i + len(usable) - len(todo), len(usable)), flush=True)
            rec = process_ticker(sb, secs[r["security_id"]], r["valid_from"])
            cache[r["ticker"]] = rec
            fh.write(json.dumps(rec) + "\n"); fh.flush()
    print("PROGRESS %d/%d" % (len(usable), len(usable)), flush=True)
    recs = [cache[r["ticker"]] for r in usable]
    return run_tests(recs, a.boot, a.seed)


if __name__ == "__main__":
    main()
