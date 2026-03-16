-- Replace 4 per-level opening instructions with one universal prompt
-- Level guidelines already control greeting complexity per CEFR level

INSERT INTO ai_prompts (key, prompt_text, description, placeholders)
VALUES (
  'conversation.opening_instruction',
  'Greet the student warmly to start the conversation.',
  'Universal opening instruction — level guidelines control greeting complexity',
  ARRAY['language']
)
ON CONFLICT (key) DO NOTHING;

-- Deactivate old per-level opening instructions
UPDATE ai_prompts SET is_active = false WHERE key IN (
  'conversation.opening_instruction.a1',
  'conversation.opening_instruction.a2',
  'conversation.opening_instruction.b1_b2',
  'conversation.opening_instruction.c1_c2'
) AND is_active = true;
