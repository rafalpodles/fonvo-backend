from pydantic import BaseModel


class UserPreferencesResponse(BaseModel):
    target_language: str
    appearance: str
    use_realtime_api: bool
    language_levels: dict[str, str]
    preferred_topics: dict[str, list[str]]


class UserPreferencesUpdateRequest(BaseModel):
    target_language: str | None = None
    appearance: str | None = None
    use_realtime_api: bool | None = None
    language_levels: dict[str, str] | None = None
    preferred_topics: dict[str, list[str]] | None = None
