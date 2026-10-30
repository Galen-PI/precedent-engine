-- G7 event_premium_20d, ARM 1 (Addendum 10 of results/PREREG_g7_proven_rerun_2026-10-29.md), written 2026-10-30 before any run.
-- The function ratio_period(lo, hi), live definition read from the database on 2026-10-30 (identical to the 2026-10-16 text), copied clause for clause with these changes only: the target is the new empty table events_ratio_g7_arm1 (in the INSERT and in the NOT EXISTS clause), and events that have an exclude row in event_exclusions are left out (one added clause).
-- Run as three calls, like the original session: SELECT ratio_period_g7_arm1($$2004-01-01$$::date, $$2011-01-01$$::date); then ($$2011-01-01$$::date, $$2019-01-01$$::date); then ($$2019-01-01$$::date, $$2026-10-01$$::date).
CREATE TABLE events_ratio_g7_arm1 (LIKE events_ratio);
CREATE OR REPLACE FUNCTION ratio_period_g7_arm1(lo date, hi date) RETURNS bigint LANGUAGE plpgsql AS $fn$
DECLARE n bigint;
BEGIN
  INSERT INTO events_ratio_g7_arm1
  WITH et AS (SELECT DISTINCT ON (etr.event_id) etr.event_id, t.name AS etype
              FROM event_type_relationships etr JOIN event_types t ON t.id = etr.event_type_id
              ORDER BY etr.event_id, t.name),
  src AS (
    SELECT event_id, ticker, abnormal_return_20d FROM event_market_reactions_corrected
    UNION ALL
    SELECT event_id, ticker, abnormal_return_20d FROM reactions_view_only
  )
  SELECT erv.event_id, src.ticker,
         CASE WHEN et.etype = $$capital_raise$$ THEN $$b_capital_raise$$
              WHEN et.etype = $$corporate_action$$ THEN $$c_corporate_action$$
              ELSE $$a_all_other_types$$ END,
         date_trunc($$month$$, e.event_date)::date,
         ABS(src.abnormal_return_20d) / (erv.rv90 * SQRT(20.0)),
         l.ratio
  FROM event_realized_vol erv
  JOIN events e ON e.id = erv.event_id
  JOIN securities s ON s.entity_id = erv.entity_id
  JOIN src ON src.event_id = erv.event_id AND src.ticker = s.ticker
  JOIN et ON et.event_id = erv.event_id
  CROSS JOIN LATERAL (
    SELECT x.v64 / x.v250 AS ratio FROM vol_estimators x
    WHERE x.security_id = s.id AND x.d < e.event_date::date AND x.v250 > 0
    ORDER BY x.d DESC LIMIT 1) l
  WHERE src.abnormal_return_20d IS NOT NULL
    AND e.event_date >= lo AND e.event_date < hi
    AND erv.event_id NOT IN (SELECT event_id FROM event_component_dates)
    AND NOT (e.title ILIKE $$%spin%$$ OR e.title ILIKE $$%separation%$$ OR e.title ILIKE $$%split-off%$$ OR e.title ILIKE $$%split off%$$)
    AND NOT EXISTS (SELECT 1 FROM event_exclusions xe WHERE xe.event_id = erv.event_id AND xe.severity = $$exclude$$)
    AND NOT EXISTS (SELECT 1 FROM events_ratio_g7_arm1 x WHERE x.event_id = erv.event_id AND x.ticker = src.ticker);
  GET DIAGNOSTICS n = ROW_COUNT;
  RETURN n;
END
$fn$;
