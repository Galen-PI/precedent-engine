-- Monthly calibration factor for range_card.py (FROZEN METHOD v1_6mo_recal_2026-10-14).
-- k = 80th percentile of past scaled moves over the 6 months before the prior month.
CREATE OR REPLACE FUNCTION range_k6(m date)
RETURNS TABLE(k double precision, n bigint) LANGUAGE sql STABLE AS $fn$
  SELECT PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY a / (v64 * SQRT(20.0))),
         COUNT(*)
  FROM vol_estimators
  WHERE d >= m - interval $$7 months$$ AND d < m - interval $$1 month$$
$fn$;
