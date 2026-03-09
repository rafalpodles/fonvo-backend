-- Centralized AI prompt templates and model configuration

CREATE TABLE ai_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL UNIQUE,
    prompt_text TEXT NOT NULL,
    description TEXT,
    placeholders TEXT[] DEFAULT '{}',
    version INT NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ai_prompts_key ON ai_prompts(key);
CREATE INDEX idx_ai_prompts_active ON ai_prompts(is_active) WHERE is_active = true;

CREATE TABLE ai_model_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL UNIQUE,
    provider TEXT NOT NULL,
    model_id TEXT NOT NULL,
    display_name TEXT,
    extra_config JSONB DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ai_model_config_key ON ai_model_config(key);
