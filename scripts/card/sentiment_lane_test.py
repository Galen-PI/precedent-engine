#!/usr/bin/env python3
"""
sentiment_lane_test.py -- READ-ONLY (local matrices; the database is read for article counts, 8-K filings and recorded events). Writes nothing.
THE QUESTION. The ledger lists 'GDELT sentiment' as untested because the table covered about a third of the companies with a level break in June 2023; it was repaired on 2026-10-21 (420-447 companies per month, consistent counts). Design rules agreed for every lane: only a flag KNOWN BEFORE the day counts for a forward
range; the test must say whether it adds anything beyond what the range already knows (the stock's own volatility and its last move); every filter shows n and eras; failures stay in the ledger as 'no documented effect'.
THE FLAG. ARTICLE SPIKE on day t-1: the detector's rule (company_sentiment_timeline article count that day >= 3 and >= 3x the mean of the previous 28 trading days, floor 0.5; unorganised weekend counts added to the next trading day), taken from the detector's own functions. The flag for DAY t is a spike on day t-1, so it is
public before day t opens. Counts only: the table's tone columns are not used (their names were not checked); a tone lane is a separate test.
THE OUTCOME. Day t's squared band unit and its coverage: the share of stock-days with |band unit| <= k_ref, where k_ref is the 90th percentile of |band unit| on UNFLAGGED days of the same era (so unflagged coverage is 90% by construction). SHORTFALL = unflagged coverage - flagged coverage, in points.
POPULATION. ORDINARY stock-days t only: the band unit exists for t and t-1, the article count had coverage on t-1, and NO recorded event and NO earnings window (Item 2.02 filing day and the next) on days t-2, t-1 or t, so a flag cannot just be a restatement of a known event. Eras: 2015-2020 and 2021-2026.
MATCHING. A spike often follows a big move, and volatility clusters, so a flag could be only a proxy for the last move, which a range already sees. MATCHED SHORTFALL = flagged and unflagged days compared within 23 bins of |band unit on day t-1| (5%-wide bins up to the 90th percentile, then 96, 98, 99 and 99.5; edges from the unflagged days of the era), weighted by the flagged counts.
VALIDATION (synthetic worlds written before any real run; 260 stocks, 2014-2024): CONTROL reads 0.1 / -0.4 points (NO LANE); a planted 25% volatility lift on the day after a spike reads +6.3 / +5.6 matched [lower ends +5.1 / +4.3] (lane justified); a CONFOUND world (big moves cause both spikes and next-day volatility; no direct effect) reads +18.7 unmatched and +3.3 / +2.9 with the coarser deciles (labelled clustering, not a lane); finer tail bins are the fix and their result is in the session notes.
INTERVALS: calendar months resampled (500 resamples). PLACEBO: the same test with each stock's flag shifted back by a random 10-40 days (it must read about 0).
PRE-SET RULE. THE LANE JUSTIFIES A RANGE MULTIPLIER (a separate, held-out multiplier check would follow) if in BOTH eras: flagged stock-days >= 5,000, MATCHED shortfall >= 5 points with the 95% interval's lower end above 3 points, and the placebo's matched shortfall within +-1.5 points. If the UNMATCHED shortfall is >= 5 points in both eras but the matched one fails:
'VOLATILITY CLUSTERING, not a separate lane'. Otherwise 'NO LANE'.
PREDICTIONS (before the real run): flagged stock-days 8,000-20,000 per era; unmatched shortfall 3-8 points; MATCHED shortfall 0-4 points (the lane justifies a multiplier with probability about 25%); placebo within +-1; the matched mean squared band unit ratio 1.05-1.25.
Usage:   python3 -u scripts/card/sentiment_lane_test.py        Needs data_cache/audit_matrices.npz and the repaired company_sentiment_timeline.
"""
import os, sys, bisect, time, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc

CACHE_FILE = uc.CACHE_FILE
ERAS = [("2015-2020", 2015, 2020), ("2021-2026", 2021, 2026)]
MIN_FLAGGED = 5000
N_BOOT = 500
SEED = 20261026
EDGE_PCTS = list(range(5, 95, 5)) + [96, 98, 99, 99.5]      # decile-like bins, finer in the tail where spike days sit (a coarser top decile left a residual confound in validation)
DEC = len(EDGE_PCTS) + 1


def main():
    t0 = time.time()
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E_, SD = d["dates"], d["ids"].tolist(), d["E"].astype(np.float64), d["SD"].astype(np.float64)
    N, n = E_.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    months = np.array([int(x[:4]) * 12 + int(x[5:7]) - 1 for x in dl])
    with np.errstate(invalid="ignore", divide="ignore"):
        Zsq = (E_ / SD) ** 2
    valid = np.isfinite(Zsq)
    S = np.where(valid, Zsq, 0.0).sum(axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        bu2 = Zsq / qo
    bu2[~((cnt[None, :] > 20) & np.isfinite(bu2))] = np.nan
    fin = np.isfinite(bu2)
    absbu = np.sqrt(bu2)

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    AC, nent, nrows = uc.load_articles(sb, ids, dl)
    SP, COV = uc.article_spike(AC)
    print("article rows read %d for %d entities | stock-days with article coverage %.1f%% | spike days %d | %.0fs" % (nrows, nent, 100.0 * COV.mean(), int(SP.sum()), time.time() - t0), flush=True)
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
    kn[:, 2:] |= known[:, :-2]                                  # known event or earnings on t-2..t

    def shift(A, s, fill):
        out = np.full_like(A, fill)
        out[:, s:] = A[:, :n - s]
        return out
    fin1 = shift(fin, 1, False)
    X1 = shift(absbu, 1, np.nan)                                # |band unit| on day t-1
    base_ok = fin & fin1 & ~kn
    rng = np.random.RandomState(SEED)
    lags = rng.randint(10, 41, size=N)

    def era_stats(flag_prev, cov_prev, lo, hi):
        """flag_prev / cov_prev are indexed at day t-1 already shifted to day t."""
        V = base_ok & cov_prev & (years >= lo)[None, :] & (years <= hi)[None, :]
        F, U = V & flag_prev, V & ~flag_prev
        if F.sum() == 0 or U.sum() == 0:
            return None
        kref = float(np.percentile(absbu[U], 90))
        edges = np.percentile(X1[U], EDGE_PCTS)
        dec = np.digitize(np.nan_to_num(X1, nan=0.0), edges)
        mo = months - months.min()
        Mn = int(mo.max()) + 1
        out = {}
        for name, mask in (("f", F), ("u", U)):
            kk, tt = np.nonzero(mask)
            idx3 = mo[tt] * DEC + dec[kk, tt]
            out["n" + name] = np.bincount(idx3, minlength=Mn * DEC).reshape(Mn, DEC).astype(float)
            out["h" + name] = np.bincount(idx3, weights=(absbu[kk, tt] <= kref).astype(float), minlength=Mn * DEC).reshape(Mn, DEC)
            out["s" + name] = np.bincount(idx3, weights=bu2[kk, tt], minlength=Mn * DEC).reshape(Mn, DEC)
        return kref, out, int(F.sum()), int(U.sum()), Mn, mo

    def summarize(st, W=None):
        kref, o, nf_, nu_, Mn, mo = st
        w = np.ones(Mn) if W is None else W
        nf, hf, sf, nu, hu, su = (w @ o["nf"], w @ o["hf"], w @ o["sf"], w @ o["nu"], w @ o["hu"], w @ o["su"])
        ok = (nf > 0) & (nu > 0)
        wd = nf[ok] / nf[ok].sum()
        short = float(np.sum(wd * (hu[ok] / nu[ok] - hf[ok] / nf[ok])))
        ratio = float(np.sum(wd * (sf[ok] / nf[ok])) / np.sum(wd * (su[ok] / nu[ok])))
        un = float(hu.sum() / nu.sum() - hf.sum() / nf.sum())
        return short, ratio, un

    results = {}
    for lab, lo, hi in ERAS:
        st = era_stats(shift(SP, 1, False), shift(COV, 1, False), lo, hi)
        PSP, PCOV = np.zeros((N, n), dtype=bool), np.zeros((N, n), dtype=bool)
        for k in range(N):
            L = int(lags[k]) + 1
            PSP[k, L:] = SP[k, :n - L]
            PCOV[k, L:] = COV[k, :n - L]
        sp = era_stats(PSP, PCOV, lo, hi)
        if st is None or sp is None:
            print("%s: no flagged or no unflagged days" % lab); results[lab] = None; continue
        short, ratio, un = summarize(st)
        pshort, pratio, pun = summarize(sp)
        mo_present = np.where(st[1]["nf"].sum(axis=1) + st[1]["nu"].sum(axis=1) > 0)[0]
        brng = np.random.RandomState(SEED + hi)
        bs, br = [], []
        for _ in range(N_BOOT):
            W = np.bincount(brng.choice(mo_present, size=len(mo_present)), minlength=st[4]).astype(float)
            s_, r_, _u = summarize(st, W)
            bs.append(s_); br.append(r_)
        lo_s, hi_s = np.percentile(bs, [2.5, 97.5])
        lo_r, hi_r = np.percentile(br, [2.5, 97.5])
        results[lab] = dict(nf=st[2], nu=st[3], kref=st[0], un=un, short=short, lo_s=lo_s, hi_s=hi_s, ratio=ratio, lo_r=lo_r, hi_r=hi_r, pshort=pshort, pun=pun)
        print("%s | flagged %d, unflagged %d | k_ref %.2f | UNMATCHED shortfall %+.1f pts | MATCHED shortfall %+.1f pts [%+.1f, %+.1f] | matched mean-square ratio %.2f [%.2f, %.2f] | PLACEBO matched %+.1f pts (unmatched %+.1f)" % (
            lab, st[2], st[3], st[0], 100 * un, 100 * short, 100 * lo_s, 100 * hi_s, ratio, lo_r, hi_r, 100 * pshort, 100 * pun), flush=True)
    ok_all = all(r is not None for r in results.values())
    if ok_all and all(r["nf"] >= MIN_FLAGGED and r["short"] >= 0.05 and r["lo_s"] > 0.03 and abs(r["pshort"]) <= 0.015 for r in results.values()):
        verdict = "THE LANE JUSTIFIES A RANGE MULTIPLIER (held-out multiplier check next)"
    elif ok_all and all(r["un"] >= 0.05 for r in results.values()):
        verdict = "VOLATILITY CLUSTERING, not a separate lane"
    else:
        verdict = "NO LANE"
    print("\nVERDICT (pre-set: both eras flagged >= %d, matched shortfall >= 5 points with the interval's lower end above 3, placebo within +-1.5): %s" % (MIN_FLAGGED, verdict))
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
