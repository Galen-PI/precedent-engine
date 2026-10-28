-- phase5_gate.sql: the Phase 5 gate (G1), from the "done when" of NAMING.md: every event has a reaction row, one reaction label
-- that agrees with it, a pre-context row and a ripple timeline, or a documented exclusion reason. One row per component: gaps and PASS/FAIL.
-- Read-only. Run in the Supabase SQL editor. Created 2026-10-28 (replaces the 10-28 query, which counted any exclusion row, including a
-- provenance note, as a reason for a missing ripple timeline; component 5 now accepts only an exclude or review reason).
-- Component 3 detects the stored unit of abnormal_return_20d (fractions or percent) and prints the threshold it used.
-- Sealed events are counted, never listed. A non-zero gap is read case by case, never fixed in bulk.
WITH
thr AS (SELECT CASE WHEN percentile_cont(0.5) WITHIN GROUP (ORDER BY abs(abnormal_return_20d)) > 1 THEN 3.0 ELSE 0.03 END AS t FROM event_market_reactions_corrected WHERE abnormal_return_20d IS NOT NULL),
lab AS (SELECT et.event_id, COUNT(*) AS n_labels, MIN(tg.name) AS label FROM event_tags et JOIN tags tg ON tg.id = et.tag_id WHERE tg.name IN ($$rewarded$$, $$punished$$, $$muted$$, $$diverged_from_fundamentals$$) GROUP BY et.event_id),
gaps AS (
SELECT 1 AS component, $$every event has a reaction row, or a recorded reason$$ AS requirement, COUNT(*) AS gaps FROM events e WHERE NOT EXISTS (SELECT 1 FROM event_market_reactions_corrected r WHERE r.event_id = e.id) AND NOT EXISTS (SELECT 1 FROM event_exclusions x WHERE x.event_id = e.id)
UNION ALL
SELECT 2, $$every reaction row has exactly one reaction label$$, COUNT(*) FROM event_market_reactions_corrected r LEFT JOIN lab l ON l.event_id = r.event_id WHERE COALESCE(l.n_labels, 0) <> 1
UNION ALL
SELECT 3, $$the label agrees with the 20-day abnormal return at the threshold $$ || (SELECT t FROM thr)::text, COUNT(*) FROM event_market_reactions_corrected r JOIN lab l ON l.event_id = r.event_id WHERE l.n_labels = 1 AND r.abnormal_return_20d IS NOT NULL AND ((r.abnormal_return_20d > (SELECT t FROM thr) AND l.label NOT IN ($$rewarded$$, $$diverged_from_fundamentals$$)) OR (r.abnormal_return_20d < -(SELECT t FROM thr) AND l.label NOT IN ($$punished$$, $$diverged_from_fundamentals$$)) OR (abs(r.abnormal_return_20d) <= (SELECT t FROM thr) AND l.label <> $$muted$$))
UNION ALL
SELECT 4, $$every reaction row has a pre-context row, or a recorded reason$$, COUNT(*) FROM event_market_reactions_corrected r WHERE NOT EXISTS (SELECT 1 FROM event_pre_context p WHERE p.event_id = r.event_id) AND NOT EXISTS (SELECT 1 FROM event_exclusions x WHERE x.event_id = r.event_id)
UNION ALL
SELECT 5, $$every reaction row has a ripple timeline, or an exclude or review reason (a provenance note is NOT a reason)$$, COUNT(*) FROM event_market_reactions_corrected r WHERE NOT EXISTS (SELECT 1 FROM event_ripple_timeline t WHERE t.event_id = r.event_id) AND NOT EXISTS (SELECT 1 FROM event_exclusions x WHERE x.event_id = r.event_id AND x.severity IN ($$exclude$$, $$review$$))
)
SELECT component, requirement, gaps, CASE WHEN gaps = 0 THEN $$PASS$$ ELSE $$FAIL$$ END AS verdict FROM gaps ORDER BY component;