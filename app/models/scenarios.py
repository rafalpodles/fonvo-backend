from datetime import datetime

from pydantic import BaseModel


class ScenarioResponse(BaseModel):
    """Public scenario response — locale-resolved strings."""

    id: str
    icon: str
    category: str
    minimum_level: str
    maximum_level: str
    system_prompt_addition: str
    name: str
    goals: list[str]
    sort_order: int


class ScenarioListResponse(BaseModel):
    scenarios: list[ScenarioResponse]
    hash: str


class AdminScenarioResponse(BaseModel):
    """Admin scenario response — full JSONB translations."""

    id: str
    icon: str
    category: str
    minimum_level: str
    maximum_level: str
    system_prompt_addition: str
    sort_order: int
    is_active: bool
    name: dict
    goals: dict
    created_at: datetime
    updated_at: datetime


class ScenarioCreateRequest(BaseModel):
    id: str
    icon: str
    category: str
    minimum_level: str
    maximum_level: str = "c2"
    system_prompt_addition: str
    sort_order: int = 0
    name: dict
    goals: dict


class ScenarioUpdateRequest(BaseModel):
    icon: str | None = None
    category: str | None = None
    minimum_level: str | None = None
    maximum_level: str | None = None
    system_prompt_addition: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None
    name: dict | None = None
    goals: dict | None = None
