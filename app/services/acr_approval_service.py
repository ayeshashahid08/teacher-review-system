from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.acr_approval import ACRApproval
from app.models.acr import ACRReport
from app.models.user import User
from app.schemas.acr import AcrApprovalAction, AcrApprovalResponse


def submit_acr_for_approval(acr_id: int, reporter: User, db: Session):
    acr = db.query(ACRReport).filter(ACRReport.acr_id == acr_id).first()
    if not acr:
        raise HTTPException(status_code=404, detail="ACR report not found")

    if acr.reporter_id != reporter.user_id:
        raise HTTPException(status_code=403, detail="Only the reporter can submit this ACR")

    if acr.status != "finalized":
        raise HTTPException(status_code=400, detail="ACR must be finalized before submitting for approval")

    acr.status = "pending_approval"
    db.commit()
    return {"message": "ACR submitted for principal approval"}


def approve_acr(acr_id: int, data: AcrApprovalAction, principal: User, db: Session):
    if principal.designation != "principal":
        raise HTTPException(status_code=403, detail="Only principal can approve ACR reports")

    acr = db.query(ACRReport).filter(ACRReport.acr_id == acr_id).first()
    if not acr:
        raise HTTPException(status_code=404, detail="ACR report not found")

    if acr.status != "pending_approval":
        raise HTTPException(status_code=400, detail="ACR is not pending approval")

    existing = db.query(ACRApproval).filter(ACRApproval.acr_id == acr_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="This ACR has already been acted on")

    new_approval = ACRApproval(
        acr_id=acr_id,
        principal_id=principal.user_id,
        action=data.action,
        comments=data.comments,
        acted_at=datetime.utcnow()
    )
    db.add(new_approval)

    if data.action == "approved":
        acr.status = "approved"
    elif data.action == "revision_requested":
        acr.status = "draft"
        db.query(ACRApproval).filter(ACRApproval.acr_id == acr_id).delete()

    db.commit()
    db.refresh(new_approval) if data.action == "approved" else None
    # return {"message": f"ACR {data.action}", "acr_status": acr.status}
    # in service — change return for approved case

    return new_approval  # return the ACRApproval object


def get_pending_acr_approvals(principal: User, db: Session):
    if principal.designation != "principal":
        raise HTTPException(status_code=403, detail="Only principal can view ACR approval queue")

    return db.query(ACRReport).filter(
        ACRReport.status == "pending_approval"
    ).all()


def format_acr_approval_response(approval: ACRApproval, db: Session) -> dict:
    principal = db.query(User).filter(User.user_id == approval.principal_id).first()
    return {
        "approval_id": approval.approval_id,
        "acr_id": approval.acr_id,
        "principal_name": f"{principal.first_name} {principal.last_name}",
        "action": approval.action,
        "comments": approval.comments,
        "acted_at": approval.acted_at,
    }
