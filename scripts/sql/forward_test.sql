-- FORWARD TEST of FROZEN METHOD v1_6mo_recal_2026-10-14. Design data used origin days <= 2026-07-31;
-- forward sample = origin days >= 2026-08-01. Refresh first (appends resolved days only):
-- SELECT load_vol_year('2024-10-01'::date, '2026-12-31'::date,
--                      (SELECT MAX(d) + 1 FROM vol_estimators), '2026-12-31'::date);
-- Pre-registered pass rule (after >= 6 resolved months): pooled coverage 76-84% and at most 1 of
-- 6 months outside 70-90%. On failure, record it; never edit this method (new version instead).
WITH z AS (
  SELECT d, date_trunc($$month$$, d)::date AS m, a, v64 * SQRT(20.0) AS sig,
         a / (v64 * SQRT(20.0)) AS zz
  FROM vol_estimators
),
months AS (SELECT DISTINCT m FROM z WHERE d >= $$2026-08-01$$),
k6 AS (
  SELECT mo.m, PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY z.zz) AS k
  FROM months mo
  JOIN z ON z.d >= mo.m - interval $$7 months$$ AND z.d < mo.m - interval $$1 month$$
  GROUP BY mo.m
),
sc AS (SELECT z.m, z.a, z.sig, k6.k FROM z JOIN k6 ON k6.m = z.m WHERE z.d >= $$2026-08-01$$)
SELECT m, COUNT(*) AS n, MAX(k) AS k6,
       AVG((a <= k * sig)::int) AS cov_w6,
       AVG((a <= 1.09023033542931 * sig)::int) AS cov_static,
       AVG(2 * k * sig + 10 * GREATEST(0, a - k * sig)) AS iscore_w6,
       AVG(2 * 1.09023033542931 * sig + 10 * GREATEST(0, a - 1.09023033542931 * sig)) AS iscore_static
FROM sc GROUP BY m ORDER BY m;
