-- Population baseline: scaled 20d abnormal move for EVERY tracked stock-day, 2019-01..2026-07.
-- scaled = |20d return - SPY 20d return| / (stddev of prior-64-trading-day daily returns * sqrt(20)).
-- Built 2026-10-14 (920,249 rows, mean 0.7448). Drop with: DROP TABLE daily_scaled_move;
CREATE TABLE daily_scaled_move AS
WITH spy AS (
  SELECT price_date, adjusted_close AS c
  FROM market_prices
  WHERE security_id = (SELECT id FROM securities WHERE ticker = 'SPY')
    AND price_date >= '2018-09-01'
),
p AS (
  SELECT mp.security_id, mp.price_date,
         mp.adjusted_close / LAG(mp.adjusted_close) OVER w - 1 AS ret,
         LAG(mp.adjusted_close) OVER w AS prev_close,
         LAG(mp.price_date) OVER w AS prev_date,
         LEAD(mp.adjusted_close, 20) OVER w AS close20,
         LEAD(mp.price_date, 20) OVER w AS date20
  FROM market_prices mp
  WHERE mp.price_date >= '2018-09-01'
    AND mp.security_id <> (SELECT id FROM securities WHERE ticker = 'SPY')
  WINDOW w AS (PARTITION BY mp.security_id ORDER BY mp.price_date)
),
v AS (
  SELECT p.*,
         STDDEV(ret) OVER (PARTITION BY security_id ORDER BY price_date
                           ROWS BETWEEN 64 PRECEDING AND 1 PRECEDING) AS vol,
         COUNT(ret) OVER (PARTITION BY security_id ORDER BY price_date
                          ROWS BETWEEN 64 PRECEDING AND 1 PRECEDING) AS k
  FROM p
)
SELECT v.security_id, v.price_date AS d,
       ABS((v.close20 / v.prev_close - 1) - (s20.c / s0.c - 1)) / (v.vol * SQRT(20.0)) AS scaled
FROM v
JOIN spy s0 ON s0.price_date = v.prev_date
JOIN spy s20 ON s20.price_date = v.date20
WHERE v.price_date BETWEEN '2019-01-01' AND '2026-07-31'
  AND v.prev_close IS NOT NULL AND v.close20 IS NOT NULL
  AND v.k >= 30 AND v.vol > 0;
