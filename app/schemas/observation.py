from pydantic import field_validator, BaseModel
from typing import Optional

class ObservationCreate(BaseModel):
    observee_id: int
    subject_id: int
    class_id: int
    students_present: int
    period: int
    topic: str

    @field_validator("period")
    def period_validator(cls, value):
        if value < 1 or value > 6:
            raise ValueError("Period must be between 1 and 6")
        return value
class ObservationResponse(BaseModel):
    observation_id: int
    observer_id: int
    observee_id: int
    subject_id: int
    class_id: int
    students_present: int
    period: int
    topic: str
    status: str
    observed_at: date
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

