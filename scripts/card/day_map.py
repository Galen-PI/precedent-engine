#!/usr/bin/env python3
"""
day_map.py -- READ-ONLY. The market-wide map of ONE day, one level above day_card.py (which zooms into one stock).

Usage:   python3 -u scripts/card/day_map.py 2020-03-09        (optional second argument: how many rows to list, default 8)
Needs:   the same files as day_card.py. The database is read for the day's events (every stock's own events on day 0 or +1) and their labels.
Writes:  results/maps/map_DATE.json  (one row per stock, plus the sector and event summaries) and prints the map.

WHAT IT SHOWS (every number is measured; nothing here is a forecast).
  1. THE DAY: SPY move, breadth, market-wide stress (the root-mean-square miss of all stocks in units of their own usual spread), and how much of the day's
     squared moves market + sector explained (the day's R-squared, the same measure as the track record).
  2. SECTORS: each sector's equal-weighted move, the part beyond the market, the average miss (a sector whose stocks all miss the same way is a missing
     sector-wide piece), the typical miss size in spreads, and how many stocks missed by more than 2 spreads.
  3. EVENTS: stocks with an own event on day 0 or +1: how many, which types and labels, and the key number: their SHARE of the day's unexplained squared
     miss against their share of stocks (ENRICHMENT; 1.0 = events make no difference). Event stocks listed with the label's tilt (the mean miss similar
     labels averaged) next to what happened, and how often the miss pointed the way the label did (small samples: read as a count, not a rate).
     The tilt is an annotation. No event adds a signed pull to the price (event_center_test: does not earn a place); events widen the band.
  4. WHERE THE MISSING INFORMATION IS: the biggest misses (in band units: miss / (spread x market stress x event multiplier)), flagged event / no recorded
     event, and what share of the stocks beyond 2 band units have no recorded event. Those are the candidates for news we have not recorded.
  5. ZOOM: the day_card commands for the largest misses.
"""
import os, sys, json, math, bisect, datetime
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import decomp_validation as dv
import day_card as dc

MIN_STOCKS = 50            # refuse to draw a market map from fewer stocks than this


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


def pct(x, d=2):
    return "%+.*f%%" % (d, 100 * x)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    date = sys.argv[1]
    topn = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    U = dc.load_universe()
    if date not in U["pos"]:
        sys.exit("%s is not a trading day in the price cache (last cached day: %s)." % (date, U["master"][-1]))
    t = U["pos"][date]

    rows = []
    for x in U["stocks"]:
        c = dc.chapter1(U, x, t)
        if c:
            rows.append({"id": x["id"], "ticker": x["ticker"], "sector": x.get("sector") or "(none)", "ret": c["ret"], "hyp": c["hyp"], "e1": c["e1"],
                         "sd": c["sd"], "sector_excess": c["sector_excess"], "z2": (c["e1"] / c["sd"]) ** 2})
    if len(rows) < MIN_STOCKS:
        sys.exit("Too few stocks with a valid decomposition on %s (%d)." % (date, len(rows)))
    n = len(rows)
    S = sum(r["z2"] for r in rows)
    for r in rows:
        r["q_others"] = (S - r["z2"]) / (n - 1)

    # events: every entity's events on day 0 or +1
    sb = dv.get_sb()
    ent_to_ids = defaultdict(list)
    cache_ids = {r["id"] for r in rows}
    for r in paged(lambda: sb.table("securities").select("id,entity_id").order("id")):
        if r["id"] in cache_ids and r.get("entity_id"):
            ent_to_ids[r["entity_id"]].append(r["id"])
    lo = (datetime.date.fromisoformat(date) - datetime.timedelta(days=7)).isoformat()
    evrows = paged(lambda: sb.table("ev_ent").select("event_id,entity_id,d,ptype").gte("d", lo).lte("d", date).order("event_id").order("entity_id"))
    cand = defaultdict(list)
    for e in evrows:
        i = bisect.bisect_left(U["master"], str(e["d"])[:10])
        if i == t or i + 1 == t:
            for sid in ent_to_ids.get(e["entity_id"], []):
                cand[sid].append({"event_id": e["event_id"], "ptype": e["ptype"], "off": 0 if i == t else 1})
    ev_ids = sorted({c["event_id"] for lst in cand.values() for c in lst})
    labs, titles = {}, {}
    for i in range(0, len(ev_ids), 100):
        chunk = ev_ids[i:i + 100]
        for l in sb.table("event_direction_labels").select("event_id,label,size,timing").in_("event_id", chunk).execute().data:
            labs[l["event_id"]] = l
    band_model = dc.load_json("event_band_model.json")
    label_ann = dc.load_json("label_annotation.json")
    earn_model = dc.load_json("earnings_band_model.json")
    flag_rows = defaultdict(list)
    for f in paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").gte("filing_date", lo).lte("filing_date", date).order("id")):
        if f["security_id"] in cache_ids:
            flag_rows[f["security_id"]].append(f)
    for r in rows:
        lst = cand.get(r["id"])
        r["event"], r["mult"] = None, 1.0
        if lst:
            ev = sorted(lst, key=lambda c: (c["off"], c["event_id"]))[0]
            lab = labs.get(ev["event_id"], {})
            ev = dict(ev, label=lab.get("label"), size=lab.get("size"), timing=lab.get("timing"))
            m, note = dc.band_multiplier(band_model, ev["ptype"], ev["size"], ev["timing"], ev["off"])
            r["event"], r["mult"] = ev, (m if m else 1.0)
            if ev["label"] in ("good", "bad", "mixed", "unclear") and label_ann:
                ev["tilt"] = label_ann["mean_miss_percent"][ev["label"]]["day0" if ev["off"] == 0 else "day1"] / 100.0
        fl = dc.filing_flags(flag_rows.get(r["id"], []), U["master"], t)
        r["earn_off"], r["f701"] = fl["earn_off"], fl["f701"]
        r["mult"], r["mult_src"] = dc.combine_multiplier((r["mult"] if r["event"] else None), fl, earn_model, None, bool(r["event"]))
        r["zb"] = r["e1"] / (r["sd"] * math.sqrt(r["q_others"]) * r["mult"])

    # 1. the day
    spy = U["rm"][t]
    up = sum(1 for r in rows if r["ret"] > 0)
    day_r2 = 1 - sum(r["e1"] ** 2 for r in rows) / sum(r["ret"] ** 2 for r in rows)
    L = ["=" * 86, "DAY MAP: %s   (%d stocks with a valid decomposition)" % (date, n), "=" * 86]
    L.append("1. THE DAY      SPY %s | %d%% of stocks up | market-wide stress %.2fx (others' usual spread = 1.00x)" % (pct(spy), round(100.0 * up / n), math.sqrt(S / n)))
    L.append("                market + sector explained %.0f%% of the day's squared moves (the track record's all-days figure is 45%%)" % (100 * day_r2))
    L.append("")

    # 2. sectors
    L.append("2. SECTORS      equal-weighted move | beyond market | avg miss | typical miss (spreads) | stocks beyond 2 spreads")
    secs = defaultdict(list)
    for r in rows:
        secs[r["sector"]].append(r)
    sec_out = {}
    for name, lst in sorted(secs.items(), key=lambda kv: sum(r["ret"] for r in kv[1]) / len(kv[1])):
        m = sum(r["ret"] for r in lst) / len(lst)
        avg_miss = sum(r["e1"] for r in lst) / len(lst)
        typ = math.sqrt(sum(r["z2"] for r in lst) / len(lst))
        big = sum(1 for r in lst if r["z2"] > 4)
        sec_out[name] = {"n": len(lst), "move": m, "beyond_market": m - spy, "avg_miss": avg_miss, "typical_miss_spreads": typ, "beyond_2_spreads": big}
        L.append("   %-24s n=%-3d %9s %9s %9s %7.2f %5d of %d" % (name, len(lst), pct(m), pct(m - spy), pct(avg_miss), typ, big, len(lst)))
    L.append("   (an average miss far from zero means the sector's stocks missed the same way: a sector-wide piece chapter 1 did not capture that day)")
    L.append("")

    # 3. events
    evs = [r for r in rows if r["event"]]
    L.append("3. EVENTS       stocks with their own event on day 0 or +1: %d of %d (%.1f%%)" % (len(evs), n, 100.0 * len(evs) / n))
    ev_out = {"count": len(evs)}
    if evs:
        types, labels = defaultdict(int), defaultdict(int)
        for r in evs:
            types[r["event"]["ptype"]] += 1
            labels[r["event"]["label"] or "no label"] += 1
        L.append("                types: " + ", ".join("%s %d" % kv for kv in sorted(types.items(), key=lambda kv: -kv[1])))
        L.append("                labels: " + ", ".join("%s %d" % kv for kv in sorted(labels.items(), key=lambda kv: -kv[1])))
        share_z2 = sum(r["z2"] for r in evs) / S
        share_n = len(evs) / n
        enr = share_z2 / share_n
        ev_out.update({"share_of_unexplained": share_z2, "share_of_stocks": share_n, "enrichment": enr})
        L.append("                share of the day's unexplained squared miss: %.1f%% from %.1f%% of the stocks -> enrichment %.2fx (1.00 = events make no difference)" % (100 * share_z2, 100 * share_n, enr))
        L.append("                context: on own-event days overall the mean squared miss is about 2.7x other days (2.96 vs 1.11, the full validation); with only %d event stocks, one day swings widely and says little" % len(evs))
        agree = [(r["event"]["label"], r["e1"]) for r in evs if r["event"]["label"] in ("good", "bad")]
        if agree:
            k = sum(1 for lab, e in agree if (lab == "good" and e > 0) or (lab == "bad" and e < 0))
            L.append("                good/bad-labeled event stocks whose miss pointed the way the label did: %d of %d (chance is half; one day is a tiny sample)" % (k, len(agree)))
            ev_out["label_agreement"] = [k, len(agree)]
        L.append("                the largest event-stock misses (tilt = what similar labels averaged on that day; the label's pull is an annotation, not part of the price):")
        L.append("                %-7s %-22s %-8s %-9s %9s %9s %9s %6s %9s" % ("ticker", "type", "label", "size", "actual", "miss", "tilt", "band x", "band units"))
        for r in sorted(evs, key=lambda r: -abs(r["zb"]))[:topn]:
            ev = r["event"]
            L.append("                %-7s %-22s %-8s %-9s %9s %9s %9s %5.2fx %9.2f" % (r["ticker"], ev["ptype"][:22], ev["label"], ev["size"], pct(r["ret"]), pct(r["e1"]),
                                                                           pct(ev.get("tilt", 0.0)) if "tilt" in ev else "n/a", r["mult"], r["zb"]))
    else:
        L.append("                none recorded.")
    L.append("")

    # 3b. earnings windows and Regulation FD filings
    earn = [r for r in rows if r["earn_off"] is not None]
    n701 = sum(1 for r in rows if r["f701"] and r["earn_off"] is None and not r["event"])
    L.append("3b. EARNINGS      stocks in an earnings window (8-K item 2.02 filed today or the previous trading day): %d of %d (%.1f%%)" % (len(earn), n, 100.0 * len(earn) / n))
    ev_out["earnings_windows"] = len(earn)
    if earn:
        sh_z = sum(r["z2"] for r in earn) / S
        sh_n = len(earn) / n
        ev_out["earnings_enrichment"] = sh_z / sh_n
        L.append("                share of the day's unexplained squared miss: %.1f%% from %.1f%% of the stocks -> enrichment %.2fx (all days: about 6x; the band uses 2.72x on day 0, 2.47x on day +1)" % (100 * sh_z, 100 * sh_n, sh_z / sh_n))
        L.append("                %-7s %-22s %9s %9s %9s %6s %9s" % ("ticker", "window day", "actual", "miss", "", "band x", "band units"))
        for r in sorted(earn, key=lambda r: -abs(r["zb"]))[:topn]:
            L.append("                %-7s %-22s %9s %9s %9s %5.2fx %9.2f" % (r["ticker"], "day %d%s" % (r["earn_off"], " (+ event)" if r["event"] else ""), pct(r["ret"]), pct(r["e1"]), "", r["mult"], r["zb"]))
    L.append("                Regulation FD filings (item 7.01) with no event or earnings filing: %d stocks (a weak lead, about 1.36x)" % n701)
    L.append("")

    # 4. where the missing information is
    big = [r for r in rows if abs(r["zb"]) > 2.0]
    noev = [r for r in big if not r["event"] and r["earn_off"] is None]
    _ref = dc.load_json("tail_share_reference.json")
    _typ = None
    if _ref:
        _st = math.sqrt(sum(r["q_others"] for r in rows) / len(rows)) if rows else 1.0
        _bin = next((b for b in _ref.get("daily_share_by_stress", []) if b["from"] <= _st < b["to"]), None)
        _d, _lab = (_bin, "with %s market stress, %.2f" % (_bin["name"], _st)) if _bin else (_ref["daily_share"], "(all days pooled)")
        _typ = "typical day since 2006 %s: median %.1f%%, middle half %.1f%%-%.1f%%, 5th-95th percentile %.1f%%-%.1f%%" % (
            _lab, 100 * _d["median"], 100 * _d["p25"], 100 * _d["p75"], 100 * _d["p05"], 100 * _d["p95"])
    if not _typ:
        _typ = "a Gaussian reference would be 4.6%; the measured typical share is not loaded (run band_tail_share.py)"
    L.append("4. WHERE THE MISSING INFORMATION IS   stocks beyond 2 band units: %d (%.1f%% of stocks; %s)" % (len(big), 100.0 * len(big) / n, _typ))
    if big:
        L.append("                %d of them (%.0f%%) have NO recorded event and no earnings filing on day 0 or +1: the candidates for news, analyst or other information we have not recorded" % (len(noev), 100.0 * len(noev) / len(big)))
    L.append("                %-7s %-24s %9s %9s %9s %9s  %s" % ("ticker", "sector", "actual", "explained", "miss", "band units", "recorded event"))
    for r in sorted(rows, key=lambda r: -abs(r["zb"]))[:topn]:
        L.append("                %-7s %-24s %9s %9s %9s %9.2f  %s" % (r["ticker"], r["sector"][:24], pct(r["ret"]), pct(r["hyp"]), pct(r["e1"]), r["zb"],
                                                                  ("%s (%s)" % (r["event"]["ptype"], r["event"]["label"])) if r["event"] else "none"))
    L.append("")
    L.append("5. ZOOM         " + "   ".join("day_card.py %s %s" % (r["ticker"], date) for r in sorted(rows, key=lambda r: -abs(r["zb"]))[:3]))
    L.append("")
    L.append("   Explanations from same-day market and sector moves, not forecasts. A stock without a recorded event may still have had news (only 8-K filings are recorded).")
    print("\n".join(L))

    os.makedirs(os.path.join(dc.ROOT, "results", "maps"), exist_ok=True)
    with open(os.path.join(dc.ROOT, "results", "maps", "map_%s.json" % date), "w") as fh:
        json.dump({"date": date, "spy": spy, "n": n, "stress": math.sqrt(S / n), "day_r2": day_r2, "sectors": sec_out, "events": ev_out,
                   "stocks": [dict(r) for r in rows]}, fh, default=str)


if __name__ == "__main__":
    main()
