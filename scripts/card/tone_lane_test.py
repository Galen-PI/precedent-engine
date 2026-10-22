#!/usr/bin/env python3
"""
tone_lane_test.py -- READ-ONLY (local matrices; the database is read for article counts and tone, 8-K filings and recorded events). Writes only a local cache (data_cache/gdelt_ac_tone.npz, gitignored) so a rerun does not re-read the 1.3 million rows.
THE QUESTION. sentiment_lane_test.py found no usable lane in article VOLUME (matched shortfall +0.6 / +0.5 points against a 5-point bar). The table also carries avg_tone, and tone can only matter for DIRECTION: does a tone shock the day before tell the SIGN of the next ordinary day's miss (the return beyond the market and sector pulls),
beyond what the previous day's own miss already implies? (Tone often just mirrors the last move, and a move can have short-term momentum or reversal, so a naive hit rate would be a disguised autocorrelation.)
THE FLAG (public before day t opens). TONE SHOCK on day t-1: the day's article-weighted average tone (weekend articles roll into the next trading day, like the volume loader) on at least 3 articles, with a z-score against the same stock's previous 28 trading days (at least 14 with articles, spread at least 0.2): POS if z >= +2, NEG if z <= -2.
POPULATION. ORDINARY stock-days t: band units exist for t and t-1, tone coverage on t-1, and NO recorded event and NO earnings window (Item 2.02 filing day and the next) on days t-2, t-1 or t. Eras 2015-2020 and 2021-2026.
OUTCOME. Is day t's miss positive? (sign of the band unit). PRIMARY MEASURE = MATCHED LIFT = P(miss > 0 | POS) - P(miss > 0 | NEG), compared within 24 bins of the SIGNED band unit of day t-1 (percentile edges 1, 2.5, 5, 10, 15 ... 90, 95, 97.5, 99 of the era's ordinary days), bins weighted by n_pos x n_neg / (n_pos + n_neg), bins missing either group dropped.
Also reported: the unmatched lift, and how strongly the flags track the previous day's sign (the share of POS / NEG flags whose day-t-1 miss was positive). INTERVALS: calendar months resampled (500). PLACEBO: each stock's flags shifted back by a random 10-40 days (it must read about 0).
SECONDARY (PLACE IN THE PRICE). Matched mean difference of the signed band unit, POS minus NEG (delta, in band units). Held out across eras: delta fitted on one era is used as a centre shift of +delta/2 on POS days and -delta/2 on NEG days of the OTHER era; REDUCTION = 1 - (squared miss after the shift) / (squared miss before), on flagged days.
PRE-SET RULES (before any real run). TONE POINTS THE RIGHT WAY (a lead, annotation only) if in BOTH eras: at least 2,000 POS and 2,000 NEG days, matched lift >= 3.0 points with the 95% interval's lower end above +1.0, and the placebo's matched lift within +-2.0 (the placebo's own sampling error at this size is about +-0.9; a +-1.5 guard failed a clean synthetic world). TONE EARNS A PLACE IN THE PRICE only if, in addition, the held-out
reduction is at least 0.5% in BOTH directions (fit on 2015-2020 scored on 2021-2026, and the reverse). If the UNMATCHED lift is >= 3 points in both eras but the matched rule fails: 'TONE MIRRORS THE LAST MOVE, no lane'. Otherwise 'NO LANE'.
PREDICTIONS (before the real run): flagged days 10,000-25,000 per era (POS and NEG each 4,000-14,000); POS flags follow a positive day-t-1 miss 58-70% of the time and NEG flags 30-42%; unmatched lift +1 to +6 points; MATCHED lift -1 to +2 points (rule 'points the right way' passes with probability about 8%); placebo within +-2; held-out reduction under 0.1% (place in the price: about 1%).
VALIDATION (synthetic worlds, 260 stocks, 2014-2024, written and run before the real data): CONTROL (tone unrelated to anything) matched lift -0.7 / +0.6, NO LANE. WEAK planted news drift (0.07 sd after a tone-visible news shock; only about 40% of flagged days carry a real shock, so about +2 points of lift) +1.7 / +2.8: NO LANE (below the 3-point bar, estimates positive).
STRONG planted drift (0.15 sd) +4.5 / +5.7 [lower ends +3.1 / +4.0]: TONE POINTS THE RIGHT WAY, held-out reduction +0.2% (not a place in the price). CONFOUND (tone mirrors the same-day return, loading 1.0, and returns have momentum 0.08; no news effect): POS flags follow a positive miss 83% of the time, unmatched lift +7.6 / +8.7, MATCHED +0.5 / +0.0
[intervals about +-2.4]: TONE MIRRORS THE LAST MOVE. BOTH (strong drift plus the confound): matched +8.3 / +6.9 (larger than the clean world because the echo-driven tone spread leaves fewer pure-noise flags in the matched middle bins; finer matching at 48 and 100 bins gave the same numbers, and the confound-only world reads 0): a place in the price (held-out +1.25% / +1.03%).
Two corrections were made before any real run: a placebo guard of +-1.5 failed a clean world (widened to +-2.0), and the first confound world was unrealistically strong (every POS flag followed a positive miss, so matching had no overlap; the intervals were +-30-60 points, correctly labelled but uninformative).
Usage:   python3 -u scripts/card/tone_lane_test.py [--refresh]      Needs data_cache/audit_matrices.npz and company_sentiment_timeline (avg_tone). The first run reads the table (about 25 minutes); later runs use the cache unless --refresh.
"""
import os, sys, bisect, time, warnings
from collections import defaultdict
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = uc.CACHE_FILE
TONE_CACHE = os.path.join(ROOT, "data_cache", "gdelt_ac_tone.npz")
ERAS = [("2015-2020", 2015, 2020), ("2021-2026", 2021, 2026)]
TONE_Z, MIN_ART, BASE_WIN, MIN_BASE, MIN_SD = 2.0, 3, 28, 14, 0.2
MIN_GROUP, LIFT_MIN, LIFT_LOWER, PLACEBO_MAX, REDUCTION_MIN = 2000, 0.03, 0.01, 0.02, 0.005
EDGE_PCTS = [1, 2.5, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 97.5, 99]
DEC = len(EDGE_PCTS) + 1
N_BOOT = 500
SEED = 20261027


def load_tone(sb, ids, dl):
    """Article counts and article-weighted average tone per stock and trading day (weekend and holiday articles roll into the next trading day)."""
    N, n = len(ids), len(dl)
    sec = uc.paged(lambda: sb.table("securities").select("id,entity_id").order("id"))
    ent_of = {r["id"]: r["entity_id"] for r in sec if r.get("entity_id")}
    k_of_ent = defaultdict(list)
    for k, sid in enumerate(ids):
        e = ent_of.get(sid)
        if e:
            k_of_ent[e].append(k)
    rows = uc.paged(lambda: sb.table("company_sentiment_timeline").select("entity_id,date,article_count,avg_tone").order("id"))
    pc, ps = defaultdict(dict), defaultdict(dict)
    nrows = 0
    for r in rows:
        nrows += 1
        e = r["entity_id"]
        if e not in k_of_ent or r.get("article_count") is None or r.get("avg_tone") is None:
            continue
        t = bisect.bisect_left(dl, str(r["date"])[:10])
        if t < n:
            c = int(r["article_count"])
            pc[e][t] = pc[e].get(t, 0) + c
            ps[e][t] = ps[e].get(t, 0.0) + c * float(r["avg_tone"])
    AC, TN = np.full((N, n), np.nan), np.full((N, n), np.nan)
    for e, dct in pc.items():
        ts = sorted(dct)
        lo, hi = ts[0], ts[-1]
        ac, sm = np.zeros(hi - lo + 1), np.zeros(hi - lo + 1)
        for t in ts:
            ac[t - lo], sm[t - lo] = dct[t], ps[e][t]
        with np.errstate(invalid="ignore", divide="ignore"):
            tone = np.where(ac > 0, sm / ac, np.nan)
        for k in k_of_ent[e]:
            AC[k, lo:hi + 1], TN[k, lo:hi + 1] = ac, tone
    return AC, TN, len(pc), nrows


def tone_z(tn, ac):
    n = len(tn)
    z = np.full(n, np.nan)
    if np.isfinite(tn).sum() < 100 or n <= BASE_WIN:
        return z
    Wv = sliding_window_view(tn, BASE_WIN + 1)
    base, cur = Wv[:, :BASE_WIN], Wv[:, BASE_WIN]
    cnt = np.isfinite(base).sum(axis=1)
    mean, sd = np.nanmean(base, axis=1), np.nanstd(base, axis=1, ddof=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        zz = (cur - mean) / sd
    ok = (cnt >= MIN_BASE) & np.isfinite(cur) & (sd >= MIN_SD) & (ac[BASE_WIN:] >= MIN_ART)
    z[BASE_WIN:] = np.where(ok, zz, np.nan)
    return z


def matched_stats(o, W=None):
    """matched lift, matched delta (signed band units), unmatched lift from the per-month x per-bin sufficient statistics."""
    Mn = o["np"].shape[0]
    w = np.ones(Mn) if W is None else W
    npos, nneg, hp, hn, sp, sn = (w @ o["np"], w @ o["nn"], w @ o["hp"], w @ o["hn"], w @ o["sp"], w @ o["sn"])
    ok = (npos > 0) & (nneg > 0)
    wb = (npos[ok] * nneg[ok]) / (npos[ok] + nneg[ok])
    lift = float(np.sum(wb * (hp[ok] / npos[ok] - hn[ok] / nneg[ok])) / wb.sum())
    delta = float(np.sum(wb * (sp[ok] / npos[ok] - sn[ok] / nneg[ok])) / wb.sum())
    un = float(hp.sum() / max(npos.sum(), 1) - hn.sum() / max(nneg.sum(), 1))
    return lift, delta, un


def main():
    t0 = time.time()
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E_, SD = d["dates"], d["ids"].tolist(), d["E"].astype(np.float64), d["SD"].astype(np.float64)
    N, n = E_.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    months = np.array([int(x[:4]) * 12 + int(x[5:7]) - 1 for x in dl])
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = E_ / SD
    Zsq = Z ** 2
    valid = np.isfinite(Zsq)
    S = np.where(valid, Zsq, 0.0).sum(axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        sbu = Z / np.sqrt(qo)                                  # SIGNED band unit
    sbu[~((cnt[None, :] > 20) & np.isfinite(sbu))] = np.nan
    fin = np.isfinite(sbu)

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    use_cache = os.path.exists(TONE_CACHE) and "--refresh" not in sys.argv
    if use_cache:
        c = np.load(TONE_CACHE, allow_pickle=False)
        use_cache = c["ids"].tolist() == ids and c["dates"].tolist() == dl
    if use_cache:
        AC, TN, nent, nrows = c["AC"], c["TN"], int(c["nent"]), int(c["nrows"])
        print("tone matrices read from the cache (%s)" % TONE_CACHE, flush=True)
    else:
        AC, TN, nent, nrows = load_tone(sb, ids, dl)
        os.makedirs(os.path.dirname(TONE_CACHE), exist_ok=True)
        np.savez(TONE_CACHE, AC=AC, TN=TN, ids=np.array(ids), dates=np.array(dl), nent=nent, nrows=nrows)
    Zt = np.full((N, n), np.nan)
    for k in range(N):
        Zt[k] = tone_z(TN[k], AC[k])
    POS, NEG = np.isfinite(Zt) & (Zt >= TONE_Z), np.isfinite(Zt) & (Zt <= -TONE_Z)
    COV = np.isfinite(Zt)
    print("article rows read %d for %d entities | stock-days with a tone z-score %.1f%% | POS days %d, NEG days %d | %.0fs" % (nrows, nent, 100.0 * COV.mean(), int(POS.sum()), int(NEG.sum()), time.time() - t0), flush=True)

    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids))
    known = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                known[k, t] = True
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is not None and "2.02" in set(dc.parse_items(r.get("item_codes"))):
            i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
            known[k, i:min(i + 2, n)] = True
    kn = known.copy()
    kn[:, 1:] |= known[:, :-1]
    kn[:, 2:] |= known[:, :-2]

    def shift(A, s, fill):
        out = np.full_like(A, fill)
        out[:, s:] = A[:, :n - s]
        return out
    X1 = shift(sbu, 1, np.nan)                                   # signed band unit on day t-1
    base_ok = fin & np.isfinite(X1) & ~kn
    rng = np.random.RandomState(SEED)
    lags = rng.randint(10, 41, size=N)

    def era_stats(pos_prev, neg_prev, cov_prev, lo, hi):
        V = base_ok & cov_prev & (years >= lo)[None, :] & (years <= hi)[None, :]
        Pm, Nm = V & pos_prev, V & neg_prev
        if Pm.sum() == 0 or Nm.sum() == 0:
            return None
        edges = np.percentile(X1[V], EDGE_PCTS)
        dec = np.digitize(np.nan_to_num(X1, nan=0.0), edges)
        mo = months - months.min()
        Mn = int(mo.max()) + 1
        o, tot = {}, {}
        for name, mask in (("p", Pm), ("n", Nm)):
            kk, tt = np.nonzero(mask)
            i3 = mo[tt] * DEC + dec[kk, tt]
            x = sbu[kk, tt]
            o["n" + name] = np.bincount(i3, minlength=Mn * DEC).reshape(Mn, DEC).astype(float)
            o["h" + name] = np.bincount(i3, weights=(x > 0).astype(float), minlength=Mn * DEC).reshape(Mn, DEC)
            o["s" + name] = np.bincount(i3, weights=x, minlength=Mn * DEC).reshape(Mn, DEC)
            tot[name] = (len(x), float(x.sum()), float((x * x).sum()), float((X1[kk, tt] > 0).mean()))
        return o, tot, Mn

    results = {}
    for lab, lo, hi in ERAS:
        st = era_stats(shift(POS, 1, False), shift(NEG, 1, False), shift(COV, 1, False), lo, hi)
        PP, PN, PC = (np.zeros((N, n), dtype=bool) for _ in range(3))
        for k in range(N):
            L = int(lags[k]) + 1
            PP[k, L:], PN[k, L:], PC[k, L:] = POS[k, :n - L], NEG[k, :n - L], COV[k, :n - L]
        sp = era_stats(PP, PN, PC, lo, hi)
        if st is None or sp is None:
            print("%s: no POS or no NEG days" % lab); results[lab] = None; continue
        o, tot, Mn = st
        lift, delta, un = matched_stats(o)
        plift, pdelta, pun = matched_stats(sp[0])
        present = np.where(o["np"].sum(axis=1) + o["nn"].sum(axis=1) > 0)[0]
        brng = np.random.RandomState(SEED + hi)
        bl, bd = [], []
        for _ in range(N_BOOT):
            W = np.bincount(brng.choice(present, size=len(present)), minlength=Mn).astype(float)
            l_, d_, _u = matched_stats(o, W)
            bl.append(l_); bd.append(d_)
        results[lab] = dict(npos=tot["p"][0], nneg=tot["n"][0], un=un, lift=lift, lo=np.percentile(bl, 2.5), hi=np.percentile(bl, 97.5), delta=delta, dlo=np.percentile(bd, 2.5), dhi=np.percentile(bd, 97.5),
                            plift=plift, ppos=tot["p"][3], pneg=tot["n"][3], tot=tot)
        r = results[lab]
        print("%s | POS %d, NEG %d | previous-day miss positive: after POS flags %.0f%%, after NEG flags %.0f%% | UNMATCHED lift %+.1f pts | MATCHED lift %+.1f pts [%+.1f, %+.1f] | matched delta %+.3f band units [%+.3f, %+.3f] | PLACEBO matched lift %+.1f pts" % (
            lab, r["npos"], r["nneg"], 100 * r["ppos"], 100 * r["pneg"], 100 * un, 100 * lift, 100 * r["lo"], 100 * r["hi"], delta, r["dlo"], r["dhi"], 100 * plift), flush=True)
    ok = all(r is not None for r in results.values())
    red = {}
    if ok:
        labs = [e[0] for e in ERAS]
        for fit, score in ((labs[0], labs[1]), (labs[1], labs[0])):
            dh = results[fit]["delta"] / 2.0
            (np_, sxp, sxxp, _a), (nn_, sxn, sxxn, _b) = results[score]["tot"]["p"], results[score]["tot"]["n"]
            after = (sxxp - 2 * dh * sxp + np_ * dh * dh) + (sxxn + 2 * dh * sxn + nn_ * dh * dh)
            red[(fit, score)] = 1.0 - after / (sxxp + sxxn)
            print("held-out centre test: shift fitted on %s (delta %+.3f) scored on %s: squared miss of flagged days changes by %+.3f%%" % (fit, results[fit]["delta"], score, 100 * red[(fit, score)]))
    lead = ok and all(r["npos"] >= MIN_GROUP and r["nneg"] >= MIN_GROUP and r["lift"] >= LIFT_MIN and r["lo"] > LIFT_LOWER and abs(r["plift"]) <= PLACEBO_MAX for r in results.values())
    place = lead and all(v >= REDUCTION_MIN for v in red.values())
    if place:
        verdict = "TONE EARNS A PLACE IN THE PRICE"
    elif lead:
        verdict = "TONE POINTS THE RIGHT WAY (lead, annotation only); it does not earn a place in the price"
    elif ok and all(r["un"] >= 0.03 for r in results.values()):
        verdict = "TONE MIRRORS THE LAST MOVE, no lane"
    else:
        verdict = "NO LANE"
    print("\nVERDICT (pre-set: both eras >= %d POS and NEG days, matched lift >= 3.0 points with the interval's lower end above +1.0, placebo within +-2.0; a place in the price also needs a held-out reduction >= 0.5%% both ways): %s" % (MIN_GROUP, verdict))
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
