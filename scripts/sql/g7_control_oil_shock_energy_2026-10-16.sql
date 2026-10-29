-- G7 CONTROL C3 (macro_oil_shock_energy_same_day). RECORD AND RUNNABLE. Recovered on 2026-10-29 from the 2026-10-16 20:30 session transcript: the exact
-- query whose output (Energy 1.293 t 9.2 over 115 months in 2004-2018, 1.319 t 8.2 over 64 months in 2019-2026) became the ledger row. It was typed in the
-- SQL editor and never saved. Read-only; reads spy_cal, macro_data_releases (DCOILWTICO) and sector_day_z: market-wide tables.
WITH oil AS (
  SELECT sc.d, AVG(m.value) AS v
  FROM spy_cal sc JOIN macro_data_releases m ON m.series_id = $$DCOILWTICO$$ AND m.release_date = sc.d
  WHERE m.value IS NOT NULL GROUP BY sc.d
), od AS (
  SELECT d, v, LAG(v) OVER (ORDER BY d) AS pv FROM oil
), flag AS (
  SELECT d, ABS(v / pv - 1) >= 0.03 AS shock, LAG(ABS(v / pv - 1) >= 0.03) OVER (ORDER BY d) AS shock_prev
  FROM od WHERE pv > 5 AND v > 5
), tot AS (
  SELECT day, SUM(mean_z * n) AS sz, SUM(n) AS sn FROM sector_day_z GROUP BY day
), x AS (
  SELECT s.day, s.sector, LN(s.mean_z / ((t.sz - s.mean_z * s.n) / (t.sn - s.n))) AS l
  FROM sector_day_z s JOIN tot t ON t.day = s.day
  WHERE s.sector <> $$Unclassified$$ AND s.n >= 3 AND s.mean_z > 0
), j AS (
  SELECT x.sector, x.l, f.shock, f.shock_prev, date_trunc($$month$$, x.day)::date AS m,
         CASE WHEN x.day < $$2019-01-01$$::date THEN $$A_2004_2018$$ ELSE $$B_2019_2026$$ END AS era
  FROM x JOIN flag f ON f.d = x.day
), mm AS (
  SELECT sector, era, m,
         AVG(l) FILTER (WHERE shock) - AVG(l) FILTER (WHERE NOT shock) AS d_same,
         AVG(l) FILTER (WHERE shock_prev) - AVG(l) FILTER (WHERE NOT shock_prev) AS d_next
  FROM j GROUP BY sector, era, m
  HAVING COUNT(*) FILTER (WHERE shock) >= 2 AND COUNT(*) FILTER (WHERE NOT shock) >= 5
     AND COUNT(*) FILTER (WHERE shock_prev) >= 2 AND COUNT(*) FILTER (WHERE NOT shock_prev) >= 5
)
SELECT sector, era, COUNT(*) AS months,
       ROUND(EXP(AVG(d_same))::numeric, 3) AS amp_same_day,
       ROUND((AVG(d_same) / (STDDEV(d_same) / SQRT(COUNT(*))))::numeric, 1) AS t_same,
       ROUND(EXP(AVG(d_next))::numeric, 3) AS amp_next_day,
       ROUND((AVG(d_next) / (STDDEV(d_next) / SQRT(COUNT(*))))::numeric, 1) AS t_next
FROM mm GROUP BY sector, era ORDER BY sector, era;