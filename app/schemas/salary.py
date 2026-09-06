from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SalaryEligibilityDecision(BaseModel):
    is_eligible: bool
    decision_notes: Optional[str] = None


class SalaryEligibilityResponse(BaseModel):
    user_id: int
    teacher_name: str
    academic_year: str
    is_eligible: Optional[bool] = None
    decided_by: Optional[str] = None
    decision_notes: Optional[str] = None
    decided_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TeacherSalarySummary(BaseModel):
    user_id: int
    teacher_name: str
    designation: str
    years_of_service: Optional[int] = None
    teaching_load: Optional[int] = None
    academic_year: str
    total_observations: int
    approved_observations: int
    average_score: Optional[float] = None
    lowest_score: Optional[float] = None
    highest_score: Optional[float] = None
    acr_grade: Optional[str] = None
    acr_percentage: Optional[float] = None
    days_present: Optional[int] = None
    total_working_days: Optional[int] = None
    attendance_percentage: Optional[float] = None
    increment_decision: Optional[SalaryEligibilityResponse] = None