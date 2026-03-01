from pydantic import BaseModel


class ProfileResponse(BaseModel):
    display_name: str | None
    email: str | None


class ProfileUpdateRequest(BaseModel):
    display_name: str
