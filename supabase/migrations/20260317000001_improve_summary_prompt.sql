-- FNV-190: Improve conversation summary — impersonal, topic-focused
-- Changes summary instruction from "Write a one-sentence summary" to topic-focused noun phrases.
UPDATE ai_prompts
SET prompt_text = REPLACE(
    prompt_text,
    '3. Summary: Write a one-sentence summary of the conversation in {device_language}.',
    '3. Summary: Write a short topic-focused summary in {device_language}. Use noun phrases describing what was discussed, not what the student did. Example: ''Hotel reservation and breakfast options'' instead of ''Student asks about hotels''.'
)
WHERE key = 'analysis.post_conversation'
  AND prompt_text LIKE '%Write a one-sentence summary%';
