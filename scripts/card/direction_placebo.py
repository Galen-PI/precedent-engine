#!/usr/bin/env python3
"""
direction_placebo.py -- READ-ONLY. Robustness checks on the direction test. POST HOC: these do not change the pre-registered verdict; they ask
whether the result looks like news valence or like something leaking.

Usage:   python3 -u scripts/card/direction_placebo.py

Uses the SAME sample as direction_test.py (same labels, frozen reaction table, systemic_shock excluded, one event per ticker per week).
1. PLACEBO WINDOWS (the placebo that the original pre-registration named: 'labels vs the return sign 25-39 days later'). From event_ripple_timeline
   (cumulative abnormal return from the day -1 close; ~64% of events have a track):
     P1 = days 2..20  = AR[20] - AR[1]     (post-reaction drift)
     P2 = days 26..39 = AR[39] - AR[25]    (far from the event: the clean placebo)
   A label that reads the news should predict days 0-1 and little after. If it predicts P2, it is picking up something that is not the news
   reaction (memory of later outcomes, or persistent type effects). Same hit-rate and within-type permutation machinery as the main test.
2. HIT RATE BY YEAR on the primary outcome (days 0 and +1). A labeler that remembers how famous events turned out would do better on older,
   widely discussed events and worse on events after its training data ends.
3. LIFT OVER THE TYPE BASELINE BY TYPE: for each type, the hit rate expected if the labels carried no information beyond the type's mix of good and bad
   (g x p + (1 - g)(1 - p), with g = share labeled good, p = share with a positive abnormal return) against the actual hit rate.
"""
import os, sys, math
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import direction_test as dt


def fetch_ripple(sb, ids):
    out = defaultdict(dict)
    warn = 0
    for i in range(0, len(ids), 100):
        rows = sb.table("event_ripple_timeline").select("event_id,ticker,day_offset,abnormal_return") \
            .in_("event_id", ids[i:i + 100]).in_("day_offset", [1, 20, 25, 39]).execute().data
        if len(rows) >= 1000:
            warn += 1
        for r in rows:
            if r.get("abnormal_return") is not None:
                out[(r["event_id"], r["ticker"])][int(r["day_offset"])] = float(r["abnormal_return"])
    if warn:
        print("WARNING: %d request(s) returned 1,000 rows (possible truncation)" % warn)
    return out


def report(name, sub, key):
    for era, test in (("2004-2018", lambda d: d < dt.ERA_SPLIT), ("2019-2026", lambda d: d >= dt.ERA_SPLIT), ("all", lambda d: True)):
        s = [x for x in sub if test(x["date"])]
        h, n, use = dt.hits(s, key)
        if n < 30:
            print("  %-34s %-10s n=%d (too few)" % (name, era, n))
            continue
        lo, hi = dt.wilson(h, n)
        p, nullm = dt.perm_p(use, key)
        print("  %-34s %-10s n=%-5d hit rate %s [%s - %s] | within-type null %s | permutation p = %.3f" % (
            name, era, n, dt.pct(h / n), dt.pct(lo), dt.pct(hi), dt.pct(nullm / n), p))


def main():
    sb = dt.get_sb()
    labels, react = dt.load_events(sb)
    counts, rows, thin, no_react, bad_px, off_day = dt.build_sample(labels, react)
    print("same sample as the main test: %d events after thinning" % len(thin))
    rip = fetch_ripple(sb, [x["id"] for x in thin])
    have = 0
    for x in thin:
        r = rip.get((x["id"], x["ticker"]), {})
        x["p1"] = (r[20] - r[1]) if 20 in r and 1 in r else None
        x["p2"] = (r[39] - r[25]) if 39 in r and 25 in r else None
        have += x["p2"] is not None
    print("events with a ripple track covering days 25 and 39: %d (%.0f%%)\n" % (have, 100.0 * have / max(1, len(thin))))

    print("1. HIT RATE vs the same labels (good = up, bad = down); the within-type null absorbs the type mix")
    report("primary: days 0 and +1", thin, "ar1")
    report("P1 post-reaction drift: days 2-20", thin, "p1")
    report("P2 placebo: days 26-39", thin, "p2")

    print("\n2. PRIMARY OUTCOME BY YEAR (hit rate; n)")
    by = defaultdict(list)
    for x in thin:
        by[x["date"][:4]].append(x)
    line = []
    for y in sorted(by):
        h, n, _ = dt.hits(by[y], "ar1")
        if n >= 20:
            line.append("%s %.0f%% (%d)" % (y, 100.0 * h / n, n))
    for i in range(0, len(line), 6):
        print("  " + " | ".join(line[i:i + 6]))

    print("\n3. LIFT OVER THE TYPE BASELINE, BY TYPE (types with >= 40 good/bad events; baseline = g*p + (1-g)*(1-p))")
    print("  %-26s %6s %6s %6s %9s %9s %8s" % ("type", "n", "good%", "up%", "baseline", "actual", "lift"))
    grp = defaultdict(list)
    for x in thin:
        grp[x["ptype"]].append(x)
    for g, sub in sorted(grp.items(), key=lambda kv: -len(kv[1])):
        h, n, use = dt.hits(sub, "ar1")
        if n >= 40:
            gd = sum(1 for x in use if x["label"] == "good") / n
            pp = sum(1 for x in use if x["ar1"] > 0) / n
            base = gd * pp + (1 - gd) * (1 - pp)
            print("  %-26s %6d %5.0f%% %5.0f%% %8.1f%% %8.1f%% %+7.1f" % (g, n, 100 * gd, 100 * pp, 100 * base, 100.0 * h / n, 100 * (h / n - base)))
    print("\nREAD: P2 should sit near its within-type null. A hit rate well above it would mean the labels carry information beyond the news reaction.")


if __name__ == "__main__":
    main()
