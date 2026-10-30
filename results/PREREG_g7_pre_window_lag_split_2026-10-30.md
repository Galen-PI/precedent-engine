# PREREG 2026-10-30: does the 8-K filing lag explain the pre-event rise (event_pre_days_m4_m1)?   (written BEFORE any outcome was computed)
# Registered by the assistant for Galen Pike on the template results/TEMPLATE_PREREG.md. It follows results/PREREG_g7_tier1_window_nulls_2026-10-30.md, whose candidate (the pre-window ratio meeting its rule) it tries to explain. It creates NO flag.
DATA AND USE RULE: the cleaned sample of the Tier 1 registration (ARM 1: isolated events, excluded events removed from the sample and the isolation test, spin-off titles excluded, an event type present, days 0 to 1 present; both eras 2004-2026 pooled), joined to each event's source filing in the new table sec_8k_report_dates (the SEC feed's reportDate and acceptanceDateTime, loaded 2026-10-30). The lag is counted in TRADING days on the SPY calendar: the trading days after the report date up to and including the filing date. Events without a source filing or report date (about 5 percent) are left out. All companies, with non-sealed and sealed reported separately; the sealed set has never been looked at in this split, so it is a fresh test of the claim made here (not of the pre-window pattern itself, which it was part of).
ANCHOR: DATA. The measured lag distribution of 155,969 8-Ks (55.0 percent same day) and of our events (39.7 percent same trading day; 25.3, 11.1, 9.2, 9.9 and 4.8 percent at lags 1, 2, 3, 4 and 5 or more), the overall pooled ratios of the cleaned sample (burst 1.31, pre-window 1.050), and a small model fitted to those pooled numbers (below).
TRIALS: confirmatory=1 descriptive=62 ledger_before=112    (one registered decision, the lag explanation; 62 descriptive looks: seven buckets by three windows by three parts, 63 cells, less the decision)
HURDLE: the registered decision uses t>=2 (z above 2) on the same-day filings and on the difference between late and same-day filings; this test creates no flag, so the reference hurdle for a newly discovered effect (3.0, ANCHORS.md item 3) does not apply. It can only explain, weaken or leave open the Tier 1 candidate; it cannot promote anything.
DECAY: forward_fraction=1.0 because the test uses the same sample period; a claim that survives is a statement about how events are dated and is checkable on the January 2027 data.
STANDARD TEST: ratio of sums per cell, SUM(window mean) / SUM(days 25 to 39 mean), with the ratio-estimator SE used in the earlier runs (naive: events are treated as independent). The difference between two buckets has SE equal to the square root of the sum of the two squared SEs.
PLACEBO: days 21 to 24 over days 25 to 39 in every bucket (it should be near 1 everywhere); and the pooled row, which must reproduce the overall 1.050 and 1.31 within the sampling error of the five percent of events dropped.
FORWARD CHECK: the January 2027 ingestion (the new report-date script covers new filings with one request per company), re-running the same query.
PREDICTIONS: ranges are 80% intervals (11 numeric rows, about 2.2 expected to miss). They are the consequences of the lag explanation under a small model, not free guesses: the event day has an elevation that decays by a factor of 0.3 to 0.7 a day, and a share phi of about 0.5 of the late filings had their news become public only at the filing itself (the report date is the EARLIEST event reported, not necessarily the day the market learned it); the elevation (ratio about 1.4 to 1.6 on the event day) and phi were fitted to the pooled burst and pre-window numbers, so the pooled rows match by construction and the test is the SPLIT by lag, which the fit never saw. Under the model the pre-window is about 1.00 for same-day filings and rises to about 1.06 (lag 1), 1.09, 1.11 and 1.12 (lag 4), and falls back near 1.03 at lag 5 or more; the burst at the filing date is about 1.38 for same-day filings and 1.2 to 1.3 for late ones. The alternative (the rise is anticipation or leakage, independent of the filing lag) predicts about 1.05 in every bucket including lag 0 and equal bursts.
PRED-TABLE-BEGIN
# id | type | statement | point | lo | hi | level | anchor      (type: ratio, pct, diff or prob; level 80 or 95; anchor DATA <source>, LITERATURE ANCHORS#N, or NONE)
p1 | ratio | pre-window (days -4 to -1 over days 25 to 39), events filed on the SAME trading day as the event (lag 0), all companies, both eras, cleaned sample | 1.005 | 0.980 | 1.030 | 80 | DATA sec_8k_report_dates and the Arm 1 by-type sample
p2 | ratio | pre-window, lag 1 trading day | 1.065 | 1.032 | 1.098 | 80 | DATA sec_8k_report_dates and the Arm 1 by-type sample
p3 | ratio | pre-window, lag 2 trading days | 1.093 | 1.051 | 1.135 | 80 | DATA sec_8k_report_dates and the Arm 1 by-type sample
p4 | ratio | pre-window, lag 3 trading days | 1.108 | 1.064 | 1.152 | 80 | DATA sec_8k_report_dates and the Arm 1 by-type sample
p5 | ratio | pre-window, lag 4 trading days | 1.118 | 1.075 | 1.161 | 80 | DATA sec_8k_report_dates and the Arm 1 by-type sample
p6 | ratio | pre-window, lag 5 or more trading days (the true event day lies outside the window) | 1.030 | 0.966 | 1.094 | 80 | DATA sec_8k_report_dates and the Arm 1 by-type sample
p7 | ratio | burst (days 0 to 1 over days 25 to 39) at the filing date, lag 0 | 1.38 | 1.31 | 1.45 | 80 | DATA sec_8k_report_dates and the Arm 1 by-type sample
p8 | ratio | burst at the filing date, lag 1 | 1.295 | 1.230 | 1.360 | 80 | DATA sec_8k_report_dates and the Arm 1 by-type sample
p9 | ratio | burst at the filing date, lag 4 | 1.22 | 1.15 | 1.29 | 80 | DATA sec_8k_report_dates and the Arm 1 by-type sample
p10 | ratio | pre-window, all linked events pooled (a consistency check against the overall 1.050) | 1.050 | 1.035 | 1.065 | 80 | DATA sec_8k_report_dates and the Arm 1 by-type sample
p11 | ratio | burst, all linked events pooled (a consistency check against the overall 1.31) | 1.31 | 1.28 | 1.34 | 80 | DATA sec_8k_report_dates and the Arm 1 by-type sample
p12 | prob | lag 0 pre-window ratio has t below 2 against 1 (same-day filings show no significant pre-event rise) | 0.65 |  |  |  | DATA sec_8k_report_dates and the Arm 1 by-type sample
p13 | prob | the lag 1 to 4 pre-window ratios exceed the lag 0 ratio by 0.04 or more in every one of the four buckets | 0.60 |  |  |  | DATA sec_8k_report_dates and the Arm 1 by-type sample
p14 | prob | the lag explanation is SUPPORTED by the registered decision rule (conditions a, b and c in WHAT WOULD CHANGE THE PLAN) | 0.50 |  |  |  | DATA sec_8k_report_dates and the Arm 1 by-type sample
p15 | prob | the lag explanation is NOT supported (lag 0 pre-window ratio of 1.04 or more with t of 2 or more) | 0.15 |  |  |  | DATA sec_8k_report_dates and the Arm 1 by-type sample
p16 | prob | the burst at the filing date is higher for lag 0 than for lag 1 and for lag 4 | 0.75 |  |  |  | DATA sec_8k_report_dates and the Arm 1 by-type sample
p17 | prob | the pre-window ordering lag 4 at least lag 1 at least lag 0 holds | 0.65 |  |  |  | DATA sec_8k_report_dates and the Arm 1 by-type sample
PRED-TABLE-END
WHAT WOULD CHANGE THE PLAN: DECISION RULE, fixed now. The lag explanation is SUPPORTED if (a) the lag 0 pre-window ratio has t below 2 against 1, AND (b) the pooled lag 1 to 4 pre-window ratio exceeds the lag 0 ratio by at least 0.04 with the difference's t of at least 2, AND (c) lag 1 to 4 is above lag 0 in both the non-sealed and the sealed sets. It is NOT SUPPORTED if the lag 0 pre-window ratio is 1.04 or more with t of 2 or more (the rise exists where the filing and the event coincide). Anything else is MIXED and is recorded as such. If SUPPORTED: the ledger note for event_pre_days_m4_m1 records 'explained by the 8-K filing lag'; the Tier 1 candidate stays null; the January forward check for it is dropped, and the dating of events becomes the next item (the burst multipliers and every window are measured from the filing date). If NOT SUPPORTED: the candidate stands and the January forward check goes ahead. SAMPLE CHECK: if the linked sample has fewer than 9,000 events or lag 0 fewer than 3,000, investigate before reading any ratio.
LIMITS: the daily data starts at day -5, so a window re-centered on the true event day exists only for lags up to 1 and the event day itself is visible only for lags up to 5; the report date is the earliest event reported, not necessarily the day the market learned of it; the model's phi and decay are fitted, not measured, and after-close acceptance times (which move the reaction to the next trading day) are not modelled; the SEs are naive; the trading-day lag counts the SPY calendar; two-security entities are collapsed to the earliest report date; the pre-window ratio of lag 5 or more mixes aftermath days and is the weakest cell.
NOT IN THIS NOTE: re-dating all events to the true event day and re-measuring the burst (it needs data before day -5 or the report date as the new day 0 with its own windows); the acceptance-time effect on days 0 to 1; the other nulls.

## The query (run in the SQL editor, read-only; 63 rows: 7 buckets x 3 windows x 3 parts)

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
lag AS MATERIALIZED (SELECT DISTINCT ON (esf.event_id) esf.event_id,
            (SELECT COUNT(*) FROM spy_cal c WHERE c.d > r.report_date AND c.d <= r.filing_date) AS td_lag
            FROM event_source_filings esf JOIN securities s ON s.ticker = esf.ticker
            JOIN sec_8k_report_dates r ON r.security_id = s.id AND r.accession_number = esf.accession_number
            WHERE r.report_date IS NOT NULL ORDER BY esf.event_id, r.report_date),
smp AS (SELECT b.w_pre, b.w_d01, b.w_d2124, b.base AS y, (b.entity_id IN (SELECT entity_id FROM sealed_e)) AS is_sealed,
               CASE WHEN l.td_lag <= 0 THEN $$1_lag_0$$ WHEN l.td_lag = 1 THEN $$2_lag_1$$ WHEN l.td_lag = 2 THEN $$3_lag_2$$
                    WHEN l.td_lag = 3 THEN $$4_lag_3$$ WHEN l.td_lag = 4 THEN $$5_lag_4$$ ELSE $$6_lag_5_plus$$ END AS bucket
        FROM b JOIN events e ON e.id = b.event_id JOIN et ON et.event_id = b.event_id JOIN lag l ON l.event_id = b.event_id
        WHERE b.isolated AND b.w_d01 IS NOT NULL AND b.era <> $$C_pre_2004$$
          AND NOT (e.title ILIKE $$%spin%$$ OR e.title ILIKE $$%separation%$$ OR e.title ILIKE $$%split-off%$$ OR e.title ILIKE $$%split off%$$)),
w AS (SELECT bucket, $$1_pre_days_m4_m1$$ AS win, is_sealed, w_pre AS x, y FROM smp WHERE w_pre IS NOT NULL
      UNION ALL SELECT bucket, $$2_burst_days_0_1$$, is_sealed, w_d01, y FROM smp WHERE w_d01 IS NOT NULL
      UNION ALL SELECT bucket, $$3_placebo_days_21_24$$, is_sealed, w_d2124, y FROM smp WHERE w_d2124 IS NOT NULL),
w2 AS (SELECT bucket, win, is_sealed, x, y FROM w UNION ALL SELECT $$7_all_linked$$, win, is_sealed, x, y FROM w),
v AS (SELECT bucket, win, $$all$$ AS part, x, y FROM w2
      UNION ALL SELECT bucket, win, CASE WHEN is_sealed THEN $$sealed$$ ELSE $$non_sealed$$ END, x, y FROM w2),
r AS (SELECT bucket, win, part, SUM(x) / SUM(y) AS rr FROM v GROUP BY 1, 2, 3)
SELECT v.bucket, v.win, v.part, COUNT(*) AS n, ROUND(r.rr::numeric, 3) AS ratio,
       ROUND((STDDEV(v.x - r.rr * v.y) / (SQRT(COUNT(*)) * AVG(v.y)))::numeric, 3) AS se,
       ROUND(((r.rr - 1) / (STDDEV(v.x - r.rr * v.y) / (SQRT(COUNT(*)) * AVG(v.y))))::numeric, 2) AS z_vs_1
FROM v JOIN r ON r.bucket = v.bucket AND r.win = v.win AND r.part = v.part
GROUP BY v.bucket, v.win, v.part, r.rr ORDER BY 1, 2, 3;
```

Save the output verbatim under results/g7_rerun/ with the date in the name.

## Addendum (dated; the predictions above are not edited)

(addenda go here)
