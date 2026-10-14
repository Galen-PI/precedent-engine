-- Human-reviewed rows keep their AI fields no matter what writes to the table (2026-10-14).
-- Undo with: DROP TRIGGER trg_protect_reviewed ON filing_ai_classifications;
CREATE OR REPLACE FUNCTION protect_reviewed_classifications() RETURNS trigger
LANGUAGE plpgsql AS $fn$
BEGIN
  IF OLD.human_reviewed_at IS NOT NULL THEN
    NEW.ai_verdict := OLD.ai_verdict;
    NEW.ai_confidence := OLD.ai_confidence;
    NEW.ai_reasoning := OLD.ai_reasoning;
    NEW.ai_suggested_title := OLD.ai_suggested_title;
    NEW.ai_suggested_description := OLD.ai_suggested_description;
    NEW.ai_suggested_event_type := OLD.ai_suggested_event_type;
    NEW.ai_matched_known_template := OLD.ai_matched_known_template;
    NEW.model_version := OLD.model_version;
    NEW.prompt_version := OLD.prompt_version;
    NEW.flagged_for_review := OLD.flagged_for_review;
    NEW.flag_reason := OLD.flag_reason;
    NEW.classified_at := OLD.classified_at;
  END IF;
  RETURN NEW;
END
$fn$;
CREATE TRIGGER trg_protect_reviewed
BEFORE UPDATE ON filing_ai_classifications
FOR EACH ROW EXECUTE FUNCTION protect_reviewed_classifications();
