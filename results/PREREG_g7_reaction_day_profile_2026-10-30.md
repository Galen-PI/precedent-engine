# PREREG 2026-10-30: on which day does the market react, by filing lag and acceptance time?   (written BEFORE any outcome was computed)
# Registered by the assistant for Galen Pike on the template results/TEMPLATE_PREREG.md. It follows results/PREREG_g7_pre_window_lag_split_2026-10-30.md (lag 1 broke its prediction) and the counts of event_timing. It creates NO flag.
DATA AND USE RULE: the cleaned sample of the lag-split registration (ARM 1: isolated events, excluded events removed from the sample and the isolation test, spin-off titles excluded, an event type present, days 0 to 1 present; both eras 2004-2026 pooled) joined to the new table event_timing (one row per event with a source 8-K; report date, trading-day lag, acceptance time in Eastern, loaded 2026-10-30). Groups: L0_pre_open, L0_intraday, L0_after_close (lag 0, not rolled); L1_pre_open, L1_intraday, L1_after_close (lag 1, not rolled), L1_rolled (lag 1, accepted after 17:30 ET, so EDGAR dated the filing the next business day); L2_all, L3_all, L4_all; and ALL_LINKED (every event in the sample, including lag 5 or more and the 10 rolled lag-0 events). The profile of a group is the ratio on each day from -5 to +5 of the summed absolute abnormal return to the summed average of days 25 to 39 of the same events. Reported for all companies, non-sealed and sealed. The peak day of a group is the day with the highest ratio in the all-companies part. The sealed set was part of the lag-split result that raised the question, so it is a consistency check here and not independent confirmation (confirmation is forward data, January 2027).
ANCHOR: DATA. The lag-0 burst of 1.405 and the lag-1 burst of 1.351 (days 0 and 1 averaged, lag-split result), the lag-1 pre-window of 1.015, the lag 2 to 4 pre-windows of 1.102, 1.091 and 1.129, the acceptance-time counts (lag 0: 31 percent before the open, 20 percent during the session, 49 percent after the close; lag 1: 40, 17, 29 percent, 14 percent rolled), and the lag-split model (event-day ratio about 1.5, decay about 0.5 a day, about half of the late filings public only at the filing). The numeric predictions are set so that the group profiles average back to the observed bursts (for example the three lag-0 groups, weighted 31, 20 and 49 percent, give about 1.405).
TRIALS: confirmatory=1 descriptive=362 ledger_before=112    (one registered decision, the reaction-day alignment; 11 groups by 3 parts by 11 days is 363 ratios, so 362 descriptive looks beside it)
HURDLE: the registered decision uses peak days and, for condition iii, t>=2 (z of 2 or more); this test creates no flag, so the reference hurdle for a newly discovered effect (3.0, ANCHORS.md item 3) does not apply. It can only decide whether the acceptance window may be used to place the reaction day, and it cannot promote anything.
DECAY: forward_fraction=1.0 because the test uses the same sample period; a surviving rule is a statement about how events are timed and is checkable on the January 2027 data.
STANDARD TEST: per day, the ratio of sums with the ratio-estimator SE used in the earlier runs (naive: events are treated as independent). A difference between two days of the same group has no SE in the output, because the days share events; peak days are read from the point estimates and are reported together with the gap to the runner-up in units of the day's SE.
PLACEBO: none inside the profile; the days -5 to -2 of the lag 0 groups and the days +3 to +5 of every group act as the quiet reference (they should sit near 1), and ALL_LINKED must reproduce the earlier burst, (day 0 + day +1) / 2 = 1.311 within 0.01.
FORWARD CHECK: the January 2027 ingestion, re-running the same query on the new events.
POWER WARNING (written before the result): earlier I expected the lag 1 window averages to differ by about 0.03 between the acceptance windows, against a standard error of about 0.03 (assistant's estimate); a window-average test on that would be underpowered, which is why this registration uses the day-by-day profile and the position of the peak. Even so, the per-day SE is about 0.04 for the groups of 1,000 to 2,000 events and about 0.1 for L1_rolled and L1_intraday (about 400 to 500 events), so a peak that is only 0.05 above its neighbour is not a finding.
PREDICTIONS: ranges are 80% intervals (13 numeric rows, about 2.6 expected to miss). Priors: news that reaches the market with the filing falls on day 0 when the filing is accepted before the close, and on day +1 when it is accepted after the close; the groups are scaled so that they average back to the observed bursts; the day -k ratios of lags 2 to 4 come from the lag-split model (event-day ratio about 1.5, about half of the late filings public at the report date). The alternative (acceptance time says nothing about the reaction day) predicts the same peak day for every lag-0 group, and no bump at day -k for lags 2 to 4.
PRED-TABLE-BEGIN
# id | type | statement | point | lo | hi | level | anchor      (type: ratio, pct, diff or prob; level 80 or 95; anchor DATA <source>, LITERATURE ANCHORS#N, or NONE)
p1 | ratio | L0_pre_open (filed the day of the event, accepted before 09:30 ET), ratio on day 0 | 1.75 | 1.50 | 2.00 | 80 | DATA event_timing and the lag-split results
p2 | ratio | L0_pre_open, ratio on day -1 | 1.02 | 0.96 | 1.09 | 80 | DATA event_timing and the lag-split results
p3 | ratio | L0_intraday (accepted 09:30 to 16:00 ET), ratio on day 0 | 1.60 | 1.35 | 1.90 | 80 | DATA event_timing and the lag-split results
p4 | ratio | L0_after_close (accepted 16:00 ET or later, not rolled), ratio on day 0 | 1.03 | 0.96 | 1.12 | 80 | DATA event_timing and the lag-split results
p5 | ratio | L0_after_close, ratio on day +1 | 1.75 | 1.50 | 2.05 | 80 | DATA event_timing and the lag-split results
p6 | ratio | L1_rolled (lag 1, accepted after 17:30 ET so EDGAR dated it the next business day), ratio on day 0 | 1.55 | 1.30 | 1.85 | 80 | DATA event_timing and the lag-split results
p7 | ratio | L1_rolled, ratio on day -1 | 1.05 | 0.96 | 1.16 | 80 | DATA event_timing and the lag-split results
p8 | ratio | L1_pre_open (lag 1, accepted before 09:30 ET), ratio on day 0 | 1.65 | 1.40 | 1.95 | 80 | DATA event_timing and the lag-split results
p9 | ratio | L1_pre_open, ratio on day -1 | 1.05 | 0.98 | 1.13 | 80 | DATA event_timing and the lag-split results
p10 | ratio | L1_after_close (lag 1, accepted 16:00 ET or later, not rolled), ratio on day +1 | 1.65 | 1.38 | 1.95 | 80 | DATA event_timing and the lag-split results
p11 | ratio | L2_all (lag 2), ratio on day -2 (the real event day if the news was public at the report date) | 1.26 | 1.12 | 1.40 | 80 | DATA event_timing and the lag-split results
p12 | ratio | L3_all (lag 3), ratio on day -3 | 1.21 | 1.08 | 1.35 | 80 | DATA event_timing and the lag-split results
p13 | ratio | L4_all (lag 4), ratio on day -4 | 1.28 | 1.13 | 1.43 | 80 | DATA event_timing and the lag-split results
p14 | prob | the peak day (highest ratio over days -5 to +5, all-companies part) of L0_after_close is day +1 | 0.90 |  |  |  | DATA event_timing and the lag-split results
p15 | prob | the peak day of L0_pre_open is day 0 | 0.90 |  |  |  | DATA event_timing and the lag-split results
p16 | prob | the peak day of L0_intraday is day 0 (late-session filings may peak on day +1) | 0.65 |  |  |  | DATA event_timing and the lag-split results
p17 | prob | the peak day of L1_rolled is day 0 | 0.85 |  |  |  | DATA event_timing and the lag-split results
p18 | prob | the peak day of L1_pre_open is day 0 | 0.80 |  |  |  | DATA event_timing and the lag-split results
p19 | prob | the peak day of L1_after_close is day +1 | 0.60 |  |  |  | DATA event_timing and the lag-split results
p20 | prob | at least two of L2_all day -2, L3_all day -3 and L4_all day -4 have a ratio of 1.10 or more with z of 2 or more (all-companies part) | 0.75 |  |  |  | DATA event_timing and the lag-split results
p21 | prob | ALL_LINKED (day 0 ratio plus day +1 ratio) / 2 is within 0.01 of the earlier burst 1.311 (an identity check of the join, not a hypothesis) | 0.95 |  |  |  | DATA event_timing and the lag-split results
p22 | prob | reaction-day alignment is CONFIRMED by the registered decision rule (conditions i, ii and iii in WHAT WOULD CHANGE THE PLAN) | 0.55 |  |  |  | DATA event_timing and the lag-split results
PRED-TABLE-END
WHAT WOULD CHANGE THE PLAN: DECISION RULE, fixed now (all-companies part). Reaction-day alignment is CONFIRMED if (i) the peak day of L0_after_close is day +1 AND the peak day of L0_pre_open is day 0, AND (ii) the peak day of L1_rolled is day 0 AND the peak day of L1_pre_open is day 0, AND (iii) at least two of L2_all on day -2, L3_all on day -3 and L4_all on day -4 have a ratio of 1.10 or more with z of 2 or more. It is NOT CONFIRMED if the peak day of L0_after_close is not +1 (then the acceptance window carries no information about the reaction day and no time-based correction is made). Anything else is PARTIAL and recorded as such. If CONFIRMED: the next registration (item 2, the burst at the true event day) may use the acceptance window as a time-only rule, reaction day = filing day for filings accepted before 16:00 ET and the next trading day for later ones, and the report date for the late filings of lags 2 to 4. If NOT CONFIRMED or PARTIAL: day 0 stays the filing date, and the lag-split findings stand as a description of where the news sits relative to the filing. SAMPLE CHECK: if any L0 or L1 group has fewer than 250 events in the all-companies part, or ALL_LINKED misses 1.311 by more than 0.02, investigate before reading any ratio.
LIMITS: the daily data starts at day -5, so the lag 4 bump at day -4 is the earliest event day that can be seen and the event days of lag 5 or more are not visible; the isolation rule (no other event of the company from 5 days before to 39 days after the filing date, in calendar days) leaves the days -5 to -4 of lag 3 and lag 4 events exposed to a neighbouring event 6 or more days earlier; the report date is the earliest event reported, not necessarily the day the market learned of it; the profile uses absolute abnormal returns, so it shows the size of the move and not its sign; the SEs are naive; the sealed set is partly used; the acceptance window is only a proxy for when the news reached the market, since a company can announce earlier in the day than it files.
NOT IN THIS NOTE: the burst at the true event day by aligned lag (item 2); the decision on a re-dated day 0 (item 3); the sign of the moves.

## The query (run in the SQL editor, read-only; 66 rows: 11 groups x 3 parts x 2 statistics, with one column per day from -5 to +5)

```sql
WITH ex AS MATERIALIZED (SELECT event_id FROM event_exclusions WHERE severity = $$exclude$$),
per AS (
  SELECT d.event_id, d.entity_id,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 25 AND 39) AS base,
         COUNT(d.adr) FILTER (WHERE d.day_offset BETWEEN 25 AND 39) AS nb,
         AVG(d.adr) FILTER (WHERE d.day_offset = -5) AS d_m5,
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
                       AND oe.event_date::date BETWEEN e.event_date::date - 5 AND e.event_date::date + 39
                       AND NOT EXISTS (SELECT 1 FROM ex WHERE ex.event_id = o.event_id)) AS isolated
  FROM per JOIN events e ON e.id = per.event_id
  WHERE per.base > 0 AND per.nb >= 10
),
sealed_e AS MATERIALIZED (SELECT s.entity_id FROM securities s JOIN explore_sealed_tickers z ON z.ticker = s.ticker),
et AS (SELECT DISTINCT ON (etr.event_id) etr.event_id, t.name AS etype
            FROM event_type_relationships etr JOIN event_types t ON t.id = etr.event_type_id
            ORDER BY etr.event_id, t.name),
smp AS (SELECT b.base AS y, b.d_m5, b.d_m4, b.d_m3, b.d_m2, b.d_m1, b.d_0, b.d_p1, b.d_p2, b.d_p3, b.d_p4, b.d_p5,
               (b.entity_id IN (SELECT entity_id FROM sealed_e)) AS is_sealed,
               CASE WHEN t.td_lag = 0 AND NOT ((t.acceptance_datetime AT TIME ZONE $$America/New_York$$)::date < t.filing_date) THEN $$L0_$$ || t.accepted_bucket
                    WHEN t.td_lag = 1 AND ((t.acceptance_datetime AT TIME ZONE $$America/New_York$$)::date < t.filing_date) THEN $$L1_rolled$$
                    WHEN t.td_lag = 1 THEN $$L1_$$ || t.accepted_bucket
                    WHEN t.td_lag IN (2, 3, 4) THEN $$L$$ || t.td_lag::text || $$_all$$ END AS grp
        FROM b JOIN events e ON e.id = b.event_id JOIN et ON et.event_id = b.event_id JOIN event_timing t ON t.event_id = b.event_id
        WHERE b.isolated AND b.w_d01 IS NOT NULL AND b.era <> $$C_pre_2004$$
          AND NOT (e.title ILIKE $$%spin%$$ OR e.title ILIKE $$%separation%$$ OR e.title ILIKE $$%split-off%$$ OR e.title ILIKE $$%split off%$$)),
lng AS (SELECT s.grp, s.is_sealed, v.dd, v.x, s.y FROM smp s CROSS JOIN LATERAL (VALUES (-5, s.d_m5), (-4, s.d_m4), (-3, s.d_m3), (-2, s.d_m2), (-1, s.d_m1), (0, s.d_0), (1, s.d_p1), (2, s.d_p2), (3, s.d_p3), (4, s.d_p4), (5, s.d_p5)) AS v(dd, x) WHERE v.x IS NOT NULL),
lng2 AS (SELECT grp, is_sealed, dd, x, y FROM lng WHERE grp IS NOT NULL UNION ALL SELECT $$ALL_LINKED$$, is_sealed, dd, x, y FROM lng),
v2 AS (SELECT grp, dd, $$all$$ AS part, x, y FROM lng2
       UNION ALL SELECT grp, dd, CASE WHEN is_sealed THEN $$sealed$$ ELSE $$non_sealed$$ END, x, y FROM lng2),
r AS (SELECT grp, part, dd, SUM(x) / SUM(y) AS rr, COUNT(*) AS n FROM v2 GROUP BY 1, 2, 3),
s AS (SELECT v2.grp, v2.part, v2.dd, r.rr, r.n, STDDEV(v2.x - r.rr * v2.y) / (SQRT(COUNT(*)) * AVG(v2.y)) AS se
      FROM v2 JOIN r ON r.grp = v2.grp AND r.part = v2.part AND r.dd = v2.dd GROUP BY v2.grp, v2.part, v2.dd, r.rr, r.n)
SELECT grp, part, $$1_ratio$$ AS stat, MAX(n) AS n, ROUND(MAX(CASE WHEN dd = -5 THEN rr END)::numeric, 3) AS d_m5, ROUND(MAX(CASE WHEN dd = -4 THEN rr END)::numeric, 3) AS d_m4, ROUND(MAX(CASE WHEN dd = -3 THEN rr END)::numeric, 3) AS d_m3, ROUND(MAX(CASE WHEN dd = -2 THEN rr END)::numeric, 3) AS d_m2, ROUND(MAX(CASE WHEN dd = -1 THEN rr END)::numeric, 3) AS d_m1, ROUND(MAX(CASE WHEN dd = 0 THEN rr END)::numeric, 3) AS d_0, ROUND(MAX(CASE WHEN dd = 1 THEN rr END)::numeric, 3) AS d_p1, ROUND(MAX(CASE WHEN dd = 2 THEN rr END)::numeric, 3) AS d_p2, ROUND(MAX(CASE WHEN dd = 3 THEN rr END)::numeric, 3) AS d_p3, ROUND(MAX(CASE WHEN dd = 4 THEN rr END)::numeric, 3) AS d_p4, ROUND(MAX(CASE WHEN dd = 5 THEN rr END)::numeric, 3) AS d_p5 FROM s GROUP BY grp, part
UNION ALL
SELECT grp, part, $$2_se$$, MAX(n), ROUND(MAX(CASE WHEN dd = -5 THEN se END)::numeric, 3) AS d_m5, ROUND(MAX(CASE WHEN dd = -4 THEN se END)::numeric, 3) AS d_m4, ROUND(MAX(CASE WHEN dd = -3 THEN se END)::numeric, 3) AS d_m3, ROUND(MAX(CASE WHEN dd = -2 THEN se END)::numeric, 3) AS d_m2, ROUND(MAX(CASE WHEN dd = -1 THEN se END)::numeric, 3) AS d_m1, ROUND(MAX(CASE WHEN dd = 0 THEN se END)::numeric, 3) AS d_0, ROUND(MAX(CASE WHEN dd = 1 THEN se END)::numeric, 3) AS d_p1, ROUND(MAX(CASE WHEN dd = 2 THEN se END)::numeric, 3) AS d_p2, ROUND(MAX(CASE WHEN dd = 3 THEN se END)::numeric, 3) AS d_p3, ROUND(MAX(CASE WHEN dd = 4 THEN se END)::numeric, 3) AS d_p4, ROUND(MAX(CASE WHEN dd = 5 THEN se END)::numeric, 3) AS d_p5 FROM s GROUP BY grp, part
ORDER BY 1, 2, 3;
```

Save the output verbatim under results/g7_rerun/ with the date in the name.

## Addendum (dated; the predictions above are not edited)

(addenda go here)
