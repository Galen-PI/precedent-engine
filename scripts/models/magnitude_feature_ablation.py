"""
magnitude_feature_ablation.py

Real feature ablation study for the validated magnitude-prediction finding
(multi_feature_model_magnitude.py, +9.2 to +13.4pp across 5 real cutoffs).
Fetches the real dataset ONCE (reusing build_dataset from the magnitude
model directly, same real data, no duplication), then runs two real,
disciplined comparisons at the already-validated 2022-01-01 cutoff:

1. SINGLE-FEATURE: each of the 5 real features alone -- which one carries
   the most real signal independently?
2. LEAVE-ONE-OUT: the full 5-feature set, minus one at a time -- which
   removal hurts accuracy the most (tells us what's NOT redundant)?

Same real LogisticRegression/OneHotEncoder setup as the validated model --
no new methodology invented, just varying which columns feed it.

Usage:
    python magnitude_feature_ablation.py
"""
import sys
sys.path.insert(0, "scripts/models")
from multi_feature_model_magnitude import build_dataset
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder

CUTOFF = "2022-01-01"
ALL_FEATURES = ["event_type", "firm_state", "regime", "storm_tier", "confidence_trend"]
ROBUSTNESS_CUTOFFS = ["2018-01-01", "2020-01-01", "2022-01-01", "2023-01-01", "2024-01-01"]


def score(rows, train_rows, test_rows, feature_cols):
    X_train_raw = [[r[c] for c in feature_cols] for r in train_rows]
    X_test_raw = [[r[c] for c in feature_cols] for r in test_rows]
    y_train = [r["reaction"] for r in train_rows]
    y_test = [r["reaction"] for r in test_rows]

    enc = OneHotEncoder(handle_unknown="ignore")
    X_train = enc.fit_transform(X_train_raw)
    X_test = enc.transform(X_test_raw)

    baseline = max(set(y_train), key=y_train.count)
    baseline_test_acc = 100 * y_test.count(baseline) / len(y_test)

    model = LogisticRegression(max_iter=1000, C=0.5)
    model.fit(X_train, y_train)
    test_acc = 100 * model.score(X_test, y_test)
    return test_acc, baseline_test_acc, X_train.shape[1]


def main():
    print("Building the real dataset once (same as the validated magnitude model)...")
    rows = build_dataset(exclude_bundled=False)
    train_rows = [r for r in rows if r["event_date"] < CUTOFF]
    test_rows = [r for r in rows if r["event_date"] >= CUTOFF]
    print(f"Train: {len(train_rows)}, Test: {len(test_rows)}\n")

    print("=" * 70)
    print("SINGLE-FEATURE: each feature alone")
    print("=" * 70)
    for feat in ALL_FEATURES:
        acc, baseline, n_feat = score(rows, train_rows, test_rows, [feat])
        beat = acc - baseline
        print(f"  {feat:20s} alone: {acc:5.1f}% vs {baseline:5.1f}% baseline "
              f"({beat:+5.1f}pp, {n_feat} real one-hot columns)")

    print()
    print("=" * 70)
    print("FULL SET (all 5 features) -- real baseline for comparison below")
    print("=" * 70)
    full_acc, full_baseline, full_n = score(rows, train_rows, test_rows, ALL_FEATURES)
    print(f"  ALL 5 features: {full_acc:5.1f}% vs {full_baseline:5.1f}% baseline "
          f"({full_acc - full_baseline:+5.1f}pp, {full_n} real one-hot columns)")

    print()
    print("=" * 70)
    print("LEAVE-ONE-OUT: full set minus one feature at a time")
    print("=" * 70)
    for feat in ALL_FEATURES:
        remaining = [f for f in ALL_FEATURES if f != feat]
        acc, baseline, n_feat = score(rows, train_rows, test_rows, remaining)
        drop = full_acc - acc
        print(f"  WITHOUT {feat:20s}: {acc:5.1f}% (vs full set {full_acc:5.1f}%, "
              f"{'HURT by removing -- real, non-redundant signal' if drop > 0.5 else 'barely changed -- may be redundant'} "
              f"{drop:+5.1f}pp change)")


def regime_robustness():
    print("Building the real dataset once...")
    rows = build_dataset(exclude_bundled=False)
    print()
    print("=" * 70)
    print("REGIME ALONE: robustness across 5 real cutoffs")
    print("=" * 70)
    for cutoff in ROBUSTNESS_CUTOFFS:
        train_rows = [r for r in rows if r["event_date"] < cutoff]
        test_rows = [r for r in rows if r["event_date"] >= cutoff]
        acc, baseline, n_feat = score(rows, train_rows, test_rows, ["regime"])
        print(f"  {cutoff}: {acc:5.1f}% vs {baseline:5.1f}% baseline ({acc - baseline:+5.1f}pp)  "
              f"[train={len(train_rows)}, test={len(test_rows)}]")


def storm_within_regime():
    """REAL test to resolve the storm_tier/regime confound found above:
    does storm_tier still predict magnitude WITHIN a single, fixed regime
    (same macro era for every row), or does its apparent power collapse
    once regime can't vary underneath it?"""
    print("Building the real dataset once...")
    rows = build_dataset(exclude_bundled=False)
    print()
    print("=" * 70)
    print("STORM_TIER WITHIN A SINGLE REGIME (real test of the confound)")
    print("=" * 70)

    from collections import Counter
    regime_counts = Counter(r["regime"] for r in rows)
    print(f"Real regime counts in full dataset: {dict(regime_counts)}")
    print()

    # Test within the two largest non-crisis regimes separately -- real,
    # large enough samples, and genuinely NOT crisis periods, so if storm
    # still predicts magnitude here, that's real evidence it's not just
    # riding on regime.
    test_feature = sys.argv[sys.argv.index("--storm-within-regime") + 1] if \
        len(sys.argv) > sys.argv.index("--storm-within-regime") + 1 and \
        not sys.argv[sys.argv.index("--storm-within-regime") + 1].startswith("--") else "storm_tier"

    for target_regime in ["post_crisis_recovery_2009_2015", "rate_normalization_2016_2019",
                           "covid_recovery_stimulus_2020_2021", "rate_hiking_cycle_2022_2023",
                           "ai_boom_2023_2026"]:
        subset = [r for r in rows if r["regime"] == target_regime]
        if len(subset) < 200:
            print(f"  {target_regime}: only {len(subset)} rows, too small, skipping")
            continue
        cutoff_idx = int(len(subset) * 0.7)
        subset_sorted = sorted(subset, key=lambda r: r["event_date"])
        train_sub = subset_sorted[:cutoff_idx]
        test_sub = subset_sorted[cutoff_idx:]
        acc, baseline, n_feat = score(rows, train_sub, test_sub, [test_feature])
        print(f"  WITHIN {target_regime} (n={len(subset)}, 70/30 chronological split): "
              f"{test_feature} alone = {acc:.1f}% vs {baseline:.1f}% baseline ({acc - baseline:+.1f}pp)")


HIGH_MAGNITUDE_TYPES = {"financial_result", "strategic_partnership", "restructuring"}


def test_collapsed_event_type():
    """REAL test: is a simpler, demonstrated-behavior collapse of event_type
    (high-magnitude types vs everything else) a better feature than the
    noisy, full 12+ category one-hot version? Real finding that motivated
    this: the two LARGEST categories (acquisition n=4667, leadership_change
    n=4535 -- over half the dataset) sit almost exactly at the 50% baseline,
    diluting real signal from smaller, more informative categories like
    financial_result (+10.5pp from baseline) in the aggregate test."""
    print("Building the real dataset once...")
    rows = build_dataset(exclude_bundled=False)
    train_rows = [r for r in rows if r["event_date"] < CUTOFF]
    test_rows = [r for r in rows if r["event_date"] >= CUTOFF]

    for r in rows:
        r["event_type_collapsed"] = "high_magnitude" if r["event_type"] in HIGH_MAGNITUDE_TYPES else "other"

    print(f"Train: {len(train_rows)}, Test: {len(test_rows)}\n")
    print("=" * 70)
    print("RAW event_type (12+ noisy categories) vs COLLAPSED (2 real buckets)")
    print("=" * 70)
    acc_raw, baseline, n_raw = score(rows, train_rows, test_rows, ["event_type"])
    acc_collapsed, _, n_collapsed = score(rows, train_rows, test_rows, ["event_type_collapsed"])
    print(f"  RAW event_type:       {acc_raw:5.1f}% vs {baseline:5.1f}% baseline "
          f"({acc_raw - baseline:+5.1f}pp, {n_raw} real columns)")
    print(f"  COLLAPSED (2 buckets): {acc_collapsed:5.1f}% vs {baseline:5.1f}% baseline "
          f"({acc_collapsed - baseline:+5.1f}pp, {n_collapsed} real columns)")


def find_confidence_partner():
    """REAL test: confidence_trend is 0.0pp alone but hurts (-0.6pp) when
    removed from the full model -- a real interaction effect. Find WHICH
    feature it's genuinely paired with by testing confidence_trend + each
    other feature individually at the validated 2022-01-01 cutoff."""
    print("Building the real dataset once...")
    rows = build_dataset(exclude_bundled=False)
    train_rows = [r for r in rows if r["event_date"] < CUTOFF]
    test_rows = [r for r in rows if r["event_date"] >= CUTOFF]
    print(f"Train: {len(train_rows)}, Test: {len(test_rows)}\n")

    print("=" * 70)
    print("FINDING confidence_trend's real partner (cutoff 2022-01-01)")
    print("=" * 70)
    others = ["event_type", "firm_state", "regime", "storm_tier"]
    for other in others:
        acc_other, baseline, _ = score(rows, train_rows, test_rows, [other])
        acc_pair, _, _ = score(rows, train_rows, test_rows, [other, "confidence_trend"])
        gain = acc_pair - acc_other
        print(f"  {other:15s} alone: {acc_other:5.1f}%  |  + confidence_trend: {acc_pair:5.1f}%  "
              f"({gain:+5.1f}pp real gain from adding confidence_trend)")


if __name__ == "__main__":
    if "--regime-robustness" in sys.argv:
        regime_robustness()
    elif "--storm-within-regime" in sys.argv:
        storm_within_regime()
    elif "--find-confidence-partner" in sys.argv:
        find_confidence_partner()
    elif "--collapsed-event-type" in sys.argv:
        test_collapsed_event_type()
    else:
        main()
