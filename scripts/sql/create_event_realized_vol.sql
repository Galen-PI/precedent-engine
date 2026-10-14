-- Prior-90-day realized volatility per (event, company), built 2026-10-13.
-- Window: 95 calendar days before the event date (strictly before), >= 30 daily returns.
-- Drop with: DROP TABLE event_realized_vol;
CREATE TABLE event_realized_vol AS
WITH pairs AS (
  SELECT DISTINCT eer.event_id, eer.entity_id, s.id AS security_id, e.event_date::date AS d
  FROM event_entity_relationships eer
  JOIN securities s ON s.entity_id = eer.entity_id
  JOIN events e ON e.id = eer.event_id
),
p AS (
  SELECT pr.event_id, pr.entity_id, mp.price_date, mp.adjusted_close
  FROM pairs pr
  JOIN market_prices mp ON mp.security_id = pr.security_id
                       AND mp.price_date >= pr.d - 95 AND mp.price_date < pr.d
),
r AS (
  SELECT event_id, entity_id,
         adjusted_close / LAG(adjusted_close) OVER (PARTITION BY event_id, entity_id ORDER BY price_date) - 1 AS ret
  FROM p
)
SELECT event_id, entity_id, STDDEV(ret) AS rv90, COUNT(ret) AS n_ret
FROM r WHERE ret IS NOT NULL
GROUP BY event_id, entity_id
HAVING COUNT(ret) >= 30 AND STDDEV(ret) > 0;
ALTER TABLE event_realized_vol ADD COLUMN id bigserial PRIMARY KEY;
