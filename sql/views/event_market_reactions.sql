-- 2026-10-19: event_market_reactions is now a thin wrapper over event_market_reactions_v2 (see sql/views/event_market_reactions_v2.sql).
-- The pre-repair definition is kept in sql/views/event_market_reactions_OLD_before_repair_20261019.sql (rollback: run that file).
CREATE OR REPLACE VIEW event_market_reactions AS SELECT * FROM event_market_reactions_v2;
