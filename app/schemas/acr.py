from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class AcrCreate(BaseModel):
    reported_id: int
    days_present: int


class AcrResponseInput(BaseModel):
    acr_question_id: int
    acr_response_marks: int

    @field_validator("acr_response_marks")
    def validate_marks(cls, value):
        if value < 0:
            raise ValueError("Marks cannot be negative")
        return value


class ACRReportResponse(BaseModel):
    acr_id: int
    academic_year: str
    reported_name: str
    reporter_name: str
    days_present: Optional[int] = None
    total_marks: Optional[int] = None
    total_working_days: Optional[int] = None
    percentage: Optional[float] = None
    grade: Optional[str] = None
    status: str
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AcrApprovalAction(BaseModel):
    action:str
    comments:Optional[str] = None

    @field_validator("action")
    def validate_action(cls, value):
        allowed = ["approved", "revision_requested"]
        if value not in allowed:
            raise ValueError(f"Action must be one of: {allowed}")
        return value

class AcrApprovalResponse(BaseModel):
    approval_id: int
    acr_id: int
    principal_name: Optional[str] = None
    action: str
    comments: Optional[str] = None
    acted_at: Optional[datetime] = None

    class Config:
        from_attributes = True