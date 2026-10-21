#!/usr/bin/env python3
"""
verdict_vs_reaction.py -- READ-ONLY (results/guidance_variance_sample.csv; the database is read for the classifier's verdicts). In the content-blind sample of isolated 8.01/7.01 filings, does the classifier's real_event / noise label line up with how much the stock moved?
Per verdict: n, mean 2-day squared band unit and the multiplier against the quiet-day mean (argument, default 0.834 from the study run); AUC = the chance that a randomly chosen real_event filing had a larger 2-day move than a randomly chosen likely_noise filing (0.5 = no relationship), with a
filing-level bootstrap interval; and the TOP-DECILE CAPTURE: of the 10% of filings with the largest 2-day move, what share the classifier called real_event versus its share overall (lift).
PREDICTIONS (before the run): AUC 0.55-0.65 (a slight relationship); real_event multiplier about 1.5x vs likely_noise about 1.2x; top-decile real_event share about 1.2-1.8x its overall share. A big move can have another cause (market, competitor, a different filing), so this measures alignment, not the classifier's error rate.
Usage:   python3 -u scripts/card/verdict_vs_reaction.py [quiet_day_mean]
"""
import os, sys, csv
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_width_test as ew
RESULTS = os.path.join(os.path.abspath(os.path.join(HERE, "..", "..")), "results")


def auc(pos, neg):
    """Mann-Whitney AUC with average ranks for ties."""
    allv = np.concatenate([pos, neg])
    uniq, inv = np.unique(allv, return_inverse=True)
    order = np.argsort(allv, kind="mergesort")
    ranks = np.empty(len(allv))
    ranks[order] = np.arange(1, len(allv) + 1)
    sums = np.bincount(inv, weights=ranks)
    cnts = np.bincount(inv)
    r = (sums / cnts)[inv]
    return (r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2.0) / (len(pos) * len(neg))


def main():
    base = float(sys.argv[1]) if len(sys.argv) > 1 else 0.834
    rows = list(csv.DictReader(open(os.path.join(RESULTS, "guidance_variance_sample.csv"))))
    sb = ew.get_sb()
    accs = sorted({r["accession_number"] for r in rows if r["accession_number"]})
    lab = {}
    for i in range(0, len(accs), 100):
        for q in sb.table("filing_ai_classifications").select("accession_number,ai_verdict").in_("accession_number", accs[i:i + 100]).execute().data:
            lab[q["accession_number"]] = q["ai_verdict"]
    v = np.array([lab.get(r["accession_number"], "(no label)") for r in rows])
    m = np.array([float(r["two_day_mean_bu2"]) for r in rows])
    print("filings %d | labelled %d | quiet-day mean squared band unit %.3f" % (len(rows), int((v != "(no label)").sum()), base))
    for k in ("real_event", "uncertain", "likely_noise", "(no label)"):
        s = v == k
        if s.sum():
            print("  %-13s n %4d (%4.1f%%) | mean 2-day %.2f | multiplier %.2fx | median-based %.2fx" % (k, s.sum(), 100.0 * s.mean(), m[s].mean(), np.sqrt(m[s].mean() / base), np.sqrt(np.median(m[s]) / np.median(m))))
    pos, neg = m[v == "real_event"], m[v == "likely_noise"]
    a = auc(pos, neg)
    rng = np.random.RandomState(7)
    bs = [auc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(300)]
    print("\nAUC (real_event vs likely_noise, larger move = positive) = %.3f [%.3f, %.3f]   (0.5 = no relationship; n %d vs %d)" % (a, np.percentile(bs, 2.5), np.percentile(bs, 97.5), len(pos), len(neg)))
    thr = np.percentile(m, 90)
    top = m >= thr
    share_all, share_top = float((v == "real_event").mean()), float((v[top] == "real_event").mean())
    print("TOP DECILE of 2-day moves (>= %.1f): %d filings, %.0f%% called real_event vs %.0f%% overall (lift %.2fx); %.0f%% of them were called likely_noise" % (thr, top.sum(), 100 * share_top, 100 * share_all, share_top / max(share_all, 1e-9), 100 * float((v[top] == "likely_noise").mean())))


if __name__ == "__main__":
    main()
