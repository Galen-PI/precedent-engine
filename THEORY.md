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

### The Cascade Effect -- multi-hop, event-nature-based propagation
**Status: real design work started 2026-09-29, converged on a workable next step. Not yet
built or tested.** Raised 2026-09-29: does Event 1 propagate to cause Event 2 at a
DIFFERENT entity, which then causes Event 3 at a third -- a real, directional, multi-hop
cascade. Distinct from the sector-peer ripple finding (same-WINDOW magnitude correlation,
not directional causation) and the storm/compounding finding (a company's OWN reaction
size, not propagation to others). Deliberately given a distinct name from this codebase's
existing "chain" terminology (same_entity_sequence, chain_position, follow_on), which all
turned out to mean same-company narrative continuity, not cross-entity propagation.

**Real existing infrastructure found and reused, not reinvented:**
- `event_relationships` (116 real rows) already has a `comparison_signal` type (39
  instances) that is genuinely cross-entity: one shared macro root cause -> several
  different companies' own distinct, independently-documented reactions (e.g. COVID panic
  -> Boeing's CEO ouster, SLB's restructuring, Pfizer's vaccine-revenue turnaround). This
  IS real Tier-1 material (macro trigger -> company reaction) and does not need to be
  rebuilt.
- Confirmed `events` rows CAN exist with zero entity link (the Fed's 2020-03-15 emergency
  rate cut has no linked ticker) -- genuinely exogenous triggers are already representable
  in this schema without new columns.
- `follow_on`/`same_entity_sequence` (70 combined instances) are same-company only and
  irrelevant to this hypothesis -- confirmed by reading all 15 real `follow_on` examples,
  every one was same-ticker-to-same-ticker.

**First real design attempt, and why it failed:** tried using SECTOR membership +/-40 days
as a structured screen for candidate Company-A-event -> Company-B-event pairs (same sector,
different ticker). Sized at three thresholds: 135,770 raw candidates (unscoped), 14,769
(Company A restricted to |20d abnormal return| > p90 = 13.2%), 3,070 (BOTH sides restricted
to p90+). Read a real random sample of 25 of the 3,070 "both large" pairs individually.
**Result: essentially none were genuine A-causes-B links.** Nearly every pair was two
DIFFERENT companies independently reacting to the SAME known systemic event (2008 crisis,
COVID) in the same rough window -- exactly what `comparison_signal` already captures, not
new propagation. The "require both sides large" filter inadvertently just re-selects
crisis-clustering periods, since that's when large reactions cluster across every sector
simultaneously.

**Real reframing (2026-09-29), based on reading the failed sample:** the problem wasn't
timing/sector proximity -- it was that both sides of nearly every failed pair were
company-INITIATED, PROACTIVE decisions (an acquisition, a promotion, a strategic
restructuring). Two companies making independent proactive choices in the same window
looks like coincidence because it largely is one. The one real working precedent
(`comparison_signal`'s COVID/Fed link) worked specifically because the Fed's action is
genuinely exogenous -- no company decision involved at all.

**Also confirmed: `event_pre_context.size_bucket` has ZERO real variance** (15,976 of
15,976 populated rows all read `large_or_mega_cap_tracked_universe`) -- this project's
tracked universe is exclusively large/mega-cap by design (GICS sector anchors). A
company-SIZE-based tier ("large company -> medium company -> small company") is **not
buildable with this data.** The real, correct tiering dimension is event NATURE
(exogenous/forced vs. company-initiated/proactive), not company size.

**Revised real tier structure:**
- **Tier 0** -- genuinely exogenous, zero company decision involved (Fed/regulatory
  actions, macro conditions, natural disasters, geopolitical events). May have no entity
  link at all, per the confirmed Fed-cut precedent.
- **Tier 1** -- a company's REACTIVE event, forced by a Tier 0 trigger, not a company's own
  initiative. This is what `comparison_signal` already captures for the two big known
  crises (2008, COVID).
- **Tier 2** -- does Company A's Tier-1 REACTIVE event (not proactive) cause a DIFFERENT
  Company B's own REACTIVE event? This is the genuinely untested piece. Hypothesis:
  restricting BOTH sides to reactive/forced events (not just large-magnitude ones) should
  perform better than the failed sector-timing attempt, which had no such restriction.

**Real sizing check on the reframed approach:** a crude text-pattern search (title/
description containing "in response to," "following," "forced," "mandated," "compelled,"
"as a result of," "amid") matched 374 of 16,746 events (2.2%). Read a real random sample
of 20 by hand: roughly 8-9 (40-45%) were genuinely externally-triggered (macro conditions,
commodity prices, sanctions/geopolitical, regulatory rulings, government legal action);
the other 10-11 were false positives -- same-company events using "following" to reference
the COMPANY'S OWN prior action (a CEO departure following the company's own divestiture,
an appointment following the company's own acquisition) -- structurally identical to the
already-null same_entity_sequence pattern, just caught by different wording. At ~40-45%
real precision, the 374 crude matches imply roughly **150-170 genuinely externally-
triggered candidate events** -- a real, human-reviewable starting pool.

**Concrete next step, not yet done:** read through the estimated ~150-170 real Tier-1
candidates (filtering out the same-company-reference false positives first), then for each
one, search for a DIFFERENT company's own reactive event (same reactive-language filter,
not a magnitude filter) in the following window. This is the real, still-untested version
of Tier 2. Deliberately scoped as a dedicated future session -- read-and-classify work
at this scale, not a quick query.

---

## Consumer Confidence Trend -- real, mixed result after multi-cutoff robustness testing (2026-09-30)

**Status: one real, fairly robust partial signal (falling->punished); one
apparent signal (rising->muted) that did NOT survive robustness testing and is
likely cutoff-specific, not a genuine effect. Not added to the full model.**
Raised while scoping Government Decisions/Population Sentiment: does consumer
confidence TREND (University of Michigan Consumer Sentiment, this month vs. the
prior month) predict `reaction_character`? Added UMCSENT to the real FRED
ingestion (392 real observations, 1994-2026) and built a standalone walk-forward
test, same pattern as every other feature tested this session.

**First result, single cutoff 2024-01-01, looked genuinely promising:**
falling->punished +5.0pp (n=858), rising->muted +3.8pp (n=559), stable->rewarded
-2.4pp (n=268). **Real, important correction after testing 4 more cutoffs
(2021-06, 2022-06, 2023-01, 2025-01), same n=4,139 dataset throughout:**

- **Falling -> punished holds up reasonably well**: beats baseline at 4 of 5
  cutoffs (+1.4pp, +3.8pp, +5.0pp, +5.0pp), flat/tied (not a miss) at the
  earliest cutoff (36.4% vs 36.8%). The one part of this finding that looks
  real, though the effect size growing at later cutoffs is itself worth more
  investigation -- could be a genuinely strengthening relationship, or a
  time-varying confound (e.g. the 2022+ rate environment) masquerading as one.
- **Rising bucket is NOT robust -- real, important finding.** The training
  data's own "most common reaction for rising confidence" changes across
  cutoffs: punished (2021), punished (2022), rewarded (2023), muted (2024),
  muted (2025). Two cutoffs were real misses (-4.4pp, -3.1pp), one was a large
  miss (-6.0pp), and only the two most recent cutoffs showed a beat. This
  pattern -- the predicted label itself shifting with the training window --
  is a real, textbook sign of instability, not a genuine standalone effect.
  The original "rising->muted, +3.8pp" report was real FOR THAT ONE SPLIT, but
  does not generalize and should not be treated as a validated finding.
- **Stable bucket confirmed as a genuine non-predictor**: underperforms
  baseline at every single cutoff tested (31.0%, 31.0%, 32.1%, 29.2%),
  consistently, not just in the original test.

**Real, honest overall conclusion:** this is NOT a clean validated finding the
way storm/sector-peer-ripple are. It's a real, partial, asymmetric result --
falling confidence plausibly does correlate with punished reactions, with
reasonable (not full) robustness; rising and stable confidence show no reliable
pattern. Worth keeping as an open, partially-promising lead, not treating as
settled. Real next steps, not done: investigate why falling->punished's effect
size grows at later cutoffs (real strengthening vs. confound); test for overlap
with `regime`/`firm_state` before considering any version of this for the full
model.

## CORRECTED 2026-10-02: the "sentiment excludes pre-2015 events" claim below was WRONG

**Real, important correction, left visible rather than deleted, so the mistake
and the fix are both on record.** The entry below claimed sentiment's 2015
cutoff structurally excludes 53% of this project's events from
multi_feature_model.py. **This was asserted without checking
get_sentiment_bucket()'s real fallback behavior first, and it's wrong.** When
no real GDELT tone data exists for a window, that function returns the string
`"no_data"` -- not `None`. `"no_data"` passes the `sentiment is None` check
completely and becomes just another valid one-hot category, same as
"negative"/"neutral"/"positive". **Sentiment does NOT act as a hard exclusion
filter at all.**

Proven directly: built a sentiment-free variant
(`multi_feature_model_no_sentiment.py`) and added matching pre-2015/post-2015
debug counts to BOTH scripts, run back to back on the same real database
state. Identical result either way: 2,639 pre-2015 rows, 6,187 post-2015
rows, 8,826 total. Removing sentiment changed nothing -- proof the original
claim was false, not a close call.

**What's still real and unchanged from the entry below:** the `firm_state`
(financial_condition_score) finding -- its real, sharp 2004-2008 coverage
gap, confirmed directly against real `financial_metrics` row counts by year,
tracking the SEC's real XBRL mandate phase-in. That part holds. The
"sentiment causes a 2015+ cutoff" framing around it does not, and is struck
below rather than restated.

---

~~## Real, Major Structural Finding: multi_feature_model.py Is Effectively 2015+ Only (2026-10-02)~~

~~**Read this before interpreting ANY multi_feature_model.py result in this
document, past or future.**~~ -- WRONG, see correction above. Sentiment's
`"no_data"` fallback means it never actually excludes anything; the real
dataset is shaped by `firm_state`/`storm_tier`/`reaction` availability, not
sentiment's date coverage.

~~`company_sentiment_timeline` has ZERO rows before 2015-02-17 -- not reduced
coverage, a hard, complete cutoff.~~ -- this fact about the raw table is
still true, but it does NOT propagate into the model as an exclusion, because
of the `"no_data"` fallback above. Struck as a claim about the model's
behavior; the raw table fact itself is harmless trivia, not a finding.

**Real, secondary finding from the same investigation, still valid:**
`firm_state` (financial_condition_score, built from SEC XBRL data) shows a
sharp, real, explainable spike in missing coverage specifically in 2004-2008
(839-928 missing events/year, vs 37-66/year before 2004 and a declining
trickle after 2009) -- confirmed directly against real `financial_metrics`
row counts by year (2006: 1 row; 2007: 180; 2008: 593; 2009: 1,040; climbing
steadily after) that this tracks the SEC's real XBRL mandate phase-in (2009
for large accelerated filers, phasing to smaller companies through 2011) --
genuine quarterly XBRL data barely existed industry-wide before 2007-2009.
Not a bug in this project's pipeline -- a real, external, historical
data-availability constraint. `storm_tier`'s missing-coverage pattern is much
milder by comparison (a modest 2004-2009 bump, 76-112/year, settling to a
steady ~30-75/year baseline) and doesn't need the same real-world
explanation -- consistent with ordinary price-data edge cases, not a
structural external cause.

~~**Real, honest implication, not yet acted on:** a genuinely clean test of
whether any of these features matter across the FULL tracked history...~~ --
moot; building the sentiment-free variant to test this is exactly what
proved the original claim wrong (see correction above).

## Methodology Standard

Every finding above followed the n=30-50 minimum sample threshold and, where claimed
"validated," genuine out-of-sample testing (train/test date split, no re-tuning on the
held-out window). See `PROJECT_PLAN.md` Section 6 for the full prediction-contract
discipline (universe, horizon, benchmark, base rate, similarity keys, magnitude/dispersion,
out-of-sample window) this project holds every claimed pattern to.

## Sentiment-free model tested across the real full 1994-2026 history (2026-10-02)

Real follow-up to the correction above. Ran `multi_feature_model_no_sentiment.py`
(event_type, firm_state, regime, storm_tier, confidence_trend -- no sentiment,
no storm_x_sentiment) at two real cutoffs, same 8,826-row dataset both times:

- **2015-01-01** (inverted split, train 2,587 / test 6,239): test accuracy
  34.3% vs. 37.3% baseline -- a real -3.0pp gap, below baseline.
- **2020-01-01** (balanced split, train 5,272 / test 3,554): test accuracy
  34.4% vs. 33.3% baseline -- a real +1.1pp gap, small and not treated as a
  validated finding.

**Real, honest conclusion: the result flips sign depending on where the
cutoff falls, which is itself the informative part.** A genuinely robust
finding wouldn't swing from below to above baseline just from moving the
split point. `confidence_trend` does not appear in either run's top-10
coefficients. Testing across the real, full 1994-2026 history -- not just the
modern era -- still does not produce a validated signal, consistent with
every other full-model result this session (sentiment, trend, chain-position,
storm x sentiment interior cells). Only storm/sector-peer-ripple (both
magnitude, not direction, findings) and the partial, still-caveated
falling-confidence->punished standalone result have cleared that bar so far.

## VALIDATED: Magnitude Prediction Beats Baseline, Consistently, Across 5 Independent Cutoffs (2026-10-02)

**Real, genuinely validated finding -- the strongest, most robust result of this
entire session.** Raised directly from a real observation: `reaction_character`
(rewarded/punished/muted) compresses a continuous number into a 3-way label with
no sense of scale, and the one finding that validated cleanly all session
(storm/sector-peer-ripple) is explicitly a MAGNITUDE finding, not a direction
finding -- consistent with the well-known reality that price direction is close
to a random walk in efficient markets while volatility/magnitude genuinely
clusters and is forecastable.

Built `multi_feature_model_magnitude.py`: same real features as the sentiment-free
model (event_type, firm_state, regime, storm_tier, confidence_trend), but the
target is real |abnormal_return_20d| bucketed at the genuine dataset median
(0.0421168336824002) into large/small -- a real balanced 50/50 baseline by
construction, not an arbitrary or favorable cutoff.

**Real result, same 8,815-row dataset, tested at 5 independent cutoffs:**

| Cutoff | Test accuracy | Baseline | Beat |
|---|---|---|---|
| 2018-01-01 | 53.5% | 44.3% | +9.2pp |
| 2020-01-01 | 54.8% | 42.5% | +12.3pp |
| 2022-01-01 | 55.1% | 43.7% | +11.4pp |
| 2023-01-01 | 54.3% | 43.5% | +10.8pp |
| 2024-01-01 | 55.3% | 41.9% | +13.4pp |

Every single cutoff beats baseline by a double-digit margin, same direction,
tight range (+9.2 to +13.4pp) -- no sign flips, no misses, nothing resembling
the instability that sank the `confidence_trend` rising-bucket claim. Train-test
gap stayed small (2-3 points) at every cutoff tested -- not overfitting.

**Real bug found and fixed during this build, worth remembering:** the
coefficient-printing code used `model.coef_[0]` for BOTH classes unconditionally
in the binary case, producing identical (not mirrored) output for "large" and
"small" -- confirmed and fixed (sklearn's binary LogisticRegression stores one
row, representing log-odds of `classes_[1]` relative to `classes_[0]`; the first
class needs the negated row, not a copy). Model accuracy itself was never
affected -- this was a real display bug, not a fitting bug -- but it would have
led to exactly backwards interpretation of which features predict large vs.
small reactions had it gone unnoticed.

**Real, corrected, trustworthy coefficients (cutoff 2022-01-01):**
Predicts LARGE reactions: `event_type_systemic_shock` (+0.753), `storm_tier_large`
(+0.356), `regime_financial_crisis_2008_2009` (+0.313), `regime_covid_panic_2020`
(+0.240). Predicts SMALL reactions: `event_type_cybersecurity_incident`,
`event_type_capital_raise`, `event_type_legal_settlement` -- more routine
corporate actions.

**Real, independent cross-validation, not just internal consistency:**
`storm_tier_large` predicting larger reactions matches the separately-validated
storm/compounding finding exactly. `regime_financial_crisis_2008_2009` pushing
toward larger reactions matches the direction model's own earlier finding
(crisis regime -> less muted, more extreme reactions) from a completely
different model and target. Two independent confirmations of the same real
pattern, not a coincidence.

**Real, honest next steps, not yet done:** test for overlap with storm_tier
specifically (does magnitude prediction collapse to just "is this a storm
event" dressed up differently, or does it carry real independent signal beyond
that one feature); consider whether this is ready to become a real, stored
`expected_magnitude_bucket` feature (same treatment as storm_tier's
productionization) now that it's cleared 5/5 cutoffs.
