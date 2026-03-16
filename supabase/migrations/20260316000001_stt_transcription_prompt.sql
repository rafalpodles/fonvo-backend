-- STT transcription prompt — hints the model to transcribe in the target language
INSERT INTO ai_prompts (key, prompt_text, description, placeholders)
VALUES (
  'stt.transcription_prompt',
  'This is a {language} language lesson. The student is practicing {language}. Transcribe the audio as {language} text only. If you hear words from another language, transcribe them as the closest {language} equivalent.',
  'Prompt hint for STT model to enforce target language transcription',
  ARRAY['language']
)
ON CONFLICT (key) DO NOTHING;
