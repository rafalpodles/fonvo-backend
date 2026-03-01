from pydantic import BaseModel


class StreakInfoResponse(BaseModel):
    current_streak: int
    has_activity_today: bool
