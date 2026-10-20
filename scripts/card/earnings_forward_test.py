#!/usr/bin/env python3
"""
earnings_forward_test.py -- THE FORWARD TEST, WRITTEN BEFORE ITS DATA EXIST. READ-ONLY (local matrices; the database is read for quarterly statements and 8-K item 2.02 filings).

WHY. On the historical data the operating-income surprise predicted the sign of the two-day earnings miss better than the revenue surprise the pre-set rule named (55.1% / 54.4% on
identical events, against 53.7% / 53.0%), but that was a post-hoc look at all three measures and both eras together. This tests it on earnings windows that did not exist when the
rule was written.

FROZEN 2026-10-20 (committed before any of the data): do not edit anything between here and the next paragraph after the season has started.
  WINDOWS: events whose 8-K item 2.02 filing is dated FORWARD_START to FORWARD_END (inclusive), with no recorded event on day 0 or +1, matched to a quarterly statement as in
           earnings_surprise_test.py (the first item 2.02 filing after the period end + 3 days and no later than 3 days after the statement's filed date).
  SURPRISE: operating income, defined exactly as in earnings_surprise_test.py (year-over-year change against the previous 8 quarters' changes, standardized; at least 6 needed).
  OUTCOME:  the sign of the two-day cumulative chapter-1 miss over day 0 and day +1.
  PASS:     >= 300 events, hit rate >= 54%, and a permutation p <= 0.05 (surprise signs shuffled within the calendar quarter, 2,000 shuffles, seed 20261020).
  VERDICTS: PASS; DOES NOT PASS (a conclusive negative) only if there are >= 500 events; otherwise INCONCLUSIVE (with 300-500 events the power is about 45-60% if the true hit rate
            is 54.5%, so a miss is not evidence of nothing); fewer than 300 events is TOO FEW.
  EVALUATE ONCE, after the season, without changing the definition. Revenue and net income are printed for shape only and carry no verdict.

USAGE.
  python3 -u scripts/card/earnings_forward_test.py               READINESS CHECK ONLY: counts and data coverage, no hit rate.
  python3 -u scripts/card/earnings_forward_test.py --evaluate    the verdict (run once, after the season).
BEFORE EVALUATING the price cache and the matrices must reach the windows: python3 -u scripts/card/build_return_cache.py (resume-safe), then
  python3 -u scripts/card/gap_audit.py --rebuild. The quarterly statements for the new quarter appear when the 10-Qs are filed (weeks after the releases), so the matched share
  rises over time; the readiness check shows it.
"""
import os, sys, math, time, bisect, warnings
from collections import defaultdict
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
import earnings_surprise_test as est

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE_FILE = os.path.join(ROOT, "data_cache", "audit_matrices.npz")
FORWARD_START = "2026-10-14"
FORWARD_END = "2026-12-31"
MEASURE = "operating_income"
HIT_BAR = 0.54
MIN_EVENTS_PASS = 300
MIN_EVENTS_CONCLUSIVE = 500
PERMS = 2000
SEED = 20261020


def main():
    evaluate = "--evaluate" in sys.argv
    t0 = time.time()
    if not os.path.exists(CACHE_FILE):
        sys.exit("Run gap_audit.py first: it builds %s." % CACHE_FILE)
    d = np.load(CACHE_FILE, allow_pickle=False)
    dates, ids, E, SD = d["dates"], d["ids"], d["E"], d["SD"]
    N, n = E.shape
    dl = [str(x) for x in dates]
    last_day = dl[-1]
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = E / SD
    valid = ~np.isnan(Z)

    sb = ew.get_sb()
    idx = {sid: k for k, sid in enumerate(ids.tolist())}
    f202 = defaultdict(set)
    n_window_filings = 0
    for r in est.paged(lambda: sb.table("sec_8k_filings").select("security_id,filing_date,item_codes").like("item_codes", "%2.02%").order("id")):
        f = str(r["filing_date"])[:10]
        f202[r["security_id"]].add(f)
        if FORWARD_START <= f <= FORWARD_END and r["security_id"] in idx:
            n_window_filings += 1
    stm = est.paged(lambda: sb.table("financial_statements").select("security_id,period_end,fiscal_year,fiscal_quarter,filed_date,revenue,operating_income,net_income")
                    .eq("period_type", "quarterly").order("id"))
    by_sec = defaultdict(list)
    for r in stm:
        if r.get("period_end") and r.get("filed_date"):
            by_sec[r["security_id"]].append(r)
    einfo, use_labels, nlab = ew.load_event_info(sb, dl, set(ids.tolist()))
    EV = np.zeros((N, n), dtype=bool)
    for sid, days in einfo.items():
        k = idx.get(sid)
        if k is not None:
            for t in days:
                EV[k, t] = True

    used, events = set(), []
    n_match = n_scored = 0
    for sid, rows in by_sec.items():
        k = idx.get(sid)
        if k is None:
            continue
        flist = sorted(f202.get(sid, []))
        for pe, fd, sues in est.surprises(rows):
            cand = [f for f in flist if est.add_days(pe, 3) < f <= est.add_days(fd, 3) and (sid, f) not in used]
            if not cand:
                continue
            f = cand[0]
            used.add((sid, f))
            if not (FORWARD_START <= f <= FORWARD_END):
                continue
            n_match += 1
            i = bisect.bisect_left(dl, f)
            if i + 1 >= n or not (valid[k, i] and valid[k, i + 1]) or EV[k, i] or EV[k, i + 1]:
                continue
            n_scored += 1
            events.append({"yq": (int(f[:4]), (int(f[5:7]) - 1) // 3 + 1), "sue": sues, "C": float(E[k, i]) + float(E[k, i + 1])})

    n_oi = sum(1 for e in events if e["sue"].get(MEASURE) not in (None, 0.0))
    print("FORWARD TEST, frozen 2026-10-20. Window: item 2.02 filings dated %s to %s | measure: %s | bar: hit rate >= %.0f%%, p <= 0.05, >= %d events" % (
        FORWARD_START, FORWARD_END, MEASURE, 100 * HIT_BAR, MIN_EVENTS_PASS))
    print("READINESS")
    print("  price cache / matrices end: %s%s" % (last_day, "" if last_day >= FORWARD_END else "  <- BEFORE the window ends: windows after this date cannot be scored yet"))
    print("  item 2.02 filings in the window (stocks in the matrices): %d" % n_window_filings)
    print("  matched to a quarterly statement: %d (%.0f%% of the filings; this rises as 10-Qs are filed)" % (n_match, 100.0 * n_match / max(n_window_filings, 1)))
    print("  with a usable two-day outcome and no recorded event: %d" % n_scored)
    print("  with an %s surprise (the events the test would use): %d" % (MEASURE, n_oi))
    if n_oi < MIN_EVENTS_PASS:
        print("  -> %d is below %d: too few to pass; wait for more statements and prices." % (n_oi, MIN_EVENTS_PASS))
    elif n_oi < MIN_EVENTS_CONCLUSIVE:
        print("  -> %d is enough to pass but, short of %d, a miss would be INCONCLUSIVE, not a negative." % (n_oi, MIN_EVENTS_CONCLUSIVE))
    else:
        print("  -> %d events: a miss would be a conclusive negative." % n_oi)
    if not evaluate:
        print("\nReadiness check only (no hit rate computed). Run with --evaluate ONCE, after the season, to get the verdict. Total %.0fs" % (time.time() - t0))
        return

    rng = np.random.RandomState(SEED)
    print("\nVERDICT RUN (the definition above, unchanged)")
    res = {}
    for m in (MEASURE, "revenue", "net_income"):
        sel = [e for e in events if e["sue"].get(m) not in (None, 0.0)]
        if len(sel) < 30:
            print("  %-18s %6d events (too few to score)" % (m, len(sel)))
            continue
        pred = np.array([1 if e["sue"][m] > 0 else -1 for e in sel])
        act = np.array([1 if e["C"] > 0 else -1 for e in sel])
        groups = defaultdict(list)
        for j, e in enumerate(sel):
            groups[e["yq"]].append(j)
        gl = [np.array(v) for v in groups.values()]
        hits = int((pred == act).sum())
        nperm = np.array([sum(int((rng.permutation(pred[g]) == act[g]).sum()) for g in gl) for _ in range(PERMS)])
        p = float(((nperm >= hits).sum() + 1) / (PERMS + 1))
        lo, hi = est.wilson(hits, len(sel))
        res[m] = (len(sel), hits / len(sel), lo, hi, p)
        print("  %-18s %6d events  hit rate %5.1f%%  (95%% interval %5.1f%% - %5.1f%%)  null mean %5.1f%%  permutation p = %.3f%s" % (
            m + (" *" if m == MEASURE else ""), len(sel), 100.0 * hits / len(sel), 100 * lo, 100 * hi, 100.0 * nperm.mean() / len(sel), p, "" if m == MEASURE else "   (shape only, no verdict)"))
    if MEASURE not in res:
        print("\nVERDICT: TOO FEW events to score.")
        return
    n_ev, hit, lo, hi, p = res[MEASURE]
    if n_ev < MIN_EVENTS_PASS:
        verdict = "TOO FEW (%d < %d events)" % (n_ev, MIN_EVENTS_PASS)
    elif hit >= HIT_BAR and p <= 0.05:
        verdict = "PASS"
    elif n_ev >= MIN_EVENTS_CONCLUSIVE:
        verdict = "DOES NOT PASS (conclusive: >= %d events)" % MIN_EVENTS_CONCLUSIVE
    else:
        verdict = "INCONCLUSIVE (%d events; under %d a miss is not evidence of nothing)" % (n_ev, MIN_EVENTS_CONCLUSIVE)
    print("\nVERDICT, forward test of the %s surprise sign: %s" % (MEASURE, verdict))
    print("Record it in the flag ledger row earnings_surprise_sign_operating_income_forward. Total %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
