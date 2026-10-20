#!/usr/bin/env python3
"""
event_center_test.py -- READ-ONLY (local cache; the database is read for the event list and the direction labels).
Chapter 3, CENTER: on days with the stock's own event, does the labeler's good / bad / mixed / unclear add a signed pull to chapter 1's miss,
BEYOND what the event type alone gives, judged on years the pull was never fit on?

Usage:
    python3 -u scripts/card/event_center_test.py --limit 40 --stride 5     (trial)
    python3 -u scripts/card/event_center_test.py                           (full run)

SETUP (as in event_width_test.py). Chapter 1 = each stock's market + sector fit over the last 250 valid days, giving a miss e1 for every stock-day.
An EVENT DAY is day 0 or day +1 of one of the stock's own events (ev_ent; a non-trading date snaps to the next trading day); if two events share a
day the first by event_id supplies the type and label, day 0 beats day +1. Only event days whose event HAS a label are used. Walk-forward: every
pull is fit on years BEFORE the test year and scored on the test year (test years 2005 on). A 'pull' is a predicted miss, in return units.
MODELS (each predicts the miss e1 on an event day; score = squared miss; day offset 0 or +1 is always part of the cell):
  Z  = zero (chapter 1 alone).
  T0 = the mean miss of prior event days of the same TYPE and offset (a cell needs >= 100 prior days, else the mean of all prior event days at that offset).
  C2 = the mean miss of prior event days of the same TYPE, LABEL and offset, shrunk toward the T0 pull: (n x cell mean + 100 x T0 pull) / (n + 100).
       If the labels carry no information beyond the type, C2 is about T0; so C2 versus T0 is the label's own contribution.
SCORE: gain = 1 - (sum of squared misses after the model) / (sum before), over event days.
PRE-SET CLASSIFICATION (written before the first run), for the primary comparison C2 versus T0:
  EARNS ITS PLACE  = gain >= 0.5% in EACH of 2005-2012, 2013-2019, 2020-2026 AND positive in >= 70% of test years.
  TILT ONLY        = gain > 0 in each era and positive in >= 70% of test years, but below 0.5% in at least one era.
  DOES NOT         = anything else.
Also reported, descriptive: T0 versus Z (does the type alone give a signed pull?), C2 versus Z, the gain restricted to days labeled good or bad, and the
calibrated mean miss by label, by day, and by type and label.
PREDICTIONS (before the run): the direction test found a modest lift (about +4 points of hit rate over type) concentrated in regulatory and legal
  settlements, so I expect TILT ONLY or a marginal EARNS: a real but small gain, under 1% of event-day squared miss, driven by those types. Squared
  misses are dominated by extreme days, which makes any gain here small even when the sign information is real.
"""
import os, sys, math, time, bisect
from collections import deque, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decomp_validation as dv

STATS_START = "1995-01-01"
TEST_START = 2005
K_SHRINK = 100
MIN_CELL = 100
ERAS = [("2005-2012", 2005, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]


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


def load_event_info(sb, master, cache_ids):
    """security id -> {day index: (ptype, offset, label)} for events that have a label."""
    ent_to_sec = defaultdict(list)
    for r in paged(sb, "securities", "id,entity_id", ["id"]):
        if r["id"] in cache_ids and r.get("entity_id"):
            ent_to_sec[r["entity_id"]].append(r["id"])
    labels = {r["event_id"]: r["label"] for r in paged(sb, "event_direction_labels", "event_id,label", ["event_id"])}
    cand = defaultdict(lambda: defaultdict(list))
    for r in paged(sb, "ev_ent", "event_id,entity_id,d,ptype", ["event_id", "entity_id"]):
        lab = labels.get(r["event_id"])
        if lab is None or r["ptype"] == "systemic_shock":
            continue
        i = bisect.bisect_left(master, str(r["d"])[:10])
        if i >= len(master):
            continue
        for sid in ent_to_sec.get(r["entity_id"], []):
            for off in (0, 1):
                if i + off < len(master):
                    cand[sid][i + off].append((off, r["event_id"], r["ptype"], lab))
    info = {}
    for sid, days in cand.items():
        info[sid] = {}
        for t, lst in days.items():
            off, eid, pt, lab = min(lst, key=lambda x: (x[0], x[1]))
            info[sid][t] = (pt, off, lab)
    return info, len(labels)


def add(S, year, key, e):
    s = S[(year, key)]
    s[0] += 1
    s[1] += e
    s[2] += e * e


def run_stock(ret, rm, s, dates, einfo, S, stride):
    n = len(dates)
    K = 3
    A = [[0.0] * K for _ in range(K)]
    b = [0.0] * K
    syy = 0.0
    win = deque()
    cnt = 0
    for t in range(1, n):
        y, xm, xs = ret[t], rm[t], s[t]
        if None in (y, xm, xs):
            continue
        row = (1.0, xm, xs)
        m = len(win)
        if m >= dv.MIN_EST and dates[t] >= STATS_START and t % stride == 0:
            ev = einfo.get(t)
            if ev is not None:
                c = dv.solve(A, b, [0, 1, 2])
                if c:
                    e1 = y - (c[1] * xm + c[2] * xs)
                    year = int(dates[t][:4])
                    pt, off, lab = ev
                    add(S, year, ("T", pt, off), e1)
                    add(S, year, ("C", pt, lab, off), e1)
                    add(S, year, ("L", lab, off), e1)
                    add(S, year, ("O", off), e1)
                    cnt += 1
        win.append((y,) + row)
        for i in range(K):
            ri = row[i]
            b[i] += y * ri
            Ai = A[i]
            for j in range(K):
                Ai[j] += ri * row[j]
        syy += y * y
        if len(win) > dv.EST:
            o = win.popleft()
            yo, ro = o[0], o[1:]
            for i in range(K):
                b[i] -= yo * ro[i]
                Ai = A[i]
                for j in range(K):
                    Ai[j] -= ro[i] * ro[j]
            syy -= yo * yo
    return cnt


def era_of_year(y):
    for name, lo, hi in ERAS:
        if lo <= y <= hi:
            return name
    return None


def sse(s, pull):
    return s[2] - 2 * pull * s[1] + s[0] * pull * pull


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    stride = int(sys.argv[sys.argv.index("--stride") + 1]) if "--stride" in sys.argv else 1
    t0 = time.time()
    secs, _m = dv.load_cache()
    spy = [x for x in secs if x["ticker"] == "SPY"]
    if not spy:
        sys.exit("SPY is not in the cache.")
    master = list(spy[0]["dates"])
    pos = {d: i for i, d in enumerate(master)}
    n = len(master)
    stocks = [x for x in secs if x["ticker"] != "SPY"]
    rm, _ = dv.aligned_returns(spy[0], pos, n)
    rets = {}
    ssum, scnt = defaultdict(lambda: [0.0] * n), defaultdict(lambda: [0] * n)
    for x in stocks:
        r, _ = dv.aligned_returns(x, pos, n)
        rets[x["id"]] = r
        if x.get("sector"):
            su, sc = ssum[x["sector"]], scnt[x["sector"]]
            for t in range(n):
                if r[t] is not None:
                    su[t] += r[t]
                    sc[t] += 1
    einfo, nlab = load_event_info(get_sb(), master, {x["id"] for x in stocks})
    print("cache: %d securities | stride %d | labeled events: %d | securities with event days: %d" % (len(stocks), stride, nlab, len(einfo)), flush=True)

    S = defaultdict(lambda: [0.0, 0.0, 0.0])
    todo = stocks[:limit] if limit else stocks
    total = 0
    for k, x in enumerate(todo, 1):
        r, sec = rets[x["id"]], x.get("sector")
        if not sec or x["id"] not in einfo:
            continue
        su, sc = ssum[sec], scnt[sec]
        sarr = [None] * n
        for t in range(1, n):
            if r[t] is not None and rm[t] is not None and sc[t] - 1 >= dv.MIN_PEERS:
                sarr[t] = (su[t] - r[t]) / (sc[t] - 1) - rm[t]
        total += run_stock(r, rm, sarr, master, einfo[x["id"]], S, stride)
    print("labeled event-days scored: %d | %.0fs" % (total, time.time() - t0), flush=True)

    years = sorted({y for (y, key) in S})
    pri = defaultdict(lambda: [0.0, 0.0, 0.0])
    comps = ("T0-Z", "C2-T0", "C2-Z", "GB: C2-T0 on good/bad days")
    base = {c: defaultdict(float) for c in comps}
    after = {c: defaultdict(float) for c in comps}
    yearly = {c: {} for c in comps}
    for Y in years:
        cells = [(key, s) for (yy, key), s in S.items() if yy == Y]
        if Y >= TEST_START and pri[("O", 0)][0] >= MIN_CELL and pri[("O", 1)][0] >= MIN_CELL:
            era = era_of_year(Y)
            o_mean = {off: pri[("O", off)][1] / pri[("O", off)][0] for off in (0, 1)}
            def pull_t0(pt, off):
                p = pri[("T", pt, off)]
                return p[1] / p[0] if p[0] >= MIN_CELL else o_mean[off]
            tot = {c: [0.0, 0.0] for c in comps}                       # [sse before, sse after]
            for key, s in cells:
                if key[0] != "C":
                    continue
                _, pt, lab, off = key
                t0p = pull_t0(pt, off)
                pc = pri[("C", pt, lab, off)]
                c2p = (pc[0] * (pc[1] / pc[0] if pc[0] else 0.0) + K_SHRINK * t0p) / (pc[0] + K_SHRINK)
                z, st0, sc2 = sse(s, 0.0), sse(s, t0p), sse(s, c2p)
                for name, b_, a_ in (("T0-Z", z, st0), ("C2-T0", st0, sc2), ("C2-Z", z, sc2)):
                    tot[name][0] += b_
                    tot[name][1] += a_
                if lab in ("good", "bad"):
                    tot["GB: C2-T0 on good/bad days"][0] += st0
                    tot["GB: C2-T0 on good/bad days"][1] += sc2
            for name in comps:
                b_, a_ = tot[name]
                if b_ > 0:
                    base[name][era] += b_
                    after[name][era] += a_
                    yearly[name][Y] = 1 - a_ / b_
        for key, s in cells:
            pri[key] = [p + q for p, q in zip(pri[key], s)]

    print("\nGAIN IN SQUARED MISS ON LABELED EVENT-DAYS, walk-forward (positive = better)")
    print("  %-34s %10s %10s %10s | years positive" % ("", ERAS[0][0], ERAS[1][0], ERAS[2][0]))
    desc = {"C2-T0": "PRIMARY  C2 vs T0 (label beyond type)", "T0-Z": "T0 vs zero (type alone)", "C2-Z": "C2 vs zero (type + label)",
            "GB: C2-T0 on good/bad days": "C2 vs T0, good/bad days only"}
    res = {}
    for name in ("C2-T0", "T0-Z", "C2-Z", "GB: C2-T0 on good/bad days"):
        vals = [(1 - after[name][e[0]] / base[name][e[0]]) if base[name][e[0]] > 0 else None for e in ERAS]
        ys = yearly[name]
        npos = sum(1 for v in ys.values() if v > 0)
        fmt = lambda g: "%+8.3f%%" % (100 * g) if g is not None else "      n/a"
        print("  %-34s %10s %10s %10s | %d of %d" % (desc[name], fmt(vals[0]), fmt(vals[1]), fmt(vals[2]), npos, len(ys)))
        have = [v for v in vals if v is not None]
        if len(have) == 3 and ys:
            if all(v >= 0.005 for v in have) and npos / len(ys) >= 0.70:
                res[name] = "EARNS ITS PLACE"
            elif all(v > 0 for v in have) and npos / len(ys) >= 0.70:
                res[name] = "TILT ONLY"
            else:
                res[name] = "DOES NOT"
        else:
            res[name] = "no verdict (an era is missing)"

    print("\nCALIBRATED PULLS on all years: mean chapter-1 miss on event days, by label and day (percent; n)")
    print("  %-10s %22s %22s" % ("label", "day 0", "day +1"))
    for lab in ("good", "bad", "mixed", "unclear"):
        cols = []
        for off in (0, 1):
            p = pri[("L", lab, off)]
            cols.append("%+6.2f%%  (n=%d)" % (100 * p[1] / p[0], p[0]) if p[0] else "n/a")
        print("  %-10s %22s %22s" % (lab, cols[0], cols[1]))
    print("\n  by type and label (days 0 and +1 pooled; types and labels with >= 100 event-days)")
    print("  %-26s %-8s %8s %12s" % ("type", "label", "days", "mean miss"))
    pooled = defaultdict(lambda: [0.0, 0.0])
    for key, s in pri.items():
        if key[0] == "C":
            pooled[(key[1], key[2])][0] += s[0]
            pooled[(key[1], key[2])][1] += s[1]
    for (pt, lab), (cnt, sm) in sorted(pooled.items()):
        if cnt >= MIN_CELL and lab in ("good", "bad"):
            print("  %-26s %-8s %8d %+11.2f%%" % (pt, lab, cnt, 100 * sm / cnt))

    print("\nVERDICT under the pre-set classification (primary comparison C2 vs T0, label beyond type): %s" % res.get("C2-T0", "n/a"))
    print("  (type alone, T0 vs zero: %s | type + label vs zero: %s)" % (res.get("T0-Z", "n/a"), res.get("C2-Z", "n/a")))
    print("\ntotal %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
