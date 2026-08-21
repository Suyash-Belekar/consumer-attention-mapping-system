-- Migration: convert attention_sessions timestamps to TIMESTAMPTZ (timezone-aware)
-- Interprets existing timestamp values as UTC during conversion.

BEGIN;

ALTER TABLE attention_sessions
    ALTER COLUMN entry_time
    TYPE TIMESTAMP WITH TIME ZONE
    USING entry_time AT TIME ZONE 'UTC';

ALTER TABLE attention_sessions
    ALTER COLUMN exit_time
    TYPE TIMESTAMP WITH TIME ZONE
    USING exit_time AT TIME ZONE 'UTC';

COMMIT;
