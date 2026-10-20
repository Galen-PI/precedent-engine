#!/usr/bin/env python3
"""
day_web_layers.py -- bridges day_card.py into day_web.py. READ-ONLY (reads results/cards/card_<TICKER>_<DATE>.json; runs day_card.py to make it when it is missing or stale).

WHY. day_web.py (v1) judges the stock's raw move against its own recent volatility; the card judges the miss against what the market and sector did and against a band whose edge is
calibrated for the kind of day. The two can disagree on the same stock-day (a stock that rises 8% on a day the market rises 9.5% is far outside its own ordinary range but inside the card's
band). The page now READS THE CARD so the numbers are the same everywhere, and it gains the layers the card has: the earnings window (8-K item 2.02, day 0 / +1) and Regulation FD (7.01).
Nothing is recomputed here and nothing is multiplied: the card's multiplier is a measured group value.

Used by day_web.py through six small insertions; every function tolerates a missing card (the page then says so and carries on).
"""
import os, sys, json, html, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CARD_DIR = os.path.join(ROOT, "results", "cards")
DEPENDS_ON = [os.path.join(HERE, "day_card.py"), os.path.join(ROOT, "models", "band_calibration.json"),
              os.path.join(ROOT, "models", "earnings_band_model.json"), os.path.join(ROOT, "models", "event_band_model.json")]
LEDGER_EARN_WIDTH = "event_earnings_window_width"
LEDGER_EARN_SIGN = "earnings_surprise_sign_revenue"
LEDGER_FD = "eightk_item_7_01_width"


def _pct(x):
    return "n/a" if x is None else "%+.2f%%" % (100.0 * x)


def _fresh(path):
    if not os.path.exists(path):
        return False
    t = os.path.getmtime(path)
    return all(t >= os.path.getmtime(p) for p in DEPENDS_ON if os.path.exists(p))


def _read(path):
    try:
        with open(path) as fh:
            c = json.load(fh)
    except (OSError, ValueError):
        return None
    return c if isinstance(c, dict) and "band_edge" in c and "chapter1" in c else None


def load_card(ticker, ds):
    """(card dict or None, note or None). Runs day_card.py when the JSON is missing, stale (older than the card script or the model files) or from before the calibrated edge."""
    path = os.path.join(CARD_DIR, "card_%s_%s.json" % (ticker, ds))
    if _fresh(path):
        c = _read(path)
        if c:
            return c, None
    print("running day_card.py %s %s (the page reads the card's numbers) ..." % (ticker, ds), file=sys.stderr, flush=True)
    try:
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "day_card.py"), ticker, ds], cwd=ROOT, capture_output=True, text=True, timeout=900)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, "Chapter-1 card unavailable: could not run day_card.py (%s)" % e
    c = _read(path) if r.returncode == 0 else None
    if c:
        return c, None
    tail = (r.stderr or r.stdout or "").strip().splitlines()
    return None, "Chapter-1 card unavailable: day_card.py failed (%s)" % (tail[-1][:160] if tail else "no output")


def _inside(card):
    u, e = card.get("band_units_of_miss"), card.get("band_edge")
    return None if u is None or e is None else abs(u) <= e


def stock_details(card, note):
    """Extra lines for the stock node."""
    if not card:
        return ["chapter-1 view unavailable: %s" % (note or "no card")]
    c1, d = card.get("chapter1") or {}, card.get("day") or {}
    out = ["The range above is unconditional (the stock's own raw move against its recent volatility). The card's band below is conditional on what the market and the sector did that day."]
    hp = card.get("hypothetical_price")
    if c1.get("hyp") is not None:
        out.append("chapter 1: market and sector alone would have moved it %s%s; the miss beyond that is %s" % (
            _pct(c1["hyp"]), (" (price %.2f)" % hp) if hp else "", _pct(c1.get("e1"))))
    br = card.get("band_return")
    if br and d.get("prev_close") and d.get("close") is not None:
        pc, ins = d["prev_close"], _inside(card)
        out.append("calibrated 90%% band: %s to %s (price %.2f to %.2f); actual price %.2f is %s, %.2f band units (edge %.3f: %s)" % (
            _pct(br[0]), _pct(br[1]), pc * (1 + br[0]), pc * (1 + br[1]), d["close"], "INSIDE" if ins else "OUTSIDE",
            abs(card.get("band_units_of_miss") or 0.0), card.get("band_edge") or 0.0, card.get("band_edge_source") or ""))
    if card.get("event_multiplier") is not None:
        out.append("band multiplier %.2fx: %s" % (card["event_multiplier"], card.get("band_multiplier_source") or ""))
    return out


def add_filing_layers(card, note, led, evid, led_info, edge_kind, add_node, add_edge, checked):
    """The earnings window (8-K item 2.02, day 0 / +1) and Regulation FD (7.01) as company-side nodes, taken from the card's own filing flags."""
    if note:
        checked.append(note)
    if not card:
        return
    ff = card.get("filing_flags") or {}
    mult, src = card.get("event_multiplier"), card.get("band_multiplier_source") or ""
    if ff.get("earn_off") is not None:
        off = ff["earn_off"]
        st, tx = led_info(led, evid, LEDGER_EARN_WIDTH)
        _, tx_sign = led_info(led, evid, LEDGER_EARN_SIGN)
        det = ["band multiplier %s: %s" % (("%.2fx" % mult) if mult is not None else "n/a", src),
               "width only: the filing time is not in the table, so day 0 and day +1 are both flagged",
               "ledger (width): " + tx, "ledger (sign of a revenue-trend surprise): " + tx_sign, "magnitude only: no direction claim"]
        add_node("c_earn", 4, "Earnings window", "8-K 2.02 filed %s, day %s" % (ff.get("earn_date"), "0" if off == 0 else "+1"), "new" if off == 0 else "persist", det,
                 ["sec_8k_filings: item 2.02 filing dated %s for this stock" % ff.get("earn_date")])
        add_edge("c_earn", "c_stock", edge_kind(st), tx, "window: day 0 and day +1 (no filing time in the table)")
        if ff.get("f701"):
            checked.append("Regulation FD filing (item 7.01) also on day 0 or +1: not counted separately; the earnings-window value is the measured group")
    elif ff.get("f701"):
        st, tx = led_info(led, evid, LEDGER_FD)
        add_node("c_fd", 4, "Reg FD filing", "8-K 7.01 on day 0 or +1", "new",
                 ["band multiplier %s: %s" % (("%.2fx" % mult) if mult is not None else "n/a", src), "ledger: " + tx],
                 ["sec_8k_filings: item 7.01 filing on day 0 or +1 for this stock"])
        add_edge("c_fd", "c_stock", edge_kind(st), tx, "window: day 0 and day +1 (no filing time in the table)")
    else:
        checked.append("8-K earnings window (item 2.02) or Regulation FD filing (item 7.01) on day 0 or +1: none (the other routine 8-K items were tested one by one and only item 7.01 passed, as a lead)")


def band_summary(card, note):
    """A JSON-safe summary kept in the page's facts."""
    if not card:
        return {"available": False, "note": note or "no card"}
    c1, d = card.get("chapter1") or {}, card.get("day") or {}
    return {"available": True, "group": card.get("band_group"), "edge": card.get("band_edge"), "edge_source": card.get("band_edge_source"),
            "multiplier": card.get("event_multiplier"), "multiplier_source": card.get("band_multiplier_source"), "band_return": card.get("band_return"),
            "hyp_return": c1.get("hyp"), "hyp_price": card.get("hypothetical_price"), "units": card.get("band_units_of_miss"), "inside": _inside(card),
            "close": d.get("close"), "prev_close": d.get("prev_close")}


def band_html(b):
    """One paragraph for the top of the page."""
    if not b:
        return ""
    if not b.get("available"):
        return "<p><i>%s</i></p>" % html.escape(b.get("note") or "Chapter-1 card unavailable.")
    br, pc, close = b.get("band_return"), b.get("prev_close"), b.get("close")
    if not br or not pc or close is None:
        return "<p><i>Chapter-1 card present but incomplete.</i></p>"
    return ("<p><b>Chapter 1 and the band (from the card).</b> Market and sector alone: %s%s. Calibrated 90%% band: %s to %s (price %.2f to %.2f); the actual price %.2f is <b>%s</b> "
            "(%.2f band units; edge %.3f: %s; multiplier %.2fx). The edge is set for this kind of day and checked walk-forward (coverage 88-91%% by era); it is an explanation line using the same "
            "day's market stress, not a forecast range.</p>") % (
        _pct(b.get("hyp_return")), (" (price %.2f)" % b["hyp_price"]) if b.get("hyp_price") else "", _pct(br[0]), _pct(br[1]), pc * (1 + br[0]), pc * (1 + br[1]), close,
        "INSIDE" if b.get("inside") else "OUTSIDE", abs(b.get("units") or 0.0), b.get("edge") or 0.0, html.escape(b.get("edge_source") or ""), b.get("multiplier") or 1.0)


# ---------------------------------------------------------------- per-event lines and edge style (added after the first day_web patch)
def _short(s, n):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n - 1] + "\u2026"


def ledger_blurb(led, key):
    """' -- what this row tested: <description>' so a type row (written for an earlier test) is read for what it measured, not as a verdict on today."""
    r = (led or {}).get(key) if key else None
    d, pr = (r or {}).get("description"), (r or {}).get("pass_rule")
    out = (" -- what this row tested: " + _short(d, 150)) if d else ""
    if pr:
        out += " -- its pass rule: " + _short(pr, 240)
    return out


def _event(card, event_id):
    if not card:
        return None
    return next((e for e in (card.get("events") or []) if str(e.get("event_id")) == str(event_id)), None)


def _event_mult(ev):
    """(multiplier or None, note) from the joint event-day model, exactly as the card computes it."""
    try:
        import day_card as dc
        return dc.band_multiplier(dc.load_json("event_band_model.json"), ev.get("ptype"), ev.get("size"), ev.get("timing"), ev.get("off"))
    except Exception as e:      # the page must never fail because of this line
        return None, "joint model not available (%s)" % type(e).__name__


def event_lines(card, event_id):
    """The labeler's size and timing for this event and the joint event-day model's multiplier (the one the card uses), as detail lines."""
    ev = _event(card, event_id)
    if not ev:
        return []
    out = []
    bits = [str(x) for x in (ev.get("size"), ev.get("timing")) if x]
    if bits:
        out.append("labeler fields: %s" % ", ".join(bits))
    m, note = _event_mult(ev)
    if m is not None:
        line = "joint event-day model: %.2fx for %s / %s / %s, day %s (floored at 1.0; a measured average for events like this)" % (
            m, ev.get("ptype"), ev.get("size") or "size n/a", ev.get("timing") or "timing n/a", ev.get("off"))
        if str(card.get("band_group") or "").startswith("earnings window"):
            line += "; the day's band uses the measured earnings + event group value %.2fx instead" % (card.get("event_multiplier") or 1.0)
        out.append(line)
    elif note:
        out.append("joint event-day model: no multiplier (%s)" % note)
    return out


def event_edge(card, event_id, gstatus, gtext):
    """(status, text) for the line from an event to the stock. The line follows what was measured for THIS kind of event: the proven own-event width row when the joint model gives a
    multiplier above 1.0; a dashed line when it floors at 1.0 (for example capital raises: no widening); dotted when the type has no multiplier."""
    ev = _event(card, event_id)
    if not ev:
        return gstatus, gtext
    m, note = _event_mult(ev)
    if m is None:
        return None, "%s; no multiplier for this kind of event (%s)" % (gtext, note)
    if m <= 1.0 + 1e-9:
        return "null", "%s; but the joint model gives this kind of event no widening (multiplier floored at 1.0)" % gtext
    return gstatus, "%s; joint model %.2fx for this kind of event" % (gtext, m)
