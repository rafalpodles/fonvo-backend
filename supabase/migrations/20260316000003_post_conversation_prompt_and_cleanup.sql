-- Add post_conversation batch analysis prompt (was hardcoded in Swift)
INSERT INTO ai_prompts (key, prompt_text, description, placeholders)
VALUES (
  'analysis.post_conversation',
  'You are a language learning analyst. Analyze the following {language} conversation between a student (level: {level}) and their tutor ({character_name}).

Perform ALL four tasks and return a single JSON object:

1. Error Analysis: Find grammar, vocabulary, and structure errors in the student''s messages.{voice_note}
2. Vocabulary Extraction: Extract interesting/useful {language} words the student encountered or should learn.
3. Summary: Write a one-sentence summary of the conversation in {device_language}.
4. Level Detection: Based on the student''s language use, estimate their CEFR level (a1, a2, b1, b2, c1, c2).

Return ONLY this JSON (no markdown, no explanation):
{
  "errors": [
    {
      "original_text": "what student said",
      "corrected_text": "correct version",
      "explanation": "brief explanation in {device_language}",
      "error_type": "{error_types}",
      "severity": "minor|major",
      "message_index": 0
    }
  ],
  "vocabulary": [
    {
      "term": "word in {language}",
      "translation": "translation in {device_language}",
      "context_sentence": "example sentence"
    }
  ],
  "summary": "One sentence summary in {device_language}",
  "detected_level": "b1"
}

If no errors found, return empty errors array. Extract 3-10 vocabulary items.',
  'Batch post-conversation analysis prompt — errors, vocabulary, summary, level detection in one call',
  ARRAY['language', 'level', 'character_name', 'device_language', 'error_types', 'voice_note']
)
ON CONFLICT (key) DO NOTHING;

-- Deactivate dead prompts (no longer used after PostConversationAnalyzer refactor)
UPDATE ai_prompts SET is_active = false WHERE key IN (
  'conversation.summary',
  'conversation.inline_corrections_on',
  'analysis.error_analysis',
  'analysis.error_analysis_level_instruction',
  'analysis.error_analysis_return_format_errors_only',
  'analysis.error_analysis_return_format_with_level',
  'analysis.error_analysis_voice_disclaimer',
  'analysis.vocabulary_extraction'
) AND is_active = true;
