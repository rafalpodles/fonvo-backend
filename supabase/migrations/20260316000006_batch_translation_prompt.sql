-- Batch translation prompt (was hardcoded in TranscriptViewModel)
INSERT INTO ai_prompts (key, prompt_text, description, placeholders)
VALUES (
  'translation.batch',
  'Translate each numbered message from {language} to {device_language}. Return ONLY a JSON array of objects with "index" (Int) and "translation" (String). Keep the same indices. No extra text.',
  'Batch translate all conversation messages for transcript view',
  ARRAY['language', 'device_language']
)
ON CONFLICT (key) DO NOTHING;
