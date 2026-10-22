#!/usr/bin/env python3
"""
earnings_roles.py -- shared helpers for ROLE-BASED earnings bands (used by build_earnings_role_model.py and the day card, so the two cannot drift apart).
THE IDEA (earnings_role_band_test.py, verdict ROLE BANDS IMPROVE: interval score 0.890 / 0.869 / 0.857 of the pooled bands by era, placebo 1.003): the 8-K table has no release time, so the card's pooled day-0 / day-+1 bands are right on average but wrong on each day
(they cover a stock's reaction day only 81% and its other day 98%). A stock's own habit, read from the opening gaps of its earlier quarters, says which of the two days carries the reaction.
HABIT RULE (identical to the role test). Overnight gap G = open / previous close - 1 (|G| <= 0.5); gap spread = standard deviation of G over the previous 60 trading days (at least 40 valid); gap z = |G| / spread. An earlier quarter is CLASSIFIABLE if the larger of its day-i and day-(i+1) gap z is at least 2.0:
label 1 (after the close: the day-i+1 gap is the larger) or 0 (before the open). Earnings days are the first trading day on or after each Item 2.02 filing date, thinned to at least 20 trading days apart. The HABIT is the majority of the last 4 EARLIER classifiable quarters (ties go to the most recent); fewer than 4 means no habit.
The reaction day is day i for habit 0 and day i+1 for habit 1; the other day is the other one.
"""
import os, re, bisect, pickle
import numpy as np

GAP_WIN, GAP_MIN, MAX_GAP, CLASSIFY_Z, HIST, THIN = 60, 40, 0.5, 2.0, 4, 20
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
REACTION, OTHER = "earnings window, reaction day", "earnings window, other day"


def majority(v):
    s, m = sum(v), len(v)
    return 1 if 2 * s > m else (0 if 2 * s < m else v[-1])


def gap_z_1d(O, C):
    """|overnight gap| / gap spread over the previous 60 days, for ONE stock (arrays aligned to the master calendar)."""
    n = len(O)
    G = np.full(n, np.nan)
    G[1:] = O[1:] / C[:-1] - 1.0
    G[np.abs(G) > MAX_GAP] = np.nan
    V = np.isfinite(G)
    X = np.where(V, G, 0.0)
    c1, c2, cc = (np.concatenate([[0.0], np.cumsum(a)]) for a in (X, X * X, V.astype(float)))
    GSD = np.full(n, np.nan)
    if n > GAP_WIN:
        S1, S2, Cn = c1[GAP_WIN:n] - c1[:n - GAP_WIN], c2[GAP_WIN:n] - c2[:n - GAP_WIN], cc[GAP_WIN:n] - cc[:n - GAP_WIN]
        with np.errstate(invalid="ignore", divide="ignore"):
            var = (S2 - S1 * S1 / Cn) / (Cn - 1)
            GSD[GAP_WIN:] = np.where(Cn >= GAP_MIN, np.sqrt(np.maximum(var, 0.0)), np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.abs(G) / GSD


def thin(events):
    keep = []
    for i in sorted(set(events)):
        if not keep or i - keep[-1] >= THIN:
            keep.append(i)
    return keep


def habit_at(events, ZG, i0, n, first_i=0):
    """The forward habit before the earnings day i0 (a master-calendar index), from EARLIER quarters only; None if i0 is not a kept event or fewer than 4 classifiable quarters exist."""
    keep = thin(events)
    if i0 not in keep:
        return None
    hist = []
    for i in keep:
        if i == i0:
            break
        if i < GAP_WIN + 1 or i + 1 >= n or i < first_i:
            continue
        a, b = ZG[i], ZG[i + 1]
        if np.isfinite(a) and np.isfinite(b) and max(a, b) >= CLASSIFY_Z:
            hist.append(1 if b > a else 0)
    if len(hist) < HIST:
        return None
    last = hist[-HIST:]
    return {"habit": majority(last), "n_used": len(last), "n_after_close": int(sum(last)), "last": last[-1]}


def apply_role(fl, has_event, hab, rm):
    """Replace the pooled earnings group by the role group when the stock-day is an ISOLATED earnings window (no own recorded event, no Regulation FD filing) and a habit exists.
    Returns (multiplier, multiplier_source, group, edge, edge_source, note) or None to leave the card's pooled logic untouched."""
    if not rm or not hab or fl.get("earn_off") is None or has_event or fl.get("f701"):
        return None
    g = rm.get("groups", {})
    reaction = fl["earn_off"] == hab["habit"]
    name = REACTION if reaction else OTHER
    if name not in g:
        return None
    when = "after the close (reaction on day +1)" if hab["habit"] == 1 else "before the open (reaction on day 0)"
    n_after = hab["n_after_close"]
    n_before = hab["n_used"] - n_after
    tie = 2 * n_after == hab["n_used"]
    role_word = "REACTION day" if reaction else "other day"
    if tie:
        basis = "this stock's last %d classifiable quarters split evenly (%d after the close, %d before the open), so its most recent one decides: %s" % (hab["n_used"], n_after, n_before, "after the close" if hab["habit"] == 1 else "before the open")
        src = "earnings window (8-K item 2.02 filed %s, day %d): WEAK HABIT: %s; so today is treated as its %s; the measured multiplier of that role on all stocks since 2006" % (fl["earn_date"], fl["earn_off"], basis, role_word)
        note = "ROLE BAND  WEAK HABIT: the last %d classifiable quarters split %d-%d and the most recent one (%s) decides, so the release time may differ this quarter; treated as its %s. Ties were not validated separately (the pooled day-0 / day-+1 band covers reaction days only about 81%% and other days about 98%%)." % (hab["n_used"], n_after, n_before, "after the close" if hab["habit"] == 1 else "before the open", role_word.lower())
    else:
        src = ("earnings window (8-K item 2.02 filed %s, day %d): this stock released %s in %d of its last %d classifiable quarters, so today is its %s; the measured multiplier of that role on all stocks since 2006"
               % (fl["earn_date"], fl["earn_off"], "after the close" if hab["habit"] == 1 else "before the open", n_after if hab["habit"] == 1 else n_before, hab["n_used"], role_word))
        note = "ROLE BAND  usual release time %s from the opening gaps of its last %d classifiable quarters; today is its %s (the pooled day-0 / day-+1 band covers reaction days only about 81%% and other days about 98%%)." % (when, hab["n_used"], "reaction day" if reaction else "other day")
    return g[name]["multiplier"], src, name, g[name]["edge_90"], "calibrated 90%% edge for: %s (card units: times the multiplier it equals the ordinary-scale 90th percentile of that role)" % name, note


def load_one_ohlc(sec_id, master, ohlc_dir=None):
    path = os.path.join(ohlc_dir or os.path.join(ROOT, "data_cache", "ohlc"), "%s.pkl" % sec_id)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        d = pickle.load(fh)
    if not d.get("dates"):
        return None
    pos = {x: i for i, x in enumerate(master)}
    n = len(master)
    O, C = np.full(n, np.nan), np.full(n, np.nan)
    ii = np.array([pos.get(x, -1) for x in d["dates"]], dtype=np.int64)
    ok = ii >= 0
    O[ii[ok]] = np.array([np.nan if v is None else v for v in d["open"]], dtype=float)[ok]
    C[ii[ok]] = np.array([np.nan if v is None else v for v in d["close"]], dtype=float)[ok]
    O[O <= 0] = np.nan
    C[C <= 0] = np.nan
    return O, C


def habit_for_card(sb, sec_id, master, i0, date, ohlc_dir=None, first_year=2006):
    """The card-time habit for the earnings day i0 (master index) of one stock: OHLC from the local cache, earlier Item 2.02 filings from the database. None whenever any ingredient is missing."""
    oc = load_one_ohlc(sec_id, master, ohlc_dir)
    if oc is None:
        return None
    O, C = oc
    n = len(master)
    events, off = [], 0
    while True:
        rows = sb.table("sec_8k_filings").select("filing_date,item_codes").eq("security_id", sec_id).lte("filing_date", date).order("filing_date").range(off, off + 999).execute().data or []
        for r in rows:
            if "2.02" in re.split(r"[,\s;]+", str(r.get("item_codes") or "")):
                events.append(bisect.bisect_left(master, str(r["filing_date"])[:10]))
        if len(rows) < 1000:
            break
        off += 1000
    first_i = next((j for j, x in enumerate(master) if int(x[:4]) >= first_year), 0)
    return habit_at(events, gap_z_1d(O, C), i0, n, first_i)
