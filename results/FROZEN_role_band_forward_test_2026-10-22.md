# FROZEN RULE: role-band forward test
Written 2026-10-22, BEFORE any price after 2026-10-13 and any 8-K filing after 2026-09-18 is loaded. The commit of this file is the freeze.

QUESTION. Do the earnings bands as deployed on the card (role bands for a clear habit, pooled bands otherwise) beat the pooled day-0 / day+1 earnings bands on earnings releases the models never saw?

WINDOW. 8-K item 2.02 filings dated 2026-10-14 through 2026-12-31 (the matrices and the role model end 2026-10-13). Day i = the first trading day on or after the filing date. Evaluation needs prices through the first trading day after the last release (about 2027-01-05). Before that, only READINESS COUNTS may be printed.

POPULATION (as in earnings_role_band_test.py). Isolated releases: no own recorded event and no item 7.01 filing on day i or i+1; finite band units on both days; a FORWARD HABIT from at least 4 earlier classifiable quarters (the card's rule, earnings_roles.py). A 2-2 tie is a TIE: the card uses the pooled band for it. DOCUMENTED LIMIT: the recorded-events table ends 2026-09-11, so the no-own-event filter is VACUOUS in the window; days with an unrecorded company event stay in the sample for every model alike (expect slightly lower coverage than in the walk-forward).

MODELS, FIXED AT THE FREEZE (no refit before the verdict; hashes below).
- POOLED: day i and day i+1 half-widths = the pooled earnings edge x multiplier (earnings_band_model.json, band_calibration.json).
- CARD (ROLES): clear habit -> role half-widths from earnings_role_band_model.json (reaction day q90 5.322, other day q90 1.904, ordinary band units, fitted without 2-2 ties); tie -> pooled.
- PLACEBO: CARD with the habits shuffled across clear-habit events (200 shuffles, seed 20261022); the MEAN ratio is used.

MEASURES (ordinary band units). Interval score IS = 2h + 20 x max(|band unit| - h, 0), averaged over all observations (two per event). RATIO = mean IS(CARD) / mean IS(POOLED); paired bootstrap over events (2,000 resamples, seed 20261022) for its 95% interval. Coverage of CARD on habit-assigned reaction days and on other days, clear-habit events only.

VERDICT. TOO FEW: fewer than 250 evaluated clear-habit events: no verdict (counts and intervals only). Otherwise:
- PASS: (a) RATIO <= 0.98 AND the bootstrap upper bound < 1.00; (b) CARD coverage within 86-94% on reaction days AND on other days; (c) mean PLACEBO ratio >= 0.99.
- PARTIAL: (a) and (c) hold, (b) fails. NOT SHOWN: (a) fails with n >= 250. VOID: (c) fails (the gain would be an artifact).
- The coverage window is wider than the walk-forward's 88-92% on purpose: one season has about 300-400 events (SE about 1.6 points per day type), so 88-92% would fail a correctly calibrated model about a third of the time. The walk-forward verdict (PASSED, ratio 0.868 overall) is not changed by this.

NOT ALLOWED before the verdict: editing the models, earnings_roles.py, earnings_role_band_test.py, day_card.py or the forward script (scripts/card/earnings_role_forward_test.py, to be written and committed BEFORE any refresh); printing any ratio or coverage (the readiness mode prints counts only).

PREDICTIONS (before any outcome; point and range): isolated releases with a forward habit 380 (290-460); clear-habit events 350 (270-430); RATIO 0.90 (0.83-0.96); CARD coverage on reaction days 89% (85-93) and other days 92% (88-96) (the other-day multiplier has drifted down by era, 1.52 -> 1.43 -> 1.31, so over-coverage is the likelier error); mean PLACEBO ratio 1.004 (0.998-1.012); probability of PASS 65% (n >= 250 about 90%, ratio about 93%, coverage window about 88%, placebo about 95%, shaded down for my measured optimism about new things working).

## Frozen files (git HEAD 291c7911b0e45578c2bdfc700c3e11bed4d79167 at the time of writing)
```
7f9c9ab11a52e1977d788a71e65fdb039f9ff878f9f990f25757fe5ed88c99a5  models/earnings_band_model.json
e1722576ac1e4eb9c4451d16e10c80d8ed363a59ea79e9a36c55376f9299929b  models/earnings_role_band_model.json
0924d1ea034fc57cc97c1ad9f2995b5933dd2a6423198ccb936469d635060272  models/band_calibration.json
fccdfd1b3618538a83ad4a62c888e822e9daa46584b6ca547783b2239bcfab26  scripts/card/earnings_roles.py
954f88e5d80433e79b89f49e2b82f0b7e789ab374ce76981ea86692215f65aeb  scripts/card/earnings_role_band_test.py
1b07641fd34e7ae3e1329b2b82928e4204f6a8a4360e63dd5d73be5786cdf116  scripts/card/day_card.py
```
