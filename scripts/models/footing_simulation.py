#!/usr/bin/env python3
"""
footing_simulation.py -- READ-ONLY calibration check (written 2026-10-26; needs numpy). Draws random groups of events with NO tag signal (multinomial draws from the overall reaction mix) at the size of each tag and reports how often the OLD test (chi-square against an even 25/25/25/25 split, test_pattern_significance.py) and the NEW test (chi-square against the overall mix) call them significant, where the real tags sit among random groups of the same size, and the family-wise rates over 13 tags with and without a Holm adjustment. The overall counts and the 13 tag sizes below are those of 2026-10-26.
"""
import math, numpy as np
ALL = [6349, 3644, 3652, 2307]; N = float(sum(ALL)); P = [a / N for a in ALL]
SIZES = {"multi_stage_divestiture":88,"activist_investor_campaign":6,"same_industry_comparison":5,"confounded_earnings":14,"same_entity_sequence":394,"plausible_unconfirmed":26,"leadership_reversal":53,"cross_entity_ripple":47,"confounded_regulatory_action":38,"high_confidence_causal_link":414,"explicitly_not_attributed":8,"confounded_macro_conditions":72,"confounded_corporate_action":47}
OBS = {"same_entity_sequence":(172,93,76,53),"high_confidence_causal_link":(177,98,90,49),"multi_stage_divestiture":(40,26,16,6),"leadership_reversal":(18,20,10,5),"confounded_regulatory_action":(15,14,5,4),"confounded_corporate_action":(21,10,13,3)}
R = 20000; rng = np.random.default_rng(7)
sf3 = np.vectorize(lambda v: math.erfc(math.sqrt(max(v, 1e-12) / 2.0)) + math.sqrt(2.0 * max(v, 1e-12) / math.pi) * math.exp(-max(v, 1e-12) / 2.0))
sim = {}
print("random groups, share called significant at p < .05 (old test, new test):")
for tag, n in sorted(SIZES.items(), key=lambda kv: -kv[1]):
    d = rng.multinomial(n, P, size=R).astype(float)
    ce = ((d - n / 4.0) ** 2 / (n / 4.0)).sum(axis=1); cn = ((d - np.array(P) * n) ** 2 / (np.array(P) * n)).sum(axis=1)
    sim[tag] = (ce, cn)
    print("  n %4d  old %5.1f%%  new %5.1f%%" % (n, 100 * (sf3(ce) < .05).mean(), 100 * (sf3(cn) < .05).mean()))
for tag, obs in OBS.items():
    n = sum(obs); o = np.array(obs, float); old = (((o - n / 4.0) ** 2) / (n / 4.0)).sum()
    print("%-30s old chi2 %.1f: %.1f%% of random groups of the same size are at least this far from even" % (tag, old, 100 * (sim[tag][0] >= old).mean()))
raw = np.stack([sf3(sim[t][1]) for t in SIZES], axis=1); oldp = np.stack([sf3(sim[t][0]) for t in SIZES], axis=1)
def holm_min(row):
    order = np.argsort(row); k = len(row); run = 0.0; best = 1.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (k - rank) * row[i])); best = min(best, run)
    return best
print("13 random tags: any raw p < .05 (new test) %.1f%% | after Holm %.1f%% | old test %.1f%%; old test, mean number 'significant' %.1f" % (100 * (raw.min(axis=1) < .05).mean(), 100 * (np.array([holm_min(r) for r in raw]) < .05).mean(), 100 * (oldp.min(axis=1) < .05).mean(), (oldp < .05).sum(axis=1).mean()))
