-- Conversation scenarios table with JSONB translations
CREATE TABLE scenarios (
    id TEXT PRIMARY KEY,
    icon TEXT NOT NULL,
    category TEXT NOT NULL,
    minimum_level TEXT NOT NULL,
    maximum_level TEXT NOT NULL DEFAULT 'c2',
    system_prompt_addition TEXT NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    name JSONB NOT NULL,
    goals JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_scenarios_active ON scenarios (is_active) WHERE is_active = true;
CREATE INDEX idx_scenarios_level ON scenarios (minimum_level, maximum_level) WHERE is_active = true;
