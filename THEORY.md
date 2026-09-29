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

## Methodology Standard

Every finding above followed the n=30-50 minimum sample threshold and, where claimed
"validated," genuine out-of-sample testing (train/test date split, no re-tuning on the
held-out window). See `PROJECT_PLAN.md` Section 6 for the full prediction-contract
discipline (universe, horizon, benchmark, base rate, similarity keys, magnitude/dispersion,
out-of-sample window) this project holds every claimed pattern to.
