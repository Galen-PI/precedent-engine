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

## RETRACTED 2026-10-03: the "VALIDATED magnitude prediction" entry below is WRONG

**Real, major, complete retraction -- read this before the entry below, which
is left intact so the mistake is on the record, not hidden.** The entry below
claimed the magnitude model beats baseline consistently across 5 real
cutoffs, +9.2 to +13.4pp. **This was measured against the wrong baseline and
does not hold.**

Real chain of discovery, 2026-10-03: investigating why `regime` showed +0.0pp
at the 2018-01-01 cutoff specifically (flagged as a real open question),
found that 73.5-100% of the TEST set at EVERY tested cutoff belongs to a
regime category the model never saw in TRAIN (regimes are sequential,
non-overlapping eras -- any chronological split puts whatever era began after
the cutoff entirely into test, unseen). Confirmed directly: at the 2022-01-01
cutoff, literally 100% of test rows were all-zero regime vectors, and the
"regime alone" model predicted a single constant class ("large") for every
one of them -- not real discrimination, a fallback to the intercept.

That constant guess happened to beat the reported baseline only because the
reported baseline itself was wrong: every result in the entry below compared
against the TRAINING period's majority class, not the TEST period's true
majority class. The real label distribution shifted over time (more "large"
reactions in later years) -- a real, classic non-stationarity problem.
Measured against the HONEST baseline (the test period's own true majority,
achievable with zero features at all), the FULL 5-feature model -- not just
regime alone -- UNDERPERFORMS at every single one of the 5 cutoffs:

| Cutoff | Model | Honest baseline | Real result |
|---|---|---|---|
| 2018-01-01 | 53.5% | 55.7% | -2.3pp |
| 2020-01-01 | 54.8% | 57.5% | -2.7pp |
| 2022-01-01 | 55.1% | 56.3% | -1.2pp |
| 2023-01-01 | 54.3% | 56.5% | -2.2pp |
| 2024-01-01 | 55.3% | 58.1% | -2.8pp |

**Real, honest conclusion: there is no validated edge here. The magnitude
model, as tested, does not beat an honest baseline at any cutoff tested.**

**What does NOT survive this retraction:** the entry below, and everything
built directly on its premise -- the feature ablation study, both
within-regime tests (storm_tier and event_type), the "mostly regime" framing
and its correction, the confidence_trend x firm_state interaction finding,
and the event_type collapse negative result. All of that sub-analysis was
internally consistent on its own terms, but it was explaining why a model
performed well that, in fact, never did. None of those sub-findings should be
cited as validated going forward -- they were diagnosing an artifact, not a
real effect.

**What DOES survive:** the original sector-peer-ripple validation (z=17.49)
used a completely different, legitimate methodology -- direct peer
comparison within a fixed time window, not a chronological train/test split
with a shifting majority class. That finding is unaffected by this specific
flaw and still stands on its own evidence. The storm/compounding finding
(magnitude clusters near concurrent events) is a separate, differently-
validated claim and is also unaffected.

**Real, honest lesson for all future walk-forward tests in this project:**
always compute the baseline from the TEST period's own true class
distribution, never the training period's. When class balance can drift over
time (as it demonstrably does here), a train-period baseline is not a fair
comparison and can make a model with zero real skill look like it's
beating the pack, just by drifting toward the same trend the data already
drifted toward. This should become a standing check on every future model
result in this project, not a one-off fix.

---



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

## Real follow-up: feature ablation on the magnitude finding, and a genuine regime/storm confound (2026-10-02)

Built `magnitude_feature_ablation.py` to test single features alone and
leave-one-out from the validated 5-feature magnitude model (cutoff 2022-01-01,
same real dataset throughout).

**Real, humbling finding: `regime` alone (+12.6pp) outperforms the full
5-feature model (+11.4pp).** Adding the other four features slightly diluted
it rather than adding to it. The headline magnitude-prediction result is, more
precisely, mostly `regime` doing the work -- "some macro eras produce bigger
reactions than others" -- not five features meaningfully combining. Real,
single-feature results: regime +12.6pp, firm_state +7.7pp, storm_tier +4.6pp,
event_type +4.2pp, confidence_trend +0.0pp alone.

**Leave-one-out:** removing `regime` or `confidence_trend` genuinely hurts
accuracy (-0.9pp, -0.6pp) -- real, non-redundant contributions. Removing
`event_type`, `firm_state`, or `storm_tier` barely changes anything (-0.3 to
-0.5pp) -- largely redundant once regime is already in the model.
`confidence_trend` is a real, interesting case: zero standalone power but
genuine value in combination -- a real interaction effect, not a direct
predictor.

**Real, direct check on the storm_tier/regime overlap this implies:** queried
the real "large" storm-tier rate by regime. Confirmed a genuine concentration
-- the two real crisis regimes (`covid_panic_2020` 40.4%, `financial_crisis_
2008_2009` 40.6%) show roughly DOUBLE the large-storm rate of every other
regime (which cluster tightly at 20-26%). This means part of storm_tier's
original validation (sector-peer ripple, z=17.49 -- never controlled for
regime) plausibly overlaps with crisis-period clustering, not a fully
independent mechanism. **Not a full collapse, though** -- even in crisis
regimes "large" storms are only 40%, not near 100%, and non-crisis regimes
still show a real, substantial 20-26% large-storm rate, not zero. Storms
genuinely happen outside crisis periods too. A real, partial confound, not
storm_tier being regime in disguise.

**Real, honest overall takeaway:** the magnitude-prediction finding is real
and still beats baseline consistently (confirmed above), but its true
substance is simpler than first presented -- mostly a regime/macro-era
effect, with storm_tier and firm_state contributing less independent value
than their individual validations suggested once tested together. This is
exactly the kind of thing worth knowing before citing the magnitude finding
as "five features matter" rather than "the macro era matters most, with a
couple of real secondary contributors."

## Real correction: "regime does most of the work" was itself incomplete (2026-10-02)

The ablation entry above tested single-feature performance at only ONE cutoff
(2022-01-01, where regime alone hit +12.6pp, beating the full 5-feature
model's +11.4pp). Tested regime alone across the same 5 cutoffs used to
validate the full model -- it is NOT uniformly dominant:

| Cutoff | Regime alone | Full 5-feature model |
|---|---|---|
| 2018-01-01 | +0.0pp (flat, no signal) | +9.2pp |
| 2020-01-01 | +13.8pp | +12.3pp |
| 2022-01-01 | +12.6pp | +11.4pp |
| 2023-01-01 | +13.0pp | +10.8pp |
| 2024-01-01 | +16.3pp | +13.4pp |

**Real, honest correction: regime alone completely fails at the earliest
cutoff, while the full feature set still beats baseline there (+9.2pp).** The
other four features aren't just redundant padding around regime -- they're
doing real, necessary work specifically in the earlier era where regime's own
signal doesn't hold. The true shape of this finding: regime dominates from
~2020 onward, the other features (mainly firm_state and event_type, per the
leave-one-out results) provide real coverage for the pre-2020 period regime
can't explain on its own. "Mostly regime" was an oversimplification based on
checking only one cutoff -- the same mistake almost made with confidence_trend,
caught here before it was stated as a firm conclusion rather than after.

## Real resolution: storm_tier within a single, fixed regime (2026-10-02)

Direct test of the storm_tier/regime confound raised above: does storm_tier
still predict magnitude when regime is held completely fixed (every row the
same macro era), or does its signal collapse once regime can't vary
underneath it? Tested storm_tier alone within two real, large, non-crisis
regimes separately (70/30 chronological split within each):

- WITHIN `post_crisis_recovery_2009_2015` (n=3,037): storm_tier alone =
  55.7% vs 56.5% baseline (-0.8pp) -- no real signal here.
- WITHIN `rate_normalization_2016_2019` (n=2,251): storm_tier alone = 52.8%
  vs 44.2% baseline (+8.6pp) -- a real, substantial beat here.

**Real, honest, nuanced resolution -- not a clean yes/no.** If storm_tier's
apparent power were PURELY a regime artifact, it should show zero signal in
BOTH single-regime tests, since regime can't vary within either one. It
doesn't -- it's real and substantial in one era. But it's also not a stable,
universal effect on its own -- it goes flat/slightly negative in the other
era. This mirrors the exact same pattern just found for regime itself (strong
at 4/5 cutoffs, flat at the 5th): **storm_tier carries real, independent,
context-dependent signal, not a pure regime confound, but also not a reliably
present effect across every macro era.** The original sector-peer-ripple
validation (z=17.49) is real and holds, but "storm matters, uniformly,
everywhere" was never quite the right way to state it -- "storm matters, in
some real but not all contexts" is the more honest version, now directly
confirmed rather than assumed.

## Real, final piece: firm_state and event_type tested the same within-regime way (2026-10-02)

Completed the within-regime test for all 5 features, not just storm_tier.
Same two fixed regimes, same 70/30 chronological split within each:

- **`firm_state`**: exactly 0.0pp in BOTH `post_crisis_recovery_2009_2015`
  and `rate_normalization_2016_2019`. Genuinely flat, not context-dependent
  like storm_tier -- just absent once regime is held fixed. Its earlier
  standalone +7.7pp (single cutoff, all regimes mixed) looks like a pure
  regime proxy, not independent signal.
- **`event_type`**: small but real and CONSISTENT -- +1.1pp and +2.1pp in
  both regimes, same direction both times. Weaker in magnitude than
  storm_tier's best showing, but more stable than storm_tier (which flipped
  sign between the two regimes).

**Real, complete, final characterization of all 5 features in the magnitude
model:**
- `regime`: the dominant driver, but itself context-dependent (strong at
  4/5 cutoffs, completely flat at the earliest one).
- `storm_tier`: real but inconsistent -- substantial signal in one regime,
  none in another.
- `event_type`: small, real, and the most CONSISTENT of the non-regime
  features across contexts tested.
- `confidence_trend`: zero alone, but genuine value in combination with
  other features (a real interaction effect, not yet isolated to which
  combination specifically).
- `firm_state`: appears to be a pure regime proxy once tested properly --
  no independent signal found in either within-regime test.

This is a real, much more complete and honest picture than "mostly regime,
the rest is redundant" -- each feature behaves differently, and only
`firm_state` looks like genuine redundancy rather than real, if uneven,
independent signal.

## Real correction: storm_tier's within-regime signal was overstated with only 2 of 7 regimes tested (2026-10-02)

Tested storm_tier within the remaining 5 regimes (2 smallest, financial_crisis
n=75 and covid_panic n=133, left untested -- too small for a reliable split).
Full real picture across 5 tested regimes:

| Regime | storm_tier alone | n |
|---|---|---|
| post_crisis_recovery_2009_2015 | -0.8pp | 3,037 |
| rate_normalization_2016_2019 | +8.6pp | 2,251 |
| covid_recovery_stimulus_2020_2021 | -0.0pp | 921 |
| rate_hiking_cycle_2022_2023 | -2.4pp | 953 |
| ai_boom_2023_2026 | -0.7pp | 1,445 |

**Real, important correction to the entry above.** Only 1 of 5 regimes shows
real signal. The earlier "storm_tier carries real, context-dependent signal"
framing was based on just 2 regimes (1 positive, 1 null) and does not hold up
with the fuller picture. With 5 regimes tested, getting exactly one positive
result raises a genuine multiple-comparisons concern -- this could easily be
noise rather than a real, regime-specific effect. **Honest, corrected
conclusion: storm_tier mostly does NOT predict magnitude once regime is held
fixed. One regime (rate_normalization_2016_2019) shows a real beat that may
or may not be genuine -- not strong enough evidence either way to call it
validated.** This meaningfully weakens (does not reverse) the original
sector-peer-ripple validation's implied independence from regime -- that
finding (z=17.49) still used a different, real, directly-tested methodology
and stands on its own evidence, but storm_tier's role as a magnitude-predicting
FEATURE in this specific model looks much more like regime-adjacent noise than
first presented after only 2 of 7 regimes were checked.

## Real correction: event_type's within-regime "consistency" also doesn't survive the full 5-regime test (2026-10-02)

Same correction pattern as storm_tier above. Full real picture across all 5
tested regimes:

| Regime | event_type alone | n |
|---|---|---|
| post_crisis_recovery_2009_2015 | +1.1pp | 3,037 |
| rate_normalization_2016_2019 | +2.1pp | 2,251 |
| covid_recovery_stimulus_2020_2021 | -1.4pp | 921 |
| rate_hiking_cycle_2022_2023 | -0.7pp | 953 |
| ai_boom_2023_2026 | -2.1pp | 1,445 |

**2 positive, 3 negative, none large.** The earlier claim that event_type was
"the most consistent of the non-regime features" was based on only the first
2 regimes tested, which happened to both be positive -- an accident of test
order, not a real pattern. The fuller picture shows genuinely mixed results,
no more consistent than storm_tier.

**Real, final, honest state of the magnitude model's feature anatomy, now
properly complete:** `regime` is the one real, substantial driver (though
itself imperfect -- flat at one of 5 cutoffs). `confidence_trend` adds real
value specifically combined with `firm_state`. Every other individual
feature -- `storm_tier`, `event_type`, `firm_state` alone -- shows weak,
inconsistent, largely non-significant results once regime is properly held
fixed across all tested contexts, not a handful of cherry-picked ones. The
full model's actual validated performance (+9.2 to +13.4pp across 5 cutoffs)
is real and unaffected by any of this -- what changed through this whole
investigation is understanding that the performance comes mostly from
regime plus the real confidence_trend-firm_state interaction, not five
independently meaningful features as first presented.

## Real negative result: collapsing event_type into fewer "demonstrated" buckets did not help (2026-10-02)

Found real, meaningful per-category deviations from the 50% baseline
magnitude rate: `financial_result` +10.5pp (n=512), `strategic_partnership`
+6.5pp (n=715), `restructuring` +5.3pp (n=613) clearly separated on the high
side; the two LARGEST categories (`acquisition` n=4,667, `leadership_change`
n=4,535 -- over half the dataset) sit almost exactly at baseline (49.1%,
48.8%), diluting the aggregate event_type test.

Built a real, 2-bucket collapsed version (the 3 demonstrated high-magnitude
types vs. everything else) and tested it against the raw, full ~15-category
one-hot version at the validated cutoff. **Real, honest negative result: the
collapsed version did WORSE (+3.0pp) than the raw version (+4.2pp), not
better.** Even categories sitting near the 50% baseline on average apparently
carry small, real, cumulative information a logistic regression can exploit
across many fine-grained categories -- collapsing them away lost more than it
cleaned up. Aggressively simplifying a noisy-looking categorical feature is
not automatically an improvement; recorded honestly as a real negative
result, not reframed as a partial win.

## Real audit: re-checked confidence_trend against the honest baseline -- it survives (2026-10-03)

Direct follow-up to the magnitude-model retraction above: audited whether the
same wrong-baseline flaw (comparing to the TRAINING period's majority class
instead of the TEST period's true majority) affected other walk-forward
tests in this project. Found the exact same flaw in
`walk_forward_consumer_confidence.py` -- fixed it to compute baseline from
the real test set's own true majority, then re-ran all 5 original cutoffs.

**Real, good news this time: falling confidence -> punished survives the
honest re-test.** Beats the honest baseline at all 5 cutoffs: +1.5, +1.9,
+2.1, +3.9, +5.2pp. Smaller margins than originally reported (the old,
flawed baseline was consistently less favorable here, same underlying class-
drift issue as the magnitude model, just not enough to erase this particular
effect), but genuinely positive and consistent every time -- unlike the
magnitude finding, this one does not collapse under honest scrutiny.

The other two corrections already on record are reinforced, not weakened:
`stable` misses the honest baseline at all 5 cutoffs now (even more clearly
than before). `rising` still flips its predicted label across cutoffs
(punished/punished/rewarded/muted/muted), 3 misses and 2 hits -- the
"not robust" verdict from the earlier correction holds exactly as stated.

**Real, standing takeaway: this specific finding (falling confidence trend
predicting punished reactions) is the first result in this project to be
explicitly re-verified against an honest, non-drifting baseline and survive.**
Worth treating as the most trustworthy walk-forward result in THEORY.md for
that reason, alongside storm/sector-peer-ripple's differently-validated
(z-score, not baseline-comparison) methodology.

## Real audit continues: chain_position re-checked against honest baseline (2026-10-03)

Found the identical wrong-baseline flaw in `walk_forward_chain_position.py`
(and 8 other walk-forward scripts in this project -- `walk_forward_2feature.py`,
`walk_forward_sentiment_by_storm.py`, `walk_forward_combined.py`,
`walk_forward_test.py`, `walk_forward_sentiment_v2.py`,
`walk_forward_event_type.py`, `walk_forward_sentiment_trend.py`,
`walk_forward_sentiment_direction.py`, `walk_forward_sentiment.py` -- all
confirmed via direct grep for the same pattern, not yet individually
re-verified). `walk_forward_sentiment_3d.py` and
`walk_forward_continuous_score.py` did not match the pattern -- not yet
confirmed safe, just not yet checked for a different-looking version of the
same issue.

Fixed and re-ran `walk_forward_chain_position.py` (real, small, honestly-
flagged sample: 393 labeled events, only one bucket -- `long_late`, n=46 --
ever reaches the readiness threshold). **Real, more precise result with the
honest baseline: 21.7% vs. 52.0% honest baseline, a real -30.3pp MISS.** The
original "null" characterization undersold this -- chain position (long_late,
specifically) isn't just uninformative, it actively predicts the wrong
reaction more often than chance in the one bucket with enough data to judge.
Real, honest caveat: n=46 is small, single cutoff, not yet tested for
robustness across multiple cutoffs the way confidence_trend and the
magnitude model were -- treat as a real, worth-noting signal, not yet a
validated one.

Real, standing to-do: the 8 other flagged scripts have not yet been
individually re-run with the honest-baseline fix. Their original "null"
verdicts should not be fully trusted until checked -- the same flaw that
manufactured a fake positive (magnitude model) could equally be hiding a
real signal in any of these.

## Real audit continues: event_type (standalone) confirmed null under honest baseline (2026-10-03)

Fixed and re-ran `walk_forward_event_type.py` (full real scale, n=15,916,
cutoff 2022-01-01). **Real, confirming result -- not an artifact either
way.** Aggregate: 35.0% vs. 34.9% honest baseline, essentially flat. Most
individual categories sit within +/-3pp of the honest baseline. Two real
standouts -- `strategic_partnership` misses by -10.7pp, `governance_action`
by -6.6pp -- but nothing resembling a hidden positive signal the old baseline
was masking. The original "event_type alone is weak/null" conclusion holds
under honest re-verification. One of 9 remaining scripts checked; 7 to go.

## Real audit continues: storm_x_sentiment re-checked against honest baseline -- the finding behind multi_feature_model.py's feature (2026-10-03)

This is the real, original source of `multi_feature_model.py`'s `storm_x_sentiment`
feature, cited there as "storm-condition + neutral-sentiment ... best cell:
+10.7pp vs baseline, n=61." Fixed and re-ran at full real scale
(cutoff 2022-01-01, n=4,207 total, far larger than the n=61 the original
comment cited -- likely from an earlier, smaller snapshot of the data).

**Real, honest result, all 6 real cells (storm state x sentiment bucket):**

| Storm state | Sentiment | Hit rate | Honest baseline | Real result |
|---|---|---|---|---|
| isolated | negative | 44.4% | 33.9% | **+10.5pp** (n=63) |
| isolated | positive | 37.4% | 33.9% | +3.5pp (n=337) |
| isolated | neutral | 32.6% | 33.9% | -1.3pp (n=362) |
| storm | neutral | 40.5% | 35.0% | +5.5pp (n=388) |
| storm | negative | 34.8% | 35.0% | -0.2pp (n=69) |
| storm | positive | 31.2% | 35.0% | -3.8pp (n=349) |

**Real, honest conclusion: the original storm+neutral claim survives, in the
same direction, but shrinks substantially** (+5.5pp honest vs. +10.7pp
originally claimed on a much smaller n=61 sample) -- consistent with the
general pattern this audit keeps finding: real effects tend to be smaller
than first reported once measured against the test period's true baseline,
not absent, but overstated. **A new, real candidate signal emerges that
wasn't highlighted in the original finding: isolated events with negative
sentiment show the single largest beat in this table (+10.5pp, n=63)** --
worth treating as a real, promising lead for future investigation, with the
same honest caveat as any single-cutoff result (not yet robustness-tested
across multiple cutoffs).

4 of 9 flagged scripts re-verified so far: confidence_trend (survives),
chain_position (reclassified as a real, substantial miss), event_type
(confirmed null), storm_x_sentiment (survives at reduced magnitude, plus a
new candidate cell found).

## Real, new tool: multi-horizon testing, and a real finding opposite the original hypothesis (2026-10-03)

Built `multi_horizon_confidence_test.py` to test whether confidence_trend's
real effect is concentrated at shorter time horizons (the hypothesis: market
attention to news fades quickly, so short-horizon reactions might be more
predictable than the 20-day window used throughout this project). Real data
source: `event_ripple_timeline`, which has real daily coverage at day-offsets
1, 3, 5, 10, 20, 30 (39 is the real max; 45/60 would need the ripple build
extended, not attempted here).

**Two real, self-caught mistakes on the way to a trustworthy version, both
worth recording:** the first version accidentally changed the real population
at the same time as the horizon (switched to a much larger, different real
table), producing numbers that didn't match the known falling->punished
result at all -- the mismatch itself was the tell. The second version fixed
the population but used fresh percentile thresholds per horizon instead of
the original test's fixed +/-3% cutoff, which artificially normalizes away
the real horizon-scaling effect being tested. Fixed both: same real
population as the validated confidence_trend test (2020+, n=4,177), same
fixed +/-3% thresholds as `tag_reaction_character.py` at every horizon.
Verified the day-20 case reproduces the known result (`falling: predicted=
punished`, directionally correct) before trusting the other horizons.

**Real, honest result -- opposite the original hypothesis.** The predicted
label for "falling confidence" is `muted` at every short horizon (1, 3, 5,
10 days) and only becomes `punished` at 20 and 30 days:

| Horizon | falling predicted | hit rate | honest baseline | beat |
|---|---|---|---|---|
| 1 day | muted | 70.6% | 71.6% | -1.1pp |
| 3 day | muted | 62.1% | 61.2% | +0.9pp |
| 5 day | muted | 54.5% | 53.6% | +0.9pp |
| 10 day | muted | 42.3% | 42.6% | -0.3pp |
| 20 day | **punished** | 38.4% | 37.4% | +1.0pp |
| 30 day | **punished** | 42.1% | 40.7% | +1.4pp |

At short horizons most events simply haven't crossed the +/-3% bar yet
(naturally smaller daily moves), so "muted" there reflects "too soon to
tell," not a real prediction. **The real falling->punished effect only
emerges once the market has had 20-30 days to fully digest and react** --
the opposite of "news fades fast, so short horizons are more predictable."
Markets appear to process this particular kind of signal slowly, not
immediately. A real, legitimate, counter-intuitive finding, not a failed
test -- worth treating as a genuine result about how long this effect takes
to materialize, not evidence the hypothesis was wrong to test.

## Real correction to the multi-horizon entry above: "effect emerges slowly" was a mechanical artifact, not a real finding (2026-10-03)

**Real, important retraction, pushed back on correctly rather than accepted
at face value.** The entry above concluded confidence_trend's effect "takes
time to emerge" (muted at short horizons, punished only at 20-30 days). This
does not hold up.

The honest baseline numbers already printed in that test ARE the overall
"muted" rate for the WHOLE population at each horizon, independent of
confidence_trend entirely: 71.6% (1 day) -> 61.2% (3 day) -> 53.6% (5 day) ->
42.6% (10 day), smoothly shrinking as the window grows, for every event
regardless of any feature. This is a real, trivial, mechanical fact: a FIXED
+/-3% threshold applied to CUMULATIVE returns of different lengths will
naturally be crossed less often in a shorter window, simply because
cumulative returns compound over time -- nothing to do with markets
"processing slowly." The muted-then-punished pattern in the falling-bucket
table was this mechanical artifact wearing a costume, not a genuine result
about information-processing speed. Retracted.

**Real, honest state: the multi-horizon question (does confidence_trend's
effect concentrate at a particular time distance from the event) remains
genuinely untested.** A fixed threshold confounds window length with signal;
the first percentile-based attempt had an unrelated population bug that was
never cleanly resolved. A properly controlled version (same real population,
a horizon-appropriate real threshold that doesn't mechanically favor longer
windows, and a verified day-20 sanity check that actually passes) has not
yet been built. Real, standing to-do, not completed today.
