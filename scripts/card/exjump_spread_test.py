#!/usr/bin/env python3
"""
exjump_spread_test.py -- READ-ONLY (two local matrix files; the database is read for 8-K filings and recorded event days). Writes nothing.
THE QUESTION. Does a spread estimated WITHOUT each stock's own earnings, recorded-event and Regulation FD days (data_cache/audit_matrices_exjump.npz, built by build_matrices_exjump.py) describe
ORDINARY days better than today's spread (data_cache/audit_matrices.npz), which includes those days in its 250-day window and is inflated by them? (My arithmetic from the group sizes says
the variance is inflated by about 14%. The earlier "0.84" mean squared band unit is not clean evidence of it: that unit is scaled by the day's cross-section, which flagged stocks inflate too.)

Usage:   python3 -u scripts/card/exjump_spread_test.py

PRE-SET RULE (written before the first run). On ORDINARY stock-days (no own recorded event, no earnings window, no Regulation FD filing, on day 0 or +1) that both matrices score, from 2006:
  Gaussian log score of the day's return under each model = -ln(SD) - 0.5 (E/SD)^2 (the return's own density; E, SD from that model). GAIN = score(ex-jump) - score(today), per stock-day.
  The ex-jump spread EARNS ITS PLACE if the gain is >= +0.005 nats per stock-day in EACH of 2006-2012, 2013-2019, 2020-2026 AND positive in >= 70% of the test years (years with >= 10,000 ordinary
  stock-days). (My arithmetic: with variance inflated by v = 1.14 the Gaussian gain is about 0.5(v - 1 - ln v) = 0.0046; with v = 1.19 about 0.008. So the expected gain sits AT the bar, which was
  inherited from the earlier tests: a real but small improvement can miss it, and the printout will show the size either way.)

The test judges ORDINARY days only. Flagged days are scored here for information (their bands rely on the group multipliers, which would be re-measured under any new baseline), with NO verdict.
PREDICTIONS (before the run): the median SD ratio (ex-jump / today) on ordinary days is 0.93-0.97; the log-score gain is +0.003 to +0.008 in every era, so the chance that it clears +0.005 in all
three eras AND 70% of years is about 45%; the UNSCALED mean squared miss on ordinary days (z^2, not rescaled by the day's cross-section) moves from about 0.85-0.90 to about 1.00; the stress-scaled
band unit and the approximate group multipliers barely move (within about 5%: they are relative to the cross-section, so a uniform spread change cancels); flagged stocks hold a share of each day's
total squared miss several times their share of stocks (about 5-6x for earnings windows, consistent with the 6x enrichment measured earlier); the per-stock spread change is larger for stocks with
many flagged days (95th percentile of the per-stock median ratio below 0.92); on FLAGGED days the gain is negative (their spread got smaller).
"""
import os, sys, time, bisect, math, warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import day_card as dc

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OLD = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
NEW = os.path.join(ROOT, "data_cache", "audit_matrices_exjump.npz")
TEST_START = 2006
GAIN_BAR = 0.005
YEAR_SHARE = 0.70
MIN_YEAR_CELLS = 10000
ERAS = [("2006-2012", 2006, 2012), ("2013-2019", 2013, 2019), ("2020-2026", 2020, 2100)]


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


def b2_matrix(E, S):
    """Squared standardized miss scaled by the day's stress as the card does: z^2 / q_others, q_others = mean z^2 of all OTHER stocks that day."""
    with np.errstate(invalid="ignore", divide="ignore"):
        z2 = (E / S) ** 2
    valid = np.isfinite(z2)
    tot = np.where(valid, z2, 0.0).sum(axis=0)
    cnt = valid.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qo = (tot[None, :] - np.where(valid, z2, 0.0)) / (cnt[None, :] - 1)
        return z2 / qo, z2


def main():
    t0 = time.time()
    for f in (OLD, NEW):
        if not os.path.exists(f):
            sys.exit("Missing %s (build_matrices_exjump.py builds the second one; gap_audit.py the first)." % f)
    a, b = np.load(OLD, allow_pickle=False), np.load(NEW, allow_pickle=False)
    if a["E"].shape != b["E"].shape or not (a["ids"] == b["ids"]).all() or not (a["dates"] == b["dates"]).all():
        sys.exit("The two matrix files do not describe the same stocks and dates.")
    dates, ids = a["dates"], a["ids"]
    E0, S0 = a["E"].astype(np.float64), a["SD"].astype(np.float64)
    E1, S1 = b["E"].astype(np.float64), b["SD"].astype(np.float64)
    N, n = E0.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids.tolist())}
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids.tolist()))
    EV = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                EV[k, t] = True
    EA0 = np.zeros((N, n), dtype=bool)
    EA1 = np.zeros((N, n), dtype=bool)
    F701 = np.zeros((N, n), dtype=bool)
    for r in paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
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
    EA = EA0 | EA1
    only701 = F701 & ~EA & ~EV
    ordinary_flag = ~EV & ~EA & ~only701

    both = (np.isfinite(E0) & np.isfinite(S0) & (S0 > 0) & np.isfinite(E1) & np.isfinite(S1) & (S1 > 0) & (years >= TEST_START)[None, :])
    ordc = both & ordinary_flag
    print("matrices: %d stocks x %d days | stock-days scored by both: %d | ordinary: %d | %.0fs" % (N, n, int(both.sum()), int(ordc.sum()), time.time() - t0), flush=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        LS0 = -np.log(S0) - 0.5 * (E0 / S0) ** 2
        LS1 = -np.log(S1) - 0.5 * (E1 / S1) ** 2
    gain = LS1 - LS0

    print("\nLOG-SCORE GAIN OF THE EX-JUMP SPREAD OVER TODAY'S, ordinary stock-days (nats per stock-day; the bar is +%.3f in each era and positive in >= %.0f%% of years)" % (GAIN_BAR, 100 * YEAR_SHARE))
    per_year = {}
    for Y in sorted(set(years.tolist())):
        if Y < TEST_START:
            continue
        m = ordc & (years == Y)[None, :]
        c = int(m.sum())
        if c >= MIN_YEAR_CELLS:
            per_year[Y] = (float(gain[m].mean()), c)
    era_gain = {}
    for lab, lo, hi in ERAS:
        m = ordc & ((years >= lo) & (years <= hi))[None, :]
        era_gain[lab] = (float(gain[m].mean()), int(m.sum())) if m.any() else (float("nan"), 0)
        print("  %-10s gain %+.4f over %9d stock-days %s" % (lab, era_gain[lab][0], era_gain[lab][1], "(clears the bar)" if era_gain[lab][0] >= GAIN_BAR else "(BELOW the bar)"))
    pos = sum(1 for v in per_year.values() if v[0] > 0)
    print("  years positive: %d of %d (%.0f%%)  | by year: %s" % (pos, len(per_year), 100.0 * pos / max(len(per_year), 1), " ".join("%d:%+.3f" % (y, v[0]) for y, v in sorted(per_year.items()))))
    ok_eras = all(v[0] >= GAIN_BAR for v in era_gain.values())
    ok_years = len(per_year) > 0 and pos >= YEAR_SHARE * len(per_year)

    b20, z20 = b2_matrix(np.where(both, E0, np.nan), np.where(both, S0, np.nan))
    b21, z21 = b2_matrix(np.where(both, E1, np.nan), np.where(both, S1, np.nan))
    print("\nDESCRIPTIVE (no verdict)")
    print("  ordinary days, mean squared band unit (z^2 / q_others; 1.0 = the spread is right): today %.3f | ex-jump %.3f" % (float(np.nanmean(b20[ordc])), float(np.nanmean(b21[ordc]))))
    print("  ordinary days, mean z^2 NOT rescaled by the day's cross-section (1.0 = the spread is exactly right; this is the direct measure of spread inflation): today %.3f | ex-jump %.3f" % (
        float(np.nanmean(z20[ordc])), float(np.nanmean(z21[ordc]))))
    for lab_, zz in (("today", z20), ("ex-jump", z21)):
        flagged_cells = both & ~ordinary_flag
        sh_cells = float(flagged_cells.sum()) / float(both.sum())
        sh_sq = float(np.nansum(np.where(flagged_cells, zz, 0.0))) / float(np.nansum(np.where(both, zz, 0.0)))
        print("  flagged stocks (event, earnings, Regulation FD windows), %s matrices: %.1f%% of stock-days hold %.1f%% of the total squared miss (%.1fx)" % (lab_, 100 * sh_cells, 100 * sh_sq, sh_sq / sh_cells))
    ratio = S1 / S0
    print("  spread ratio ex-jump / today on ordinary stock-days: median %.4f | 5th %.4f | 95th %.4f" % (float(np.median(ratio[ordc])), float(np.quantile(ratio[ordc], 0.05)), float(np.quantile(ratio[ordc], 0.95))))
    per_stock = []
    for k in range(N):
        mk = ordc[k]
        if mk.sum() >= 250:
            per_stock.append(float(np.median(ratio[k][mk])))
    if per_stock:
        q = np.quantile(per_stock, [0.05, 0.25, 0.5, 0.75, 0.95])
        print("  per-stock median ratio (%d stocks): 5th %.3f | 25th %.3f | median %.3f | 75th %.3f | 95th %.3f  (the lower end = stocks whose spread was most inflated by their own jump days)" % ((len(per_stock),) + tuple(q)))
    groups = [("earnings day 0 (no event)", both & EA0 & ~EV), ("earnings day +1 (no event)", both & EA1 & ~EV), ("recorded event, no earnings", both & EV & ~EA), ("Regulation FD (7.01) only", both & only701)]
    print("  approximate group multipliers, sqrt(mean band unit^2 of the group / of ordinary days) (a rough replication of the card's measured 2.72 / 2.47 / event model / 1.36, not identical to them):")
    print("    %-30s %9s %9s %8s" % ("group", "today", "ex-jump", "change"))
    for lab, m in groups:
        if int(m.sum()) < 1000:
            continue
        m0 = math.sqrt(float(np.nanmean(b20[m])) / float(np.nanmean(b20[ordc])))
        m1 = math.sqrt(float(np.nanmean(b21[m])) / float(np.nanmean(b21[ordc])))
        print("    %-30s %9.3f %9.3f %+7.1f%%" % (lab, m0, m1, 100 * (m1 / m0 - 1)))
    fl = both & ~ordinary_flag
    print("  FLAGGED stock-days (no verdict): log-score gain of the ex-jump spread %+.4f over %d stock-days (expected negative: their spread got smaller and their bands rely on multipliers)" % (float(gain[fl].mean()), int(fl.sum())))

    print()
    if ok_eras and ok_years:
        print("VERDICT under the pre-set rule: the ex-jump spread EARNS ITS PLACE on ordinary days.")
    else:
        why = []
        if not ok_eras:
            why.append("era gains below +%.3f: %s" % (GAIN_BAR, ", ".join("%s %+.4f" % (k, v[0]) for k, v in era_gain.items() if v[0] < GAIN_BAR)))
        if not ok_years:
            why.append("positive in %d of %d years (< %.0f%%)" % (pos, len(per_year), 100 * YEAR_SHARE))
        print("VERDICT under the pre-set rule: the ex-jump spread does NOT earn its place. " + "; ".join(why))
    print("total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
