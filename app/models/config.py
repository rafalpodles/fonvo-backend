from datetime import datetime

from pydantic import BaseModel


class PromptResponse(BaseModel):
    key: str
    prompt_text: str
    description: str | None = None
    placeholders: list[str] = []
    version: int = 1
    updated_at: datetime


class ModelConfigResponse(BaseModel):
    key: str
    provider: str
    model_id: str
    display_name: str | None = None
    extra_config: dict = {}


class ConfigBundle(BaseModel):
    prompts: dict[str, str]
    models: dict[str, ModelConfigResponse]
    hash: str


class PromptUpdateRequest(BaseModel):
    prompt_text: str
    description: str | None = None
    placeholders: list[str] | None = None


class ModelConfigUpdateRequest(BaseModel):
    provider: str | None = None
    model_id: str | None = None
    display_name: str | None = None
    extra_config: dict | None = None
