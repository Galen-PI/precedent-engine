#!/usr/bin/env python3
"""
day_decomp.py (v2) -- READ-ONLY. How much of one stock's move on one day do the market, its sector and the macro factors explain (signed), and what is left?

Usage:   python3 scripts/card/day_decomp.py JPM 2025-04-09
Output:  printed summary and scripts/card/out/decomp_JPM_2025-04-09.json

METHOD (an EXPLANATION using same-day factor moves, not a forecast):
  r      = the stock's daily return (adjusted close to adjusted close)
  r_m    = SPY's return that day;  s = (equal-weighted mean return of the other stocks in the same sector, >= 5 peers) - r_m
  oil    = WTI daily return (days with both prices > 5 only);  yield = change in the 10-year yield (percentage points);
  credit = change in the Baa-minus-Aaa spread (percentage points)
  LAYER 1 = market and sector.  LAYER 2 = layer 1 plus oil, yield and credit, in ONE joint regression (terms can offset each other).
  Betas = ordinary least squares with an intercept over the 250 trading days BEFORE the day; the day itself is never used to fit.
  Each pull = beta x that factor's value today; hypothetical return = the sum of the pulls (intercept ignored);
  residual = actual - hypothetical; residual z = residual / the model's own in-sample residual stdev.
  Both layers are fit on the SAME rows (days where all five factors exist) so they are comparable.
  HOLDOUT CHECK: both layers are re-fit on the first part of the estimation window and scored on its last 60 days (never used to fit);
  R2_oos = 1 - (model squared error) / (squared error of predicting zero). Layer 2 keeps its place only if it beats layer 1 there.
Not included: company events and anything else that is magnitude-only in the ledger (a signed effect needs its own validated test).
Reads: securities, market_prices, macro_long. Writes nothing to the database.
"""
import os, sys, json, math
from datetime import date, timedelta
from collections import defaultdict

EST_DAYS = 250
MIN_PEERS = 5
MIN_EST = 120
HOLDOUT = 60
FACTORS = ["market", "sector", "oil", "yield", "credit"]
LABELS = {"market": "market (SPY)", "sector": "sector beyond market", "oil": "oil return", "yield": "10-year yield change (pp)", "credit": "credit spread change (pp)"}


def get_sb():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def fetch(sb, table, cols, filters=(), order=None, limit=None):
    rows, off = [], 0
    while True:
        q = sb.table(table).select(cols)
        for f in filters:
            q = f(q)
        if order:
            q = q.order(order)
        if limit is not None:
            return q.limit(limit).execute().data
        page = q.range(off, off + 999).execute().data
        if not page:
            break
        rows.extend(page)
        if len(page) < 1000:
            break
        off += 1000
    return rows


def prices_for(sb, ids, start, end):
    out = defaultdict(dict)
    ids = list(ids)
    for i in range(0, len(ids), 25):
        chunk = ids[i:i + 25]
        rows = fetch(sb, "market_prices", "security_id,price_date,adjusted_close",
                     [lambda q: q.in_("security_id", chunk), lambda q: q.gte("price_date", start), lambda q: q.lte("price_date", end)],
                     order="price_date")
        for r in rows:
            if r["adjusted_close"] is not None:
                out[r["security_id"]][r["price_date"]] = float(r["adjusted_close"])
    return out


def macro_changes(sb, start, end):
    def series(sid):
        rows = fetch(sb, "macro_long", "obs_date,value", [lambda q: q.eq("series_id", sid), lambda q: q.gte("obs_date", start), lambda q: q.lte("obs_date", end)], order="obs_date")
        return [(r["obs_date"], float(r["value"])) for r in rows if r["value"] is not None]
    oil, y10, aaa, baa = series("DCOILWTICO"), series("DGS10"), dict(series("DAAA")), dict(series("DBAA"))
    out = {"oil": {}, "yield": {}, "credit": {}}
    for i in range(1, len(oil)):
        (d, v), pv = oil[i], oil[i - 1][1]
        if pv > 5 and v > 5:
            out["oil"][d] = v / pv - 1
    for i in range(1, len(y10)):
        out["yield"][y10[i][0]] = y10[i][1] - y10[i - 1][1]
    sp = sorted((d, baa[d] - aaa[d]) for d in aaa if d in baa)
    for i in range(1, len(sp)):
        out["credit"][sp[i][0]] = sp[i][1] - sp[i - 1][1]
    return out


def ols(X, y):
    """X = list of factor rows, y = list; returns [intercept, b1, ..., bk] by normal equations, or None if singular."""
    k = len(X[0]) + 1
    A = [[0.0] * k for _ in range(k)]
    b = [0.0] * k
    for xi, yi in zip(X, y):
        row = [1.0] + list(xi)
        for i in range(k):
            b[i] += row[i] * yi
            for j in range(k):
                A[i][j] += row[i] * row[j]
    for i in range(k):
        p = max(range(i, k), key=lambda r: abs(A[r][i]))
        if abs(A[p][i]) < 1e-18:
            return None
        A[i], A[p] = A[p], A[i]
        b[i], b[p] = b[p], b[i]
        for r in range(i + 1, k):
            f = A[r][i] / A[i][i]
            for j in range(i, k):
                A[r][j] -= f * A[i][j]
            b[r] -= f * b[i]
    x = [0.0] * k
    for i in range(k - 1, -1, -1):
        x[i] = (b[i] - sum(A[i][j] * x[j] for j in range(i + 1, k))) / A[i][i]
    return x


def fit_stats(X, y, coef):
    res = [yi - (coef[0] + sum(c * v for c, v in zip(coef[1:], xi))) for xi, yi in zip(X, y)]
    k = len(coef)
    sd = math.sqrt(sum(e * e for e in res) / (len(res) - k))
    ybar = sum(y) / len(y)
    sst = sum((v - ybar) ** 2 for v in y)
    r2 = 1 - sum(e * e for e in res) / sst if sst > 0 else None
    return sd, r2


def decompose(sb, ticker, ds):
    day = date.fromisoformat(ds)
    sec = fetch(sb, "securities", "id,ticker,sector", [lambda q: q.eq("ticker", ticker)], limit=3)
    if not sec:
        sys.exit("No security with ticker " + ticker)
    sid, sector = sec[0]["id"], sec[0].get("sector")
    spy = fetch(sb, "securities", "id,ticker", [lambda q: q.eq("ticker", "SPY")], limit=1)
    if not spy:
        sys.exit("SPY not found in securities")
    peers = [r["id"] for r in fetch(sb, "securities", "id,ticker,sector", [lambda q: q.eq("sector", sector)]) if r["id"] not in (sid, spy[0]["id"])] if sector else []
    start = (day - timedelta(days=420)).isoformat()
    P = prices_for(sb, [sid, spy[0]["id"]] + peers, start, ds)
    M = macro_changes(sb, start, ds)
    sp, mp = P.get(sid, {}), P.get(spy[0]["id"], {})
    dates = sorted(sp)
    if not dates or dates[-1] != ds:
        sys.exit("No price for %s on %s (last found: %s)" % (ticker, ds, dates[-1] if dates else "none"))
    idx = len(dates) - 1
    if idx < MIN_EST:
        sys.exit("Not enough price history before %s (%d days)" % (ds, idx))

    def ret(series, d, pd):
        if d in series and pd in series and series[pd] > 0:
            return series[d] / series[pd] - 1
        return None

    def peer_mean(d, pd):
        v = [ret(P[p], d, pd) for p in peers if p in P]
        v = [x for x in v if x is not None]
        return (sum(v) / len(v), len(v)) if len(v) >= MIN_PEERS else (None, len(v))

    def factors_on(k):
        d, pd = dates[k], dates[k - 1]
        r, rm = ret(sp, d, pd), ret(mp, d, pd)
        rs, npr = peer_mean(d, pd)
        mo, my, mc = M["oil"].get(d), M["yield"].get(d), M["credit"].get(d)
        if None in (r, rm, rs, mo, my, mc):
            return None, npr
        return (r, [rm, rs - rm, mo, my, mc]), npr

    est = []
    for k in range(max(1, idx - EST_DAYS), idx):
        row, _ = factors_on(k)
        if row:
            est.append(row)
    if len(est) < MIN_EST:
        sys.exit("Too few usable estimation days with all five factors (%d); oil, yield or credit data may be missing" % len(est))
    today, npr = factors_on(idx)
    if not today:
        sys.exit("Missing a factor today (%s): check macro_long for oil, yield, credit on this date, and peers (%d found)" % (ds, npr))
    r_today, x_today = today
    prev_close, actual = sp[dates[idx - 1]], sp[dates[idx]]
    y = [e[0] for e in est]
    X5 = [e[1] for e in est]
    X2 = [e[1][:2] for e in est]

    models = {}
    for name, X, cols in (("layer1", X2, [0, 1]), ("layer2", X5, [0, 1, 2, 3, 4])):
        coef = ols(X, y)
        if coef is None:
            sys.exit("Regression was singular for " + name)
        sd, r2 = fit_stats(X, y, coef)
        pulls = {FACTORS[c]: coef[1 + j] * x_today[c] for j, c in enumerate(cols)}
        hyp = sum(pulls.values())
        models[name] = {"intercept": coef[0], "betas": {FACTORS[c]: coef[1 + j] for j, c in enumerate(cols)}, "pulls": pulls,
                        "hypothetical_return": hyp, "residual": r_today - hyp, "residual_sd": sd, "residual_z": (r_today - hyp) / sd,
                        "hypothetical_price": prev_close * (1 + hyp), "r2_in_sample": r2}

    # holdout: fit on all but the last HOLDOUT estimation rows, score the last HOLDOUT rows
    ho = None
    if len(est) >= MIN_EST + HOLDOUT:
        n_fit = len(est) - HOLDOUT
        res = {}
        for name, X, ncol in (("layer1", X2, 2), ("layer2", X5, 5)):
            coef = ols(X[:n_fit], y[:n_fit])
            if coef is None:
                res = None
                break
            err = sum((yi - (coef[0] + sum(c * v for c, v in zip(coef[1:], xi)))) ** 2 for xi, yi in zip(X[n_fit:], y[n_fit:]))
            res[name] = err
        if res:
            zero = sum(v * v for v in y[n_fit:])
            ho = {"days_scored": HOLDOUT, "r2_oos_layer1": 1 - res["layer1"] / zero, "r2_oos_layer2": 1 - res["layer2"] / zero,
                  "r2_gain_layer2": (1 - res["layer2"] / zero) - (1 - res["layer1"] / zero)}
    return {"ticker": ticker, "date": ds, "sector": sector, "peers_today": npr, "est_days": len(est), "return": r_today,
            "factors_today": dict(zip(FACTORS, x_today)), "prev_close": prev_close, "actual_price": actual,
            "layer1": models["layer1"], "layer2": models["layer2"], "holdout": ho}


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    ticker, ds = sys.argv[1].upper(), sys.argv[2]
    o = decompose(get_sb(), ticker, ds)
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "decomp_%s_%s.json" % (ticker, ds))
    with open(path, "w") as fh:
        json.dump(o, fh, indent=1)
    pc = lambda x: "%+.2f%%" % (100 * x)
    print("%s on %s (%s): actual move %s (previous close %.2f, actual close %.2f)" % (o["ticker"], o["date"], o["sector"], pc(o["return"]), o["prev_close"], o["actual_price"]))
    for name, title in (("layer1", "LAYER 1 (market + sector)"), ("layer2", "LAYER 2 (adds oil, yield, credit; one joint fit)")):
        m = o[name]
        print("\n  %s -- R-squared on the %d fit days: %.2f" % (title, o["est_days"], m["r2_in_sample"]))
        for f in FACTORS:
            if f in m["pulls"]:
                x = o["factors_today"][f]
                xs = pc(x) if f in ("market", "sector", "oil") else "%+.2f pp" % x
                print("    %-26s today %-10s x beta %+7.2f -> pulls %s" % (LABELS[f], xs, m["betas"][f], pc(m["pulls"][f])))
        print("    hypothetical move %s -> price %.2f | actual %.2f | residual %s (%.1f usual residual sds; sd %s)" % (
            pc(m["hypothetical_return"]), m["hypothetical_price"], o["actual_price"], pc(m["residual"]), m["residual_z"], pc(m["residual_sd"])))
    h = o["holdout"]
    if h:
        g = h["r2_gain_layer2"]
        verdict = "BEATS" if g >= 0.02 else ("is WORSE than" if g <= -0.02 else "is about the same as (within 0.02)")
        print("\n  HOLDOUT (fit before the last %d estimation days, scored on them): R2_oos layer 1 %+.2f, layer 2 %+.2f -> layer 2 %s layer 1 there" % (
            h["days_scored"], h["r2_oos_layer1"], h["r2_oos_layer2"], verdict))
    print("\n  better on this day: %s (smaller absolute residual)" % ("layer 2" if abs(o["layer2"]["residual"]) < abs(o["layer1"]["residual"]) else "layer 1"))
    print("  saved %s" % path)


if __name__ == "__main__":
    main()
