# PREREG 2026-10-30: the two window nulls event_pre_days_m4_m1 and event_lasting_days_6_20 (Tier 1 of the G7 re-run)   (written BEFORE any outcome was computed)
# Registered by the assistant for Galen Pike on the template results/TEMPLATE_PREREG.md. It sits beside results/PREREG_g7_proven_rerun_2026-10-29.md (the 15 proven flags) and does not edit it.
DATA AND USE RULE: all companies, as in the original tests of both flags (the sealed tickers were part of them; see Addendum 6 of the proven-flags registration), with every statistic also reported for the non-sealed and the sealed company sets separately as a CONSISTENCY check between two disjoint sets, not as a blind confirmation. The sample is the by-type run's sample (isolated events: no other event of the company within -5 to +39 days; spin-off, separation and split-off titles excluded; an event type present; days 0 to 1 present), read from the view event_profile_base (ARM 0) or from its inline rebuild with excluded events removed from the sample and from the isolation test (ARM 1). No price levels are used.
ANCHOR: DATA. The ledger evidence of both flags (flag_ledger_evidence: pre-window 1.062 on n 5,155 and 1.028 on n 2,681; days 6 to 20 0.986 on n 5,155 and 0.981 on n 2,682) and the by-type run of 2026-10-29 (same view, same sample definition: ALL_POOLED n 6,914 and 3,846 in ARM 0, 7,193 and 3,982 in ARM 1).
TRIALS: confirmatory=2 descriptive=14 ledger_before=112    (two registered rules; 14 descriptive looks: the placebo window in 3 parts and 2 eras, and the non-sealed and sealed parts of the two windows in 2 eras)
HURDLE: each flag passes by its OWN registered rule, unchanged: days -4 to -1 (or 6 to 20) positive with t>=2 (z above 2) in BOTH eras (t = (ratio - 1) / SE). The reference hurdle for a newly discovered effect is 3.0 (ANCHORS.md item 3); it does not apply to a re-test of a registered rule. A FLIP of a null to a lead needs ALL of: the registered rule met in ARM 1; a ratio of 1.03 or more in 2019-2026 (a pre-stated minimum effect); the same sign (above 1) in the non-sealed and the sealed sets in both eras; and a forward check on the January 2027 data before any status change beyond a ledger note.
DECAY: forward_fraction=1.0 because the re-run uses the same sample period; decay belongs to the forward check on new data, which is the only confirmation open to these two flags (the sealed set was part of the original tests).
STANDARD TEST: ratio of sums, SUM(window mean) / SUM(days 25 to 39 mean), per era; SE by the ratio estimator, STDDEV(x - ratio * y) / (SQRT(n) * AVG(y)); the same estimator as the by-type run. The SEs treat events as independent (naive). ARM 1-NULL (the ARM 1 query with an empty exclusion list) must equal ARM 0 in every row before ARM 1 is read.
PLACEBO: days 21 to 24 over days 25 to 39, which should be near 1 if the baseline window is clean (the lasting effect may still leak into it slightly); and ARM 1-NULL against ARM 0 (the rebuild is faithful).
FORWARD CHECK: the January 2027 ingestion and the ripple builder; a flip is re-tested there with the same query before it is called a lead.
PREDICTIONS: ranges are 80% intervals (8 numeric rows, so about 1.6 are expected to miss); the probability rows state whether a rule is met or a stated pattern holds. Predictions describe ARM 1 (the cleaned data). The point values assume the new events (about 34% more than in the original runs) behave like the old ones with a modest pull toward 1; pre-window B is the only cell near a line, and its probability is the whole question.
PRED-TABLE-BEGIN
# id | type | statement | point | lo | hi | level | anchor      (type: ratio, pct, diff or prob; level 80 or 95; anchor DATA <source>, LITERATURE ANCHORS#N, or NONE)
p1 | ratio | event_pre_days_m4_m1: ratio of days -4 to -1 over days 25 to 39, 2004-2018, all companies, ARM 1 (old 1.062 on n 5,155) | 1.048 | 1.026 | 1.070 | 80 | DATA flag_ledger_evidence
p2 | ratio | event_pre_days_m4_m1: same, 2019-2026, ARM 1 (old 1.028 on n 2,681) | 1.022 | 0.998 | 1.046 | 80 | DATA flag_ledger_evidence
p3 | diff | event_pre_days_m4_m1: z against 1 in 2019-2026, ARM 1 (old 1.75) | 1.7 | -0.1 | 3.4 | 80 | DATA flag_ledger_evidence
p4 | prob | event_pre_days_m4_m1 meets its registered rule in ARM 1 (positive with z above 2 in both eras) | 0.35 |  |  |  | DATA flag_ledger_evidence
p5 | prob | ARM 1 gives a lower 2004-2018 pre-window ratio than ARM 0 (the mis-dated bundles hypothesis) | 0.65 |  |  |  | DATA flag_ledger_evidence
p6 | diff | event_pre_days_m4_m1: ARM 1 minus ARM 0, 2004-2018 ratio | -0.004 | -0.015 | 0.006 | 80 | DATA flag_ledger_evidence
p7 | ratio | event_lasting_days_6_20: ratio of days 6 to 20 over days 25 to 39, 2004-2018, all companies, ARM 1 (old 0.986 on n 5,155) | 0.985 | 0.970 | 1.000 | 80 | DATA flag_ledger_evidence
p8 | ratio | event_lasting_days_6_20: same, 2019-2026, ARM 1 (old 0.981 on n 2,682) | 0.984 | 0.966 | 1.002 | 80 | DATA flag_ledger_evidence
p9 | prob | event_lasting_days_6_20 meets its registered rule in ARM 1 (positive with z above 2 in both eras) | 0.02 |  |  |  | DATA flag_ledger_evidence
p10 | prob | event_lasting_days_6_20 ratio is below 1 in both eras in ARM 1 (descriptive) | 0.85 |  |  |  | DATA flag_ledger_evidence
p11 | ratio | placebo days 21 to 24 over days 25 to 39, 2004-2018, all companies, ARM 1 (descriptive; no old value) | 0.99 | 0.975 | 1.006 | 80 | DATA flag_ledger_evidence
p12 | ratio | placebo days 21 to 24, 2019-2026, ARM 1 (descriptive; no old value) | 0.99 | 0.973 | 1.008 | 80 | DATA flag_ledger_evidence
p13 | prob | the 2019-2026 pre-window ratio is above 1 in BOTH the non-sealed and the sealed company sets in ARM 1 | 0.60 |  |  |  | DATA flag_ledger_evidence
p14 | prob | the 2004-2018 pre-window ratio is above 1 in BOTH the non-sealed and the sealed company sets in ARM 1 | 0.97 |  |  |  | DATA flag_ledger_evidence
p15 | prob | ARM 1 isolated events in the 2004-2018 pre-window sample exceed ARM 0's (duplicates and bundles no longer block neighbours) | 0.85 |  |  |  | DATA flag_ledger_evidence
p16 | prob | at least one of the two flags meets its registered rule in ARM 1 | 0.36 |  |  |  | DATA flag_ledger_evidence
PRED-TABLE-END
WHAT WOULD CHANGE THE PLAN: (1) ARM 1-NULL not equal to ARM 0 in every row: stop, ARM 1 is not read, the rebuild is fixed first. (2) ARM 0 more than 5 percent above or below the by-type run's n for the same era (6,914 and 3,846) after the extra non-null windows: investigate the sample before reading any ratio. (3) A flip: recorded as a CANDIDATE only; the ledger status stays null until the January check; the pre-window ratio of 2019-2026 below 1.03 means no flip whatever its z. (4) A surprise (a result outside its range) is recorded plainly and traced by comparing ARM 1 with ARM 0.
LIMITS: THE ORIGINAL QUERY IS NOT RECOVERED. This registration reconstructs the sample from the by-type query; the original ran before the ripple table gained about 6,600 tracks, so its n (5,155 and 2,681 to 2,682) is about 27 percent below what the same definition gives today, and ARM 0 cannot be checked against the ledger's numbers (the by-type run could, because its ledger rows were refreshed after that growth). The SEs are naive (event days are not independent of the market around them). The sealed set was part of the original tests, so a sealed-set result is a consistency check only. The note on pre-window says 'could be mis-dated bundled events': ARM 1 tests that for the excluded bundles only, since other mis-dated events are not identified.
NOT IN THIS NOTE: the three Tier 1 nulls whose registered rule is recorded only as 'earlier session' (direction_overreaction_reversal, tag_specific_ranges, time_to_threshold_asymmetry), which cannot be re-run faithfully until their rules are recovered; the Tier 2 nulls; any new hypothesis. OBSERVED BEFORE THIS REGISTRATION (descriptive, not scored): in the by-type run of 2026-10-29 event_type_financial_result read 1.068 (n 170) and 1.585 (n 123) in ARM 0 and 1.057 (n 177) and 1.579 (n 126) in ARM 1 (z of the difference between eras 2.67 and 2.76: it still flips across eras, no number); event_type_regulatory read 1.541 (n 425) and 1.308 (n 148) in ARM 0 and 1.526 (n 448) and 1.279 (n 156) in ARM 1 (z versus pooled 1.80 and -0.22 in ARM 0: not distinct, uses pooled); the ledger's own rerun of 2026-10-16 already gave 1.068 and 1.582, and 1.541 and 1.308, so both are unchanged.

## Old numbers (flag_ledger_evidence, 2026-10-16)

| flag | era | n | ratio (SE) | z against 1 |
|---|---|---|---|---|
| event_pre_days_m4_m1 | 2004-2018 | 5,155 | 1.062 (0.014) | +4.4 |
| event_pre_days_m4_m1 | 2019-2026 | 2,681 | 1.028 (0.016) | +1.75 (rule not met) |
| event_lasting_days_6_20 | 2004-2018 | 5,155 | 0.986 (0.008) | -1.75 |
| event_lasting_days_6_20 | 2019-2026 | 2,682 | 0.981 (0.009) | -2.1 (negative: rule not met) |

## Queries (run in the SQL editor, in this order, each its own step; read-only)

ARM 0 (the view as it is):

```sql
WITH sealed_e AS MATERIALIZED (SELECT s.entity_id FROM securities s JOIN explore_sealed_tickers z ON z.ticker = s.ticker),
et AS (SELECT DISTINCT ON (etr.event_id) etr.event_id, t.name AS etype
            FROM event_type_relationships etr JOIN event_types t ON t.id = etr.event_type_id
            ORDER BY etr.event_id, t.name),
smp AS (SELECT b.era, b.w_pre, b.w_d620, b.w_d2124, b.base AS y, (b.entity_id IN (SELECT entity_id FROM sealed_e)) AS is_sealed
        FROM event_profile_base b JOIN events e ON e.id = b.event_id JOIN et ON et.event_id = b.event_id
        WHERE b.isolated AND b.w_d01 IS NOT NULL AND b.era <> $$C_pre_2004$$
          AND NOT (e.title ILIKE $$%spin%$$ OR e.title ILIKE $$%separation%$$ OR e.title ILIKE $$%split-off%$$ OR e.title ILIKE $$%split off%$$)),
w AS (SELECT $$1_pre_days_m4_m1$$ AS win, era, is_sealed, w_pre AS x, y FROM smp WHERE w_pre IS NOT NULL
      UNION ALL SELECT $$2_lasting_days_6_20$$, era, is_sealed, w_d620, y FROM smp WHERE w_d620 IS NOT NULL
      UNION ALL SELECT $$3_placebo_days_21_24$$, era, is_sealed, w_d2124, y FROM smp WHERE w_d2124 IS NOT NULL),
v AS (SELECT win, era, $$all$$ AS part, x, y FROM w
      UNION ALL SELECT win, era, CASE WHEN is_sealed THEN $$sealed$$ ELSE $$non_sealed$$ END, x, y FROM w),
r AS (SELECT win, era, part, SUM(x) / SUM(y) AS rr FROM v GROUP BY 1, 2, 3)
SELECT v.win, v.era, v.part, COUNT(*) AS n, ROUND(r.rr::numeric, 3) AS ratio,
       ROUND((STDDEV(v.x - r.rr * v.y) / (SQRT(COUNT(*)) * AVG(v.y)))::numeric, 3) AS se,
       ROUND(((r.rr - 1) / (STDDEV(v.x - r.rr * v.y) / (SQRT(COUNT(*)) * AVG(v.y))))::numeric, 2) AS z_vs_1
FROM v JOIN r ON r.win = v.win AND r.era = v.era AND r.part = v.part
GROUP BY v.win, v.era, v.part, r.rr ORDER BY 1, 2, 3;
```

ARM 1-NULL is the ARM 1 query below with its first line replaced by this exact line (the exclusion list emptied):

```sql
WITH ex AS MATERIALIZED (SELECT event_id FROM event_exclusions WHERE FALSE),
```

ARM 1 (excluded events removed from the sample and from the isolation test):

```sql
WITH ex AS MATERIALIZED (SELECT event_id FROM event_exclusions WHERE severity = $$exclude$$),
per AS (
  SELECT d.event_id, d.entity_id,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 25 AND 39) AS base,
         COUNT(d.adr) FILTER (WHERE d.day_offset BETWEEN 25 AND 39) AS nb,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN -4 AND -1) AS w_pre,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 0 AND 1) AS w_d01,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 2 AND 5) AS w_d25,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 6 AND 20) AS w_d620,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 21 AND 24) AS w_d2124
  FROM event_daily_abn d WHERE NOT EXISTS (SELECT 1 FROM ex WHERE ex.event_id = d.event_id) GROUP BY 1, 2
),
b AS (
  SELECT per.*, e.event_date::date AS d0,
         CASE WHEN e.event_date < $$2004-01-01$$ THEN $$C_pre_2004$$
              WHEN e.event_date < $$2019-01-01$$ THEN $$A_2004_2018$$ ELSE $$B_2019_2026$$ END AS era,
         NOT EXISTS (SELECT 1 FROM event_entity_relationships o JOIN events oe ON oe.id = o.event_id
                     WHERE o.entity_id = per.entity_id AND o.event_id <> per.event_id
                       AND oe.event_date::date BETWEEN e.event_date::date - 5 AND e.event_date::date + 39
                       AND NOT EXISTS (SELECT 1 FROM ex WHERE ex.event_id = o.event_id)) AS isolated
  FROM per JOIN events e ON e.id = per.event_id
  WHERE per.base > 0 AND per.nb >= 10
),
sealed_e AS MATERIALIZED (SELECT s.entity_id FROM securities s JOIN explore_sealed_tickers z ON z.ticker = s.ticker),
et AS (SELECT DISTINCT ON (etr.event_id) etr.event_id, t.name AS etype
            FROM event_type_relationships etr JOIN event_types t ON t.id = etr.event_type_id
            ORDER BY etr.event_id, t.name),
smp AS (SELECT b.era, b.w_pre, b.w_d620, b.w_d2124, b.base AS y, (b.entity_id IN (SELECT entity_id FROM sealed_e)) AS is_sealed
        FROM b b JOIN events e ON e.id = b.event_id JOIN et ON et.event_id = b.event_id
        WHERE b.isolated AND b.w_d01 IS NOT NULL AND b.era <> $$C_pre_2004$$
          AND NOT (e.title ILIKE $$%spin%$$ OR e.title ILIKE $$%separation%$$ OR e.title ILIKE $$%split-off%$$ OR e.title ILIKE $$%split off%$$)),
w AS (SELECT $$1_pre_days_m4_m1$$ AS win, era, is_sealed, w_pre AS x, y FROM smp WHERE w_pre IS NOT NULL
      UNION ALL SELECT $$2_lasting_days_6_20$$, era, is_sealed, w_d620, y FROM smp WHERE w_d620 IS NOT NULL
      UNION ALL SELECT $$3_placebo_days_21_24$$, era, is_sealed, w_d2124, y FROM smp WHERE w_d2124 IS NOT NULL),
v AS (SELECT win, era, $$all$$ AS part, x, y FROM w
      UNION ALL SELECT win, era, CASE WHEN is_sealed THEN $$sealed$$ ELSE $$non_sealed$$ END, x, y FROM w),
r AS (SELECT win, era, part, SUM(x) / SUM(y) AS rr FROM v GROUP BY 1, 2, 3)
SELECT v.win, v.era, v.part, COUNT(*) AS n, ROUND(r.rr::numeric, 3) AS ratio,
       ROUND((STDDEV(v.x - r.rr * v.y) / (SQRT(COUNT(*)) * AVG(v.y)))::numeric, 3) AS se,
       ROUND(((r.rr - 1) / (STDDEV(v.x - r.rr * v.y) / (SQRT(COUNT(*)) * AVG(v.y))))::numeric, 2) AS z_vs_1
FROM v JOIN r ON r.win = v.win AND r.era = v.era AND r.part = v.part
GROUP BY v.win, v.era, v.part, r.rr ORDER BY 1, 2, 3;
```

Each query returns 18 rows (3 windows x 2 eras x all, non_sealed, sealed). Each run's output is saved verbatim under results/g7_rerun/ with the date in the name.

## Addendum (dated; the predictions above are not edited)

(addenda go here)
