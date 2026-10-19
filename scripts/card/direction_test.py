#!/usr/bin/env python3
"""
direction_test.py -- READ-ONLY. Does the news-direction label (good / bad, from event_direction_labels) predict the SIGN of the stock's
abnormal return around the event?

Usage:   python3 -u scripts/card/direction_test.py          (works on however many labels exist; a small set is a smoke test only)

OUTCOME. Computed from the closes in event_market_reactions (not from the stored return columns):
  stock return over days 0 and +1 = day_1_close / prior_close - 1;  SPY the same with the spy_* closes;  abnormal = stock - SPY.
  (Self-check: the stored abnormal_return_1d is compared and the agreement is printed.)  Secondary, descriptive: day 0 only, and 5 days.
SAMPLE. Events labeled good or bad (mixed and unclear are excluded and counted), with usable closes (event_market_reactions was repaired
  2026-10-19: one window rule for every row, one row per event and ticker; each label is matched to its OWN ticker's row); THINNED to one event per ticker per
  calendar week (the earliest) so events are not stacked on each other. Eras split at 2019-01-01.
HIT. label good and abnormal > 0, or label bad and abnormal < 0 (events with exactly zero abnormal return are dropped).
PRE-REGISTERED PASS LINE (set before any label existed): in BOTH eras, at least 800 events, hit rate >= 55%, the 95% Wilson interval's
  lower end above 50%, AND the hit rate beats a within-type permutation null (p <= 0.05): labels are shuffled among the events of the same
  event type and era (2,000 shuffles), so a type that is simply 'usually bad' cannot pass on its own. An era with fewer than 800 events
  gets no verdict ('too thin').
Also reported, descriptive only: mean and median abnormal return by label, hit rate by timing (new / previously_announced), by size hint,
  and by event type. THE LABELER'S PROMPT IS FROZEN: no result here may be used to change it.
"""
import os, sys, math, random, datetime
from collections import defaultdict

ERA_SPLIT = "2019-01-01"
MIN_N = 800
B = 2000


def get_sb():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def paged(sb, table, cols, orders):
    rows, off = [], 0
    while True:
        q = sb.table(table).select(cols)
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


def wilson(h, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = h / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)


def ratio(a, b):
    return a / b - 1 if a is not None and b is not None and b > 0 else None


def week_key(d):
    y, w, _ = datetime.date.fromisoformat(str(d)[:10]).isocalendar()
    return "%d-%02d" % (y, w)


def load_events(sb):
    labels = {r["event_id"]: r for r in paged(sb, "event_direction_labels", "event_id,ticker,ptype,event_date,label,size,timing", ["event_id"])}
    ids = [i for i, r in labels.items() if r["label"] in ("good", "bad")]
    react = {}
    for i in range(0, len(ids), 100):
        rows = sb.table("event_market_reactions").select(
            "event_id,ticker,event_date,event_price_date,prior_close,event_close,day_1_close,day_5_close,spy_prior_close,spy_event_close,spy_day1_close,spy_day5_close,abnormal_return_1d,date_was_corrected"
        ).in_("event_id", ids[i:i + 100]).execute().data
        for r in rows:
            react[(r["event_id"], r["ticker"])] = r
    return labels, react


def build_sample(labels, react):
    counts = defaultdict(int)
    for r in labels.values():
        counts[r["label"]] += 1
    rows, no_react, bad_px, off_day = [], 0, 0, 0
    for eid, lab in labels.items():
        if lab["label"] not in ("good", "bad"):
            continue
        r = react.get((eid, lab.get("ticker")))      # this label's own company: a multi-ticker event has one reaction row per ticker
        if not r:
            no_react += 1
            continue
        s1, m1 = ratio(r["day_1_close"], r["prior_close"]), ratio(r["spy_day1_close"], r["spy_prior_close"])
        s0, m0 = ratio(r["event_close"], r["prior_close"]), ratio(r["spy_event_close"], r["spy_prior_close"])
        s5, m5 = ratio(r["day_5_close"], r["prior_close"]), ratio(r["spy_day5_close"], r["spy_prior_close"])
        if s1 is None or m1 is None:
            bad_px += 1
            continue
        d = str(lab.get("event_date") or r.get("event_date"))[:10]
        rows.append({"id": eid, "date": d, "ticker": lab.get("ticker") or r.get("ticker"), "ptype": lab["ptype"], "label": lab["label"],
                     "size": lab.get("size"), "timing": lab.get("timing"), "ar1": s1 - m1,
                     "ar0": (s0 - m0) if s0 is not None and m0 is not None else None,
                     "ar5": (s5 - m5) if s5 is not None and m5 is not None else None, "stored1": r.get("abnormal_return_1d")})
    rows.sort(key=lambda x: (x["date"], x["id"]))
    seen, thin = set(), []
    for x in rows:
        k = (x["ticker"], week_key(x["date"]))
        if k in seen:
            continue
        seen.add(k)
        thin.append(x)
    return counts, rows, thin, no_react, bad_px, off_day


def hits(rows, key="ar1"):
    use = [x for x in rows if x.get(key) is not None and x[key] != 0]
    h = sum(1 for x in use if (x["label"] == "good") == (x[key] > 0))
    return h, len(use), use


def perm_p(use, key="ar1", seed=11):
    rng = random.Random(seed)
    cells = defaultdict(list)
    for x in use:
        cells[(x["ptype"], x["date"] >= ERA_SPLIT)].append(x)
    obs = sum(1 for x in use if (x["label"] == "good") == (x[key] > 0))
    packs = [([x[key] > 0 for x in c], [x["label"] == "good" for x in c]) for c in cells.values()]
    ge, tot_null = 0, 0.0
    for _ in range(B):
        h = 0
        for pos, good in packs:
            g2 = good[:]
            rng.shuffle(g2)
            h += sum(1 for p, g in zip(pos, g2) if p == g)
        ge += h >= obs
        tot_null += h
    return (1 + ge) / (B + 1), tot_null / B


def pct(x):
    return "%5.1f%%" % (100 * x)


def main():
    sb = get_sb()
    labels, react = load_events(sb)
    counts, rows, thin, no_react, bad_px, off_day = build_sample(labels, react)
    print("labels: %d total | by label: %s" % (len(labels), dict(counts)))
    print("good/bad events with no reaction row: %d | excluded for other window problems: %d | unusable closes: %d | usable: %d | after one-per-ticker-per-week: %d" % (no_react, off_day, bad_px, len(rows), len(thin)))
    if not thin:
        print("Nothing to test.")
        return
    comp = [(x["ar1"], x["stored1"]) for x in rows if x["stored1"] is not None]
    if comp:
        diffs = sorted(abs(a - float(b)) for a, b in comp)
        print("self-check against the stored abnormal_return_1d: %d events, median abs difference %.6f, share within 0.001: %.1f%%" % (
            len(diffs), diffs[len(diffs) // 2], 100.0 * sum(1 for d in diffs if d <= 0.001) / len(diffs)))
        if sum(1 for d in diffs if d <= 0.001) / len(diffs) < 0.95:
            print("  WARNING: the stored column is defined differently from (day-1 close / prior close) - SPY; this test uses the closes.")

    print("\nPRIMARY OUTCOME: abnormal return over days 0 and +1")
    verdict = {}
    for era, test in (("2004-2018", lambda d: d < ERA_SPLIT), ("2019-2026", lambda d: d >= ERA_SPLIT)):
        sub = [x for x in thin if test(x["date"])]
        h, n, use = hits(sub)
        if n == 0:
            print("  %s: no events" % era)
            verdict[era] = None
            continue
        lo, hi = wilson(h, n)
        p, nullm = perm_p(use)
        ng, nb = sum(1 for x in use if x["label"] == "good"), sum(1 for x in use if x["label"] == "bad")
        print("  %s: %d events (%d good, %d bad) | hit rate %s [95%% CI %s - %s] | within-type null mean %s, permutation p = %.3f" % (
            era, n, ng, nb, pct(h / n), pct(lo), pct(hi), pct(nullm / n), p))
        if n < MIN_N:
            verdict[era] = "thin"
        else:
            verdict[era] = (h / n >= 0.55 and lo > 0.50 and p <= 0.05)
    vs = [verdict.get("2004-2018"), verdict.get("2019-2026")]
    if any(v is None for v in vs):
        res = "no conclusion (an era has no events)"
    elif any(v == "thin" for v in vs):
        res = "too thin (fewer than %d events in an era): smoke test only, no verdict" % MIN_N
    elif all(vs):
        res = "PASS"
    else:
        res = "not passed"
    print("\nVERDICT under the pre-set line (both eras: >= %d events, hit rate >= 55%%, CI lower end > 50%%, permutation p <= 0.05): %s" % (MIN_N, res))

    print("\nDESCRIPTIVE (thinned sample, all eras)")
    for lab in ("good", "bad"):
        v = sorted(x["ar1"] for x in thin if x["label"] == lab)
        if v:
            print("  %-5s n=%d  mean abnormal return %+.2f%%  median %+.2f%%" % (lab, len(v), 100 * sum(v) / len(v), 100 * v[len(v) // 2]))
    for name, key in (("timing", "timing"), ("size hint", "size")):
        print("  hit rate by %s:" % name)
        grp = defaultdict(list)
        for x in thin:
            grp[x.get(key) or "(none)"].append(x)
        for g, sub in sorted(grp.items(), key=lambda kv: -len(kv[1])):
            h, n, _ = hits(sub)
            if n:
                print("     %-22s n=%-5d hit rate %s" % (g, n, pct(h / n)))
    print("  hit rate by event type (types with >= 25 good/bad events):")
    grp = defaultdict(list)
    for x in thin:
        grp[x["ptype"]].append(x)
    for g, sub in sorted(grp.items(), key=lambda kv: -len(kv[1])):
        h, n, use = hits(sub)
        if n >= 25:
            ng = sum(1 for x in use if x["label"] == "good")
            pos = sum(1 for x in use if x["ar1"] > 0)
            print("     %-26s n=%-5d good %-4d bad %-4d | hit rate %s | share of events with positive abnormal return %s" % (g, n, ng, n - ng, pct(h / n), pct(pos / n)))
    for name, key in (("day 0 only", "ar0"), ("5 days", "ar5")):
        h, n, _ = hits(thin, key)
        if n:
            print("  secondary window %s: n=%d hit rate %s" % (name, n, pct(h / n)))


if __name__ == "__main__":
    main()
