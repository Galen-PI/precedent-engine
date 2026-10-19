-- event_market_reactions_v2 (2026-10-19). Replaces the logic of the old event_market_reactions view.
-- WHY: the old live branch used price_date < event_date for the prior close and price_date > event_date for the reaction day (the event date's
-- own session was skipped, so return_0d spanned two sessions), measured 1d/5d/20d from the reaction-day close instead of the prior close, had no
-- limit on how far after the event the first price could be, joined event_market_reactions_corrected on event_id alone (stamping one ticker's
-- numbers onto every ticker of a multi-ticker event: 114 rows), and fanned out on duplicate relationship links (3 rows).
-- RULE NOW: reaction day = first session on or after the event day within 7 days; prior = the session before it; every horizon is cumulative from
-- that prior close; the corrected table supplies only corrected EVENT DATES; time zone pinned to UTC; one row per event and ticker.
-- VALIDATED: on 15,812 single-ticker events the reaction day and prior day matched event_market_reactions_corrected in 100% of rows and the
-- 0d/1d returns in 100% (5d 99.97%, 20d 99.94%, abnormal 1d 99.9%, abnormal 20d 98.8%).
CREATE OR REPLACE VIEW event_market_reactions_v2 AS
WITH event_entities AS (
    SELECT DISTINCT ON (ev.id, s.id)
           ev.id AS event_id,
           ev.title,
           COALESCE(CASE WHEN c.date_was_corrected THEN c.event_date END,
                    (ev.event_date::timestamptz AT TIME ZONE $$UTC$$)::date) AS event_day,
           COALESCE(c.date_was_corrected, false) AS date_was_corrected,
           s.id AS security_id,
           s.ticker
      FROM events ev
      JOIN event_entity_relationships eer ON eer.event_id = ev.id
      JOIN securities s ON s.entity_id = eer.entity_id
      LEFT JOIN event_market_reactions_corrected c ON c.event_id = ev.id
     WHERE eer.relationship_type <> $$actor$$
     ORDER BY ev.id, s.id
), live AS (
    SELECT ee.event_id, ee.title, ee.ticker, ee.event_day, ee.date_was_corrected,
           r.price_date AS event_price_date, r.close AS event_close,
           p.price_date AS prior_price_date, p.close AS prior_close,
           d1.price_date AS d1_date, d1.close AS day_1_close,
           d5.price_date AS d5_date, d5.close AS day_5_close,
           d20.price_date AS d20_date, d20.close AS day_20_close
      FROM event_entities ee
      LEFT JOIN LATERAL (
           SELECT mp.price_date, mp.close FROM market_prices mp
            WHERE mp.security_id = ee.security_id
              AND mp.price_date >= ee.event_day AND mp.price_date <= ee.event_day + 7
            ORDER BY mp.price_date LIMIT 1) r ON true
      LEFT JOIN LATERAL (
           SELECT mp.price_date, mp.close FROM market_prices mp
            WHERE mp.security_id = ee.security_id AND mp.price_date < r.price_date
            ORDER BY mp.price_date DESC LIMIT 1) p ON true
      LEFT JOIN LATERAL (
           SELECT mp.price_date, mp.close FROM market_prices mp
            WHERE mp.security_id = ee.security_id AND mp.price_date > r.price_date
            ORDER BY mp.price_date LIMIT 1) d1 ON true
      LEFT JOIN LATERAL (
           SELECT mp.price_date, mp.close FROM market_prices mp
            WHERE mp.security_id = ee.security_id AND mp.price_date > r.price_date
            ORDER BY mp.price_date OFFSET 4 LIMIT 1) d5 ON true
      LEFT JOIN LATERAL (
           SELECT mp.price_date, mp.close FROM market_prices mp
            WHERE mp.security_id = ee.security_id AND mp.price_date > r.price_date
            ORDER BY mp.price_date OFFSET 19 LIMIT 1) d20 ON true
), with_spy AS (
    SELECT l.*,
           sp.close AS spy_prior_close, se.close AS spy_event_close,
           s1.close AS spy_day1_close, s5.close AS spy_day5_close, s20.close AS spy_day20_close
      FROM live l
      LEFT JOIN LATERAL (SELECT mp.close FROM market_prices mp WHERE mp.security_id = $$09e39bb1-7b36-406d-b5d1-db755e37ad54$$::uuid AND mp.price_date = l.prior_price_date LIMIT 1) sp ON true
      LEFT JOIN LATERAL (SELECT mp.close FROM market_prices mp WHERE mp.security_id = $$09e39bb1-7b36-406d-b5d1-db755e37ad54$$::uuid AND mp.price_date = l.event_price_date LIMIT 1) se ON true
      LEFT JOIN LATERAL (SELECT mp.close FROM market_prices mp WHERE mp.security_id = $$09e39bb1-7b36-406d-b5d1-db755e37ad54$$::uuid AND mp.price_date = l.d1_date LIMIT 1) s1 ON true
      LEFT JOIN LATERAL (SELECT mp.close FROM market_prices mp WHERE mp.security_id = $$09e39bb1-7b36-406d-b5d1-db755e37ad54$$::uuid AND mp.price_date = l.d5_date LIMIT 1) s5 ON true
      LEFT JOIN LATERAL (SELECT mp.close FROM market_prices mp WHERE mp.security_id = $$09e39bb1-7b36-406d-b5d1-db755e37ad54$$::uuid AND mp.price_date = l.d20_date LIMIT 1) s20 ON true
)
SELECT x.event_id, x.title, x.ticker,
       (x.event_day::timestamp AT TIME ZONE $$UTC$$) AS event_date,
       x.prior_price_date, x.prior_close, x.event_price_date, x.event_close,
       x.day_1_close, x.day_5_close, x.day_20_close,
       x.event_close  / NULLIF(x.prior_close, 0) - 1 AS return_0d,
       x.day_1_close  / NULLIF(x.prior_close, 0) - 1 AS return_1d,
       x.day_5_close  / NULLIF(x.prior_close, 0) - 1 AS return_5d,
       x.day_20_close / NULLIF(x.prior_close, 0) - 1 AS return_20d,
       x.spy_prior_close, x.spy_event_close, x.spy_day1_close, x.spy_day5_close, x.spy_day20_close,
       (x.event_close  / NULLIF(x.prior_close, 0) - 1) - (x.spy_event_close / NULLIF(x.spy_prior_close, 0) - 1) AS abnormal_return_0d,
       (x.day_1_close  / NULLIF(x.prior_close, 0) - 1) - (x.spy_day1_close  / NULLIF(x.spy_prior_close, 0) - 1) AS abnormal_return_1d,
       (x.day_5_close  / NULLIF(x.prior_close, 0) - 1) - (x.spy_day5_close  / NULLIF(x.spy_prior_close, 0) - 1) AS abnormal_return_5d,
       (x.day_20_close / NULLIF(x.prior_close, 0) - 1) - (x.spy_day20_close / NULLIF(x.spy_prior_close, 0) - 1) AS abnormal_return_20d,
       x.date_was_corrected
  FROM with_spy x;
