"""
magnitude_vol_baseline.py

Re-scores the validated magnitude model (multi_feature_model_magnitude.py,
+9.2 to +13.4pp vs a 50/50 majority baseline) against a REALIZED-VOLATILITY-ONLY
baseline. Needs the event_realized_vol table (prior-90d daily-return stddev).
Models, all on the SAME rows (those with a realized-vol value):
  M0 majority class | M1 volatility only | M2 original 5 features
  M3 original 5 + volatility | M4 four non-storm features + volatility
(M4 has no future-looking storm_tier, which uses +-40-day neighbors.)
Volatility is binned into deciles using TRAIN-period quantiles only.
Usage: python magnitude_vol_baseline.py
"""
import sys
sys.path.insert(0, "scripts/models")
import numpy as np
from multi_feature_model_magnitude import build_dataset, paginated
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder

CUTOFFS = ["2018-01-01", "2020-01-01", "2022-01-01", "2023-01-01", "2024-01-01"]
FIVE = ["event_type", "firm_state", "regime", "storm_tier", "confidence_trend"]
FOUR = ["event_type", "firm_state", "regime", "confidence_trend"]


def correct(train, test, cols):
    enc = OneHotEncoder(handle_unknown="ignore")
    Xtr = enc.fit_transform([[r[c] for c in cols] for r in train])
    Xte = enc.transform([[r[c] for c in cols] for r in test])
    ytr = [r["reaction"] for r in train]
    yte = np.array([r["reaction"] for r in test])
    m = LogisticRegression(max_iter=1000, C=0.5).fit(Xtr, ytr)
    return (m.predict(Xte) == yte).astype(float)


def diff(a, b):
    d = a - b
    return 100 * d.mean(), 100 * d.std(ddof=1) / np.sqrt(len(d))


def main():
    print("Building dataset...")
    rows = build_dataset()
    vol = {(r["event_id"], r["entity_id"]): r["rv90"]
           for r in paginated("event_realized_vol", "id,event_id,entity_id,rv90", "id")}
    rows = [dict(r, rv=vol[(r["event_id"], r["entity_id"])]) for r in rows
            if (r["event_id"], r["entity_id"]) in vol]
    print(f"Rows with realized vol: {len(rows)}\n")
    for cutoff in CUTOFFS:
        train = [r for r in rows if r["event_date"] < cutoff]
        test = [r for r in rows if r["event_date"] >= cutoff]
        if len(train) < 200 or len(test) < 100:
            print(f"cutoff {cutoff}: skipped (train {len(train)}, test {len(test)})\n")
            continue
        edges = np.quantile([r["rv"] for r in train], np.linspace(0, 1, 11)[1:-1])
        for r in train + test:
            r["vol_bin"] = str(int(np.searchsorted(edges, r["rv"])))
        ytr = [r["reaction"] for r in train]
        maj = max(set(ytr), key=ytr.count)
        yte = np.array([r["reaction"] for r in test])
        c0 = (yte == maj).astype(float)
        c1 = correct(train, test, ["vol_bin"])
        c2 = correct(train, test, FIVE)
        c3 = correct(train, test, FIVE + ["vol_bin"])
        c4 = correct(train, test, FOUR + ["vol_bin"])
        print(f"cutoff {cutoff}: train {len(train)}, test {len(test)}")
        print(f"  M0 majority {100*c0.mean():.1f}% | M1 vol-only {100*c1.mean():.1f}% | "
              f"M2 five-features {100*c2.mean():.1f}% | M3 five+vol {100*c3.mean():.1f}% | "
              f"M4 four+vol (no storm) {100*c4.mean():.1f}%")
        for label, a, b in [("M1-M0", c1, c0), ("M2-M1", c2, c1), ("M4-M1", c4, c1), ("M3-M2", c3, c2)]:
            m, se = diff(a, b)
            print(f"  {label}: {m:+.1f} pts (SE {se:.1f})")
        print()


if __name__ == "__main__":
    main()
