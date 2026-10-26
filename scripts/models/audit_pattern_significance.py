#!/usr/bin/env python3
"""
audit_pattern_significance.py -- READ-ONLY AUDIT of pattern_significance_tests (written 2026-10-26). test_pattern_significance.py compares every tag with an EVEN 25/25/25/25 split over muted / punished / rewarded / diverged_from_fundamentals; the overall mix of all tagged events is nowhere near even (2026-10-26: muted 39.8%, punished 22.8%, rewarded 22.9%, diverged 14.5% of 15,952 events), so a typical tag looks 'significant' against it. This script redoes the test for every stored tag against the OVERALL mix: chi-square (3 df), an EXACT multinomial test where n <= 100 (small expected counts), a Holm adjustment across the tags; a tag SURVIVES only if its Holm p is below 0.05. It is an audit of earlier results and creates no flag.
Usage:   python3 scripts/models/audit_pattern_significance.py --overall muted=6349,punished=3644,rewarded=3652,diverged=2307
(the overall counts: SELECT t.name, COUNT(DISTINCT et.event_id) FROM event_tags et JOIN tags t ON t.id = et.tag_id WHERE t.name IN ('rewarded','punished','muted','diverged_from_fundamentals') GROUP BY 1)
"""
import os, sys, math, argparse

ORDER = ["muted", "punished", "rewarded", "diverged"]


def chi_sf3(x):
    return math.erfc(math.sqrt(x / 2.0)) + math.sqrt(2.0 * x / math.pi) * math.exp(-x / 2.0) if x > 0 else 1.0


def chi2(obs, probs):
    n = sum(obs)
    return sum((o - n * p) ** 2 / (n * p) for o, p in zip(obs, probs))


def logmult(obs, probs):
    n = sum(obs)
    return math.lgamma(n + 1) - sum(math.lgamma(o + 1) for o in obs) + sum(o * math.log(p) for o, p in zip(obs, probs))


def exact_p(obs, probs):
    n = sum(obs); lo = logmult(obs, probs) + 1e-9; tot = 0.0
    for a in range(n + 1):
        for b in range(n - a + 1):
            for c in range(n - a - b + 1):
                lp = logmult((a, b, c, n - a - b - c), probs)
                if lp <= lo:
                    tot += math.exp(lp)
    return min(1.0, tot)


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); out = [None] * len(ps); running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i])); out[i] = running
    return out


def audit(rows, overall, out=print):
    N = float(sum(overall[k] for k in ORDER)); P = [overall[k] / N for k in ORDER]
    res = []
    for r in rows:
        obs = (r["muted_count"], r["punished_count"], r["rewarded_count"], r["diverged_from_fundamentals_count"]); n = sum(obs)
        p_even = chi_sf3(chi2(obs, [0.25] * 4))
        p_chi = chi_sf3(chi2(obs, P))
        res.append({"tag": r["tag_name"], "n": n, "p_even": p_even, "p_chi": p_chi, "p": exact_p(obs, P) if n <= 100 else p_chi, "kind": "exact" if n <= 100 else "chi2", "old": bool(r.get("is_significant"))})
    h = holm([x["p"] for x in res])
    out("overall mix of %d tagged events: %s" % (N, "  ".join("%s %.1f%%" % (k, 100 * p) for k, p in zip(ORDER, P))))
    for x, hp in zip(res, h):
        x["holm"] = hp
        out("%-30s n %4d  p vs even %-9.2g  p vs overall mix %-8.3g (%s)  Holm %-6.3g %s%s" % (x["tag"], x["n"], x["p_even"], x["p"], x["kind"], hp, "OLD-SIGNIFICANT " if x["old"] else "", "SURVIVES" if hp < 0.05 else ""))
    out("old significant: %d of %d | raw p < .05 against the overall mix: %d | Holm p < .05: %d" % (sum(x["old"] for x in res), len(res), sum(x["p"] < 0.05 for x in res), sum(x["holm"] < 0.05 for x in res)))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--overall", required=True)
    a = ap.parse_args()
    overall = {k: int(v) for k, v in (kv.split("=") for kv in a.overall.split(","))}
    if sorted(overall) != sorted(ORDER):
        raise SystemExit("--overall needs muted=, punished=, rewarded=, diverged=")
    from supabase import create_client
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    rows = sb.table("pattern_significance_tests").select("tag_name,n,muted_count,punished_count,rewarded_count,diverged_from_fundamentals_count,is_significant").execute().data
    audit(rows, overall)
