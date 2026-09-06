from pydantic import BaseModel
from typing import Optional


class CoordinatorAssignmentCreate(BaseModel):
    user_id: int
    coordinator_type: str
    grade_id: Optional[int] = None      # for peer coordinators
    subject_id: Optional[int] = None    # for subject coordinators


class CoordinatorAssignmentResponse(BaseModel):
    assignment_id: int
    user_id: int
    coordinator_name: str
    coordinator_type: str
    class_display: Optional[str] = None
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True
