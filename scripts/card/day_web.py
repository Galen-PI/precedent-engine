#!/usr/bin/env python3
"""
day_web.py -- one company, one day: the web of everything recorded that touches it. READ-ONLY (writes nothing to the database).

Usage:   python3 scripts/card/day_web.py XOM 2020-03-09
Output:  scripts/card/out/web_XOM_2020-03-09.html  and  scripts/card/out/web_XOM_2020-03-09.json
View:    python3 -m http.server 8000 --directory scripts/card/out   (then open the forwarded port)

WHAT IT SHOWS (v1). Nodes: the date, market and policy items active that day, the company's sector, the stock, and company-side items.
Edges are drawn by what the flag ledger says, never by a made-up weight:
  solid teal   = ledger status proven or lead for that link
  dashed gray  = tested, no documented effect (ledger status null or retired)
  dotted       = untested, or the ledger row was not found
  thin gray    = belongs to / same sector
Every thread ends in one of: source (a recorded row you can open), tested with no documented effect, untested, or expired.
"Still affecting" follows evidence: daily shock flags count on their own day only (next-day tests found nothing); company events count on
day 0 and day +1 (the measured burst); the Fed state and market regime are shown as in force until replaced (not a measured effect).
Orders and laws are shown on their signing date only (no measured window). Nothing is added or multiplied across threads.

Magnitude only: no direction claims. Reads: securities, market_prices, vol_estimators, macro_long, fed_state_daily, market_regimes,
government_decisions, policy_area_sector_map, flag_ledger, flag_ledger_evidence, ev_ent, events, event_source_filings, sector_day_z,
sector_peer_ripple, company_sentiment_timeline.
"""
import os, sys, json, math, html, bisect
from collections import defaultdict
from datetime import date, timedelta

ORDINARY_PCT = (0.56, 1.17, 2.06)     # ordinary-day |move|/v64 p50/p80/p95 (event_move_dist, 2004+, all eras)
K_REF = 1.18                          # ordinary one-day range half-width in units of v64
EVENT_MULT = 1.25                     # frozen multiplier for day 0 and day +1 of non-capital-raise events (ledger: proven)

# (flag id, sector or ALL, ledger key). Industry-level evidence is mapped to the GICS sector by name (Banks -> Financials).
FLAG_LINKS = [
    ("oil", "Energy", "macro_oil_shock_energy_same_day"),
    ("yield", "Financials", "longhist_yield_shock_banks"),
    ("yield", "Health Care", "longhist_yield_shock_health_dampening"),
    ("yield", "Utilities", "longhist_yield_shock_utilities"),
    ("yield", "Real Estate", "longhist_yield_shock_real_estate"),
    ("credit", "Financials", "longhist_credit_widening_banks"),
    ("fed_day", "Financials", "fed_change_day_banks_amplification"),
    ("eo", "ALL", "eo_relevant_signing_market_wide_amplification"),
]
FLAG_NAMES = {"oil": "Oil move", "yield": "10-year yield move", "credit": "Credit spread", "fed_day": "Fed announcement",
              "fed_state": "Fed state", "regime": "Market regime", "eo": "Orders signed", "law": "Laws signed"}


WARNINGS = []


def get_sb():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def fetch(sb, table, cols, filters=(), order=None, desc=False, limit=None):
    rows, off = [], 0
    while True:
        q = sb.table(table).select(cols)
        for f in filters:
            q = f(q)
        if order:
            q = q.order(order, desc=desc)
        try:
            if limit is not None:
                return q.limit(limit).execute().data
            page = q.range(off, off + 999).execute().data
        except Exception as e:
            if "timeout" in str(e).lower() or "57014" in str(e):
                WARNINGS.append(table)
                return rows if limit is None else []
            raise
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return rows


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def fl(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def as_dict(sd):
    if isinstance(sd, dict):
        return sd
    if isinstance(sd, str):
        try:
            v = json.loads(sd)
            return v if isinstance(v, dict) else {}
        except ValueError:
            return {}
    return {}


def load_ledger(sb):
    led = {r["flag_key"]: r for r in fetch(sb, "flag_ledger", "flag_key,status,description,notes")}
    ev = defaultdict(list)
    for r in fetch(sb, "flag_ledger_evidence", "flag_key,era,n,estimate,se,unit"):
        ev[r["flag_key"]].append(r)
    return led, ev


def led_info(led, ev, key):
    r = led.get(key)
    if not r:
        return None, "ledger row not found: %s" % key
    bits = []
    for e in ev.get(key, [])[:3]:
        v = fl(e.get("estimate"))
        if v is not None:
            bits.append("%s %.3f (n=%s)" % (e.get("era"), v, e.get("n")))
    return r["status"], "%s: %s%s" % (key, r["status"], ("; " + "; ".join(bits)) if bits else "")


def find_key(led, *subs):
    for k in sorted(led):
        if all(s in k for s in subs):
            return k
    return None


def edge_kind(status):
    if status in ("proven", "lead"):
        return "solid"
    if status in ("null", "retired"):
        return "dashed"
    return "dotted"


def end_text(kind):
    return {"solid": "ledger supports a link", "dashed": "tested: no detectable average effect (this date may differ)", "dotted": "untested (or ledger row not found)"}[kind]


def short(s, n):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n - 1] + "\u2026"


def build_web(sb, ticker, ds):
    day = date.fromisoformat(ds)
    sec = fetch(sb, "securities", "id,entity_id,ticker,sector", [lambda q: q.eq("ticker", ticker)], limit=5)
    if not sec:
        sys.exit("No security with ticker " + ticker)
    sid, eid, sector = sec[0]["id"], sec[0]["entity_id"], sec[0].get("sector") or "Unclassified"
    led, evid = load_ledger(sb)

    prices = fetch(sb, "market_prices", "price_date,adjusted_close", [lambda q: q.eq("security_id", sid),
                   lambda q: q.gte("price_date", (day - timedelta(days=170)).isoformat()), lambda q: q.lte("price_date", ds)], order="price_date")
    prices = [p for p in prices if p.get("adjusted_close") is not None]
    dates = [p["price_date"] for p in prices]
    if not dates or dates[-1] != ds:
        sys.exit("No price for %s on %s (not a trading day, or no data). Last price date found: %s" % (ticker, ds, dates[-1] if dates else "none"))
    i_t = len(dates) - 1
    ret = fl(prices[i_t]["adjusted_close"]) / fl(prices[i_t - 1]["adjusted_close"]) - 1 if i_t >= 1 else None
    ve = fetch(sb, "vol_estimators", "d,v64", [lambda q: q.eq("security_id", sid), lambda q: q.eq("d", ds)], limit=1)
    v64 = fl(ve[0]["v64"]) if ve else None
    z = abs(ret) / v64 if (ret is not None and v64) else None

    nodes, edges, facts = [], [], {}
    sourcerows = defaultdict(list)
    checked = []

    def add_node(nid, col, label, sub, kind, det=None, src=None):
        nodes.append({"id": nid, "col": col, "label": label, "sub": sub, "kind": kind, "details": det or [], "sources": src or []})

    def add_edge(a, b, kind, status_text, end=None):
        edges.append({"from": a, "to": b, "kind": kind, "text": status_text, "end": end or end_text(kind)})

    # ---- market and policy items (column 1)
    def last_two(sid_):
        rows = fetch(sb, "macro_long", "obs_date,value", [lambda q: q.eq("series_id", sid_), lambda q: q.lte("obs_date", ds)], order="obs_date", desc=True, limit=2)
        rows = [(r["obs_date"], fl(r["value"])) for r in rows if fl(r["value"]) is not None]
        return rows
    flags = {}
    oil = last_two("DCOILWTICO")
    if len(oil) == 2 and oil[0][0] == ds:
        (d1, v1), (d0, v0) = oil[0], oil[1]
        chg = v1 / v0 - 1
        flags["oil"] = dict(active=(v0 > 5 and v1 > 5 and abs(chg) >= 0.03), sub="%+.1f%%" % (100 * chg),
                            src=["macro_long DCOILWTICO %s %.2f; previous %s %.2f" % (d1, v1, d0, v0)])
    else:
        flags["oil"] = dict(active=False, sub="no observation that day", src=["macro_long DCOILWTICO: no row on %s" % ds])
    y10 = last_two("DGS10")
    if len(y10) == 2 and y10[0][0] == ds:
        dy = y10[0][1] - y10[1][1]
        flags["yield"] = dict(active=abs(dy) >= 0.10 - 1e-9, sub="%+.0fbp" % (100 * dy),
                              src=["macro_long DGS10 %s %.2f; previous %s %.2f" % (y10[0][0], y10[0][1], y10[1][0], y10[1][1])])
    else:
        flags["yield"] = dict(active=False, sub="no observation that day", src=["macro_long DGS10: no row on %s" % ds])
    aaa, baa = last_two("DAAA"), last_two("DBAA")
    if len(aaa) == 2 and len(baa) == 2 and aaa[0][0] == ds and baa[0][0] == ds and aaa[1][0] == baa[1][0]:
        dsp = (baa[0][1] - aaa[0][1]) - (baa[1][1] - aaa[1][1])
        flags["credit"] = dict(active=dsp >= 0.03 - 1e-9, sub="%+.0fbp" % (100 * dsp),
                               src=["macro_long DBAA-DAAA %s spread %.2f; previous %s spread %.2f" % (ds, baa[0][1] - aaa[0][1], aaa[1][0], baa[1][1] - aaa[1][1])])
    else:
        flags["credit"] = dict(active=False, sub="no observation that day", src=["macro_long DAAA/DBAA: no matching rows on %s" % ds])

    fed_dec = fetch(sb, "government_decisions", "id,decision_date,title,source_url", [lambda q: q.eq("decision_type", "interest_rate"),
                    lambda q: q.gte("decision_date", (day - timedelta(days=1)).isoformat()), lambda q: q.lte("decision_date", ds)])
    if fed_dec:
        dd = fed_dec[0]["decision_date"]
        flags["fed_day"] = dict(active=True, sub="announced %s (%s)" % (dd, "day 0" if dd == ds else "day +1"),
                                src=["government_decisions %s %s" % (fed_dec[0]["id"], fed_dec[0].get("source_url") or "")])
    else:
        flags["fed_day"] = dict(active=False, sub="none", src=[])

    last_dec = fetch(sb, "government_decisions", "decision_date,direction,structured_data", [lambda q: q.eq("decision_type", "interest_rate"),
                     lambda q: q.lte("decision_date", ds)], order="decision_date", desc=True, limit=1)
    fs = []
    if last_dec:
        r0 = last_dec[0]
        sd0 = as_dict(r0.get("structured_data"))
        since = (day - date.fromisoformat(str(r0["decision_date"])[:10])).days
        st0 = ("tightening" if r0.get("direction") == "hiking" else "easing") if since < 365 else "hold"
        fs = [{"day": ds, "target_upper": sd0.get("new_rate"), "last_change": sd0.get("change"), "last_change_date": str(r0["decision_date"])[:10],
               "days_since_change": since, "state": st0}]
    else:
        checked.append("Fed state: no interest_rate decision row on or before this date (rows start 2015-12-16)")
    regs = [r for r in fetch(sb, "market_regimes", "id,name,start_date,end_date,description", [lambda q: q.lte("start_date", ds)])
            if not r.get("end_date") or r["end_date"] >= ds]

    gd = fetch(sb, "government_decisions", "id,decision_date,decision_type,title,source_url,source_document_number,structured_data", [lambda q: q.eq("decision_date", ds)])
    eos = [r for r in gd if r["decision_type"] == "executive_order"]
    laws = [r for r in gd if r["decision_type"] == "enacted_law"]
    eo_rel = [r for r in eos if as_dict(r.get("structured_data")).get("relevance_verdict") == "relevant"]
    law_rel = [r for r in laws if as_dict(r.get("structured_data")).get("relevance_verdict") == "relevant"]
    flags["eo"] = dict(active=len(eo_rel) > 0, sub="%d signed (%d relevant)" % (len(eos), len(eo_rel)),
                       src=["government_decisions %s %s" % (r["id"], r.get("source_url") or "") for r in eos[:12]],
                       det=[short(r["title"], 110) + ("" if as_dict(r.get("structured_data")).get("relevance_verdict") == "relevant" else " [not relevant]") for r in eos[:12]])
    flags["law"] = dict(active=len(law_rel) > 0, sub="%d signed (%d relevant)" % (len(laws), len(law_rel)),
                        src=["government_decisions %s %s" % (r["id"], r.get("source_url") or "") for r in laws[:12]],
                        det=[short(r["title"], 110) for r in law_rel[:12]])

    links_for_sector = defaultdict(list)
    for fid, sct, key in FLAG_LINKS:
        if sct in (sector, "ALL"):
            links_for_sector[fid].append((sct, key))

    need_all = False
    sector_in_kinds = []
    market_ids = []
    for fid in ("oil", "yield", "credit", "fed_day", "eo", "law"):
        f = flags[fid]
        linked = fid in links_for_sector or fid == "law"
        if not f["active"] and not (linked and fid in ("oil", "yield", "credit")):
            checked.append("%s: none active (%s)" % (FLAG_NAMES[fid], f["sub"]))
            continue
        nid = "m_" + fid
        add_node(nid, 1, FLAG_NAMES[fid], f["sub"] + ("" if f["active"] else ", not active"), "new" if f["active"] else "inactive",
                 f.get("det"), f.get("src"))
        market_ids.append(nid)
        if not f["active"]:
            continue
        if fid == "law":
            continue
        if fid in links_for_sector:
            for sct, key in links_for_sector[fid]:
                status, text = led_info(led, evid, key)
                kind = edge_kind(status)
                tgt = "s_all" if sct == "ALL" else "s_sector"
                need_all = need_all or sct == "ALL"
                add_edge(nid, tgt, kind, text)
                if tgt == "s_sector":
                    sector_in_kinds.append(kind)
        else:
            add_edge(nid, "s_sector", "dotted", "no ledger test for %s on %s" % (FLAG_NAMES[fid], sector))
            sector_in_kinds.append("dotted")
    # laws: sector map
    if flags["law"]["active"]:
        pmap = defaultdict(list)
        for r in fetch(sb, "policy_area_sector_map", "policy_area,sector,grp"):
            pmap[r["policy_area"]].append((r["sector"], r["grp"]))
        lkey = find_key(led, "law", "sign")
        status, text = led_info(led, evid, lkey) if lkey else (None, "ledger row not found: no key containing 'law' and 'sign'")
        kind = edge_kind(status)
        to_sector = to_all = False
        notes = []
        for r in law_rel:
            sd = as_dict(r.get("structured_data"))
            area = next((v for k, v in sd.items() if "policy" in k.lower() and isinstance(v, str)), None)
            if not area:
                notes.append("no policy-area key in structured_data for %s" % short(r["title"], 60))
                continue
            for sct, grp in pmap.get(area, []):
                if grp == "sector_specific" and sct == sector:
                    to_sector = True
                elif grp == "market_wide":
                    to_all = True
        flags["law"]["det"] = flags["law"].get("det", []) + notes
        if to_sector:
            add_edge("m_law", "s_sector", kind, text)
            sector_in_kinds.append(kind)
        if to_all:
            add_edge("m_law", "s_all", kind, text)
            need_all = True
        if not to_sector and not to_all:
            add_edge("m_law", "s_sector", "dotted", "law policy area not mapped to %s (or key not found)" % sector)
            sector_in_kinds.append("dotted")
    if fs:
        r = fs[0]
        add_node("m_fedstate", 1, "Fed state", "%s, day %s" % (r["state"], r["days_since_change"]), "persist",
                 ["target upper %s; last change %s on %s" % (r["target_upper"], r["last_change"], r["last_change_date"]), "in force until replaced; no measured effect window"],
                 ["government_decisions interest_rate %s (state computed here with the view's rule: direction of the last change if under 365 days old, else hold)" % r["last_change_date"]])
        market_ids.append("m_fedstate")
        add_edge("m_fedstate", "s_sector", "dotted", "no ledger test of the Fed state on %s" % sector)
        sector_in_kinds.append("dotted")
    for r in regs[:2]:
        add_node("m_reg_%s" % r["id"], 1, "Regime", short(r["name"], 22) + ", hindsight", "persist",
                 [short(r.get("description") or "", 200), "hindsight label, context only"], ["market_regimes id=%s" % r["id"]])
        market_ids.append("m_reg_%s" % r["id"])
        add_edge("m_reg_%s" % r["id"], "s_sector", "dotted", "hindsight label; no ledger test", "context only (named afterwards)")
    if not regs:
        checked.append("Market regime: none covers this date")

    # ---- sector (column 2)
    sd_rows = fetch(sb, "sector_day_z", "day,n,mean_z", [lambda q: q.eq("sector", sector), lambda q: q.gte("day", (day - timedelta(days=370)).isoformat()),
                    lambda q: q.lte("day", ds)], order="day")
    today_row = next((r for r in sd_rows if r["day"] == ds), None)
    prior = [fl(r["mean_z"]) for r in sd_rows if r["day"] < ds and fl(r["mean_z"]) is not None]
    sec_sub, sec_det = "no sector data", []
    if today_row and prior:
        ratio = fl(today_row["mean_z"]) / _median(prior)
        sec_sub = "%.2fx its usual move" % ratio
        sec_det = ["sector_day_z mean_z %.3f over %s stocks; prior-year median %.3f (a median, so a past crisis does not inflate 'usual')" % (fl(today_row["mean_z"]), today_row["n"], _median(prior))]
        facts["sector_ratio"] = ratio
    add_node("s_sector", 2, sector, sec_sub, "new" if "solid" in sector_in_kinds else "plain", sec_det, ["sector_day_z sector=%s day=%s" % (sector, ds)])
    if need_all:
        add_node("s_all", 2, "All stocks", "market-wide", "plain", [], [])

    # ---- the stock (column 3)
    stock_sub = "no return" if ret is None else "%+.1f%%, z %s" % (100 * ret, "n/a" if z is None else "%.2f" % z)
    det = []
    if v64:
        det.append("ordinary one-day range: +-%.1f%% (%.2f x v64 %.4f)" % (100 * K_REF * v64, K_REF, v64))
        if ret is not None:
            det.append("move %+.2f%% is %s the ordinary range" % (100 * ret, "inside" if abs(ret) <= K_REF * v64 else "outside"))
    if z is not None:
        p50, p80, p95 = ORDINARY_PCT
        pos = "below the ordinary median" if z < p50 else ("between the ordinary median and 80th percentile" if z < p80 else ("between the ordinary 80th and 95th percentiles" if z < p95 else "above the ordinary 95th percentile"))
        det.append("z %.2f is %s (ordinary-day percentiles %.2f / %.2f / %.2f)" % (z, pos, p50, p80, p95))
    if z is not None and today_row and fl(today_row["mean_z"]):
        det.append("this stock's z is %.2fx the average z of its sector's stocks today (%.3f)" % (z / fl(today_row["mean_z"]), fl(today_row["mean_z"])))
    add_node("c_stock", 3, ticker, stock_sub, "stock", det, ["market_prices %s %s; vol_estimators v64 %s" % (ticker, ds, v64)])
    add_edge("s_sector", "c_stock", "member", "belongs to the %s sector" % sector, "belongs to")
    if need_all:
        add_edge("s_all", "c_stock", "member", "applies to every stock", "belongs to")

    # ---- company side (column 4)
    ee = fetch(sb, "ev_ent", "event_id,entity_id,sector,d,ptype,gov", [lambda q: q.eq("entity_id", eid),
               lambda q: q.gte("d", (day - timedelta(days=200)).isoformat()), lambda q: q.lte("d", ds)], order="d")
    own = []
    for r in ee:
        off = i_t - bisect.bisect_left(dates, r["d"])
        own.append((off, r))
    ids = [r["event_id"] for off, r in own]
    titles = {}
    filings = defaultdict(list)
    if ids:
        pick = ids[-40:]
        for r in fetch(sb, "events", "id,title,event_date", [lambda q: q.in_("id", pick)]):
            titles[r["id"]] = r
        for r in fetch(sb, "event_source_filings", "event_id,ticker,filing_date,accession_number", [lambda q: q.in_("event_id", pick)]):
            filings[r["event_id"]].append(r)
    gstatus, gtext = led_info(led, evid, "event_burst_day0_1")
    active_own = [(o, r) for o, r in own if o in (0, 1)]
    for k, (o, r) in enumerate(sorted(active_own, key=lambda t: t[0])):
        t = titles.get(r["event_id"], {}).get("title") or "(title not found)"
        tkey = find_key(led, "event_type", r["ptype"])
        st, tx = led_info(led, evid, tkey) if tkey else (None, None)
        use_status, use_text = (st, tx) if tkey else (gstatus, gtext)
        nid = "c_ev_%d" % k
        add_node(nid, 4, short(r["ptype"], 22), "day %s: %s" % ("0" if o == 0 else "+1", short(t, 20)), "new" if o == 0 else "persist",
                 [t, "ledger (type): " + (tx or "no type-specific row"), "ledger (general burst): " + gtext, "gov-direct flag: %s" % r.get("gov")],
                 ["events id=%s" % r["event_id"]] + ["filing %s %s %s" % (f["ticker"], f["filing_date"], f["accession_number"]) for f in filings.get(r["event_id"], [])])
        add_edge(nid, "c_stock", edge_kind(use_status), use_text, "burst window: day 0 and day +1 only")
    older = [(o, r) for o, r in own if o >= 2]
    if not active_own:
        checked.append("Company events on day 0 or day +1: none")
        if older:
            o, r = min(older, key=lambda t: t[0])
            t = titles.get(r["event_id"], {}).get("title") or "(title not found)"
            add_node("c_ev_old", 4, "Last event: expired", "%s, %d days ago" % (short(r["ptype"], 16), o), "expired",
                     [t, "outside the measured burst window (day 0 and day +1)"], ["events id=%s" % r["event_id"]] +
                     ["filing %s %s %s" % (f["ticker"], f["filing_date"], f["accession_number"]) for f in filings.get(r["event_id"], [])])
            add_edge("c_ev_old", "c_stock", "dotted", "expired: %d trading days ago" % o, "expired")
        else:
            add_node("c_ev_none", 4, "Company events", "none in the last 200 days", "expired", [], ["ev_ent entity=%s" % eid])
            add_edge("c_ev_none", "c_stock", "dotted", "no company events found", "none found")

    peers = fetch(sb, "ev_ent", "event_id,entity_id,sector,d,ptype", [lambda q: q.eq("sector", sector), lambda q: q.eq("d", ds), lambda q: q.neq("entity_id", eid)], limit=300)
    if peers:
        pids = [p["event_id"] for p in peers][:40]
        ptitles = {r["id"]: r["title"] for r in fetch(sb, "events", "id,title", [lambda q: q.in_("id", pids)])}
        rip = fetch(sb, "sector_peer_ripple", "trigger_event_id,trigger_ticker,trigger_abnormal_return_5d,peer_abnormal_return_5d",
                    [lambda q: q.eq("peer_entity_id", eid), lambda q: q.in_("trigger_event_id", pids)])
        pkey = find_key(led, "peer")
        pst, ptx = led_info(led, evid, pkey) if pkey else (None, "no ledger row for peer events")
        det = [short(ptitles.get(p["event_id"], "(title not found)"), 100) + " [%s]" % p["ptype"] for p in peers[:6]]
        for r in rip[:5]:
            det.append("peer ripple: trigger %s 5-day abnormal %s; this stock 5-day abnormal %s" % (r["trigger_ticker"], r["trigger_abnormal_return_5d"], r["peer_abnormal_return_5d"]))
        add_node("c_peers", 4, "Peer events today", "%d in %s" % (len(peers), sector), "new", det + ["ledger: " + ptx],
                 ["events id=%s" % p["event_id"] for p in peers[:8]])
        add_edge("c_peers", "c_stock", edge_kind(pst), ptx, "peer ripple (untested unless a ledger row exists)")
    else:
        checked.append("Peer events in %s today: none" % sector)

    st_rows = fetch(sb, "company_sentiment_timeline", "date,article_count,avg_tone", [lambda q: q.eq("entity_id", eid),
                    lambda q: q.gte("date", (day - timedelta(days=35)).isoformat()), lambda q: q.lte("date", ds)], order="date")
    today_t = next((r for r in st_rows if r["date"] == ds), None)
    if today_t and fl(today_t["avg_tone"]) is not None:
        tr = [fl(r["avg_tone"]) for r in st_rows if r["date"] < ds and fl(r["avg_tone"]) is not None]
        zt = None
        if len(tr) >= 10:
            mu = sum(tr) / len(tr)
            sd_ = math.sqrt(sum((x - mu) ** 2 for x in tr) / len(tr))
            zt = (fl(today_t["avg_tone"]) - mu) / sd_ if sd_ > 0 else None
        skey = find_key(led, "sentiment") or find_key(led, "gdelt")
        sst, stx = led_info(led, evid, skey) if skey else (None, "no ledger row for news tone")
        add_node("c_tone", 4, "News tone", "%+.2f, %s articles%s" % (fl(today_t["avg_tone"]), today_t["article_count"], "" if zt is None else ", z %+.1f" % zt), "new",
                 ["ledger: " + stx, "tone may follow the price move rather than cause it"], ["company_sentiment_timeline entity=%s date=%s" % (eid, ds)])
        add_edge("c_tone", "c_stock", edge_kind(sst), stx, "may follow price")
    else:
        checked.append("News tone: no company row for this date (coverage starts 2015)")

    checked.extend("COULD NOT READ %s (query timed out): unknown, not empty" % t for t in sorted(set(WARNINGS)))
    facts.update({"ticker": ticker, "date": ds, "sector": sector, "return": ret, "v64": v64, "z": z,
                  "daily_markers_active": sum(1 for f in ("oil", "yield", "credit") if flags[f]["active"]),
                  "extra_active": [f for f in ("fed_day", "eo", "law") if flags[f]["active"]], "checked": checked})
    return {"facts": facts, "nodes": nodes, "edges": edges}


CSS = """
:root{--bg:#fff;--fg:#1f1f1e;--mut:#5f5e5a;--tf:#E1F5EE;--ts:#0F6E56;--tt:#085041;--gf:#F1EFE8;--gs:#888780;--gt:#444441;--line:#888780;--ok:#1D9E75;--dot:#B4B2A9}
@media (prefers-color-scheme: dark){:root{--bg:#1c1c1a;--fg:#e8e6df;--mut:#b4b2a9;--tf:#04342C;--ts:#5DCAA5;--tt:#9FE1CB;--gf:#2c2c2a;--gs:#888780;--gt:#d3d1c7;--line:#9c9a92;--ok:#5DCAA5;--dot:#6a6963}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:24px auto;max-width:1100px;padding:0 16px}
h1{font-size:22px;font-weight:500}h2{font-size:17px;font-weight:500;margin-top:28px}
table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid var(--dot);padding:6px 8px;text-align:left;vertical-align:top}
.n-new rect,.n-stock rect{fill:var(--tf);stroke:var(--ts);stroke-width:1.2}.n-persist rect{fill:var(--tf);stroke:var(--ts);stroke-width:1.2;stroke-dasharray:5 3}
.n-inactive rect,.n-plain rect{fill:var(--gf);stroke:var(--gs);stroke-width:1}.n-expired rect{fill:var(--gf);stroke:var(--gs);stroke-width:1;stroke-dasharray:5 3}
.n-new text,.n-persist text,.n-stock text{fill:var(--tt)}.n-inactive text,.n-plain text,.n-expired text{fill:var(--gt)}.n-inactive{opacity:.6}
.lab{font-size:13px;font-weight:500}.sub{font-size:11px}
.e-solid{stroke:var(--ok);stroke-width:2;fill:none}.e-dashed{stroke:var(--line);stroke-width:1.2;stroke-dasharray:5 3;fill:none}
.e-dotted{stroke:var(--dot);stroke-width:1.4;stroke-dasharray:1 4;fill:none;stroke-linecap:round}.e-member,.e-hub{stroke:var(--line);stroke-width:1;fill:none}
.legend span{display:inline-block;margin-right:18px;font-size:13px;color:var(--mut)}
"""


def linkify(s):
    import re
    esc = html.escape(s)
    return re.sub(r'(https?://[^\s<]+)', r'<a href="\1">\1</a>', esc)


def layout(nodes):
    X = {1: 150, 2: 410, 3: 600, 4: 800}
    Wd = {1: 210, 2: 140, 3: 140, 4: 230}
    cols = defaultdict(list)
    for n in nodes:
        cols[n["col"]].append(n)
    rows = max([len(cols[1]), len(cols[4]), 2])
    H = rows * 64 + 80
    mid = H / 2
    pos = {}
    for c, lst in cols.items():
        for i, n in enumerate(lst):
            cy = mid - (len(lst) - 1) * 32 + i * 64
            pos[n["id"]] = (X[c], cy - 25, Wd[c], 50, c)
    return pos, H, mid


def render_svg(web):
    nodes, edges = web["nodes"], web["edges"]
    pos, H, mid = layout(nodes)
    W = 1060
    out = ['<svg viewBox="0 0 %d %d" width="100%%" role="img"><title>Web for %s on %s</title>' % (W, H, html.escape(web["facts"]["ticker"]), web["facts"]["date"]),
           '<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>']
    hub = (65, mid)
    for n in nodes:
        if n["col"] == 1:
            x, y, w, h, c = pos[n["id"]]
            out.append('<line class="e-hub" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (hub[0] + 45, hub[1], x, y + h / 2))
    for e in edges:
        if e["from"] not in pos or e["to"] not in pos:
            continue
        xa, ya, wa, ha, ca = pos[e["from"]]
        xb, yb, wb, hb, cb = pos[e["to"]]
        if ca < cb:
            x1, x2 = xa + wa, xb
        else:
            x1, x2 = xa, xb + wb
        y1, y2 = ya + ha / 2, yb + hb / 2
        mk = ' marker-end="url(#arr)"' if e["kind"] != "member" else ""
        out.append('<line class="e-%s" x1="%d" y1="%d" x2="%d" y2="%d"%s/>' % (e["kind"], x1, y1, x2 - (3 if ca < cb else -3), y2, mk))
    out.append('<g class="n-new"><circle cx="%d" cy="%d" r="45" style="fill:var(--tf);stroke:var(--ts);stroke-width:1.2"/><text class="lab" x="%d" y="%d" text-anchor="middle" dominant-baseline="central" style="fill:var(--tt)">%s</text></g>'
               % (hub[0], hub[1], hub[0], hub[1], web["facts"]["date"]))
    for n in nodes:
        x, y, w, h, c = pos[n["id"]]
        out.append('<a href="#%s"><g class="n-%s"><rect x="%d" y="%d" width="%d" height="%d" rx="8"/>'
                   '<text class="lab" x="%d" y="%d" text-anchor="middle" dominant-baseline="central">%s</text>'
                   '<text class="sub" x="%d" y="%d" text-anchor="middle" dominant-baseline="central">%s</text></g></a>'
                   % (n["id"], n["kind"], x, y, w, h, x + w / 2, y + 18, html.escape(n["label"]), x + w / 2, y + 36, html.escape(n["sub"])))
    out.append("</svg>")
    return "".join(out)


def render_html(web):
    f, nodes, edges = web["facts"], web["nodes"], web["edges"]
    names = {n["id"]: n["label"] for n in nodes}
    names["c_stock"] = f["ticker"]
    page = ['<!doctype html><html><head><meta charset="utf-8"><title>%s %s web</title><style>%s</style></head><body>' % (f["ticker"], f["date"], CSS),
            "<h1>%s on %s (%s)</h1>" % (html.escape(f["ticker"]), f["date"], html.escape(f["sector"]))]
    mv = "no return" if f["return"] is None else "%+.2f%%" % (100 * f["return"])
    zz = "n/a" if f["z"] is None else "%.2f" % f["z"]
    page.append("<p>Move %s, z %s (|move| / prior 64-day volatility). Daily markers active: %d of 3 (oil, yield, credit)%s. Counted as facts; nothing is added or multiplied. Magnitude only.</p>"
                % (mv, zz, f["daily_markers_active"], (" plus " + ", ".join(f["extra_active"])) if f["extra_active"] else ""))
    page.append('<div class="legend"><span>solid line: ledger supports a link</span><span>dashed: tested, no detectable average effect</span><span>dotted: untested</span>'
                '<span>solid box: new that day</span><span>dashed box: still in force or expired</span><span>faded: not active</span></div>')
    page.append(render_svg(web))
    page.append("<h2>Where the threads end</h2><table><tr><th>From</th><th>To</th><th>Line</th><th>End</th><th>Ledger or fact</th></tr>")
    for e in edges:
        page.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            html.escape(names.get(e["from"], e["from"])), html.escape(names.get(e["to"], e["to"])), e["kind"], html.escape(e["end"]), html.escape(e["text"] or "")))
    counts = defaultdict(int)
    for e in edges:
        counts[e["kind"]] += 1
    page.append("</table><p>Threads: %d solid, %d dashed, %d dotted (untested or expired), %d membership.</p>" % (counts["solid"], counts["dashed"], counts["dotted"], counts["member"]))
    page.append("<h2>Checked, nothing found</h2><ul>" + "".join("<li>%s</li>" % html.escape(c) for c in f.get("checked", [])) + "</ul>")
    page.append("<h2>Nodes and sources</h2><table><tr><th>Node</th><th>Detail</th><th>Sources (open these)</th></tr>")
    for n in nodes:
        page.append('<tr id="%s"><td><b>%s</b><br>%s</td><td>%s</td><td>%s</td></tr>' % (
            n["id"], html.escape(n["label"]), html.escape(n["sub"]), "<br>".join(html.escape(d) for d in n["details"]), "<br>".join(linkify(s) for s in n["sources"])))
    page.append("</table></body></html>")
    return "".join(page)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    ticker, ds = sys.argv[1].upper(), sys.argv[2]
    sb = get_sb()
    web = build_web(sb, ticker, ds)
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(outdir, exist_ok=True)
    base = os.path.join(outdir, "web_%s_%s" % (ticker, ds))
    with open(base + ".json", "w") as fh:
        json.dump(web, fh, indent=1, default=str)
    with open(base + ".html", "w") as fh:
        fh.write(render_html(web))
    print("nodes %d, edges %d -> %s.html" % (len(web["nodes"]), len(web["edges"]), base))
    fx = web["facts"]
    print("move %s, z %s, sector ratio %s, daily markers active %d of 3, checked-and-empty %d" % (
        "n/a" if fx["return"] is None else "%+.2f%%" % (100 * fx["return"]), "n/a" if fx["z"] is None else "%.2f" % fx["z"],
        "n/a" if fx.get("sector_ratio") is None else "%.2f" % fx["sector_ratio"], fx["daily_markers_active"], len(fx["checked"])))
    for e in web["edges"]:
        print("  %-8s %s -> %s | %s" % (e["kind"], e["from"], e["to"], (e["text"] or "")[:90]))


if __name__ == "__main__":
    main()
