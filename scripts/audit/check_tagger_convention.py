#!/usr/bin/env python3
"""
check_tagger_convention.py -- READ-ONLY live regression check (2026-10-26). After patch_tagger_baseline.py: does the tagger's labelling function (compute_abnormal_return, prior-close convention) agree with the saved abnormal_return_20d in event_market_reactions_corrected? It samples N random events (SEALED companies are excluded; the sample is seeded), recomputes each 20-day abnormal return from the stored prices with the tagger's own function, and compares value and label. It writes nothing; about 3 requests per event.
PRE-SET RULE (fixed before the first run): PASS if the labels agree for at least 95% of the events that could be computed AND the median absolute difference is below 0.001; anything else prints REVIEW. (Reason for 95%: the saved columns were computed at tagging time, so later price refreshes can move a few events across the +-3% line.)
Run from the repository root:   python3 scripts/audit/check_tagger_convention.py [--n 100] [--seed 1]
"""
import sys, argparse, random, statistics
sys.path.insert(0, "scripts/tagging")
import tag_reaction_character as T


def pages(sb, table, select, order):
    rows, off = [], 0
    while True:
        page = sb.table(table).select(select).order(order).range(off, off + 999).execute().data
        if not page:
            break
        rows += page
        if len(page) < 1000:
            break
        off += 1000
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=100); ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    sb = T.supabase
    sealed = {r["ticker"] for r in pages(sb, "explore_sealed_tickers", "ticker", "ticker")}
    if not sealed:
        raise SystemExit("explore_sealed_tickers is empty: refusing to run without the sealed set")
    rows = [r for r in pages(sb, "event_market_reactions_corrected", "event_id,ticker,event_date,abnormal_return_20d", "event_id") if r["ticker"] not in sealed and r.get("abnormal_return_20d") is not None]
    sample = random.Random(a.seed).sample(rows, min(a.n, len(rows)))
    done, nones, diffs, agree, worst = 0, 0, [], 0, []
    for r in sample:
        ar = T.compute_abnormal_return(r["ticker"], str(r["event_date"])[:10], 20)
        if ar is None:
            nones += 1; continue
        col = float(r["abnormal_return_20d"]); d = abs(ar - col); done += 1
        diffs.append(d); agree += T.classify(ar) == T.classify(col)
        worst.append((d, r["ticker"], str(r["event_date"])[:10], ar, col))
    print("explore-set events with a saved value: %d; sampled %d (seed %d); computed %d; function returned None for %d" % (len(rows), len(sample), a.seed, done, nones))
    if not done:
        raise SystemExit("nothing could be computed")
    srt = sorted(diffs)
    pct = 100.0 * agree / done; med = statistics.median(diffs)
    print("label agreement: %d of %d = %.1f%% | |difference| median %.6f, 90th percentile %.6f, max %.6f" % (agree, done, pct, med, srt[int(0.9 * (len(srt) - 1))], srt[-1]))
    print("largest differences (ticker, event date, recomputed, saved):")
    for d, t, dt, ar, col in sorted(worst, reverse=True)[:5]:
        print("   %-6s %s  %+.4f  %+.4f  (diff %.4f)" % (t, dt, ar, col, d))
    print("VERDICT: %s" % ("PASS" if pct >= 95.0 and med < 0.001 else "REVIEW (do not commit the patch until this is understood)"))


if __name__ == "__main__":
    main()
