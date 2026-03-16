-- Per-level inline correction prompts (replaces single inline_corrections_on)
-- Saves ~100 tokens per request by only including the relevant level's instructions

INSERT INTO ai_prompts (key, prompt_text, description, placeholders)
VALUES
  ('conversation.inline_corrections_on.a1_a2',
   'When the student makes an error: model the correct form naturally in your reply, then gently invite repetition ("Can you say: [correct phrase]?"). Praise the attempt before correcting. Max 1 error per turn. Never say "That''s wrong." Occasionally acknowledge notable {language} use by echoing the form naturally. Never praise and correct in the same turn.',
   'Inline correction style for A1/A2 beginners — model + invite repetition',
   ARRAY['language']),
  ('conversation.inline_corrections_on.b1_b2',
   'When the student makes an error: recast — use the correct form naturally in your next sentence, then elicit production ("And you?" / "How would you put that?"). Max 1 error per turn. Never explicitly name the error. Occasionally acknowledge notable {language} use by echoing the form naturally. Never praise and correct in the same turn.',
   'Inline correction style for B1/B2 intermediate — recast + elicitation',
   ARRAY['language']),
  ('conversation.inline_corrections_on.c1_c2',
   'When the student makes an error: recast only — weave the correct form into your reply naturally. Do not draw attention to it. The student will notice. Occasionally acknowledge notable {language} use by echoing the form naturally. Never praise and correct in the same turn.',
   'Inline correction style for C1/C2 advanced — pure recast',
   ARRAY['language'])
ON CONFLICT (key) DO NOTHING;

-- Deactivate old single inline_corrections_on (keep for reference)
UPDATE ai_prompts SET is_active = false WHERE key = 'conversation.inline_corrections_on' AND is_active = true;
