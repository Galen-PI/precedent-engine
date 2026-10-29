-- G7 by-type burst, ARM 0: the ORIGINAL query, byte for byte. Recovered 2026-10-29 from the 2026-10-16 16:27 session transcript; its output became the ledger rows
-- (ALL_POOLED 6,871 and 3,836; acquisition 2,127 and 936; capital_raise 505 and 355). Reads the view event_profile_base (created 2026-10-16). Read-only.
WITH et AS (SELECT DISTINCT ON (etr.event_id) etr.event_id, t.name AS etype
            FROM event_type_relationships etr JOIN event_types t ON t.id = etr.event_type_id
            ORDER BY etr.event_id, t.name),
v0 AS (SELECT b.era,
              CASE WHEN et.etype = $$corporate_action$$ AND e.title ~* $$split$$ THEN $$corporate_action_split$$
                   WHEN et.etype = $$corporate_action$$ THEN $$corporate_action_other$$ ELSE et.etype END AS etype,
              b.w_d01 AS x, b.base AS y
       FROM event_profile_base b JOIN events e ON e.id = b.event_id JOIN et ON et.event_id = b.event_id
       WHERE b.isolated AND b.w_d01 IS NOT NULL AND b.era <> $$C_pre_2004$$
         AND NOT (e.title ILIKE $$%spin%$$ OR e.title ILIKE $$%separation%$$ OR e.title ILIKE $$%split-off%$$ OR e.title ILIKE $$%split off%$$)),
v AS (SELECT * FROM v0 UNION ALL SELECT era, $$ALL_POOLED$$, x, y FROM v0),
r AS (SELECT era, etype, SUM(x) / SUM(y) AS rr FROM v GROUP BY 1, 2)
SELECT v.etype, v.era, COUNT(*) AS n, ROUND(r.rr::numeric, 3) AS ratio_day_0_1,
       ROUND((STDDEV(v.x - r.rr * v.y) / (SQRT(COUNT(*)) * AVG(v.y)))::numeric, 3) AS se
FROM v JOIN r ON r.era = v.era AND r.etype = v.etype
GROUP BY v.etype, v.era, r.rr HAVING COUNT(*) >= 60 ORDER BY 1, 2;