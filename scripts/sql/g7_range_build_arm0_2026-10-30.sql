-- G7 event_daily_range_coverage, ARM 0 (Addendum 11 of results/PREREG_g7_proven_rerun_2026-10-29.md), written 2026-10-30 before any run.
-- The two statements that built flag_days and ctrl_days in the session of 2026-10-16 16:27 (recovered from its transcript), copied clause for clause, with these changes only: the new table names flag_days_g7_arm0 and ctrl_days_g7_arm0 (no IF NOT EXISTS).
-- The original ran the day-list in this order: flag_days, then ctrl_days, then the overlap was deleted from ctrl_days.
CREATE TABLE flag_days_g7_arm0 AS
SELECT s.id AS security_id, c.d, COUNT(DISTINCT e.id)::int AS n_events,
       BOOL_OR(c.rn - c0.rn = -1) AS has_m1, BOOL_OR(c.rn - c0.rn = 0) AS has_0, BOOL_OR(c.rn - c0.rn = 1) AS has_p1
FROM events e
JOIN event_entity_relationships r ON r.event_id = e.id
JOIN securities s ON s.entity_id = r.entity_id
JOIN LATERAL (SELECT sc.rn FROM spy_cal sc WHERE sc.d >= e.event_date::date ORDER BY sc.d LIMIT 1) c0 ON true
JOIN spy_cal c ON c.rn BETWEEN c0.rn - 1 AND c0.rn + 1
WHERE e.id NOT IN (SELECT event_id FROM event_component_dates)
  AND e.event_date >= $$2004-01-01$$ AND e.event_date < $$2026-08-01$$
  AND NOT (e.title ILIKE $$%spin%$$ OR e.title ILIKE $$%separation%$$ OR e.title ILIKE $$%split-off%$$ OR e.title ILIKE $$%split off%$$)
  AND COALESCE((SELECT t.name FROM event_type_relationships x JOIN event_types t ON t.id = x.event_type_id
                WHERE x.event_id = e.id ORDER BY t.name LIMIT 1), $$none$$) <> $$capital_raise$$
  AND NOT (s.ticker = $$HON$$ AND e.event_date >= $$2026-06-01$$)
GROUP BY s.id, c.d;

CREATE TABLE ctrl_days_g7_arm0 AS
SELECT DISTINCT s.id AS security_id, c.d
FROM events e
JOIN event_entity_relationships r ON r.event_id = e.id
JOIN securities s ON s.entity_id = r.entity_id
JOIN LATERAL (SELECT sc.rn FROM spy_cal sc WHERE sc.d >= e.event_date::date ORDER BY sc.d LIMIT 1) c0 ON true
JOIN spy_cal c ON c.rn BETWEEN c0.rn + 25 AND c0.rn + 39
WHERE e.id NOT IN (SELECT event_id FROM event_component_dates)
  AND e.event_date >= $$2004-01-01$$ AND e.event_date < $$2026-06-01$$
  AND NOT (e.title ILIKE $$%spin%$$ OR e.title ILIKE $$%separation%$$ OR e.title ILIKE $$%split-off%$$ OR e.title ILIKE $$%split off%$$)
  AND COALESCE((SELECT t.name FROM event_type_relationships x JOIN event_types t ON t.id = x.event_type_id
                WHERE x.event_id = e.id ORDER BY t.name LIMIT 1), $$none$$) <> $$capital_raise$$
  AND NOT (s.ticker = $$HON$$ AND e.event_date >= $$2026-06-01$$);

DELETE FROM ctrl_days_g7_arm0 cd USING flag_days_g7_arm0 fd WHERE fd.security_id = cd.security_id AND fd.d = cd.d;
