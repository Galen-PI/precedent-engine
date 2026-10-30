# PREREG 2026-10-30: are the early-day reactions at filing lags 2 to 4 caused by neighbouring events?   (written BEFORE any outcome was computed)
# Registered by the assistant for Galen Pike on the template results/TEMPLATE_PREREG.md. It is item 2 of the timing thread and follows results/PREREG_g7_reaction_day_profile_2026-10-30.md (result: results/g7_rerun/reaction_day_profile_results_2026-10-30.out). It creates NO flag.
DATA AND USE RULE: the same cleaned sample and the same profile query as the reaction-day profile, restricted to events with a filing lag of 2, 3 or 4 trading days (event_timing), with ONE change: the isolation rule now requires that the company has no other event from 14 calendar days before the filing date to 39 days after (the earlier rule used 5 days before). Reported for all companies, non-sealed and sealed. Day -5 is dropped from the output (it is null for every event). The wider sample is a subset of the earlier one, so a change in a ratio mixes the removal of contaminating neighbours with the change in composition; the earlier ratios are the comparison. The sealed set was part of the profile result, so it is a consistency check and not independent confirmation (confirmation is forward data, January 2027).
ANCHOR: DATA. The profile result for lags 2 to 4 under the earlier isolation: L2 day -1 1.285 (SE 0.060), day 0 1.272; L3 day -2 1.171 (SE 0.046), day -3 1.100; L4 day -4 1.210 (SE 0.062), day -3 1.177 (SE 0.044); the observation that about 49.8 percent of linked events are isolated under the earlier rule and that a further 9 calendar days of look-back should remove roughly 5 to 15 percent of those that remain.
TRIALS: confirmatory=1 descriptive=89 ledger_before=112    (one registered decision, robustness of the early-day reaction; 3 groups by 3 parts by 10 days is 90 ratios, so 89 descriptive looks beside it)
HURDLE: the registered decision uses t>=2 (z of 2 or more) on each condition; this test creates no flag, so the reference hurdle for a newly discovered effect (3.0, ANCHORS.md item 3) does not apply. It can only confirm or weaken a description of when the market reacts to late filings.
DECAY: forward_fraction=1.0 because the test uses the same sample period; a surviving statement is checkable on the January 2027 data.
STANDARD TEST: per day, the ratio of the summed absolute abnormal return to the summed average of days 25 to 39, with the ratio-estimator SE of the earlier runs (naive: events are treated as independent).
PLACEBO: none inside the output; days +3 to +5 of every group act as the quiet reference (they should sit near 1 and did in the profile result, apart from L2 day +4 at 0.900).
FORWARD CHECK: the January 2027 ingestion, re-running the same query.
PREDICTIONS: ranges are 80% intervals (9 numeric rows, about 1.8 expected to miss). Prior: the early-day reactions are real, so the wider isolation shrinks them only modestly (a few hundredths, from the loss of some events and of contamination); the alternative, that neighbouring events of the same company 6 to 14 days earlier produce the bumps, predicts a clear drop, for example L4 day -4 near 1.08 and day -3 near 1.07. The conditions of the decision rule sit 0.06 to 0.09 under the earlier values, about one to one and a half SEs, so they are not lenient.
PRED-TABLE-BEGIN
# id | type | statement | point | lo | hi | level | anchor      (type: ratio, pct, diff or prob; level 80 or 95; anchor DATA <source>, LITERATURE ANCHORS#N, or NONE)
p1 | pct | share of the original lag 2 events kept by the wider isolation (all companies; original n 1,355) | 90 | 84 | 96 | 80 | DATA the reaction-day profile result
p2 | pct | share of the original lag 3 events kept (original n 1,132) | 90 | 84 | 96 | 80 | DATA the reaction-day profile result
p3 | pct | share of the original lag 4 events kept (original n 1,204) | 90 | 84 | 96 | 80 | DATA the reaction-day profile result
p4 | ratio | L4_all, ratio on day -4 (original isolation 1.210) | 1.19 | 1.08 | 1.30 | 80 | DATA the reaction-day profile result
p5 | ratio | L4_all, ratio on day -3 (original 1.177) | 1.16 | 1.07 | 1.26 | 80 | DATA the reaction-day profile result
p6 | ratio | L3_all, ratio on day -2 (original 1.171) | 1.15 | 1.05 | 1.25 | 80 | DATA the reaction-day profile result
p7 | ratio | L3_all, ratio on day -3 (original 1.100) | 1.09 | 1.00 | 1.18 | 80 | DATA the reaction-day profile result
p8 | ratio | L2_all, ratio on day -1 (original 1.285) | 1.27 | 1.14 | 1.40 | 80 | DATA the reaction-day profile result
p9 | ratio | L2_all, ratio on day 0 (original 1.272) | 1.26 | 1.15 | 1.37 | 80 | DATA the reaction-day profile result
p10 | prob | condition a holds: L4_all day -4 ratio of 1.12 or more with t of 2 or more (all companies, wider isolation) | 0.75 |  |  |  | DATA the reaction-day profile result
p11 | prob | condition b holds: L4_all day -3 ratio of 1.12 or more with t of 2 or more | 0.85 |  |  |  | DATA the reaction-day profile result
p12 | prob | condition c holds: L3_all day -2 ratio of 1.10 or more with t of 2 or more | 0.85 |  |  |  | DATA the reaction-day profile result
p13 | prob | condition d holds: L2_all day -1 ratio of 1.20 or more with t of 2 or more | 0.85 |  |  |  | DATA the reaction-day profile result
p14 | prob | the early-day reaction at lags 2 to 4 is ROBUST to the wider isolation by the registered decision rule (at least three of the conditions a to d) | 0.75 |  |  |  | DATA the reaction-day profile result
PRED-TABLE-END
WHAT WOULD CHANGE THE PLAN: DECISION RULE, fixed now (all-companies part, wider isolation). The four conditions: (a) L4_all day -4 at 1.12 or more with t>=2; (b) L4_all day -3 at 1.12 or more with t>=2; (c) L3_all day -2 at 1.10 or more with t>=2; (d) L2_all day -1 at 1.20 or more with t>=2. ROBUST if at least three hold; NOT ROBUST if at most one holds; MIXED if exactly two. If ROBUST: the description of lags 2 to 4 in the profile result (an early reaction on the trading days after the report date, then a second wave with the filing) stands. If NOT ROBUST: the lag 3 and 4 early bumps are at least partly neighbour contamination, and the lag-split result, which used the earlier isolation, gets the same wider-isolation check before its lag 3 and 4 numbers are cited again. If MIXED: recorded as such, with the conditions that failed named. In every case the decision on day 0 (it stays the filing date, DECISION_day0_filing_date_2026-10-30.md) is unaffected, because it rests on lags 0 and 1. SAMPLE CHECK: if any group keeps fewer than 700 events in the all-companies part, investigate before reading any ratio.
LIMITS: the daily data effectively start at day -4; the wider sample is a subset, so composition changes together with contamination; the 14-day look-back is in calendar days and a filing lag of 4 trading days can reach 6 calendar days, so a neighbour inside the 14 days is removed but one 15 or more days earlier is not; the report date is the earliest event reported; absolute abnormal returns show the size of a move and not its sign; the SEs are naive; the sealed set is partly used.
NOT IN THIS NOTE: lags 0 and 1 (their peak days are not in question), lag 5 or more (not visible), and any re-dating of events.

## The query (run in the SQL editor, read-only; 18 rows: 3 groups x 3 parts x 2 statistics, one column per day from -4 to +5)

```sql
WITH ex AS MATERIALIZED (SELECT event_id FROM event_exclusions WHERE severity = $$exclude$$),
per AS (
  SELECT d.event_id, d.entity_id,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 25 AND 39) AS base,
         COUNT(d.adr) FILTER (WHERE d.day_offset BETWEEN 25 AND 39) AS nb,
         AVG(d.adr) FILTER (WHERE d.day_offset = -4) AS d_m4,
         AVG(d.adr) FILTER (WHERE d.day_offset = -3) AS d_m3,
         AVG(d.adr) FILTER (WHERE d.day_offset = -2) AS d_m2,
         AVG(d.adr) FILTER (WHERE d.day_offset = -1) AS d_m1,
         AVG(d.adr) FILTER (WHERE d.day_offset = 0) AS d_0,
         AVG(d.adr) FILTER (WHERE d.day_offset = 1) AS d_p1,
         AVG(d.adr) FILTER (WHERE d.day_offset = 2) AS d_p2,
         AVG(d.adr) FILTER (WHERE d.day_offset = 3) AS d_p3,
         AVG(d.adr) FILTER (WHERE d.day_offset = 4) AS d_p4,
         AVG(d.adr) FILTER (WHERE d.day_offset = 5) AS d_p5,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 0 AND 1) AS w_d01
  FROM event_daily_abn d WHERE NOT EXISTS (SELECT 1 FROM ex WHERE ex.event_id = d.event_id) GROUP BY 1, 2
),
b AS (
  SELECT per.*, e.event_date::date AS d0,
         CASE WHEN e.event_date < $$2004-01-01$$ THEN $$C_pre_2004$$
              WHEN e.event_date < $$2019-01-01$$ THEN $$A_2004_2018$$ ELSE $$B_2019_2026$$ END AS era,
         NOT EXISTS (SELECT 1 FROM event_entity_relationships o JOIN events oe ON oe.id = o.event_id
                     WHERE o.entity_id = per.entity_id AND o.event_id <> per.event_id
                       AND oe.event_date::date BETWEEN e.event_date::date - 14 AND e.event_date::date + 39
                       AND NOT EXISTS (SELECT 1 FROM ex WHERE ex.event_id = o.event_id)) AS isolated
  FROM per JOIN events e ON e.id = per.event_id
  WHERE per.base > 0 AND per.nb >= 10
),
sealed_e AS MATERIALIZED (SELECT s.entity_id FROM securities s JOIN explore_sealed_tickers z ON z.ticker = s.ticker),
et AS (SELECT DISTINCT ON (etr.event_id) etr.event_id, t.name AS etype
            FROM event_type_relationships etr JOIN event_types t ON t.id = etr.event_type_id
            ORDER BY etr.event_id, t.name),
smp AS (SELECT b.base AS y, b.d_m4, b.d_m3, b.d_m2, b.d_m1, b.d_0, b.d_p1, b.d_p2, b.d_p3, b.d_p4, b.d_p5,
               (b.entity_id IN (SELECT entity_id FROM sealed_e)) AS is_sealed,
               $$L$$ || t.td_lag::text || $$_all$$ AS grp
        FROM b JOIN events e ON e.id = b.event_id JOIN et ON et.event_id = b.event_id JOIN event_timing t ON t.event_id = b.event_id
        WHERE b.isolated AND b.w_d01 IS NOT NULL AND b.era <> $$C_pre_2004$$ AND t.td_lag IN (2, 3, 4)
          AND NOT (e.title ILIKE $$%spin%$$ OR e.title ILIKE $$%separation%$$ OR e.title ILIKE $$%split-off%$$ OR e.title ILIKE $$%split off%$$)),
lng AS (SELECT s.grp, s.is_sealed, v.dd, v.x, s.y FROM smp s CROSS JOIN LATERAL (VALUES (-4, s.d_m4), (-3, s.d_m3), (-2, s.d_m2), (-1, s.d_m1), (0, s.d_0), (1, s.d_p1), (2, s.d_p2), (3, s.d_p3), (4, s.d_p4), (5, s.d_p5)) AS v(dd, x) WHERE v.x IS NOT NULL),
v2 AS (SELECT grp, dd, $$all$$ AS part, x, y FROM lng
       UNION ALL SELECT grp, dd, CASE WHEN is_sealed THEN $$sealed$$ ELSE $$non_sealed$$ END, x, y FROM lng),
r AS (SELECT grp, part, dd, SUM(x) / SUM(y) AS rr, COUNT(*) AS n FROM v2 GROUP BY 1, 2, 3),
s AS (SELECT v2.grp, v2.part, v2.dd, r.rr, r.n, STDDEV(v2.x - r.rr * v2.y) / (SQRT(COUNT(*)) * AVG(v2.y)) AS se
      FROM v2 JOIN r ON r.grp = v2.grp AND r.part = v2.part AND r.dd = v2.dd GROUP BY v2.grp, v2.part, v2.dd, r.rr, r.n)
SELECT grp, part, $$1_ratio$$ AS stat, MAX(n) AS n, ROUND(MAX(CASE WHEN dd = -4 THEN rr END)::numeric, 3) AS d_m4, ROUND(MAX(CASE WHEN dd = -3 THEN rr END)::numeric, 3) AS d_m3, ROUND(MAX(CASE WHEN dd = -2 THEN rr END)::numeric, 3) AS d_m2, ROUND(MAX(CASE WHEN dd = -1 THEN rr END)::numeric, 3) AS d_m1, ROUND(MAX(CASE WHEN dd = 0 THEN rr END)::numeric, 3) AS d_0, ROUND(MAX(CASE WHEN dd = 1 THEN rr END)::numeric, 3) AS d_p1, ROUND(MAX(CASE WHEN dd = 2 THEN rr END)::numeric, 3) AS d_p2, ROUND(MAX(CASE WHEN dd = 3 THEN rr END)::numeric, 3) AS d_p3, ROUND(MAX(CASE WHEN dd = 4 THEN rr END)::numeric, 3) AS d_p4, ROUND(MAX(CASE WHEN dd = 5 THEN rr END)::numeric, 3) AS d_p5 FROM s GROUP BY grp, part
UNION ALL
SELECT grp, part, $$2_se$$, MAX(n), ROUND(MAX(CASE WHEN dd = -4 THEN se END)::numeric, 3) AS d_m4, ROUND(MAX(CASE WHEN dd = -3 THEN se END)::numeric, 3) AS d_m3, ROUND(MAX(CASE WHEN dd = -2 THEN se END)::numeric, 3) AS d_m2, ROUND(MAX(CASE WHEN dd = -1 THEN se END)::numeric, 3) AS d_m1, ROUND(MAX(CASE WHEN dd = 0 THEN se END)::numeric, 3) AS d_0, ROUND(MAX(CASE WHEN dd = 1 THEN se END)::numeric, 3) AS d_p1, ROUND(MAX(CASE WHEN dd = 2 THEN se END)::numeric, 3) AS d_p2, ROUND(MAX(CASE WHEN dd = 3 THEN se END)::numeric, 3) AS d_p3, ROUND(MAX(CASE WHEN dd = 4 THEN se END)::numeric, 3) AS d_p4, ROUND(MAX(CASE WHEN dd = 5 THEN se END)::numeric, 3) AS d_p5 FROM s GROUP BY grp, part
ORDER BY 1, 2, 3;

```

Save the output verbatim under results/g7_rerun/ with the date in the name.

## Addendum (dated; the predictions above are not edited)

(addenda go here)
