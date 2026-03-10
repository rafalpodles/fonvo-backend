-- Add detected_level column to conversations
-- Stores the AI-detected CEFR level from error analysis
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS detected_level text;

-- Index for efficient median calculation (last N conversations per user+language)
CREATE INDEX IF NOT EXISTS idx_conversations_level_detection
    ON conversations (user_id, target_language, started_at DESC)
    WHERE detected_level IS NOT NULL;
