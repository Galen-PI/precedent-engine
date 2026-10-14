-- 8-Ks that still need classifying, decided INSIDE the database (2026-10-14).
-- Never returns a human-reviewed filing; MALFORMED (unparseable) rows are retried.
CREATE OR REPLACE VIEW candidate_8k_unclassified AS
SELECT c.*
FROM candidate_8k_events c
WHERE NOT EXISTS (
  SELECT 1 FROM filing_ai_classifications f
  WHERE f.ticker = c.ticker AND f.filing_date = c.filing_date
    AND f.accession_number = c.accession_number
    AND (f.human_reviewed_at IS NOT NULL
         OR f.ai_reasoning IS NULL
         OR f.ai_reasoning NOT LIKE 'MALFORMED API RESPONSE%')
);
