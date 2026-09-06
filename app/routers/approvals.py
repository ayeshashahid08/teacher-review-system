from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.approval import ApprovalAction, ApprovalResponse
from app.services.approval_service import (
    approve_observation,
    get_pending_approvals,
    assign_substitute,
    get_substitute_needed_queue,
    format_approval_response,
)
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/approvals", tags=["Approvals"])

# ============================================================
# 1. STATIC ROUTES FIRST
# ============================================================

@router.get("/pending")
def pending_approvals(
    approver: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_pending_approvals(approver, db)


@router.get("/substitute-needed")
def substitute_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_substitute_needed_queue(current_user, db)


# ============================================================
# 2. PARAMETERIZED ROUTES ({observation_id}) SECOND
# ============================================================

@router.post("/{observation_id}/approve")
def approval(
    observation_id: int,
    data: ApprovalAction,
    approver: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = approve_observation(data, observation_id, approver, db)
    if isinstance(result, dict):
        return result
    return format_approval_response(result, db)


@router.post("/{observation_id}/assign-substitute")
def assign_sub(
    observation_id: int,
    original_role: str = Query(...),
    substitute_user_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return assign_substitute(
        observation_id, original_role, substitute_user_id, current_user, db
    )