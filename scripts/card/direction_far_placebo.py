#!/usr/bin/env python3
"""
direction_far_placebo.py -- READ-ONLY (database: labels and the frozen reaction snapshot; local price cache). The far placebo for the direction labels,
for ALL sampled events (the ripple-timeline version covered only 538).

Usage:   python3 -u scripts/card/direction_far_placebo.py        (needs data_cache/returns, the same cache as the validation scripts)

Same sample as direction_test.py (labels good/bad, systemic_shock excluded, one event per ticker per week, frozen reaction table). R = the event's
reaction day (event_price_date in the frozen table). All windows are cumulative abnormal returns (stock minus SPY on the SAME dates, adjusted closes):
  P1 = R+1 -> R+20   (days 2-20, post-reaction drift)          [consistency check against the earlier ripple-based result: 49.7% vs null 50.0%]
  P2 = R+25 -> R+39  (days 26-39: the pre-registered far placebo)
  P3 = R+39 -> R+59  (days 40-59: a second far window, descriptive)
Same hit rate (good = up, bad = down) and the same within-type, within-era permutation null as the main test.

PRE-SET RULE (written before the first run; P2 is the primary):
  The placebo is FLAGGED if, in EITHER era (2004-2018, 2019-2026), P2's hit rate beats its within-type null with a permutation p <= 0.025
  (Bonferroni over the two eras, about 5% overall false-alarm rate if the labels carry nothing at that distance). Otherwise it is CLEAN.
  A FLAGGED placebo means the labels carry information beyond the news reaction (outcome memory, or persistent effects), and the pass of the main
  direction test should not be trusted as news-reading. CLEAN does not prove the labeler is free of memory (it can remember short-run reactions);
  it says the labels do not predict windows far from the event.
Events too recent to have a full window (the cache ends at its last price date) are dropped and counted.
"""
import os, sys, glob, pickle
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import direction_test as dt

CACHE = "data_cache/returns"


def load_prices():
    out = {}
    for f in glob.glob(os.path.join(CACHE, "*.pkl")):
        if f.endswith("_macro.pkl"):
            continue
        with open(f, "rb") as fh:
            s = pickle.load(fh)
        out[s["ticker"]] = {"dates": s["dates"], "adj": s["adj"], "pos": {d: i for i, d in enumerate(s["dates"])}}
    return out


def window_ar(stock, spy, i0, i1):
    if i0 < 0 or i1 >= len(stock["dates"]):
        return None
    d0, d1 = stock["dates"][i0], stock["dates"][i1]
    j0, j1 = spy["pos"].get(d0), spy["pos"].get(d1)
    if j0 is None or j1 is None or stock["adj"][i0] <= 0 or spy["adj"][j0] <= 0:
        return None
    return (stock["adj"][i1] / stock["adj"][i0] - 1) - (spy["adj"][j1] / spy["adj"][j0] - 1)


def report(name, sub, key):
    res = {}
    for era, test in (("2004-2018", lambda d: d < dt.ERA_SPLIT), ("2019-2026", lambda d: d >= dt.ERA_SPLIT), ("all", lambda d: True)):
        s = [x for x in sub if test(x["date"])]
        h, n, use = dt.hits(s, key)
        if n < 30:
            print("  %-34s %-10s n=%d (too few)" % (name, era, n))
            continue
        lo, hi = dt.wilson(h, n)
        p, nullm = dt.perm_p(use, key)
        res[era] = (p, h / n - nullm / n, n)
        print("  %-34s %-10s n=%-5d hit rate %s [%s - %s] | within-type null %s | excess %+.1f pts | permutation p = %.3f" % (
            name, era, n, dt.pct(h / n), dt.pct(lo), dt.pct(hi), dt.pct(nullm / n), 100 * (h / n - nullm / n), p))
    return res


def main():
    sb = dt.get_sb()
    labels, react = dt.load_events(sb)
    counts, rows, thin, no_react, bad_px, off_day = dt.build_sample(labels, react)
    px = load_prices()
    spy = px.get("SPY")
    if not spy:
        sys.exit("SPY is not in the price cache.")
    dropped = 0
    for x in thin:
        r = react.get((x["id"], x["ticker"]), {})
        st = px.get(x["ticker"])
        i = st["pos"].get(str(r.get("event_price_date"))[:10]) if st else None
        x["pf1"] = x["pf2"] = x["pf3"] = None
        if st is None or i is None:
            dropped += 1
            continue
        x["pf1"] = window_ar(st, spy, i + 1, i + 20)
        x["pf2"] = window_ar(st, spy, i + 25, i + 39)
        x["pf3"] = window_ar(st, spy, i + 39, i + 59)
    have = sum(1 for x in thin if x["pf2"] is not None)
    print("same sample as the main test: %d events | with a full days 26-39 window from the cache: %d | not in the cache or too recent: %d\n" % (len(thin), have, len(thin) - have))

    print("HIT RATE (good = up, bad = down); the within-type null absorbs the type mix")
    report("primary: days 0 and +1", thin, "ar1")
    report("P1 post-reaction: days 2-20", thin, "pf1")
    p2 = report("P2 FAR PLACEBO: days 26-39", thin, "pf2")
    report("P3 second far window: days 40-59", thin, "pf3")

    flagged = [era for era in ("2004-2018", "2019-2026") if era in p2 and p2[era][0] <= 0.025 and p2[era][1] > 0]
    print("\nVERDICT under the pre-set rule (P2 beats its null with p <= 0.025 in either era = FLAGGED): %s" % (
        "FLAGGED in " + ", ".join(flagged) if flagged else ("CLEAN" if all(e in p2 for e in ("2004-2018", "2019-2026")) else "no verdict (an era is missing)")))


if __name__ == "__main__":
    main()
