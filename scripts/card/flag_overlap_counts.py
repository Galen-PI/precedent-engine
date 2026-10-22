#!/usr/bin/env python3
"""
flag_overlap_counts.py -- READ-ONLY (local matrices; the database is read for securities.sector, 8-K filings, recorded events and the macro_long series DCOILWTICO, DGS10 and PAYEMS). Writes nothing. A COUNTING step, no outcome is looked at.
WHY. The 'storm' idea: on stock-days where several documented flags overlap, does the day behave differently from what each flag alone says? Rule agreed earlier: MEASURE overlaps, NEVER multiply flags. Overlaps may be too thin to test at all, so count first.
FLAGS (stock-day masks, valid band-unit days only): OIL_E = oil-shock day (|WTI change| >= 3%, both prices > 5) for Energy stocks; YLD_F / YLD_RE / YLD_H = 10-year-yield shock day (|DGS10 change| >= 0.10 points) for Financials / Real Estate / Health Care stocks; JOB = jobs-report day (PAYEMS first-release date, every stock);
EVT = a stock's own recorded event, days 0 and +1 (as loaded by event_width_test); ERN = earnings window (Item 2.02 filing day i and i+1); FD = Regulation FD window (Item 7.01 filing day i and i+1). Timing: OIL_E and YLD_* are SAME-DAY flags (an explanation of a past day, not usable in a forward range);
JOB is SCHEDULED (the date is known in advance); EVT, ERN and FD are FILING-DRIVEN (day +1 knowable, day 0 only after the filing). Eras 2004-2018 and 2019-2026.
READING GUIDE (written before the first real run). A pair is TESTABLE if it has at least 1,000 overlapping stock-days in EACH era (a coverage shortfall at 80% then has a standard error of about 1.3 points), MARGINAL if the smaller era has 300-999, THIN below 300. THIN pairs cannot be tested and are reported with the number.
PREDICTIONS (before the run): sector-specific pairs involving OIL_E are THIN (under 300 per era) except possibly with EVT; pairs of an all-stock flag with ERN or EVT (JOB x ERN, YLD_F x ERN, YLD_F x EVT) have 300-3,000 per era; at most 6 of the 28 pairs are TESTABLE in both eras; the single-flag volumes are EVT 35,000-45,000, ERN 75,000-90,000, FD 60,000-90,000, JOB 100,000-140,000 stock-days.
Usage:   python3 -u scripts/card/flag_overlap_counts.py      Needs data_cache/audit_matrices.npz.
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
ERAS = [("2004-2018", 2004, 2018), ("2019-2026", 2019, 2100)]
OIL_PCT, YLD_PTS, OIL_MIN_PRICE = 0.03, 0.10, 5.0
FLAGS = ["OIL_E", "YLD_F", "YLD_RE", "YLD_H", "JOB", "EVT", "ERN", "FD"]
TIMING = {"OIL_E": "same-day", "YLD_F": "same-day", "YLD_RE": "same-day", "YLD_H": "same-day", "JOB": "scheduled", "EVT": "filing-driven", "ERN": "filing-driven", "FD": "filing-driven"}
SECTOR = {"OIL_E": "Energy", "YLD_F": "Financials", "YLD_RE": "Real Estate", "YLD_H": "Health Care"}
TESTABLE, MARGINAL = 1000, 300


def macro_series(sb, sid, want_release=False):
    cols = "obs_date,value,known_on,known_on_basis" if want_release else "obs_date,value"
    return list(uc.paged(lambda: sb.table("macro_long").select(cols).eq("series_id", sid).order("obs_date")))


def day_flags(rows, kind, dl):
    """market-wide day masks (length n) from a daily series: kind 'oil' or 'yield'; a day is flagged when its change from the previous observation passes the line."""
    n = len(dl)
    out = np.zeros(n, dtype=bool)
    prev = None
    for r in rows:
        v = r.get("value")
        if v is None:
            continue
        v = float(v)
        if prev is not None:
            hit = (prev > OIL_MIN_PRICE and v > OIL_MIN_PRICE and abs(v / prev - 1.0) >= OIL_PCT) if kind == "oil" else (abs(v - prev) >= YLD_PTS - 1e-12)
            if hit:
                i = bisect.bisect_left(dl, str(r["obs_date"])[:10])
                if i < n and dl[i] == str(r["obs_date"])[:10]:
                    out[i] = True
        prev = v
    return out


def count_overlaps(F, valid, years):
    singles, pairs = {}, {}
    for lab, lo, hi in ERAS:
        em = valid & ((years >= lo) & (years <= hi))[None, :]
        for a in FLAGS:
            singles.setdefault(a, {})[lab] = int((F[a] & em).sum())
        for i, a in enumerate(FLAGS):
            for b in FLAGS[i + 1:]:
                pairs.setdefault((a, b), {})[lab] = int((F[a] & F[b] & em).sum())
    return singles, pairs


def main():
    t0 = time.time()
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E_, SD = d["dates"], d["ids"].tolist(), d["E"].astype(np.float64), d["SD"].astype(np.float64)
    N, n = E_.shape
    dl = [str(x) for x in dates]
    years = np.array([int(x[:4]) for x in dl])
    with np.errstate(invalid="ignore", divide="ignore"):
        Zsq = (E_ / SD) ** 2
    valid0 = np.isfinite(Zsq)
    S = np.where(valid0, Zsq, 0.0).sum(axis=0)
    cnt = valid0.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        bu = np.sqrt(Zsq / ((S[None, :] - np.where(valid0, Zsq, 0.0)) / (cnt[None, :] - 1)))
    valid = np.isfinite(bu) & (cnt[None, :] > 20)
    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids)}
    sector = {r["id"]: r.get("sector") for r in uc.paged(lambda: sb.table("securities").select("id,sector").order("id"))}
    secmask = {name: np.array([sector.get(sid) == name for sid in ids]) for name in set(SECTOR.values())}
    print("stocks %d | sectors: %s | valid stock-days %d | %.0fs" % (N, ", ".join("%s %d" % (k, v.sum()) for k, v in secmask.items()), valid.sum(), time.time() - t0), flush=True)

    oil = day_flags(macro_series(sb, "DCOILWTICO"), "oil", dl)
    yld = day_flags(macro_series(sb, "DGS10"), "yield", dl)
    job = np.zeros(n, dtype=bool)
    try:
        prow = macro_series(sb, "PAYEMS", want_release=True)
        basis = defaultdict(int)
        for r in prow:
            basis[r.get("known_on_basis")] += 1
            if r.get("known_on_basis") == "first_release" and r.get("known_on"):
                i = bisect.bisect_left(dl, str(r["known_on"])[:10])
                if i < n:
                    job[i] = True
        print("PAYEMS rows by known_on_basis: %s -> %d jobs-report days in the calendar" % (dict(basis), job.sum()), flush=True)
    except Exception as e:
        print("WARNING: PAYEMS release dates unavailable (%s: %s): the JOB flag is EMPTY; paste the columns of macro_long and I will fix the query" % (type(e).__name__, str(e)[:120]), flush=True)
    print("market-wide days: oil shocks %d, yield shocks %d, jobs-report days %d" % (oil.sum(), yld.sum(), job.sum()), flush=True)

    F = {}
    for nm in FLAGS:
        F[nm] = np.zeros((N, n), dtype=bool)
    F["OIL_E"] = oil[None, :] & secmask["Energy"][:, None]
    F["YLD_F"] = yld[None, :] & secmask["Financials"][:, None]
    F["YLD_RE"] = yld[None, :] & secmask["Real Estate"][:, None]
    F["YLD_H"] = yld[None, :] & secmask["Health Care"][:, None]
    F["JOB"] = np.broadcast_to(job[None, :], (N, n)).copy()
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids))
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                F["EVT"][k, t] = True
    for r in uc.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").order("id")):
        k = idx.get(r["security_id"])
        if k is None:
            continue
        its = set(dc.parse_items(r.get("item_codes")))
        i = bisect.bisect_left(dl, str(r["filing_date"])[:10])
        if i >= n:
            continue
        tgt = "ERN" if "2.02" in its else ("FD" if "7.01" in its else None)
        if tgt:
            F[tgt][k, i:min(i + 2, n)] = True
    singles, pairs = count_overlaps(F, valid, years)
    labs = [e[0] for e in ERAS]
    print("\nSINGLE FLAGS (valid stock-days)      " + "  ".join("%12s" % l for l in labs) + "   timing")
    for a in FLAGS:
        print("  %-8s %-28s" % (a, ("sector " + SECTOR[a]) if a in SECTOR else "all stocks") + "  ".join("%12d" % singles[a][l] for l in labs) + "   " + TIMING[a])
    print("\nPAIRS (overlapping valid stock-days), largest smaller-era count first")
    rows = sorted(pairs.items(), key=lambda kv: -min(kv[1].values()))
    for (a, b), c in rows:
        m = min(c.values())
        verdict = "TESTABLE" if m >= TESTABLE else ("MARGINAL" if m >= MARGINAL else "THIN")
        both_known = "known in advance" if (TIMING[a] != "same-day" and TIMING[b] != "same-day") else "includes a same-day flag"
        print("  %-7s x %-7s " % (a, b) + "  ".join("%12d" % c[l] for l in labs) + "   %-8s | %s" % (verdict, both_known))
    nt = sum(1 for _, c in rows if min(c.values()) >= TESTABLE)
    nm_ = sum(1 for _, c in rows if MARGINAL <= min(c.values()) < TESTABLE)
    print("\nSUMMARY: %d of %d pairs TESTABLE in both eras (>= %d), %d MARGINAL (%d-%d), %d THIN (< %d) | total %.0fs" % (nt, len(rows), TESTABLE, nm_, MARGINAL, TESTABLE - 1, len(rows) - nt - nm_, MARGINAL, time.time() - t0))
    return singles, pairs


if __name__ == "__main__":
    main()
