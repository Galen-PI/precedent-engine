# Theory & Findings Log

Consolidated record of what's been tested against this database and what came of it —
validated findings, honest null results, and promising-but-unconfirmed leads. Kept
separate from `PROJECT_PLAN.md` (which tracks build/phase status) and `SCRIPTS.md` (which
tracks script interfaces) — this file tracks what the data has actually said so far.

A null result is recorded with the same weight as a positive one. Finding out a feature
doesn't predict `reaction_character` is real, useful information — it tells future work
where not to spend more time, and prevents re-discovering the same null a second time.

---

## Validated Findings

### Storm / compounding effect — event magnitude, not direction
**Status: validated, standing.** When a company has other large events happening nearby
in time (within ±40 days, excluding bundled/summary events on both sides), its reaction
to *this* event tends to be larger in magnitude — a higher `|abnormal_return|`. Cleared
six independent tests: a flat monotonic climb, held within event type (ruling out
crisis-severity confounding), a magnitude-weighted threshold pattern, a same-vs-opposite-
direction check (using each event's real biggest neighbor), an independent replication in
the separate `financial_market_reactions` table (not just `event_ripple_timeline`), and
held-out validation on 2+ years of genuinely unseen data (2022-01-01 cutoff). Also tested
directly against the volatility-confound alternative explanation (large neighbors still
produce an elevation above each company's OWN baseline, not just the global average).

**Important distinction, clarified 2026-09-29**: this is a claim about MAGNITUDE
(bigger reaction), not DIRECTION (which of rewarded/punished/muted). See the null result
below — a storm elevating reaction size doesn't automatically make direction predictable,
and testing the two together produced a null. The magnitude finding itself was not
re-tested or challenged by that null result; they're different claims.

Implemented as `storm_tier` in `multi_feature_model.py` (`get_storm_lookup()`).

### Sector-peer ripple effect
**Status: validated, scoped build not yet started.** Companies in the same sector as a
company experiencing a large-reaction event show elevated `|abnormal_return|` themselves,
even without their own direct event. z=17.49 at the largest tested sample (n=1,215 peers).
Real, robust effect — recommended for a scoped build (large-reaction events only), not a
full unscoped rebuild across the whole ripple timeline. See GitHub issue #21.

### COVID-era factor attribution — first step
**Status: modest positive signal, first step only, not fully built.** Event magnitude,
company size, and sentiment jointly explain 13.8% of abnormal-return variance
(R²=0.138) across the 8 confirmed COVID-era global events × 15 companies (n=120, 100%
complete). Magnitude coefficient -0.615 (bigger events = worse returns, as expected),
sentiment +0.013 (better sentiment = better returns, as expected), size ≈0 (limited
variation in this large-cap sample). Real signal, worth building factors 4/5
(proximity/connections, public response) — see GitHub issue #22.

---

## Null Results

Recorded with the same rigor as positive findings — these are real answers, not failures.

### Flat sentiment level predicting `reaction_character`
**Status: null, tested at scale.** GDELT `avg_tone`, bucketed negative/neutral/positive
over the 7 days before an event, does not predict rewarded/punished/muted above a dumb
baseline. Tested at n=4,386 (445 companies), cutoff 2024-01-01. Negative and positive
buckets both performed WORSE than baseline; neutral was statistically indistinguishable
from it.

### Sentiment trend (worsening/flat/improving)
**Status: null.** Splitting the 7-day pre-event window into early/late halves and
measuring the trend direction, instead of a flat average, also failed to beat baseline —
all three buckets underperformed the dumb baseline.

### Storm × sentiment interaction, as a full-model feature
**Status: null when added to the full model, despite one suggestive standalone cell.**
A standalone walk-forward test isolating just this interaction found one promising cell —
storm-condition + neutral-sentiment (43.8-49.2% vs ~38% baseline depending on trend
sub-split, roughly n=61-80) — but this was one cell out of an 18-cell grid, at ~1.7
standard deviations, below the conventional 2-SD bar. Adding `storm_x_sentiment` as an
actual feature to `multi_feature_model.py` (alongside, not replacing, the separate
`sentiment` and `storm_tier` features) produced NO improvement: 34.2% test accuracy vs
34.4% baseline (cutoff 2022-01-01), essentially flat. The specific promising cell
(`storm_x_sentiment_storm_neutral`) did not appear in the model's top-10 coefficients for
any class. Read as: a narrow effect that may be real in isolation but gets swamped by
larger, blunter signals (`event_type_systemic_shock`, `regime_*`) once embedded in a
41-feature model under L2 regularization.

### Full multi-feature model (`event_type`, `firm_state`, `regime`, `sentiment`,
### `storm_tier`, `storm_x_sentiment`) predicting `reaction_character`
**Status: null, re-confirmed 2026-09-29 on a substantially larger and cleaner dataset.**
Cutoff 2022-01-01. Earlier run (before this session's stale-URL sweep, price refresh, and
~4,000 new promoted events): 4,043 labeled rows, 34.2-34.9% test accuracy vs ~34-35%
baseline. Re-run 2026-09-29 on the corrected dataset: **5,580 labeled rows (+38%), 35.3%
test accuracy vs 35.7% baseline** — still does not beat baseline. Sample health is good
(103 samples/feature, well above the 10-20 rule of thumb; train-test gap 8.0 points, not
alarming). This is a MORE credible null than the earlier run, not a weaker one — it closes
off the "maybe it's just dirty/insufficient data" explanation, since the same conclusion
held after materially more and better data. `storm_tier_large`'s coefficients (-0.202 for
muted, +0.118 for rewarded) are directionally consistent with the standing storm finding
(storms push away from muted) even though the overall model doesn't clear baseline.

---

## Null Results, continued

### Chain position (same_entity_sequence position/length) predicting reaction_character
**Status: null, but scoped narrower than it may sound -- read carefully before citing.**
Built a richer version of the existing chain_position_opening/middle/closing tags (chain
length bucketed short/medium/long crossed with position-as-fraction early/middle/late) and
tested it standalone. Real, honest scale problem found immediately: only 39 entities have
ANY same_entity_sequence chain (409 events total, 2.4% of the database), and of those,
97% fall into "long" chains (5+) -- there are effectively zero length-2/3/4 chains in this
data, so the length dimension couldn't really be tested. Only one bucket (long_late, the
closing/resolution phase of a long chain) cleared n=30 in the walk-forward test: predicted
punished at 45.1% training confidence, actual held-out hit rate 21.7% -- a real miss,
meaningfully worse than the 43.3% dumb baseline, not just a non-improvement.

**Important scope note (2026-09-29):** `same_entity_sequence`, despite its name, is NOT a
systematic same-company narrative link -- per `suggest_event_tags_batch.py`'s real prompt,
it's the AI judging ONE event's text in isolation for whether it explicitly self-references
a specific prior/later event (e.g. "following the prior merger," the same person returning
to a new role). It is same-COMPANY only, and requires a documented textual connection, not
inferred proximity. **This null result says nothing about the different, cross-entity
"Cascade Effect" hypothesis below** -- they share the word "chain" in this codebase's
naming (`compute_chain_position.py`) but are not the same idea. See Open Questions below
for the real, still-untested version.

---

## Open / Promising Leads (not yet conclusive)

- **The one storm+neutral-sentiment cell** (see null result above) — real enough to keep
  an eye on, not real enough to trust. Possible next step: test it in isolation as the
  ONLY non-baseline feature, rather than alongside 40 others, to see if it survives being
  fully isolated from competing signal.
- **`financial_market_reactions` as an alternative modeling target** — a complete,
  ~99%-populated dataset of abnormal returns for nearly every financial filing (35,826
  rows, 496/497 securities), independent of the `events`/`reaction_character` system.
  Confirmed 2026-09-29 to already be in active use (`test_financial_market_reactions.py`,
  and as an independent-replication check for the storm finding above) — but the actual
  RESULTS of `test_financial_market_reactions.py`'s own predictive test have not yet been
  re-read this session. Worth checking directly rather than assuming either a positive or
  null outcome.

---

## Open Questions (not yet started)

### The Cascade Effect -- multi-hop, cross-entity event propagation
**Status: genuinely new hypothesis, deliberately named distinctly from this codebase's
existing "chain" terminology to avoid the confusion above.** Raised 2026-09-29: does
Event 1 at Company A propagate to affect Company B (a sector peer or connected entity),
which then has its own Event 2, which propagates further to Company C -- a real,
directional, multi-hop cascade, not a single-company narrative link and not a same-window
magnitude correlation. This is a different, more ambitious claim than anything tested so
far in this project.

**How it differs from what's already validated:**
- The sector-peer ripple finding (see Validated Findings) shows peers react MORE STRONGLY
  in the SAME time window as a company's large event -- a correlation snapshot, not a
  directional hop-by-hop chain.
- The storm/compounding finding shows a company's OWN reaction is bigger when OTHER
  events (own-company or otherwise) cluster nearby -- magnitude, not propagation.
- Neither existing finding, nor the null same_entity_sequence result above, tests whether
  one event genuinely CAUSES a second event at a different company, which then causes a
  third.

**What would be needed to test this for real, not yet built:**
1. A real, defensible criterion for "Event 2 was plausibly caused by Event 1's ripple" --
   not just "a peer company had some event sometime after," since sector peers have
   unrelated events constantly and that alone would produce spurious chains.
2. A way to chain 3+ hops without the noise compounding at each step -- risk of finding
   apparent cascades that are really just sector-wide activity.
3. Combines pieces from three already-separate areas (storm/compounding, sector-peer
   ripple, some new real event-linking mechanism) rather than reusing any single existing
   tag or feature.

**Deliberately scoped as its own future session, not attempted tonight.**

---

## Methodology Standard

Every finding above followed the n=30-50 minimum sample threshold and, where claimed
"validated," genuine out-of-sample testing (train/test date split, no re-tuning on the
held-out window). See `PROJECT_PLAN.md` Section 6 for the full prediction-contract
discipline (universe, horizon, benchmark, base rate, similarity keys, magnitude/dispersion,
out-of-sample window) this project holds every claimed pattern to.
