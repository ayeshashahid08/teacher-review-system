from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.observation_approval import ObservationApproval
from app.models.observation import Observation
from app.models.user import User
from app.schemas.approval import ApprovalAction


stage_map = {
    "principal": {
        "expected_status": "submitted",
        "stage_name": "principal",
        "next_status_approved": "pending_chief_coordinator",
    },
    "coordinator": {
        "expected_status": "pending_chief_coordinator",
        "stage_name": "chief_coordinator",
        "next_status_approved": "pending_peer_coordinator",
    },
    "peer_coordinator": {
        "expected_status": "pending_peer_coordinator",
        "stage_name": "peer_coordinator",
        "next_status_approved": "approved",
    },
}


def approve_observation(data: ApprovalAction, observation_id: int, approver: User, db: Session):
    obs = db.query(Observation).filter(Observation.observation_id == observation_id).first()
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")

    role = approver.designation
    if role not in stage_map:
        raise HTTPException(status_code=403, detail="Your role cannot perform approvals")

    stage_info = stage_map[role]

    if obs.status != stage_info["expected_status"]:
        raise HTTPException(
            status_code=400,
            detail=f"Observation is not at the correct stage for your role. Current status: {obs.status}"
        )
    
    if (role != "principal") and (data.action == "rejected" or data.action=="revision_requested"):
        raise HTTPException(status_code=403, detail="Your role cannot perform rejections or request a revision")

    new_approval = ObservationApproval(
        approver_id=approver.user_id,
        observation_id=observation_id,
        stage=stage_info["stage_name"],
        action=data.action,
        comments=data.comments,
        acted_at=datetime.utcnow()
    )
    db.add(new_approval)

    if data.action == "approved":
        obs.status = stage_info["next_status_approved"]
    elif data.action == "rejected":
        obs.status = "rejected"
    elif data.action == "revision_requested":
        obs.status = "draft"

    db.commit()
    db.refresh(new_approval)
    return new_approval


def format_approval_response(approval: ObservationApproval, db: Session) -> dict:
    approver = db.query(User).filter(User.user_id == approval.approver_id).first()
    return {
        "approval_id": approval.approval_id,
        "observation_id": approval.observation_id,
        "approver_name": f"{approver.first_name} {approver.last_name}",
        "stage": approval.stage,
        "action": approval.action,
        "comments": approval.comments,
        "acted_at": approval.acted_at,
    }


def get_pending_approvals(approver: User, db: Session) -> list:
    role = approver.designation
    if role not in stage_map:
        raise HTTPException(status_code=403, detail="Your role has no approval queue")

    expected_status = stage_map[role]["expected_status"]
    observations = db.query(Observation).filter(
        Observation.status == expected_status
    ).all()
    return observations
