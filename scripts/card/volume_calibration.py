#!/usr/bin/env python3
"""
volume_calibration.py -- READ-ONLY (local matrices and caches; the database is read for events and 8-K filings). Writes nothing.
THE QUESTION. unrecorded_candidates.py found that 53.0% of the non-aftershock BIG ordinary misses (>= 3.0 band units, no own event / earnings / Regulation FD window) carry a volume spike (>= 2x the
median of the previous 20 days). What share of those misses carries INFORMATION? Two-component arithmetic: the observed spike rate p = pi*s + (1-pi)*f, so pi = (p - f) / (s - f), where
  s = the spike rate on days where we KNOW information arrived and the miss was big (earnings windows, recorded events, Regulation FD filings: >= 3.0 band units on the same scale),
      REWEIGHTED to the size mix of the ordinary big misses (|miss| bins 3-4, 4-5, 5-7, 7+ band units), because known-information days have bigger moves and volume rises with the size of the move;
  f = the spike rate on big misses with NO information. f CANNOT be observed, because volume also rises with the size of the move without news. Two bounds:
      f_mid  = the spike rate on MID ordinary misses (1-3 band units): a LOWER bound on f for big misses -> pi_upper is an UPPER bound on pi;
      f_extrap = a logistic curve of spike rate against |miss| fitted on ordinary stock-days under 2 band units (where news is rare), extrapolated to the size mix of the big misses -> pi_lower. It rests on the
                 assumption that the fitting range is mostly noise and that the curve's shape holds out to 3-8 band units, a long extrapolation: read pi_lower as indicative, not exact.
Populations (all stock-days from 2006 with a volume ratio, split-masked; ordinary = not in an own event / earnings / Regulation FD window; 'non-aftershock' = the previous day was not a big miss and no flagged window
ended in the previous 5 trading days): CALM < 1.0 band unit, MID 1.0-3.0, BIG >= 3.0.
Usage:   python3 -u scripts/card/volume_calibration.py          Needs: data_cache/audit_matrices.npz, data_cache/volume, the database.

PRE-SET RULE (written before the first run). DEGENERACY CHECK first: if p / s (s reweighted) at 2.0x is 0.90 or more, then ordinary big misses spike about as often as known-information days, so volume cannot
separate information from the SIZE of the move, and pi is NOT quoted at all (on a synthetic world where volume follows the size of the move, pi_upper read 0.98 for a true 0.74 and the consistency check below
still passed; only this check catches it; on a world where volume follows information, the estimate recovered the truth within 2 points). CONSISTENCY CHECK second: the single-threshold two-component picture holds only if pi_upper agrees across thresholds, that is, max - min of pi_upper over the thresholds
1.5x, 2.0x and 3.0x is at most 0.10. If it does not, the picture is misspecified (information does not produce a clean 'spike or no spike' signature) and pi must NOT be quoted as a share; only the range
[pi_lower, pi_upper] at 2.0x and the discrimination table are reported. Everything else is descriptive: bootstrap 95% intervals resample calendar MONTHS (misses cluster in time), 500 resamples.
PREDICTIONS (before the run): p / s at 2.0x is 0.65-0.85 (informative, below 0.90); s (2x, reweighted) 65-85%, s (1.5x) 80-92%, s (3x) 35-55%; f_mid (2x) 7-10%; pi_upper (2x) 0.50-0.70, higher at 1.5x and lower at 3x, so the CONSISTENCY CHECK FAILS (spread
above 0.10; probability about 60%); f_extrap (2x) 12-30% and pi_lower (2x) 0.25-0.55; earnings day 0 spikes more often than day +1 and Regulation FD less often than recorded events; the spike rate on known-information
days falls by at least 8 points from 2006-2012 to 2020-2026 (volume is less informative recently) while pi_upper moves by less than 0.10 across eras.
LIMIT TO STATE UP FRONT: recorded events, earnings and Regulation FD filings are company-filed items; analyst notes, activist stakes, rumours and sector news may have a different volume signature. The estimate is a
share of the big misses that LOOK like information by volume, not a statement about content.
"""
import os, sys, time, bisect, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc
import unrecorded_candidates as uc

CACHE_FILE = uc.CACHE_FILE
TEST_START = 2006
BIG, CALM = 3.0, 1.0
THRESHOLDS = (1.3, 1.5, 2.0, 3.0)
CHECK_T = (1.5, 2.0, 3.0)
BU_BINS = ((3.0, 4.0), (4.0, 5.0), (5.0, 7.0), (7.0, 1e9))
FIT_MAX = 2.0
N_BOOT = 500
SEED = 20261021
ERAS = [("2006-2012", 2006, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]


def fit_logit(x, k, n):
    a, b = float(np.log(max(k.sum(), 1.0) / max(n.sum() - k.sum(), 1.0))), 0.0
    for _ in range(60):
        eta = a + b * x
        p = 1.0 / (1.0 + np.exp(-eta))
        W = n * p * (1 - p)
        g = np.array([(k - n * p).sum(), ((k - n * p) * x).sum()])
        H = np.array([[W.sum(), (W * x).sum()], [(W * x).sum(), (W * x * x).sum()]]) + 1e-9 * np.eye(2)
        step = np.linalg.solve(H, g)
        a, b = a + step[0], b + step[1]
        if np.abs(step).max() < 1e-9:
            break
    return a, b


def pct(x):
    return "%5.1f%%" % (100.0 * x) if np.isfinite(x) else "  n/a "


def pi_of(p, s, f):
    return (p - f) / (s - f) if s > f else float("nan")


def main():
    t0 = time.time()
    if not os.path.exists(CACHE_FILE):
        sys.exit("Run gap_audit.py first: it builds %s." % CACHE_FILE)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E, SD = d["dates"], d["ids"].tolist(), d["E"], d["SD"]
    N, n = E.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    months = np.array([(int(x[:4]) - TEST_START) * 12 + int(x[5:7]) - 1 for x in dl])
    with np.errstate(invalid="ignore", divide="ignore"):
        Zsq = (E.astype(np.float64) / SD.astype(np.float64)) ** 2
    valid = np.isfinite(Zsq)
    S = np.where(valid, Zsq, 0.0).sum(axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (S[None, :] - np.where(valid, Zsq, 0.0)) / (cnt[None, :] - 1)
        bu = np.sqrt(Zsq / qo)
    ok = valid & (cnt[None, :] > 20) & np.isfinite(bu) & (years >= TEST_START)[None, :]

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids))
    EV = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                EV[k, t] = True
    EA0 = np.zeros((N, n), dtype=bool)
    EA1 = np.zeros((N, n), dtype=bool)
    F701 = np.zeros((N, n), dtype=bool)
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is None:
            continue
        its = dc.parse_items(r.get("item_codes"))
        i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
        if i >= n:
            continue
        if "2.02" in its:
            EA0[k, i] = True
            if i + 1 < n:
                EA1[k, i + 1] = True
        elif "7.01" in its:
            F701[k, i] = True
            if i + 1 < n:
                F701[k, i + 1] = True
    EA1 &= ~EA0
    flag_any = EV | EA0 | EA1 | F701
    cs = np.cumsum(flag_any, axis=1)
    post_flag = np.zeros((N, n), dtype=bool)
    post_flag[:, uc.POST_FLAG_DAYS + 1:] = (cs[:, uc.POST_FLAG_DAYS:-1] - cs[:, :-uc.POST_FLAG_DAYS - 1]) > 0
    prev_big = np.zeros((N, n), dtype=bool)
    prev_big[:, 1:] = np.nan_to_num(bu[:, :-1], nan=0.0) >= BIG
    VOL, SPL, have = uc.load_volume(ids, dl)
    VR = uc.vol_ratio(VOL)
    VR[SPL] = np.nan
    base = ok & ~SPL & np.isfinite(VR)
    ord_na = base & ~flag_any & ~prev_big & ~post_flag
    calm, mid, big_ord = ord_na & (bu < CALM), ord_na & (bu >= CALM) & (bu < BIG), ord_na & (bu >= BIG)
    info_big = base & flag_any & (bu >= BIG)
    types = [("earnings day 0 (no event)", info_big & EA0 & ~EV), ("earnings day +1 (no event)", info_big & EA1 & ~EV), ("recorded event, no earnings", info_big & EV & ~(EA0 | EA1)),
             ("Regulation FD (7.01) only", info_big & F701 & ~(EA0 | EA1) & ~EV), ("event + earnings", info_big & EV & (EA0 | EA1))]
    print("securities with volume: %d of %d | %.0fs" % (have, N, time.time() - t0), flush=True)
    print("\nPOPULATIONS (stock-days from %d with a volume ratio, split-masked)" % TEST_START)
    print("  ordinary non-aftershock: CALM %d | MID %d | BIG %d" % (int(calm.sum()), int(mid.sum()), int(big_ord.sum())))
    print("  KNOWN-INFORMATION days with a big miss: %d  (%s)" % (int(info_big.sum()), "; ".join("%s %d" % (a, int(m.sum())) for a, m in types)))

    print("\nSPIKE RATE BY VOLUME THRESHOLD (share of stock-days with volume >= T x the median of the previous 20 days)")
    print("  %-34s %8s | %s" % ("group", "days", "  ".join("%7s" % (">= %.1fx" % T) for T in THRESHOLDS)))
    groups = [("CALM ordinary (< 1 band unit)", calm), ("MID ordinary (1-3)", mid), ("BIG ordinary, non-aftershock", big_ord), ("KNOWN INFORMATION, big (raw)", info_big)] + types
    for lab, m in groups:
        print("  %-34s %8d | %s" % (lab, int(m.sum()), "  ".join(pct(float((VR[m] >= T).mean())) if m.any() else "  n/a " for T in THRESHOLDS)))

    # standardised s, f_mid, f_extrap, pi by threshold
    bu_big = bu[big_ord]
    wbins = [int(((bu_big >= lo) & (bu_big < hi)).sum()) for lo, hi in BU_BINS]
    xb = np.arange(0.05, FIT_MAX, 0.1)
    fitmask = ord_na & (bu < FIT_MAX)
    fit_n = np.histogram(bu[fitmask], bins=np.arange(0.0, FIT_MAX + 1e-9, 0.1))[0].astype(float)

    def std_s(T, mask_info=info_big):
        tot = wsum = 0.0
        for (lo, hi), wb in zip(BU_BINS, wbins):
            mi = mask_info & (bu >= lo) & (bu < hi)
            if int(mi.sum()) < 30 or wb == 0:
                continue
            tot += wb * float((VR[mi] >= T).mean())
            wsum += wb
        return tot / wsum if wsum else float("nan")

    print("\nTWO-COMPONENT ESTIMATE BY THRESHOLD  (pi = (p - f) / (s - f); p = observed rate on BIG ordinary non-aftershock misses)")
    print("  %-7s %7s %9s %7s %9s | %9s | %9s %10s | %s" % ("T", "p", "s (std)", "s raw", "f_mid", "pi_upper", "f_extrap", "pi_lower", "discrimination s - f_mid"))
    est = {}
    for T in THRESHOLDS:
        p = float((VR[big_ord] >= T).mean())
        s = std_s(T)
        s_raw = float((VR[info_big] >= T).mean())
        f_mid = float((VR[mid] >= T).mean())
        k = np.histogram(bu[fitmask & (VR >= T)], bins=np.arange(0.0, FIT_MAX + 1e-9, 0.1))[0].astype(float)
        a, b = fit_logit(xb, k, fit_n)
        f_ex = float((1.0 / (1.0 + np.exp(-(a + b * bu_big)))).mean())
        est[T] = (p, s, f_mid, f_ex)
        print("  >= %.1fx %7s %9s %7s %9s | %9.2f | %9s %10.2f | %+.3f" % (T, pct(p), pct(s), pct(s_raw), pct(f_mid), pi_of(p, s, f_mid), pct(f_ex), min(max(pi_of(p, s, f_ex), 0.0), 1.0), s - f_mid))
    pis = [pi_of(est[T][0], est[T][1], est[T][2]) for T in CHECK_T]
    spread = max(pis) - min(pis)

    # month-block bootstrap at T = 2
    T2 = 2.0
    M = int(months.max()) + 1
    def per_month(mask, extra=None):
        cols = np.where(mask)[1]
        return np.bincount(months[cols], minlength=M).astype(float)
    sp2 = VR >= T2
    bo_tot, bo_sp = per_month(big_ord), per_month(big_ord & sp2)
    mi_tot, mi_sp = per_month(mid), per_month(mid & sp2)
    ib_tot = np.array([per_month(info_big & (bu >= lo) & (bu < hi)) for lo, hi in BU_BINS])
    ib_sp = np.array([per_month(info_big & (bu >= lo) & (bu < hi) & sp2) for lo, hi in BU_BINS])
    bb_tot = np.array([per_month(big_ord & (bu >= lo) & (bu < hi)) for lo, hi in BU_BINS])

    def pi_from_weights(w):
        p = (w @ bo_sp) / max(w @ bo_tot, 1.0)
        f = (w @ mi_sp) / max(w @ mi_tot, 1.0)
        it, isp, bt = ib_tot @ w, ib_sp @ w, bb_tot @ w
        good = (it >= 30) & (bt > 0)
        if not good.any():
            return float("nan"), p, float("nan"), f
        s = float((bt[good] * (isp[good] / it[good])).sum() / bt[good].sum())
        return pi_of(p, s, f), p, s, f

    rng = np.random.RandomState(SEED)
    def boot(month_ids):
        out = []
        for _ in range(N_BOOT):
            w = np.bincount(rng.choice(month_ids, size=len(month_ids)), minlength=M).astype(float)
            out.append(pi_from_weights(w)[0])
        out = np.array(out)
        return np.nanpercentile(out, [2.5, 97.5])
    all_m = np.where(bo_tot + mi_tot > 0)[0]
    lo_, hi_ = boot(all_m)
    print("\nPOINT ESTIMATE AND 95%% INTERVAL (month-block bootstrap) at 2.0x: pi_upper %.2f [%.2f, %.2f]" % (pi_from_weights(np.ones(M))[0], lo_, hi_))
    print("\nBY ERA at 2.0x (known-information spike rate s is reweighted; pi_upper with a 95%% interval):")
    print("  %-10s %9s %8s %9s %9s | %s" % ("era", "p", "s (std)", "f_mid", "pi_upper", "95% interval"))
    for lab, lo, hi in ERAS:
        mids = np.array([m for m in all_m if lo <= TEST_START + m // 12 <= hi])
        w = np.zeros(M)
        w[mids] = 1.0
        pi_e, p_e, s_e, f_e = pi_from_weights(w)
        l2, h2 = boot(mids) if len(mids) > 12 else (float("nan"), float("nan"))
        print("  %-10s %9s %8s %9s %9.2f | [%.2f, %.2f]" % (lab, pct(p_e), pct(s_e), pct(f_e), pi_e, l2, h2))
    p, s, f_mid, f_ex = est[2.0]
    print("\nSENSITIVITY to f at 2.0x (p %s, s %s): pi for f = %s" % (pct(p), pct(s), ", ".join("%s -> %.2f" % (pct(f_mid + dlt).strip(), pi_of(p, s, f_mid + dlt)) for dlt in (0.0, 0.05, 0.10, 0.15, 0.20))))

    ps = est[2.0][0] / est[2.0][1]
    low = min(max(pi_of(*est[2.0][:2], est[2.0][3]), 0.0), 1.0)
    print("\nDEGENERACY CHECK (pre-set): p / s at 2.0x = %.2f (the estimate is informative only below 0.90)" % ps)
    print("CONSISTENCY CHECK (pre-set): pi_upper at 1.5x / 2.0x / 3.0x = %s; spread %.2f (allowed 0.10)" % (" / ".join("%.2f" % x for x in pis), spread))
    if ps >= 0.90:
        print("VERDICT: UNINFORMATIVE. Ordinary big misses spike about as often as known-information days (p / s = %.2f), so volume cannot separate information from the size of the move; pi is NOT quoted." % ps)
    elif spread <= 0.10:
        print("VERDICT: CONSISTENT and informative. At 2.0x the information share is at most %.2f (upper bound, mid-size noise rate) and about %.2f by the extrapolated noise rate (indicative only)." % (pis[1], low))
    else:
        print("VERDICT: NOT CONSISTENT. Information does not give a clean spike-or-no-spike signature here, so pi is NOT quoted as a share. Range at 2.0x: [%.2f (extrapolated noise rate), %.2f (mid-size noise rate)]." % (low, pis[1]))
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
