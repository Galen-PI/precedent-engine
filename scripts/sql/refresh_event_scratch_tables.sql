-- Refresh the Phase 6 scratch tables for events promoted on 2026-10-15, then compare the new cohort.
-- Run sections in order, ONE statement at a time in the Supabase SQL editor. Every statement skips rows that
-- are already loaded, so re-running a statement is safe. Run section 4 only AFTER promotion has finished
-- and no promote_events process is running (it freezes the cohort of today's events).

-- 1. event_realized_vol for events (2019+) that have no row yet (same definition as create_event_realized_vol.sql)
INSERT INTO event_realized_vol (event_id, entity_id, rv90, n_ret)
WITH pairs AS (
  SELECT DISTINCT eer.event_id, eer.entity_id, s.id AS security_id, e.event_date::date AS d
  FROM event_entity_relationships eer
  JOIN securities s ON s.entity_id = eer.entity_id
  JOIN events e ON e.id = eer.event_id
  WHERE e.event_date >= '2019-01-01'
    AND NOT EXISTS (SELECT 1 FROM event_realized_vol v WHERE v.event_id = eer.event_id AND v.entity_id = eer.entity_id)
),
p AS (
  SELECT pr.event_id, pr.entity_id, mp.price_date, mp.adjusted_close
  FROM pairs pr
  JOIN market_prices mp ON mp.security_id = pr.security_id AND mp.price_date >= pr.d - 95 AND mp.price_date < pr.d
),
r AS (
  SELECT event_id, entity_id,
         adjusted_close / LAG(adjusted_close) OVER (PARTITION BY event_id, entity_id ORDER BY price_date) - 1 AS ret
  FROM p
)
SELECT event_id, entity_id, STDDEV(ret), COUNT(ret)
FROM r WHERE ret IS NOT NULL
GROUP BY event_id, entity_id
HAVING COUNT(ret) >= 30 AND STDDEV(ret) > 0;

-- 2. reactions_view_only: one statement per year (the view times out on a larger range); change the two dates
INSERT INTO reactions_view_only
SELECT v.event_id, v.ticker, v.event_date::date, v.abnormal_return_20d::double precision
FROM event_market_reactions v
WHERE v.event_date >= '2019-01-01' AND v.event_date < '2020-01-01' AND v.abnormal_return_20d IS NOT NULL
  AND v.event_id NOT IN (SELECT event_id FROM event_market_reactions_corrected)
  AND NOT EXISTS (SELECT 1 FROM reactions_view_only x WHERE x.event_id = v.event_id AND x.ticker = v.ticker);
-- ...repeat for 2020, 2021, 2022, 2023, 2024, 2025, and 2026 (end date '2026-08-01')

-- 3. events_ratio rows for events not loaded yet (needs sections 1 and 2 first)
INSERT INTO events_ratio
WITH et AS (SELECT DISTINCT ON (etr.event_id) etr.event_id, t.name AS etype
            FROM event_type_relationships etr JOIN event_types t ON t.id = etr.event_type_id
            ORDER BY etr.event_id, t.name),
src AS (
  SELECT event_id, ticker, abnormal_return_20d FROM event_market_reactions_corrected
  UNION ALL
  SELECT event_id, ticker, abnormal_return_20d FROM reactions_view_only
)
SELECT erv.event_id, src.ticker,
       CASE WHEN et.etype = 'capital_raise' THEN 'b_capital_raise'
            WHEN et.etype = 'corporate_action' THEN 'c_corporate_action'
            ELSE 'a_all_other_types' END,
       date_trunc('month', e.event_date)::date,
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
  AND e.event_date >= '2019-01-01' AND e.event_date < '2026-08-01'
  AND erv.event_id NOT IN (SELECT event_id FROM event_component_dates)
  AND NOT (e.title ILIKE '%spin%' OR e.title ILIKE '%separation%' OR e.title ILIKE '%split-off%' OR e.title ILIKE '%split off%')
  AND NOT (src.ticker = 'HON' AND e.event_date >= '2026-06-01')
  AND NOT EXISTS (SELECT 1 FROM events_ratio x WHERE x.event_id = erv.event_id AND x.ticker = src.ticker);

-- 4. freeze today's cohort (expect about 2,106 rows) -- only after promotion has finished
CREATE TABLE IF NOT EXISTS new_events_20261015 AS
SELECT id FROM events ORDER BY age(xmin) ASC LIMIT (SELECT COUNT(*) - 19892 FROM events);

-- 5. comparison: new cohort vs earlier events, same month x volatility-ratio matched baseline
WITH base_m AS (SELECT m, SUM(mm_matched * mm_n) / SUM(mm_n) AS mm_month FROM mm_matched GROUP BY m),
e2 AS (SELECT er.bucket, er.m, er.scaled,
              CASE WHEN er.ratio < 0.775 THEN 1 WHEN er.ratio < 0.950 THEN 2 WHEN er.ratio < 1.162 THEN 3 ELSE 4 END AS b,
              (er.event_id IN (SELECT id FROM new_events_20261015)) AS is_new
       FROM events_ratio er)
SELECT e2.is_new, e2.bucket, COUNT(*) AS n,
       AVG(e2.scaled - mm.mm_matched) AS excess_matched,
       STDDEV(e2.scaled - mm.mm_matched) / SQRT(COUNT(*)) AS se
FROM e2 JOIN base_m ON base_m.m = e2.m JOIN mm_matched mm ON mm.m = e2.m AND mm.b = e2.b
GROUP BY 1, 2 ORDER BY 1, 2;
-- Pre-set rule (ordinary types, new cohort): consistent if excess +/- 2 SE contains +0.0295; failing if the upper end is < +0.02.
-- Caveat: promoted events are milder (no capital_raise/corporate_action/governance); a smaller premium is partly selection.
