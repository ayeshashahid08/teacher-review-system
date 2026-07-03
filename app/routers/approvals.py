from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.approval import (ApprovalAction, ApprovalResponse)
from app.services.approval_service import (approve_observation, format_approval_response, get_pending_approvals)

from app.database import get_db

from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/approvals", tags = ["Approval"])

@router.post("/{observation_id}/approve", response_model=ApprovalResponse)
def approval(data: ApprovalAction, observation_id: int, approver: User =Depends(get_current_user), db: Session = Depends(get_db)):
    app_obs = approve_observation(data, observation_id, approver, db)
    return format_approval_response(app_obs, db)

@router.get("/pending")
def pending_approvals(approver: User =Depends(get_current_user), db :Session = Depends(get_db)):
    return get_pending_approvals(approver, db)
