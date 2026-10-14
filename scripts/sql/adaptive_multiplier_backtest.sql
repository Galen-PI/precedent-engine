-- Rolling-recalibrated 80% range backtest (2026-10-14). Range = +- k * v64 * sqrt(20); k = 80th
-- percentile of past scaled moves (|a| / (v64*sqrt20)) over the prior 6 or 12 months, lagged by
-- at least one month (only already-known outcomes). Compared to static k = 1.09023 (fit 2019-2022).
-- Interval score = width + 10 * overshoot. Scoring starts 2020-01 (needs full lookback).
WITH z AS (
  SELECT d, date_trunc($$month$$, d)::date AS m, a, v64 * SQRT(20.0) AS sig,
         a / (v64 * SQRT(20.0)) AS zz
  FROM vol_estimators
),
months AS (
  SELECT generate_series($$2019-07-01$$::timestamp, $$2026-07-01$$::timestamp, interval $$1 month$$)::date AS m
),
k6 AS (
  SELECT mo.m, PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY z.zz) AS k
  FROM months mo
  JOIN z ON z.d >= mo.m - interval $$7 months$$ AND z.d < mo.m - interval $$1 month$$
  GROUP BY mo.m HAVING COUNT(*) >= 50000
),
k12 AS (
  SELECT mo.m, PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY z.zz) AS k
  FROM months mo
  JOIN z ON z.d >= mo.m - interval $$13 months$$ AND z.d < mo.m - interval $$1 month$$
  GROUP BY mo.m HAVING COUNT(*) >= 100000
),
sc AS (
  SELECT z.d, z.a, z.sig, EXTRACT(YEAR FROM z.d)::int AS yr, k6.k AS ka6, k12.k AS ka12
  FROM z JOIN k6 ON k6.m = z.m JOIN k12 ON k12.m = z.m
)
SELECT yr, (yr >= 2023) AS is_test, COUNT(*) AS n,
       AVG((a <= 1.09023033542931 * sig)::int) AS cov_static,
       AVG((a <= ka6 * sig)::int) AS cov_w6,
       AVG((a <= ka12 * sig)::int) AS cov_w12,
       AVG(2 * 1.09023033542931 * sig + 10 * GREATEST(0, a - 1.09023033542931 * sig)) AS is_static,
       AVG(2 * ka6 * sig + 10 * GREATEST(0, a - ka6 * sig)) AS is_w6,
       AVG(2 * ka12 * sig + 10 * GREATEST(0, a - ka12 * sig)) AS is_w12
FROM sc
GROUP BY GROUPING SETS ((yr), ((yr >= 2023)))
ORDER BY yr NULLS LAST;
