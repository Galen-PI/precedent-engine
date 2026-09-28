-- Tables created 2026-09-28 for the stale primary_document_url sweep (issue #34)
-- and the promotion / cleanup that followed.

CREATE TABLE IF NOT EXISTS stale_url_sweep_results (
  ticker text NOT NULL,
  filing_date date NOT NULL,
  accession_number text NOT NULL,
  old_ai_verdict text,
  old_human_verdict text,
  new_verdict text,
  new_confidence real,
  new_reasoning text,
  new_title text,
  new_event_type text,
  new_description text,
  fixed_url text,
  review_status text,
  swept_at timestamptz DEFAULT now(),
  PRIMARY KEY (ticker, filing_date, accession_number)
);

CREATE TABLE IF NOT EXISTS event_removal_list (event_id uuid PRIMARY KEY, note text);

-- One-time snapshots, created with CREATE TABLE AS (columns copied from the source):
--
-- stale_url_sweep_audit_old_rows: the filing_ai_classifications rows for the 27 confirmed
--   sweep flips, as they were before the write-back.
--   CREATE TABLE stale_url_sweep_audit_old_rows AS
--   SELECT fac.*, now() AS snapshotted_at FROM filing_ai_classifications fac
--   JOIN stale_url_sweep_results s ON s.ticker = fac.ticker AND s.filing_date = fac.filing_date
--     AND s.accession_number = fac.accession_number WHERE s.review_status = 'confirmed';
--
-- events_pre_promotion_ids: every events.id existing before promote_events.py passes 1-5
--   (taken after the 15-row test run). Used for child-row checks and to identify new events.
--   CREATE TABLE events_pre_promotion_ids AS SELECT id FROM events;
--
-- event_removal_audit_events, _entity_rels, _type_rels, _source_filings, _classifications:
--   copies of the rows removed with the 35 routine events (poison pills, majority-voting
--   adoptions, listing transfers, three standalone financings/buybacks), each built with
--   CREATE TABLE AS SELECT ... JOIN event_removal_list. To undo, re-insert from these.
