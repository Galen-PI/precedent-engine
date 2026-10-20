#!/usr/bin/env python3
"""
day_card.py -- READ-ONLY. The 'bottom line' card for ONE stock on ONE day, assembled from everything measured so far.

Usage:   python3 -u scripts/card/day_card.py JPM 2025-04-09
Needs:   data_cache/returns (build_return_cache.py), models/event_band_model.json, models/decomp_validation_20261020.json, models/label_annotation.json
         (the model files are optional: a missing one just removes its section). The database is read for the stock's own events and their labels.
Writes:  results/cards/card_TICKER_DATE.json  and prints the card.

WHAT THE CARD IS. An EXPLANATION of the day using same-day market and sector moves, not a forecast. Sections:
  1. THE DAY: actual move, close and previous close.
  2. CHAPTER 1, market and sector (the only SIGNED pulls that earned a place): beta x market move and beta x sector-beyond-market move, from a 250-valid-day
     fit that never uses the day itself. Hypothetical move and price; what is left over (the residual) in units of this stock's spread.
     The 250-day fit skips one-day returns beyond +/-50% (price-adjustment artifacts); the DAY BEING EXPLAINED uses every return, and moves beyond 50%
     (the stock's own, or its sector peers') are listed on the card so a real crash or a split/spin-off artifact can be told apart by eye.
  3. THE BAND (and the SECTOR PEERS that day: typical miss size, this stock's rank by miss size, and the largest positive and negative peer misses):
     1.645 x spread x sqrt(q) x event multiplier, where q = the mean squared standardized miss of ALL OTHER stocks that day (market-wide stress), and
     the multiplier is a MEASURED GROUP value, never a product: the joint event-day model for a recorded event, 2.72x / 2.47x for an earnings window (8-K item 2.02, day 0 / +1),
     2.87x for both together, 1.36x for a Regulation FD filing (item 7.01), else 1.0. Whether the actual price
     fell inside. The band's realized coverage has NOT been measured (tails are fatter than normal), so read it as a reference line.
  4. OWN EVENT(S) on this day (day 0 or +1): title, type, the labeler's label / size / timing, and what similar-labeled events averaged. ANNOTATION ONLY:
     the label's pull did not earn a place in the price (event_center_test, pre-set: DOES NOT).
  5. REGISTERED MACRO LINKS: oil, yield and credit flag states (magnitude-only links; no signed pull earned a place).
  6. NOT YET MEASURED: peer and sector events, earnings surprises and analyst changes, news tone. Listed so a gap is visible, not hidden.
  7. TRACK RECORD: how well chapter 1 has done overall, for this sector, and on event days (from the full validation run).
Every number is labeled with where it comes from.
"""
import os, sys, json, math, bisect, datetime
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import decomp_validation as dv

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MODELS = os.path.join(ROOT, "models")
EXCLUDED_TYPES = ("ipo_spinoff", "systemic_shock", "geopolitical", "natural_disaster")
FLAG_LINES = {"oil": 0.03, "yield": 0.10, "credit": 0.03}


def load_json(name):
    p = os.path.join(MODELS, name)
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        return json.load(fh)


def load_universe():
    secs, macro = dv.load_cache()
    spy = [x for x in secs if x["ticker"] == "SPY"]
    if not spy:
        sys.exit("SPY is not in the price cache.")
    master = list(spy[0]["dates"])
    pos = {d: i for i, d in enumerate(master)}
    n = len(master)
    rm, _ = dv.aligned_returns(spy[0], pos, n)
    stocks = [x for x in secs if x["ticker"] != "SPY"]
    rets, raw, members = {}, {}, defaultdict(list)
    ssum, scnt = defaultdict(lambda: [0.0] * n), defaultdict(lambda: [0] * n)
    for x in stocks:
        r, _ = dv.aligned_returns(x, pos, n)
        rets[x["id"]] = r
        old_max = dv.MAXRET
        dv.MAXRET = 1e9                                  # the unfiltered series, used only for the day being explained
        raw[x["id"]], _ = dv.aligned_returns(x, pos, n)
        dv.MAXRET = old_max
        if x.get("sector"):
            members[x["sector"]].append(x["id"])
            su, sc = ssum[x["sector"]], scnt[x["sector"]]
            for t in range(n):
                if r[t] is not None:
                    su[t] += r[t]
                    sc[t] += 1
    oil, yld, crd = dv.macro_arrays(macro, master)
    return {"master": master, "pos": pos, "n": n, "rm": rm, "stocks": stocks, "rets": rets, "raw": raw, "members": members, "_rawcache": {},
            "ssum": ssum, "scnt": scnt, "oil": oil, "yld": yld, "crd": crd}


def sector_raw(U, sec, t):
    """Sum and count of EVERY valid return (no 50% filter) of the sector's stocks on day t."""
    key = (sec, t)
    c = U["_rawcache"].get(key)
    if c is None:
        tot, cnt = 0.0, 0
        for sid in U["members"][sec]:
            v = U["raw"][sid][t]
            if v is not None:
                tot += v
                cnt += 1
        c = (tot, cnt)
        U["_rawcache"][key] = c
    return c


def chapter1(U, x, t):
    """Market + sector fit over the last 250 valid days BEFORE day t (the day is never used), and the day's split."""
    r, sec, rm = U["rets"][x["id"]], x.get("sector"), U["rm"]
    raw_t = U["raw"][x["id"]][t]
    if not sec or raw_t is None or rm[t] is None:
        return None
    su, sc = U["ssum"][sec], U["scnt"][sec]

    def s_at(k):
        if r[k] is None or rm[k] is None or sc[k] - 1 < dv.MIN_PEERS:
            return None
        return (su[k] - r[k]) / (sc[k] - 1) - rm[k]

    rs, rc = sector_raw(U, sec, t)                       # the day being explained uses EVERY valid return, moves beyond 50% included
    if rc - 1 < dv.MIN_PEERS:
        return None
    st = (rs - raw_t) / (rc - 1) - rm[t]
    A = [[0.0] * 3 for _ in range(3)]
    b = [0.0] * 3
    syy, cnt, k = 0.0, 0, t - 1
    while k >= 1 and cnt < dv.EST:
        s = s_at(k)
        if s is not None:
            row = (1.0, rm[k], s)
            y = r[k]
            for i in range(3):
                b[i] += y * row[i]
                for j in range(3):
                    A[i][j] += row[i] * row[j]
            syy += y * y
            cnt += 1
        k -= 1
    if cnt < dv.MIN_EST:
        return None
    c = dv.solve(A, b, [0, 1, 2])
    if not c:
        return None
    sd = math.sqrt(max(syy - sum(c[i] * b[i] for i in range(3)), 1e-18) / (cnt - 3))
    mkt, secp = c[1] * rm[t], c[2] * st
    hyp = mkt + secp
    return {"ret": raw_t, "market_move": rm[t], "sector_excess": st, "beta_market": c[1], "beta_sector": c[2], "market_part": mkt, "sector_part": secp,
            "hyp": hyp, "e1": raw_t - hyp, "sd": sd, "fit_days": cnt}


def band_multiplier(model, ptype, size, timing, off):
    if model is None:
        return None, "no band model file"
    if ptype in EXCLUDED_TYPES:
        return None, "event type %s is excluded from the band model" % ptype
    refs, coef = model["references"], model["coef"]
    lm = coef["intercept"]
    for label, lev in (("type", ptype), ("size", size), ("timing", timing)):
        if lev is not None and lev != refs[label]:
            lm += coef.get("%s: %s" % (label, lev), 0.0)
    if off == 1:
        lm += coef.get("day: +1", 0.0)
    return max(1.0, math.sqrt(math.exp(lm) / model["ordinary_day_mean_z5sq"])), None


def parse_items(s):
    out = set()
    for part in str(s or "").replace(";", ",").replace(" ", ",").split(","):
        p = part.strip().lower().replace("item", "").strip()
        if p and p[0].isdigit():
            out.add(p)
    return out


def filing_flags(filings, master, t):
    """From a stock's 8-K rows near day t: an earnings window (item 2.02; day 0 = the first trading day on or after the filing date, day +1 = the next)
    and a Regulation FD flag (item 7.01). The table has no filing time, so both days are flagged."""
    earn_off, earn_date, f701 = None, None, False
    for f in filings:
        d = str(f["filing_date"])[:10]
        i = bisect.bisect_left(master, d)
        if i != t and i + 1 != t:
            continue
        off = 0 if i == t else 1
        its = parse_items(f.get("item_codes"))
        if "2.02" in its:
            if earn_off is None or off < earn_off:
                earn_off, earn_date = off, d
        elif "7.01" in its:
            f701 = True
    return {"earn_off": earn_off, "earn_date": earn_date, "f701": f701}


def combine_multiplier(ev_mult, fl, earn_model, ev_note=None, has_event=False):
    """The band multiplier and where it came from. Measured GROUP values are used as they are; they are never multiplied together."""
    mm = earn_model["multipliers_vs_ordinary_day"] if earn_model else None
    if mm and fl["earn_off"] is not None:
        if has_event:
            return mm["event_and_earnings"], "earnings window (8-K item 2.02 filed %s, day %d) together with a recorded event: the measured group value, not a product" % (fl["earn_date"], fl["earn_off"])
        return mm["earnings_day0" if fl["earn_off"] == 0 else "earnings_day1"], "earnings window (8-K item 2.02 filed %s, day %d): measured on all stocks since 2006, relative to an ordinary day" % (fl["earn_date"], fl["earn_off"])
    if has_event:
        if ev_mult is None:
            return 1.0, ev_note or "recorded event with no multiplier available"
        return ev_mult, "recorded event (joint event-day model, floored at 1.0)"
    if mm and fl["f701"]:
        return mm["item_7_01"], "Regulation FD filing (8-K item 7.01) on day 0 or +1: measured about 1.36x on all such days; a weak lead, not a proven link"
    return 1.0, "no own event, earnings filing or item 7.01 filing on day 0 or +1"


def own_events(sb, ticker_sec, master, t, date):
    ent = ticker_sec.get("entity_id")
    if not ent:
        return []
    lo = (datetime.date.fromisoformat(date) - datetime.timedelta(days=7)).isoformat()
    rows = sb.table("ev_ent").select("event_id,entity_id,d,ptype").eq("entity_id", ent).gte("d", lo).lte("d", date).execute().data
    out = []
    for r in rows:
        i = bisect.bisect_left(master, str(r["d"])[:10])
        if i == t or i + 1 == t:
            out.append({"event_id": r["event_id"], "ptype": r["ptype"], "off": 0 if i == t else 1, "date": str(r["d"])[:10]})
    if not out:
        return []
    ids = [e["event_id"] for e in out]
    titles = {r["id"]: r.get("title") for r in sb.table("events").select("id,title").in_("id", ids).execute().data}
    labs = {r["event_id"]: r for r in sb.table("event_direction_labels").select("event_id,label,size,timing,reasoning").in_("event_id", ids).execute().data}
    for e in out:
        e["title"] = titles.get(e["event_id"])
        l = labs.get(e["event_id"], {})
        e["label"], e["size"], e["timing"], e["reasoning"] = l.get("label"), l.get("size"), l.get("timing"), l.get("reasoning")
    out.sort(key=lambda e: (e["off"], e["event_id"]))
    return out


def pct(x, d=2):
    return "%+.*f%%" % (d, 100 * x)


def r2_from(a):
    return 1 - a[2] / a[1] if a and a[1] > 0 else None


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    ticker, date = sys.argv[1].upper(), sys.argv[2]
    U = load_universe()
    if date not in U["pos"]:
        sys.exit("%s is not a trading day in the price cache (last cached day: %s)." % (date, U["master"][-1]))
    t = U["pos"][date]
    x = next((s for s in U["stocks"] if s["ticker"] == ticker), None)
    if x is None:
        sys.exit("%s is not in the price cache." % ticker)
    c1 = chapter1(U, x, t)
    if c1 is None:
        sys.exit("Not enough history or peers to decompose %s on %s." % (ticker, date))
    px = dict(zip(x["dates"], x["adj"]))
    prev_close, close = px.get(U["master"][t - 1]), px.get(date)
    sec_name = x.get("sector")
    big_peers = []
    for sid in U["members"].get(sec_name, []):
        v = U["raw"][sid][t]
        if sid != x["id"] and v is not None and abs(v) > dv.MAXRET:
            big_peers.append((next(s["ticker"] for s in U["stocks"] if s["id"] == sid), v))

    # q: the same day's cross-section of OTHER stocks (market-wide stress)
    z2s, others = [], []
    for y in U["stocks"]:
        if y["id"] == x["id"]:
            continue
        cy = chapter1(U, y, t)
        if cy:
            z2s.append((cy["e1"] / cy["sd"]) ** 2)
            others.append((y["ticker"], y.get("sector"), cy))
    q = sum(z2s) / len(z2s) if len(z2s) > 20 else None

    sb = dv.get_sb()
    sec_row = (sb.table("securities").select("id,entity_id,ticker,sector").eq("ticker", ticker).execute().data or [{}])[0]
    events = own_events(sb, sec_row, U["master"], t, date)
    band_model = load_json("event_band_model.json")
    label_ann = load_json("label_annotation.json")
    val = load_json("decomp_validation_20261020.json")

    earn_model = load_json("earnings_band_model.json")
    lo8 = (datetime.date.fromisoformat(date) - datetime.timedelta(days=7)).isoformat()
    filings = []
    if sec_row.get("id"):
        try:
            filings = sb.table("sec_8k_filings").select("filing_date,item_codes").eq("security_id", sec_row["id"]).gte("filing_date", lo8).lte("filing_date", date).execute().data or []
        except Exception:
            filings = []
    fl = filing_flags(filings, U["master"], t)
    lead = events[0] if events else None
    ev_mult, ev_note = (band_multiplier(band_model, lead["ptype"], lead["size"], lead["timing"], lead["off"]) if lead else (None, None))
    mult, mult_src = combine_multiplier(ev_mult, fl, earn_model, ev_note, bool(lead))
    sd_eff = c1["sd"] * (math.sqrt(q) if q else 1.0)
    half = 1.645 * sd_eff * mult
    lo_ret, hi_ret = c1["hyp"] - half, c1["hyp"] + half
    z_miss = c1["e1"] / (c1["sd"] * (math.sqrt(q) if q else 1.0) * mult)

    card = {"ticker": ticker, "date": date, "sector": x.get("sector")}
    L = []
    L.append("=" * 78)
    L.append("DAY CARD: %s on %s (%s)" % (ticker, date, x.get("sector")))
    L.append("=" * 78)
    L.append("1. THE DAY      actual move %s   (previous close %.2f -> close %.2f)" % (pct(c1["ret"]), prev_close or float("nan"), close or float("nan")))
    L.append("")
    L.append("2. CHAPTER 1    market and sector (fit on the %d valid days before today; today is never used)" % c1["fit_days"])
    L.append("   market (SPY) %s x beta %.2f   pulls %s" % (pct(c1["market_move"]), c1["beta_market"], pct(c1["market_part"])))
    L.append("   sector beyond market %s x beta %.2f   pulls %s" % (pct(c1["sector_excess"]), c1["beta_sector"], pct(c1["sector_part"])))
    if abs(c1["ret"]) > dv.MAXRET:
        L.append("   WARNING: this stock's own move exceeds 50%. It may be real or a split / spin-off price error: check before reading the split above.")
    if big_peers:
        L.append("   NOTE: sector peers beyond 50% today are INCLUDED in the sector average: " + ", ".join("%s %+.1f%%" % (tk, 100 * v) for tk, v in big_peers))
    hyp_price = prev_close * (1 + c1["hyp"]) if prev_close else None
    L.append("   hypothetical move %s -> price %.2f | actual price %.2f" % (pct(c1["hyp"]), hyp_price or float("nan"), close or float("nan")))
    L.append("   UNEXPLAINED (actual - hypothetical): %s = %.1f of this stock's usual spread (%s)" % (pct(c1["e1"]), c1["e1"] / c1["sd"], pct(c1["sd"])))
    L.append("")
    L.append("3. THE BAND     reference line, 1.645 x spread x market-stress x event multiplier")
    if q:
        L.append("   market-wide stress today (q): other stocks missed %.2fx their usual size (sqrt of the mean squared miss; %d stocks)" % (math.sqrt(q), len(z2s)))
    else:
        L.append("   market-wide stress: not available (too few other stocks)")
    L.append("   band multiplier %.2fx -- %s" % (mult, mult_src))
    if prev_close:
        L.append("   band on the move %s to %s -> price %.2f to %.2f | actual %.2f is %s" % (
            pct(lo_ret), pct(hi_ret), prev_close * (1 + lo_ret), prev_close * (1 + hi_ret), close, "INSIDE" if abs(z_miss) <= 1.645 else "OUTSIDE"))
    L.append("   the miss is %.2f band-units (1.645 = the edge). Realized coverage of this band is NOT measured; tails are fatter than normal." % z_miss)
    L.append("")
    peers = [(tk, cy) for tk, sc_, cy in others if sc_ == x.get("sector")]
    if len(peers) >= 3:
        own_z = abs(c1["e1"] / c1["sd"])
        typ = math.sqrt(sum((cy["e1"] / cy["sd"]) ** 2 for tk, cy in peers + [(ticker, c1)]) / (len(peers) + 1))
        rank = 1 + sum(1 for tk, cy in peers if abs(cy["e1"] / cy["sd"]) > own_z)
        L.append("   SECTOR PEERS today (%s, %d others): typical miss %.1f spreads; this stock's miss ranks %d of %d by size" % (x.get("sector"), len(peers), typ, rank, len(peers) + 1))
        up_ = sorted(peers, key=lambda p_: -p_[1]["e1"])[:3]
        dn_ = sorted(peers, key=lambda p_: p_[1]["e1"])[:3]
        L.append("      largest positive misses: " + ", ".join("%s %s (%.1f spreads)" % (tk, pct(cy["e1"]), cy["e1"] / cy["sd"]) for tk, cy in up_))
        L.append("      largest negative misses: " + ", ".join("%s %s (%.1f spreads)" % (tk, pct(cy["e1"]), cy["e1"] / cy["sd"]) for tk, cy in dn_))
        L.append("      (misses of both signs inside one sector point to structure within the sector, not to one missing piece for all of it)")
        L.append("")
    L.append("4. OWN EVENTS   day 0 or +1 (annotation only)")
    if not events:
        L.append("   none recorded for this stock on this day.")
    for e in events:
        L.append("   [%s] %s" % ("day 0" if e["off"] == 0 else "day +1", (e["title"] or "(no title)")[:100]))
        L.append("         type %s | label %s | size %s | timing %s | event date %s" % (e["ptype"], e["label"], e["size"], e["timing"], e["date"]))
        if e["label"] in ("good", "bad", "mixed", "unclear") and label_ann:
            m = label_ann["mean_miss_percent"][e["label"]]["day0" if e["off"] == 0 else "day1"]
            L.append("         similar '%s' events averaged %+.2f%% beyond market and sector on this day. A tilt, not part of the price: beyond the event type it" % (e["label"], m))
            L.append("         cut event-day squared miss by only +0.029 / +0.028 / +0.223% (2005-12 / 2013-19 / 2020-26; pre-set test: does not earn a place). It points the")
            L.append("         right way about 58% of the time vs 54% from type alone (direction test, passed; far placebo clean).")
    if fl["earn_off"] is not None:
        L.append("   EARNINGS WINDOW  8-K item 2.02 filed %s: today is day %d of the window (the table has no filing time, so the reaction may fall on either day)." % (fl["earn_date"], fl["earn_off"]))
        L.append("         Earnings days hold about 19.5% of all unexplained squared miss on about 3% of stock-days. The band is widened; the SIGN is not known (no surprise data tested yet).")
    elif fl["f701"]:
        L.append("   REGULATION FD FILING  8-K item 7.01 on day 0 or +1 (a weak lead: about 1.36x on average; mostly routine investor materials).")
    L.append("")
    L.append("5. MACRO LINKS  registered, magnitude-only (no signed pull earned a place); armed every day")
    for nm, key, unit in (("oil move", "oil", 1.0), ("10-year yield change", "yld", 1.0), ("credit spread change", "crd", 1.0)):
        v = U[key][t]
        line = FLAG_LINES["oil" if key == "oil" else ("yield" if key == "yld" else "credit")]
        if v is None:
            L.append("   %-22s not available" % nm)
            continue
        on = (abs(v) >= line - 1e-9) if key != "crd" else (v >= line - 1e-9)
        shown = pct(v) if key == "oil" else "%+.2f pp" % v
        L.append("   %-22s %-10s %s (flag line %s)" % (nm, shown, "ON" if on else "quiet", "%.0f%%" % (100 * line) if key == "oil" else "%.2f pp" % line))
    L.append("")
    L.append("6. NOT YET MEASURED  peer and sector events | earnings surprises and analyst changes | news tone | anything never filed in an 8-K")
    L.append("")
    L.append("7. TRACK RECORD  chapter 1 (market + sector) on every stock-day since 2005, scored on days its fit never saw")
    if val:
        a = val.get("all|all")
        L.append("   all stock-days: R-squared vs predicting zero %.2f | mean squared miss %.2f spreads^2 (1.0 = calibrated) | misses beyond 3 spreads %.1f%%" % (
            r2_from(a), a[4] / a[0], 100 * a[6] / a[0]))
        s_ = val.get("sector|%s" % x.get("sector"))
        if s_:
            L.append("   %s sector: R-squared %.2f (n=%d)" % (x.get("sector"), r2_from(s_), s_[0]))
        ev1, ev0 = val.get("event|1"), val.get("event|0")
        if ev1 and ev0:
            L.append("   own-event days: R-squared %.2f, mean squared miss %.2f (vs %.2f on other days), misses beyond 3 spreads %.1f%% (vs %.1f%%)" % (
                r2_from(ev1), ev1[4] / ev1[0], ev0[4] / ev0[0], 100 * ev1[6] / ev1[0], 100 * ev0[6] / ev0[0]))
        L.append("   so about %.0f%% of a typical stock-day's squared move is NOT explained by market and sector; on %s it is about %.0f%%." % (
            100 * (1 - r2_from(a)), x.get("sector"), 100 * (1 - r2_from(s_))) if s_ else "   so about %.0f%% of a typical stock-day's squared move is NOT explained by market and sector." % (100 * (1 - r2_from(a))))
    else:
        L.append("   (models/decomp_validation_20261020.json not found)")
    L.append("")
    L.append("   (The track record and the 250-day fits skip one-day returns beyond +/-50%: 59 stock-days since 1994, real crashes and split/spin-off artifacts mixed. The day being explained does not.)")
    L.append("   An explanation using same-day market and sector moves. Not a forecast, not advice.")
    print("\n".join(L))

    card.update({"day": {"return": c1["ret"], "prev_close": prev_close, "close": close}, "chapter1": c1, "hypothetical_price": hyp_price,
                 "q": q, "event_multiplier": mult, "band_multiplier_source": mult_src, "filing_flags": fl, "band_return": [lo_ret, hi_ret], "band_units_of_miss": z_miss, "events": events,
                 "macro": {"oil": U["oil"][t], "yield": U["yld"][t], "credit": U["crd"][t]}})
    outdir = os.path.join(ROOT, "results", "cards")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "card_%s_%s.json" % (ticker, date)), "w") as fh:
        json.dump(card, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
