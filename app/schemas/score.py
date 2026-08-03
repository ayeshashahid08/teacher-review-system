from pydantic import BaseModel, field_validator
from typing import Optional


class ScoreOverrideInput(BaseModel):
    written_score: float
    override_reason: str

    @field_validator("written_score")
    def validate_range(cls, value):
        if value < 0 or value > 9:
            raise ValueError("written_score must be between 0 and 9 (max points for the descriptive section)")
        return value

    @field_validator("override_reason")
    def validate_reason_not_empty(cls, value):
        if not value or not value.strip():
            raise ValueError("override_reason is required when overriding a score")
        return value


class ScoreDetailResponse(BaseModel):
    observation_id: int
    mcq_score: float
    ai_score: Optional[float] = None
    written_score: Optional[float] = None
    max_possible_score: float
    total_score: float
    percentage: float
    grade: str
    is_overridden: bool
    override_reason: Optional[str] = None

    class Config:
        from_attributes = True