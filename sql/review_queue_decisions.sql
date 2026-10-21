CREATE TABLE IF NOT EXISTS review_queue_decisions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  accession_number text NOT NULL,
  ticker text NOT NULL,
  miss_date date NOT NULL,
  tier text,
  classifier_verdict text,
  classifier_confidence numeric,
  decision text NOT NULL CHECK (decision IN ($$event$$, $$not_an_event$$, $$need_more$$)),
  notes text,
  reviewer text NOT NULL,
  queue_version text,
  linked_event_id uuid,
  decided_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (accession_number, miss_date)
);
ALTER TABLE review_queue_decisions ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_rqd_decision ON review_queue_decisions (decision);
