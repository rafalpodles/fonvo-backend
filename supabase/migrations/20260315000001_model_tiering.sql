-- Add per-task model configs for model tiering
-- Premium tier: gpt-4.1 (chat, error analysis)
-- Standard tier: gpt-4.1-mini (vocab extraction, suggestions)
-- Economy tier: gpt-4.1-nano (summary, goals, useful words, translation)

INSERT INTO ai_model_config (key, provider, model_id, display_name, extra_config)
VALUES
  ('error_analysis', 'openai', 'gpt-4.1', 'GPT-4.1 (Error Analysis)', '{}'),
  ('vocabulary_extraction', 'openai', 'gpt-4.1-mini', 'GPT-4.1 Mini (Vocab Extraction)', '{}'),
  ('suggestions', 'openai', 'gpt-4.1-mini', 'GPT-4.1 Mini (Suggestions)', '{}'),
  ('goal_analysis', 'openai', 'gpt-4.1-nano', 'GPT-4.1 Nano (Goal Analysis)', '{}'),
  ('summary', 'openai', 'gpt-4.1-nano', 'GPT-4.1 Nano (Summary)', '{}'),
  ('useful_words', 'openai', 'gpt-4.1-nano', 'GPT-4.1 Nano (Useful Words)', '{}'),
  ('translation', 'openai', 'gpt-4.1-nano', 'GPT-4.1 Nano (Translation)', '{}')
ON CONFLICT (key) DO NOTHING;

-- Also update the existing chat model to gpt-4.1
UPDATE ai_model_config SET model_id = 'gpt-4.1', display_name = 'GPT-4.1 (Chat)' WHERE key = 'chat';
