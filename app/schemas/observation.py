from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime


class ObservationDraftCreate(BaseModel):
    observee_id: int
    subject_id: int
    class_id: int


class ObservationDetailsUpdate(BaseModel):
    students_present: Optional[int] = None
    period: Optional[int] = None
    topic: Optional[str] = None

    @field_validator("period")
    def period_validator(cls, value):
        if value is not None and (value < 1 or value > 6):
            raise ValueError("Period must be between 1 and 6")
        return value


class MCQResponseInput(BaseModel):
    question_id: int
    selected_option_id: int
    explanation: Optional[str] = None


class RemarksInput(BaseModel):
    strengths: Optional[str] = None
    areas_of_improvement: Optional[str] = None
    suggestions_recommendations: Optional[str] = None


class ObservationResponse(BaseModel):
    observation_id: int
    observer_name: str
    observee_name: str
    subject_name: str
    class_name: str
    class_strength: Optional[int] = None
    students_present: Optional[int] = None
    period: Optional[int] = None
    topic: Optional[str] = None
    status: str
    observed_at: date
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
