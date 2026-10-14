-- Stock-day table with 20/64/250-trading-day trailing daily-return stddevs and the 20d
-- abnormal move (|20d return - SPY 20d return|). Built 2026-10-14, 915,215 rows, 2019-2026.
-- Requires 20 returns in v20, >= 50 in v64, >= 200 in v250. Running-sum stddev (verified
-- against window STDDEV: max diff 1.2e-13 for v64, 7e-16 for v20, 6e-17 for v250 on checks).
-- NOTE: load each year ONCE (an accidental repeat run doubled rows 2020-2026 and had to be
-- deduplicated; the unique index below now makes repeats fail instead).
DROP TABLE IF EXISTS vol_estimators;
CREATE TABLE vol_estimators (
  security_id uuid, d date, a double precision,
  v20 double precision, v64 double precision, v250 double precision
);
CREATE UNIQUE INDEX vol_estimators_uq ON vol_estimators (security_id, d);

CREATE OR REPLACE FUNCTION load_vol_year(lo date, hi date, out_lo date, out_hi date)
RETURNS bigint LANGUAGE plpgsql AS $fn$
DECLARE n bigint;
BEGIN
  INSERT INTO vol_estimators
  WITH spy AS (
    SELECT price_date, adjusted_close AS c
    FROM market_prices
    WHERE security_id = (SELECT id FROM securities WHERE ticker = $$SPY$$)
      AND price_date BETWEEN lo AND hi
  ),
  p AS (
    SELECT mp.security_id, mp.price_date,
           (mp.adjusted_close / LAG(mp.adjusted_close) OVER w - 1)::double precision AS ret,
           LAG(mp.adjusted_close) OVER w AS prev_close,
           LAG(mp.price_date) OVER w AS prev_date,
           LEAD(mp.adjusted_close, 20) OVER w AS close20,
           LEAD(mp.price_date, 20) OVER w AS date20
    FROM market_prices mp
    WHERE mp.price_date BETWEEN lo AND hi
      AND mp.security_id <> (SELECT id FROM securities WHERE ticker = $$SPY$$)
    WINDOW w AS (PARTITION BY mp.security_id ORDER BY mp.price_date)
  ),
  c AS (
    SELECT p.*,
           SUM(ret) OVER w2 AS c1, SUM(ret * ret) OVER w2 AS c2, COUNT(ret) OVER w2 AS cn
    FROM p
    WINDOW w2 AS (PARTITION BY security_id ORDER BY price_date
                  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
  ),
  l AS (
    SELECT c.*,
           LAG(c1, 1) OVER w3 AS p1, LAG(c2, 1) OVER w3 AS p2, LAG(cn, 1) OVER w3 AS pn,
           LAG(c1, 21) OVER w3 AS a1, LAG(c2, 21) OVER w3 AS a2, LAG(cn, 21) OVER w3 AS an,
           LAG(c1, 65) OVER w3 AS b1, LAG(c2, 65) OVER w3 AS b2, LAG(cn, 65) OVER w3 AS bn,
           LAG(c1, 251) OVER w3 AS d1, LAG(c2, 251) OVER w3 AS d2, LAG(cn, 251) OVER w3 AS dn
    FROM c
    WINDOW w3 AS (PARTITION BY security_id ORDER BY price_date)
  ),
  m AS (
    SELECT security_id, price_date, prev_close, prev_date, close20, date20,
           (pn - COALESCE(an, 0)) AS k20, (p1 - COALESCE(a1, 0)) AS s1_20, (p2 - COALESCE(a2, 0)) AS s2_20,
           (pn - COALESCE(bn, 0)) AS k64, (p1 - COALESCE(b1, 0)) AS s1_64, (p2 - COALESCE(b2, 0)) AS s2_64,
           (pn - COALESCE(dn, 0)) AS k250, (p1 - COALESCE(d1, 0)) AS s1_250, (p2 - COALESCE(d2, 0)) AS s2_250
    FROM l
  )
  SELECT m.security_id, m.price_date,
         ABS((m.close20 / m.prev_close - 1) - (s20.c / s0.c - 1))::double precision,
         SQRT(GREATEST((m.s2_20 - m.s1_20 * m.s1_20 / m.k20) / (m.k20 - 1), 0))::double precision,
         SQRT(GREATEST((m.s2_64 - m.s1_64 * m.s1_64 / m.k64) / (m.k64 - 1), 0))::double precision,
         SQRT(GREATEST((m.s2_250 - m.s1_250 * m.s1_250 / m.k250) / (m.k250 - 1), 0))::double precision
  FROM m
  JOIN spy s0 ON s0.price_date = m.prev_date
  JOIN spy s20 ON s20.price_date = m.date20
  WHERE m.price_date BETWEEN out_lo AND out_hi
    AND m.prev_close IS NOT NULL AND m.close20 IS NOT NULL
    AND m.k20 = 20 AND m.k64 >= 50 AND m.k250 >= 200;
  GET DIAGNOSTICS n = ROW_COUNT;
  DELETE FROM vol_estimators WHERE v20 <= 0 OR v64 <= 0 OR v250 <= 0;
  RETURN n;
END
$fn$;

-- One call per year, ONE AT A TIME (lo/hi = price window incl. 250-day lookback; out = output dates):
-- SELECT load_vol_year('2017-10-01'::date, '2020-02-15'::date, '2019-01-01'::date, '2019-12-31'::date);
-- SELECT load_vol_year('2018-10-01'::date, '2021-02-15'::date, '2020-01-01'::date, '2020-12-31'::date);
-- SELECT load_vol_year('2019-10-01'::date, '2022-02-15'::date, '2021-01-01'::date, '2021-12-31'::date);
-- SELECT load_vol_year('2020-10-01'::date, '2023-02-15'::date, '2022-01-01'::date, '2022-12-31'::date);
-- SELECT load_vol_year('2021-10-01'::date, '2024-02-15'::date, '2023-01-01'::date, '2023-12-31'::date);
-- SELECT load_vol_year('2022-10-01'::date, '2025-02-15'::date, '2024-01-01'::date, '2024-12-31'::date);
-- SELECT load_vol_year('2023-10-01'::date, '2026-02-15'::date, '2025-01-01'::date, '2025-12-31'::date);
-- SELECT load_vol_year('2024-10-01'::date, '2026-09-30'::date, '2026-01-01'::date, '2026-07-31'::date);
