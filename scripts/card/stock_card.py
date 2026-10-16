#!/usr/bin/env python3
"""
stock_card.py -- one company, one year, as a standalone HTML "stock card".

Usage:   python3 scripts/card/stock_card.py BMY 2019
Output:  scripts/card/out/card_BMY_2019.html
View:    python3 -m http.server 8000 --directory scripts/card/out   (then open the forwarded port)

READ-ONLY. Reads market_prices, vol_estimators, events (+ type links), flag_ledger, flag_ledger_evidence,
event_curve_pooled, event_move_dist, fed_state_daily, market_regimes, macro_long, flag_range_dist, law_stage_dates,
government_decisions and policy_area_sector_map. Writes nothing to the database.
Only ledger rows marked 'proven' change what the card draws (the orange event shading). The context lanes under the
price chart are context only, each labelled with its ledger status. Magnitude only: no direction claims.
"""
import os, sys, json, bisect
from supabase import create_client

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
K_REF = 1.18   # one-day range half-width in units of the prior-day 64-day volatility (ordinary days cover ~80%)


def fl(x):
    return None if x is None else float(x)


def paginated(table, select, filters=None, order=None):
    rows, off = [], 0
    while True:
        q = sb.table(table).select(select)
        for f in (filters or []):
            q = f(q)
        if order:
            q = q.order(order)
        page = q.range(off, off + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return rows


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    ticker, year = sys.argv[1].upper(), int(sys.argv[2])

    sec = sb.table("securities").select("id,entity_id,ticker,sector").eq("ticker", ticker).execute().data
    if not sec:
        sys.exit("No security with ticker " + ticker)
    sid, eid, sector = sec[0]["id"], sec[0]["entity_id"], sec[0].get("sector")

    prices = paginated("market_prices", "price_date,open,high,low,close,adjusted_close,volume",
                       [lambda q: q.eq("security_id", sid),
                        lambda q: q.gte("price_date", "%d-12-01" % (year - 1)),
                        lambda q: q.lte("price_date", "%d-12-31" % year)], order="price_date")
    prices = [p for p in prices if None not in (p["adjusted_close"], p["open"], p["high"], p["low"])]
    dates = [p["price_date"] for p in prices]
    start_i = max(bisect.bisect_left(dates, "%d-01-01" % year), 1)
    if start_i >= len(prices):
        sys.exit("Not enough price data for %s %d" % (ticker, year))
    n_days = len(prices) - start_i

    vols = paginated("vol_estimators", "d,v64",
                     [lambda q: q.eq("security_id", sid),
                      lambda q: q.gte("d", "%d-01-01" % year),
                      lambda q: q.lte("d", "%d-12-31" % year)], order="d")
    v64 = {v["d"]: fl(v["v64"]) for v in vols}

    # ---- events for this company and year (bundled summaries excluded) ----
    rel = paginated("event_entity_relationships", "event_id", [lambda q: q.eq("entity_id", eid)])
    all_ids = [r["event_id"] for r in rel]
    cand = []
    for i in range(0, len(all_ids), 100):
        chunk = all_ids[i:i + 100]
        cand += sb.table("events").select("id,title,event_date").in_("id", chunk) \
            .gte("event_date", "%d-01-01" % year).lt("event_date", "%d-01-01" % (year + 1)).execute().data
    ids = [e["id"] for e in cand]
    bundled = set()
    for i in range(0, len(ids), 100):
        bundled |= {r["event_id"] for r in sb.table("event_component_dates").select("event_id")
                    .in_("event_id", ids[i:i + 100]).execute().data}
    cand = [e for e in cand if e["id"] not in bundled]
    ids = [e["id"] for e in cand]
    tnames = {}
    if ids:
        trel = []
        for i in range(0, len(ids), 100):
            trel += sb.table("event_type_relationships").select("event_id,event_type_id") \
                .in_("event_id", ids[i:i + 100]).execute().data
        tids = sorted({r["event_type_id"] for r in trel})
        names = {t["id"]: t["name"] for t in sb.table("event_types").select("id,name").in_("id", tids).execute().data} if tids else {}
        for r in trel:
            nm = names.get(r["event_type_id"])
            if nm and (r["event_id"] not in tnames or nm < tnames[r["event_id"]]):
                tnames[r["event_id"]] = nm
    events = []
    for e in sorted(cand, key=lambda x: str(x["event_date"])):
        ed = str(e["event_date"])[:10]
        idx = bisect.bisect_left(dates, ed) - start_i
        events.append({"id": e["id"], "title": e["title"], "date": ed, "type": tnames.get(e["id"], "unknown"),
                       "i": idx if 0 <= idx < n_days else None})

    # ---- ledger: only 'proven' rows change what is drawn ----
    ledger = sb.table("flag_ledger").select("flag_key,family,description,status,multiplier").execute().data
    evid = sb.table("flag_ledger_evidence").select("flag_key,era,n,estimate,se,unit").execute().data
    lrow = next((r for r in ledger if r["flag_key"] == "event_daily_range_coverage"), None)
    mult, widened_on = 1.0, False
    if lrow and lrow["status"] == "proven" and lrow["multiplier"]:
        mult, widened_on = float(lrow["multiplier"]), True
    else:
        print("NOTE: event_daily_range_coverage is not proven/has no multiplier -> no widening drawn")

    flag = {}
    if widened_on:
        for ev in events:
            if ev["i"] is None or ev["type"] == "capital_raise":
                continue
            for off in (0, 1):
                j = ev["i"] + off
                if 0 <= j < n_days and j not in flag:
                    flag[j] = "0" if off == 0 else "+1"

    days = []
    for k in range(start_i, len(prices)):
        p, q = prices[k], prices[k - 1]
        pc, c, o = float(q["adjusted_close"]), float(p["adjusted_close"]), float(p["open"])
        h, l = float(p["high"]), float(p["low"])
        vv = v64.get(p["price_date"])
        d = {"d": p["price_date"], "o": o, "h": h, "l": l, "c": c, "pc": pc,
             "ret": c / pc - 1, "gap": o / pc - 1, "intra": c / o - 1, "v64": vv,
             "z": (abs(c / pc - 1) / vv) if vv else None, "lo_o": None, "hi_o": None, "in_o": None,
             "flag": 1 if (k - start_i) in flag else 0, "flag_desc": flag.get(k - start_i),
             "lo_w": None, "hi_w": None, "in_w": None}
        if vv:
            half = K_REF * vv
            d["lo_o"], d["hi_o"] = pc * (1 - half), pc * (1 + half)
            d["in_o"] = d["lo_o"] <= c <= d["hi_o"]
            if d["flag"]:
                d["lo_w"], d["hi_w"] = pc * (1 - half * mult), pc * (1 + half * mult)
                d["in_w"] = d["lo_w"] <= c <= d["hi_w"]
        days.append(d)

    curve = []
    try:
        curve = sb.table("event_curve_pooled").select("era,day_offset,rel_move,n").order("era").order("day_offset").execute().data
        curve = [{"era": r["era"], "day": int(r["day_offset"]), "rel": float(r["rel_move"]), "n": r["n"]} for r in curve]
    except Exception as ex:
        print("NOTE: event_curve_pooled not available (%s); the zoom-out chart will be empty" % type(ex).__name__)

    dist = []
    try:
        dist = sb.table("event_move_dist").select("era,etype,off,n,p50,p80,p95").execute().data
        dist = [{"era": r["era"], "etype": r["etype"], "off": int(r["off"]), "n": r["n"],
                 "p50": fl(r["p50"]), "p80": fl(r["p80"]), "p95": fl(r["p95"])} for r in dist]
    except Exception as ex:
        print("NOTE: event_move_dist not available (%s); no past-events section will be drawn" % type(ex).__name__)

    # ---- context lanes (context only; the ledger status is printed on the card) ----
    idx_of = {days[k]["d"]: k for k in range(len(days))}

    def idx_on_or_after(dstr):
        j = bisect.bisect_left(dates, dstr) - start_i
        return j if 0 <= j < len(days) else None

    fed_by_i = [None] * len(days)
    try:
        for r in paginated("fed_state_daily", "day,state,target_upper",
                           [lambda q: q.gte("day", "%d-01-01" % year), lambda q: q.lte("day", "%d-12-31" % year)], order="day"):
            k = idx_of.get(str(r["day"])[:10])
            if k is not None:
                fed_by_i[k] = [r["state"], fl(r["target_upper"])]
    except Exception as ex:
        print("NOTE: fed_state_daily not available (%s); no Fed lane" % type(ex).__name__)

    reg_by_i = [[] for _ in range(len(days))]
    try:
        for r in sb.table("market_regimes").select("name,start_date,end_date").execute().data:
            s_ = str(r["start_date"])[:10]
            e_ = str(r["end_date"])[:10] if r.get("end_date") else "9999-12-31"
            for k in range(len(days)):
                if s_ <= days[k]["d"] <= e_:
                    reg_by_i[k].append(r["name"])
    except Exception as ex:
        print("NOTE: market_regimes not available (%s); no regime lane" % type(ex).__name__)

    rel_marks = []
    try:
        for r in sb.table("macro_long").select("series_id,obs_date,known_on") \
                .in_("series_id", ["PAYEMS", "CPIAUCSL"]).eq("known_on_basis", "first_release") \
                .gte("known_on", "%d-01-01" % year).lte("known_on", "%d-12-31" % year).execute().data:
            j = idx_on_or_after(str(r["known_on"])[:10])
            if j is not None:
                rel_marks.append({"i": j, "series": r["series_id"], "date": str(r["known_on"])[:10], "period": str(r["obs_date"])[:7]})
    except Exception as ex:
        print("NOTE: release dates not available (%s); no release lane" % type(ex).__name__)

    def shocks(series_id, kind):
        out, prev = [], None
        try:
            rows = paginated("macro_long", "obs_date,value",
                             [lambda q: q.eq("series_id", series_id),
                              lambda q: q.gte("obs_date", "%d-12-15" % (year - 1)),
                              lambda q: q.lte("obs_date", "%d-12-31" % year)], order="obs_date")
        except Exception as ex:
            print("NOTE: %s not available (%s)" % (series_id, type(ex).__name__))
            return out
        for r in rows:
            v = fl(r["value"])
            if v is None:
                continue
            od = str(r["obs_date"])[:10]
            if prev is not None and od in idx_of:
                if kind == "oil":
                    chg = v / prev - 1
                    hit = prev > 5 and v > 5 and abs(chg) >= 0.03
                else:
                    chg = v - prev
                    hit = abs(chg) >= 0.10 - 1e-9
                if hit:
                    out.append({"i": idx_of[od], "chg": chg})
            prev = v
        return out

    oil_marks = shocks("DCOILWTICO", "oil") if sector == "Energy" else []
    yld_marks = shocks("DGS10", "yield")

    law_marks = []
    try:
        pmap = sb.table("policy_area_sector_map").select("policy_area,sector,grp").execute().data
        pa_ok = {r["policy_area"] for r in pmap if r["grp"] == "sector_specific" and r["sector"] == sector}
        if pa_ok:
            stage_rows = paginated("law_stage_dates", "decision_id,law_number,introduced_date,first_passage_date,final_passage_date,signed_date", order="decision_id")
            gd = paginated("government_decisions", "id,title,structured_data", [lambda q: q.eq("decision_type", "enacted_law")], order="id")
            info = {g["id"]: (g["title"], (g["structured_data"] or {}).get("policy_area")) for g in gd}
            for r in stage_rows:
                title, pa = info.get(r["decision_id"], (None, None))
                if pa not in pa_ok:
                    continue
                for stage, colname in (("introduced", "introduced_date"), ("first passage", "first_passage_date"),
                                       ("final passage", "final_passage_date"), ("signed", "signed_date")):
                    ds = r.get(colname)
                    if not ds:
                        continue
                    ds = str(ds)[:10]
                    if not ("%d-01-01" % year <= ds <= "%d-12-31" % year):
                        continue
                    j = idx_on_or_after(ds)
                    if j is not None:
                        law_marks.append({"i": j, "stage": stage, "law": r["law_number"], "title": title, "pa": pa, "date": ds})
    except Exception as ex:
        print("NOTE: law markers not available (%s)" % type(ex).__name__)

    oil_range = []
    try:
        oil_range = [{"era": r["era"], "grp": r["grp"], "n": r["n"], "p50": fl(r["p50"]), "p80": fl(r["p80"]), "p95": fl(r["p95"])}
                     for r in sb.table("flag_range_dist").select("era,grp,n,p50,p80,p95")
                     .eq("flag_key", "macro_oil_shock_energy_same_day").execute().data]
    except Exception as ex:
        print("NOTE: flag_range_dist not available (%s); no oil range text" % type(ex).__name__)

    data = {"ticker": ticker, "year": year, "sector": sector, "mult": mult, "k_ref": K_REF, "days": days, "events": events,
            "ledger": ledger, "evidence": evid, "curve": curve, "dist": dist, "oil_range": oil_range,
            "lanes": {"fed": fed_by_i, "reg": reg_by_i, "rel": rel_marks, "oil": oil_marks, "yld": yld_marks, "laws": law_marks}}
    html = TEMPLATE.replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
    os.makedirs("scripts/card/out", exist_ok=True)
    out = "scripts/card/out/card_%s_%d.html" % (ticker, year)
    with open(out, "w") as f:
        f.write(html)
    print("%s %d (%s): %d trading days, %d events (%d in a documented window), %d flagged days, lanes: %d releases, %d oil-shock, %d yield-shock, %d law markers -> %s"
          % (ticker, year, sector, len(days), len(events), sum(1 for e in events if e["i"] is not None and e["type"] != "capital_raise"),
             len(flag), len(rel_marks), len(oil_marks), len(yld_marks), len(law_marks), out))


TEMPLATE = r"""<!doctype html>
<html><head><meta charset="utf-8"><title>Stock card</title>
<style>
:root{--bg:#ffffff;--fg:#1f2937;--mut:#6b7280;--box:#f3f4f6;--hl:#b45309}
@media (prefers-color-scheme: dark){:root{--bg:#111827;--fg:#e5e7eb;--mut:#9ca3af;--box:#1f2937;--hl:#fbbf24}}
body{background:var(--bg);color:var(--fg);font-family:system-ui,Arial,sans-serif;margin:16px;max-width:1010px}
svg{width:100%;height:auto;background:var(--box);border-radius:6px;color:var(--fg)}
svg text{fill:var(--fg);font-size:11px}
#lanes{margin-top:3px}
#panel{background:var(--box);border-radius:6px;padding:10px 14px;margin:8px 0;line-height:1.55;font-size:14px}
.hl{color:var(--hl);font-weight:600}.mut{color:var(--mut);font-size:12px}
input[type=range]{width:100%}h2{margin:0 0 4px}h3{margin:16px 0 4px}
</style></head><body>
<h2 id="title"></h2>
<div class="mut">Magnitude only: this card says how big moves tend to be, never which way. Orange shading = documented event window (filing day and the day after). Prices are dividend-adjusted to today, so they sit below the quotes of the time. Drag the slider, move the mouse over the chart, or use the arrow keys.</div>
<svg id="chart"></svg>
<svg id="lanes"></svg>
<div id="lane_legend" class="mut"></div>
<input id="slider" type="range" min="0" value="0">
<div id="panel"></div>
<div id="summary" class="mut"></div>
<h3>Zoom-out: how big moves run around company-event filings (1.0 = ordinary)</h3>
<svg id="curve"></svg>
<div id="evidence"></div>
<div id="noeffect"></div>
<script>
const D = __DATA__;
const days = D.days, events = D.events, n = days.length;
const NS = "http://www.w3.org/2000/svg";
const COLORS = {acquisition:"#2563eb", leadership_change:"#d97706", legal_settlement:"#7c3aed", restructuring:"#dc2626",
  regulatory:"#0891b2", financial_result:"#059669", capital_raise:"#6b7280"};
const col = t => COLORS[t] || "#9ca3af";
function el(tag, attrs, parent){ const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
const pct = (x, dp) => x == null ? "n/a" : (x * 100).toFixed(dp == null ? 2 : dp) + "%";
const f2 = x => x == null ? "n/a" : Number(x).toFixed(2);
const esc = s => String(s).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
function addDays(s, k) { const t = new Date(s + "T00:00:00Z"); t.setUTCDate(t.getUTCDate() + k); return t.toISOString().slice(0, 10); }
const st = k => ((D.ledger.find(r => r.flag_key === k) || {}).status || "unknown");
document.getElementById("title").textContent = D.ticker + " " + D.year + " - stock card" + (D.sector ? " (" + D.sector + ")" : "");

// ---- price chart ----
const W = 980, H = 360, L = 58, R = 16, T = 10, B = 26;
const svg = document.getElementById("chart");
svg.setAttribute("viewBox", "0 0 " + W + " " + H);
let ymin = Infinity, ymax = -Infinity;
days.forEach(d => { ymin = Math.min(ymin, d.l); ymax = Math.max(ymax, d.h); });
const pad = (ymax - ymin) * 0.05; ymin -= pad; ymax += pad;
const step = (W - L - R) / Math.max(n - 1, 1);
const X = i => L + step * i;
const Y = v => T + (H - T - B) * (1 - (v - ymin) / (ymax - ymin));
for (let k = 0; k <= 4; k++) { const v = ymin + (ymax - ymin) * k / 4, y = Y(v);
  el("line", {x1: L, x2: W - R, y1: y, y2: y, stroke: "currentColor", opacity: 0.12}, svg);
  const t = el("text", {x: L - 6, y: y + 4, "text-anchor": "end"}, svg); t.textContent = v.toFixed(0); }
let lastM = "";
days.forEach((d, i) => { const m = d.d.slice(0, 7); if (m !== lastM) { lastM = m;
  const t = el("text", {x: X(i), y: H - 8}, svg); t.textContent = d.d.slice(5, 7); } });
days.forEach((d, i) => { if (d.flag) el("rect", {x: X(i) - step / 2, y: T, width: step, height: H - T - B, fill: "#f59e0b", opacity: 0.22}, svg); });
el("polyline", {points: days.map((d, i) => X(i) + "," + Y(d.c)).join(" "), fill: "none", stroke: "currentColor", "stroke-width": 1.5}, svg);
events.forEach(e => { if (e.i == null) return;
  el("line", {x1: X(e.i), x2: X(e.i), y1: T, y2: H - B, stroke: col(e.type), "stroke-width": 1, "stroke-dasharray": "3,3", opacity: 0.7}, svg);
  const c = el("circle", {cx: X(e.i), cy: T + 6, r: 4, fill: col(e.type)}, svg);
  const t = el("title", {}, c); t.textContent = e.date + " [" + e.type + "] " + e.title; });

// ---- context lanes under the chart (same x-axis) ----
const LS = D.lanes;
const lrows = [["fed", "Fed"], ["reg", "Regime"], ["rel", "Release"]];
if (D.sector === "Energy") lrows.push(["oil", "Oil shock"]);
lrows.push(["yld", "10y shock"]); lrows.push(["laws", "Laws"]);
const RH = 17, lanes = document.getElementById("lanes");
lanes.setAttribute("viewBox", "0 0 " + W + " " + (lrows.length * RH + 4));
const ry = key => 2 + lrows.findIndex(r => r[0] === key) * RH;
lrows.forEach((r, k) => { const t = el("text", {x: 4, y: 2 + k * RH + 12}, lanes); t.style.fontSize = "10px"; t.textContent = r[1]; });
const FED_COL = {tightening: "#dc2626", easing: "#16a34a", hold: "#9ca3af"};
LS.fed.forEach((f, i) => { if (!f) return;
  const r = el("rect", {x: X(i) - step / 2, y: ry("fed") + 2, width: step + 0.5, height: RH - 5, fill: FED_COL[f[0]] || "#9ca3af", opacity: 0.6}, lanes);
  const t = el("title", {}, r); t.textContent = days[i].d + " Fed: " + f[0] + " (target upper " + f[1] + "%)"; });
const PAL = ["#6366f1", "#14b8a6", "#f43f5e", "#eab308", "#8b5cf6", "#0ea5e9"];
const hashOf = s => { let h = 0; for (let k = 0; k < s.length; k++) h = (h * 31 + s.charCodeAt(k)) | 0; return Math.abs(h); };
let segStart = 0, segName = null;
const flushSeg = endI => { if (segName == null) return;
  const x0 = X(segStart) - step / 2, x1 = X(endI) + step / 2;
  const r = el("rect", {x: x0, y: ry("reg") + 2, width: x1 - x0, height: RH - 5, fill: PAL[hashOf(segName) % PAL.length], opacity: 0.5}, lanes);
  const t = el("title", {}, r); t.textContent = segName + " (named afterwards)";
  if (x1 - x0 > 80) { const tx = el("text", {x: x0 + 3, y: ry("reg") + 12}, lanes); tx.style.fontSize = "9px"; tx.textContent = segName.slice(0, Math.floor((x1 - x0) / 5)); } };
for (let i = 0; i < n; i++) { const nm = (LS.reg[i] || [])[0] || null; if (nm !== segName) { flushSeg(i - 1); segName = nm; segStart = i; } }
flushSeg(n - 1);
LS.rel.forEach(r => { const jobs = r.series === "PAYEMS";
  const ln = el("line", {x1: X(r.i), x2: X(r.i), y1: ry("rel") + 1, y2: ry("rel") + RH - 3, stroke: jobs ? "#2563eb" : "#9333ea", "stroke-width": 2}, lanes);
  const t = el("title", {}, ln); t.textContent = r.date + " " + (jobs ? "Jobs report" : "CPI") + " first release (" + r.period + " data)"; });
LS.oil.forEach(r => { const ln = el("line", {x1: X(r.i), x2: X(r.i), y1: ry("oil") + 1, y2: ry("oil") + RH - 3, stroke: "#ea580c", "stroke-width": 2}, lanes);
  const t = el("title", {}, ln); t.textContent = days[r.i].d + " oil-shock day: WTI " + pct(r.chg, 1); });
LS.yld.forEach(r => { const ln = el("line", {x1: X(r.i), x2: X(r.i), y1: ry("yld") + 1, y2: ry("yld") + RH - 3, stroke: "#64748b", "stroke-width": 2}, lanes);
  const t = el("title", {}, ln); t.textContent = days[r.i].d + " 10-year yield moved " + (r.chg * 100).toFixed(0) + "bp"; });
LS.laws.forEach(r => { const cx = X(r.i), cy = ry("laws") + RH / 2;
  const pg = el("polygon", {points: (cx - 4) + "," + cy + " " + cx + "," + (cy - 5) + " " + (cx + 4) + "," + cy + " " + cx + "," + (cy + 5),
    fill: (r.stage === "introduced" || r.stage === "first passage") ? "#94a3b8" : "#0d9488"}, lanes);
  const t = el("title", {}, pg); t.textContent = r.date + " law " + r.law + " (" + r.pa + "): " + r.stage; });
document.getElementById("lane_legend").innerHTML = "Lanes are context only; each says its ledger status when you select a day. Fed: red tightening, green easing, grey hold. Release: blue jobs, purple CPI. " +
  (D.sector === "Energy" ? "Oil shock: orange (Energy stocks only). " : "") + "10y shock: grey. Laws: diamonds for laws mapped to this company's sector (grey = early stages, teal = final passage or signing).";

const slider = document.getElementById("slider");
slider.max = n - 1;
let g1 = null, sel = 0;

// ---- zoom-out curve ----
const cv = document.getElementById("curve");
const CW = 620, CH = 230, CL = 40, CR = 10, CT = 10, CB = 22;
cv.setAttribute("viewBox", "0 0 " + CW + " " + CH);
const CX = o => CL + (CW - CL - CR) * (o + 4) / 43;
const CY = v => CT + (CH - CT - CB) * (1 - (v - 0.8) / 0.8);
[0.8, 1.0, 1.2, 1.4, 1.6].forEach(v => { el("line", {x1: CL, x2: CW - CR, y1: CY(v), y2: CY(v), stroke: "currentColor", opacity: v === 1.0 ? 0.5 :0.12, "stroke-dasharray": v === 1.0 ? "4,3" : "0"}, cv);
  const t = el("text", {x: CL - 4, y: CY(v) + 4, "text-anchor": "end"}, cv); t.textContent = v.toFixed(1); });
[-4, 0, 5, 10, 20, 30, 39].forEach(o => { const t = el("text", {x: CX(o), y: CH - 6, "text-anchor": "middle"}, cv); t.textContent = o; });
[["A_2004_2018", "#2563eb", "2004-2018"], ["B_2019_2026", "#dc2626", "2019-2026"]].forEach((a, k) => {
  const pts = D.curve.filter(r => r.era === a[0]).sort((u, v) => u.day - v.day);
  if (pts.length) el("polyline", {points: pts.map(r => CX(r.day) + "," + CY(Math.min(1.6, Math.max(0.8, r.rel)))).join(" "), fill: "none", stroke:a[1], "stroke-width": 1.6}, cv);
  const t = el("text", {x: CL + 10, y: CT + 14 + k * 14, fill: a[1]}, cv); t.style.fill = a[1]; t.textContent = a[2] + (pts.length ? " (n=" + pts[0].n + ")" : ""); });
let cg = null;

// ---- context text for the selected day ----
function ctxLines(i) {
  const out = [], d = days[i];
  const f = LS.fed[i];
  if (f) out.push("Fed state: <b>" + f[0] + "</b> (target upper " + f[1] + "%) <span class='mut'>[ledger: " + st("fed_state") + "; context only]</span>");
  const rg = LS.reg[i];
  if (rg && rg.length) out.push("Market regime (named afterwards): " + rg.map(esc).join(", ") + " <span class='mut'>[hindsight label, never a live flag]</span>");
  LS.rel.filter(r => r.i === i).forEach(r => { const jobs = r.series === "PAYEMS", key = jobs ? "macro_jobs_report_payems" : "macro_cpi";
    out.push((jobs ? "Jobs report" : "CPI") + " released today (" + r.period + " data) <span class='mut'>[ledger: " + st(key) + (st(key) === "lead" ? ": not strong enough to change any range" : ": no documented effect") + "]</span>"); });
  LS.oil.filter(r => r.i === i).forEach(r => {
    const era = D.year <= 2018 ? "2004-2018" : "2019-2026";
    const sh = D.oil_range.find(x => x.era === era && x.grp === "shock"), od = D.oil_range.find(x => x.era === era && x.grp === "ordinary");
    let s = "Oil-shock day: WTI moved <b>" + pct(r.chg, 1) + "</b> <span class='mut'>[ledger: " + st("macro_oil_shock_energy_same_day") + "; same-day explanation only, the oil move is only known at the close]</span>";
    if (sh && od && d.v64) { const b = v => "&plusmn;" + (v * d.v64 * 100).toFixed(1) + "%";
      s += "<br>On past oil-shock days (n=" + sh.n + " stock-days) an energy stock's move stayed within " + b(sh.p50) + " half the time, " + b(sh.p80) + " four times in five and " + b(sh.p95) + " 19 times in 20; on ordinary days " + b(od.p50) + ", " + b(od.p80) + ", " + b(od.p95) + ". Size only, not direction.";
      if (d.z != null) { const bt = d.z <= sh.p50 ? "below the median" : d.z <= sh.p80 ? "between the median and the 80th percentile" : d.z <= sh.p95 ? "between the 80th and 95th percentile" : "above the 95th percentile";
        s += " Today's move (" + pct(Math.abs(d.ret)) + ", " + d.z.toFixed(2) + " x typical) sits " + bt + " of past oil-shock days."; } }
    out.push(s); });
  LS.yld.filter(r => r.i === i).forEach(r => {
    let note = "no documented effect for this sector";
    if (D.sector === "Health Care") note = "health care tends to move less on days like this (about 5-14% less than other sectors; lead)";
    else if (D.sector === "Financials") note = "financials tend to move more on days like this since 1986 (about 6-14% more; lead)";
    out.push("10-year yield moved <b>" + (r.chg > 0 ? "+" : "") + (r.chg * 100).toFixed(0) + "bp</b> today: " + note + " <span class='mut'>[context; not strong enough to change any range]</span>"); });
  LS.laws.filter(r => r.i === i).forEach(r => {
    const key = {"introduced": "law_introduction_sector_move", "first passage": "law_first_passage_sector_move", "final passage": "law_final_passage_sector_move", "signed": "law_signing_sector_move"}[r.stage];
    const after = events.filter(e => e.date >= r.date && e.date <= addDays(r.date, 90));
    let s = "<span style='color:#0d9488'>&#9670;</span> Law " + esc(r.law) + " (" + esc(r.pa) + "), <b>" + r.stage + "</b> " + r.date + ": " + esc((r.title || "").slice(0, 90)) +
      "<br>This stock moved " + (d.z == null ? "n/a" : d.z.toFixed(2) + " x its typical daily move") + " that day. Sector-level evidence for large caps (2004-2026): <b>no documented effect on move size</b>, within about &plusmn;3-6% <span class='mut'>[ledger: " + st(key) + "]</span>.";
    s += "<br><span class='mut'>This company's filings in the 90 days after (this year only): " + (after.length ? after.map(e => e.date + " " + e.type).join("; ") : "none") + ". Listed as facts, not as effects of the law.</span>";
    out.push(s); });
  return out;
}

function select(i) {
  i = Math.max(0, Math.min(n - 1, i)); sel = i; slider.value = i;
  if (g1) svg.removeChild(g1);
  g1 = el("g", {}, svg);
  const d = days[i];
  el("line", {x1: X(i), x2: X(i), y1: T, y2: H - B, stroke: "currentColor", "stroke-width": 0.8, opacity: 0.6}, g1);
  el("line", {x1: X(i), x2: X(i), y1: Y(d.h), y2: Y(d.l), stroke: "currentColor", "stroke-width": 2}, g1);
  el("rect", {x: X(i) - 3, y: Math.min(Y(d.o), Y(d.c)), width: 6, height: Math.max(2, Math.abs(Y(d.o) - Y(d.c))), fill: d.c >= d.o ? "#16a34a" : "#dc2626"}, g1);
  const band = (lo, hi, dx, fill) => { const top = Y(Math.min(hi, ymax)), bot = Y(Math.max(lo, ymin));
    el("rect", {x: X(i) + dx, y: top, width: 6, height: Math.max(1, bot - top), fill: fill, opacity: 0.55}, g1); };
  if (d.lo_o != null) band(d.lo_o, d.hi_o, 6, "#9ca3af");
  if (d.flag && d.lo_w != null) band(d.lo_w, d.hi_w, 13, "#f59e0b");

  const p = [];
  p.push("<b>" + d.d + "</b> &nbsp; open " + f2(d.o) + " &nbsp; high " + f2(d.h) + " &nbsp; low " + f2(d.l) + " &nbsp; close " + f2(d.c) + " &nbsp; (prior close " + f2(d.pc) + ")");
  p.push("Gap (prior close to open) <b>" + pct(d.gap) + "</b> &nbsp;|&nbsp; intraday (open to close) <b>" + pct(d.intra) + "</b> &nbsp;|&nbsp; total <b>" + pct(d.ret) + "</b>" +
    (d.z == null ? "" : " &nbsp;|&nbsp; " + d.z.toFixed(2) + " x this stock's typical daily move (64-day)"));
  if (d.lo_o != null) {
    p.push("Ordinary 80% range, known the day before (grey bar): " + f2(d.lo_o) + " to " + f2(d.hi_o) + " &rarr; close " + (d.in_o ? "inside" : "<b>outside</b>"));
    if (d.flag) p.push("<span class='hl'>Documented event window (day " + d.flag_desc + "): range widened x" + D.mult + " (orange bar): " + f2(d.lo_w) + " to " + f2(d.hi_w) + " &rarr; close " + (d.in_w ? "inside" : "outside") + "</span>");
  } else p.push("<span class='mut'>No 64-day volatility available for this day, so no range is drawn.</span>");
  const near = events.filter(e => e.i != null && Math.abs(i - e.i) <= 5);
  if (near.length) { p.push("<b>Events within 5 trading days</b>");
    near.forEach(e => { const off = i - e.i; let note;
      if (e.type === "capital_raise") note = "capital raise: no documented burst";
      else if (off === 0 || off === 1) note = "<span class='hl'>inside the documented window</span>";
      else if (off === -1) note = "the day before: context only, not knowable in advance";
      else note = "outside the window: no documented effect";
      p.push("<span style='color:" + col(e.type) + "'>&#9679;</span> " + e.date + " [" + e.type + "] " + esc(e.title) + " &mdash; day " + (off > 0? "+" + off : off) + ": " + note); }); }
  else p.push("<span class='mut'>No events within 5 trading days.</span>");
  const act2 = events.filter(e => e.i != null && (i - e.i === 0 || i - e.i === 1));
  if (act2.length && d.v64) {
    const e = act2[act2.length - 1], off = i - e.i;
    let row = D.dist.find(r => r.era === "ALL" && r.etype === e.type && r.off === off), basis = e.type;
    if (!row || row.n < 150) { row = D.dist.find(r => r.era === "ALL" && r.etype === "ALL_TYPES" && r.off === off); basis = "all event types (too few past " + e.type + " cases)"; }
    if (row) {
      const b = v => "&plusmn;" + (v * d.v64 * 100).toFixed(1) + "%";
      const zt = d.z;
      const bandTxt = zt == null ? "n/a" : zt <= row.p50 ? "below the median" : zt <= row.p80 ? "between the median and the 80th percentile" : zt <= row.p95 ? "between the 80th and 95th percentile" : "above the 95th percentile";
      p.push("<span class='hl'>What past events like this did (" + esc(basis) + ", day " + (off > 0 ? "+" : "") + off + ", n=" + row.n + "):</span> the move stayed within " + b(row.p50) + " half the time, " + b(row.p80) + " four times in five, and " + b(row.p95) + " 19 times in 20, scaled to this stock's typical daily move. This day's move was " + pct(Math.abs(d.ret)) + ": " + bandTxt + " of past cases. <span class='mut'>Size only, not direction.</span>");
    }
  }
  const cx = ctxLines(i);
  if (cx.length) { p.push("<b>Context on this day</b> <span class='mut'>(only the orange shading changes any range)</span>"); cx.forEach(s => p.push(s)); }
  document.getElementById("panel").innerHTML = p.join("<br>");

  if (cg) cv.removeChild(cg);
  cg = el("g", {}, cv);
  const act = events.filter(e => e.i != null && e.i <= i && i - e.i <= 39 && e.type !== "capital_raise");
  if (act.length) { const e = act[act.length - 1], off = i - e.i;
    el("line", {x1: CX(off), x2: CX(off), y1: CT, y2: CH - CB, stroke: "#f59e0b", "stroke-width": 2}, cg);
    const t = el("text", {x: CX(off) > CW / 2 ? CX(off) - 4 : CX(off) + 4, y: CT + 44, "text-anchor": CX(off) > CW / 2 ? "end" : "start"}, cg); t.textContent = "selected day = day " + (off > 0 ? "+" : "") + off + " after the latest event"; }
}

svg.addEventListener("mousemove", ev => { const r = svg.getBoundingClientRect();
  select(Math.round(((ev.clientX - r.left) * W / r.width - L) / step)); });
lanes.addEventListener("mousemove", ev => { const r = lanes.getBoundingClientRect();
  select(Math.round(((ev.clientX - r.left) * W / r.width - L) / step)); });
slider.addEventListener("input", () => select(parseInt(slider.value, 10)));
document.addEventListener("keydown", ev => { if (ev.key === "ArrowLeft") select(sel - 1); if (ev.key === "ArrowRight") select(sel + 1); });

// ---- year summary: one company-year is tiny; the proof used ~33,000 flagged days ----
const withBand = days.filter(d => d.lo_o != null);
const fd = withBand.filter(d => d.flag), ud = withBand.filter(d => !d.flag);
const cnt = (a, k) => a.filter(d => d[k]).length;
let sumHtml =
  "This year: " + fd.length + " documented-window days; close inside the ordinary range on " + cnt(fd, "in_o") + " of them, inside the widened range on " + cnt(fd, "in_w") +
  ". Other days: " + ud.length + "; inside the ordinary range on " + cnt(ud, "in_o") + " (" + (ud.length ? (100 * cnt(ud, "in_o") / ud.length).toFixed(0) : "n/a") + "%). " +
  "A single company-year is far too small to judge the multiplier; the proof used about 33,000 flagged days.";
const lawDays = Array.from(new Set(LS.laws.map(r => r.i)));
if (lawDays.length) {
  const zs = lawDays.map(i => days[i].z).filter(z => z != null);
  const zo = days.filter((d, i) => lawDays.indexOf(i) < 0 && d.z != null).map(d => d.z);
  const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
  if (zs.length && zo.length) sumHtml += "<br>Law days for this sector: " + lawDays.length + " distinct days; this stock's average move on them was " + mean(zs).toFixed(2) +
    " x its typical daily move (all other days: " + mean(zo).toFixed(2) + "). One company-year is far too small to conclude anything; it is here so the company-level picture can be built up year by year.";
}
document.getElementById("summary").innerHTML = sumHtml;

// ---- ledger: what this card is allowed to use, and what has no documented effect ----
let html = "<h3>What this card is allowed to use (ledger status: proven)</h3><ul>";
D.ledger.filter(r => r.status === "proven" && !(r.flag_key === "macro_oil_shock_energy_same_day" && D.sector !== "Energy")).forEach(r => {
  const evs = D.evidence.filter(e => e.flag_key === r.flag_key).map(e => e.era + ": n=" + e.n + ", " + (e.estimate == null ? "n/a" : Number(e.estimate).toFixed(3)) + " (se " + (e.se == null ? "n/a" : Number(e.se).toFixed(3)) + ")").join("; ");
  html += "<li><b>" + esc(r.flag_key) + "</b>" + (r.multiplier ? (r.flag_key === "event_daily_range_coverage" ? " [one-day range widened x" : r.flag_key === "event_premium_20d" ? " [20-day range x" : " [typical size vs ordinary x") + r.multiplier + "]" : "") + " &mdash; " + esc(r.description)+ "<br><span class='mut'>" + esc(evs) + "</span></li>"; });
document.getElementById("evidence").innerHTML = html + "</ul>";
const ne = D.ledger.filter(r => ["null", "retired", "untested", "lead"].includes(r.status));
document.getElementById("noeffect").innerHTML = "<details><summary>Everything else tested or not yet tested (" + ne.length + ") &mdash; none of it changes the numbers above</summary><ul>" +
  ne.map(r => "<li><b>" + esc(r.status) + "</b> " + esc(r.flag_key) + " &mdash; " + esc(r.description) + "</li>").join("") + "</ul></details>";

select(0);
</script></body></html>
"""

if __name__ == "__main__":
    main()
