-- G7 by-type burst, ARM 1 (cleaned): the Arm 0 query with event_profile_base rebuilt inline and every event with an exclude row in event_exclusions removed
-- from the sample AND from the isolation test. The tail (types, seam exclusion, pooled row, SE) is identical to Arm 0. Read-only.
WITH ex AS MATERIALIZED (SELECT event_id FROM event_exclusions WHERE severity = $$exclude$$),
per AS (
  SELECT d.event_id, d.entity_id,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 25 AND 39) AS base,
         COUNT(d.adr) FILTER (WHERE d.day_offset BETWEEN 25 AND 39) AS nb,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN -4 AND -1) AS w_pre,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 0 AND 1) AS w_d01,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 2 AND 5) AS w_d25,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 6 AND 20) AS w_d620,
         AVG(d.adr) FILTER (WHERE d.day_offset BETWEEN 21 AND 24) AS w_d2124
  FROM event_daily_abn d WHERE NOT EXISTS (SELECT 1 FROM ex WHERE ex.event_id = d.event_id) GROUP BY 1, 2
),
b AS (
  SELECT per.*, e.event_date::date AS d0,
         CASE WHEN e.event_date < $$2004-01-01$$ THEN $$C_pre_2004$$
              WHEN e.event_date < $$2019-01-01$$ THEN $$A_2004_2018$$ ELSE $$B_2019_2026$$ END AS era,
         NOT EXISTS (SELECT 1 FROM event_entity_relationships o JOIN events oe ON oe.id = o.event_id
                     WHERE o.entity_id = per.entity_id AND o.event_id <> per.event_id
                       AND oe.event_date::date BETWEEN e.event_date::date - 5 AND e.event_date::date + 39
                       AND NOT EXISTS (SELECT 1 FROM ex WHERE ex.event_id = o.event_id)) AS isolated
  FROM per JOIN events e ON e.id = per.event_id
  WHERE per.base > 0 AND per.nb >= 10
),
et AS (SELECT DISTINCT ON (etr.event_id) etr.event_id, t.name AS etype
            FROM event_type_relationships etr JOIN event_types t ON t.id = etr.event_type_id
            ORDER BY etr.event_id, t.name),
v0 AS (SELECT b.era,
              CASE WHEN et.etype = $$corporate_action$$ AND e.title ~* $$split$$ THEN $$corporate_action_split$$
                   WHEN et.etype = $$corporate_action$$ THEN $$corporate_action_other$$ ELSE et.etype END AS etype,
              b.w_d01 AS x, b.base AS y
       FROM b JOIN events e ON e.id = b.event_id JOIN et ON et.event_id = b.event_id
       WHERE b.isolated AND b.w_d01 IS NOT NULL AND b.era <> $$C_pre_2004$$
         AND NOT (e.title ILIKE $$%spin%$$ OR e.title ILIKE $$%separation%$$ OR e.title ILIKE $$%split-off%$$ OR e.title ILIKE $$%split off%$$)),
v AS (SELECT * FROM v0 UNION ALL SELECT era, $$ALL_POOLED$$, x, y FROM v0),
r AS (SELECT era, etype, SUM(x) / SUM(y) AS rr FROM v GROUP BY 1, 2)
SELECT v.etype, v.era, COUNT(*) AS n, ROUND(r.rr::numeric, 3) AS ratio_day_0_1,
       ROUND((STDDEV(v.x - r.rr * v.y) / (SQRT(COUNT(*)) * AVG(v.y)))::numeric, 3) AS se
FROM v JOIN r ON r.era = v.era AND r.etype = v.etype
GROUP BY v.etype, v.era, r.rr HAVING COUNT(*) >= 60 ORDER BY 1, 2;