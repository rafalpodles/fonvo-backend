-- Add post_conversation model key for batched analysis
-- Replaces separate error_analysis, vocabulary_extraction, summary keys
INSERT INTO ai_model_config (key, provider, model_id, display_name, extra_config)
VALUES ('post_conversation', 'openai', 'gpt-4.1', 'GPT-4.1 (Post-Conversation Analysis)', '{}')
ON CONFLICT (key) DO NOTHING;

-- Mark replaced keys as inactive (keep data for reference)
UPDATE ai_model_config SET is_active = false WHERE key IN ('summary', 'vocabulary_extraction') AND is_active = true;
