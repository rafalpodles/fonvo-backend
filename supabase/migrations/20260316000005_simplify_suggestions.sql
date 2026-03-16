-- Replace 2 suggestion prompts with 1 universal
-- Level is already passed as {level} placeholder

INSERT INTO ai_prompts (key, prompt_text, description, placeholders)
VALUES (
  'conversation.suggestions',
  'The user is practicing {language} at {level} level. Based on the conversation, suggest exactly {count} short responses they could say next.

Format each on its own line as: target_text | {device_language}_translation
Keep responses natural, short, and appropriate for {level} level.
No numbering or extra text.',
  'Universal suggestion prompt — level controls complexity',
  ARRAY['language', 'level', 'count', 'device_language']
)
ON CONFLICT (key) DO NOTHING;

-- Deactivate old suggestion prompts
UPDATE ai_prompts SET is_active = false WHERE key IN (
  'conversation.suggestion_a1',
  'conversation.suggestion_default'
) AND is_active = true;
