-- scan_dead_columns.sql
--
-- Real-content scan for "always-same-value" dead tracking columns -- flags any
-- column whose non-null values collapse to a single distinct value, the pattern
-- already found in event_pre_context.size_bucket and sec_8k_filings.promoted_to_event.
-- A null-rate check alone doesn't catch this -- a column can be 97%+ populated and
-- still be useless if every populated value is identical.
--
-- Scans real pipeline tables only -- excludes one-off audit/scratch snapshot tables
-- (adsk2012_fix_audit_*, caltech_audit_*, july_redo_audit_*, event_removal_audit_*,
-- nine_drafts_audit, stale_url_sweep_audit_old_rows, events_pre_promotion_ids) since
-- those are intentional point-in-time copies, not live pipeline state.
--
-- Flags a column when: non-null row count > 10 AND distinct non-null value count == 1.
-- The >10 threshold avoids false positives on newly-created or barely-used tables.
--
-- Real run 2026-09-29: 16 flagged. 9 benign (single data source/currency/model-version
-- in use so far), 2 already known (size_bucket, promoted_to_event), 1 confirms the known
-- surprise_vs_consensus gap, 2 are stale_url_sweep_results' own intentional filter
-- criteria, 1 small-sample/likely-benign (news_ai_classifications, n=60), 1 new minor
-- finding (financial_statements.statement_type is a stale label -- the real underlying
-- balance-sheet data IS well-populated, 94-97% on total_assets/liabilities/equity/cash,
-- confirmed by direct follow-up query, not a coverage gap).
--
-- Usage: run this whole file. Results land in dead_column_scan_results; SELECT from it.

DROP TABLE IF EXISTS dead_column_scan_results;
CREATE TABLE dead_column_scan_results (
  table_name text, column_name text, nonnull_count bigint, distinct_count bigint, sample_value text
);

DO $body$
DECLARE
  r RECORD;
  nonnull_ct bigint;
  distinct_ct bigint;
  sample_val text;
BEGIN
  FOR r IN
    SELECT c.table_name, c.column_name
    FROM information_schema.columns c
    WHERE c.table_schema = 'public'
      AND c.table_name IN (
        'entities', 'securities', 'events', 'event_entity_relationships',
        'event_type_relationships', 'event_types', 'event_tags', 'event_tag_suggestions',
        'event_relationships', 'event_source_filings', 'event_pre_context',
        'event_market_reactions_corrected', 'event_ripple_timeline', 'event_entity_reactions',
        'event_article_relationships', 'event_candidate_price_reaction',
        'financial_statements', 'financial_metrics', 'financial_growth_classified',
        'company_sentiment_timeline', 'global_events', 'global_event_episodes',
        'global_event_exposure', 'global_events_daily_counts', 'global_daily_total_counts',
        'macro_data_releases', 'market_prices', 'market_regimes',
        'news_articles', 'news_article_entities', 'news_ai_classifications',
        'news_candidate_events', 'filing_ai_classifications', 'sec_8k_filings', 'sec_filings',
        'sec_item_code_reference', 'security_typical_swing', 'candidate_review_log',
        'classification_corrections', 'onboarding_runs', 'onboarding_run_steps',
        'pattern_significance_tests', 'stale_url_sweep_results', 'tags', 'event_removal_list'
      )
      AND c.data_type NOT IN ('uuid', 'timestamp with time zone', 'timestamp without time zone', 'json', 'jsonb', 'ARRAY')
      AND c.column_name NOT IN ('id', 'created_at', 'calculated_at', 'updated_at')
  LOOP
    BEGIN
      EXECUTE format(
        'SELECT COUNT(%I), COUNT(DISTINCT %I) FROM %I WHERE %I IS NOT NULL',
        r.column_name, r.column_name, r.table_name, r.column_name
      ) INTO nonnull_ct, distinct_ct;

      IF nonnull_ct > 10 AND distinct_ct = 1 THEN
        EXECUTE format(
          'SELECT %I::text FROM %I WHERE %I IS NOT NULL LIMIT 1',
          r.column_name, r.table_name, r.column_name
        ) INTO sample_val;
        INSERT INTO dead_column_scan_results VALUES (r.table_name, r.column_name, nonnull_ct, distinct_ct, sample_val);
      END IF;
    EXCEPTION WHEN OTHERS THEN
      NULL;  -- skip columns whose type can't be COUNT(DISTINCT)'d (arrays, composites)
    END;
  END LOOP;
END
$body$;

SELECT * FROM dead_column_scan_results ORDER BY table_name, column_name;
