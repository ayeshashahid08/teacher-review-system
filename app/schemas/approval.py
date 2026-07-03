from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class ApprovalAction(BaseModel):
    action: str
    comments: Optional[str] = None

    @field_validator("action")
    def validate_action(cls, value):
        allowed = ["approved", "rejected", "revision_requested"]
        if value not in allowed:
            raise ValueError(f"Action must be one of: {allowed}")
        return value


class ApprovalResponse(BaseModel):
    approval_id: int
    observation_id: int
    approver_name: str
    stage: str
    action: str
    comments: Optional[str] = None
    acted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
