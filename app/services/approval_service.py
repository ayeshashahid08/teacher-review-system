from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.observation_approval import ObservationApproval
from app.models.observation_substitute import ObservationSubstitute
from app.models.observation import Observation
from app.models.user import User
from app.models.coordinator_assignment import CoordinatorAssignment
from app.models.class_ import Class
from app.models.grade import Grade
from app.models.score import Score
from app.schemas.approval import ApprovalAction


# ─── Helpers ─────────────────────────────────────────────────────────────────

def get_school_level(class_id: int, db: Session) -> str:
    class_ = db.query(Class).filter(Class.class_id == class_id).first()
    grade = db.query(Grade).filter(Grade.grade_id == class_.grade_id).first()
    return grade.school_level


def get_grade_for_class(class_id: int, db: Session) -> Grade:
    class_ = db.query(Class).filter(Class.class_id == class_id).first()
    return db.query(Grade).filter(Grade.grade_id == class_.grade_id).first()


def get_chief_coordinator(school_level: str, db: Session) -> User:
    coord_type = "chief_primary" if school_level == "primary" else "chief_secondary"
    assignment = db.query(CoordinatorAssignment).filter(
        CoordinatorAssignment.coordinator_type == coord_type
    ).first()
    if not assignment:
        return None
    return db.query(User).filter(User.user_id == assignment.user_id).first()


def get_peer_coordinator(class_id: int, db: Session) -> User:
    grade = get_grade_for_class(class_id, db)
    if not grade:
        return None
    assignment = db.query(CoordinatorAssignment).filter(
        CoordinatorAssignment.coordinator_type == "peer",
        CoordinatorAssignment.grade_id == grade.grade_id
    ).first()
    if not assignment:
        return None
    return db.query(User).filter(User.user_id == assignment.user_id).first()


def get_subject_coordinator(subject_id: int, db: Session) -> User:
    assignment = db.query(CoordinatorAssignment).filter(
        CoordinatorAssignment.coordinator_type == "subject",
        CoordinatorAssignment.subject_id == subject_id
    ).first()
    if not assignment:
        return None
    return db.query(User).filter(User.user_id == assignment.user_id).first()


def get_required_roles_for_stage(observation_id: int, stage: int, db: Session) -> list:
    obs = db.query(Observation).filter(
        Observation.observation_id == observation_id
    ).first()
    school_level = get_school_level(obs.class_id, db)

    if stage == 1:
        return ["principal", "chief_coordinator"]
    else:
        if school_level == "primary":
            return ["peer_coordinator"]
        else:
            subject_coord = get_subject_coordinator(obs.subject_id, db)
            if subject_coord:
                return ["peer_coordinator", "subject_coordinator"]
            else:
                return ["peer_coordinator"]


def stage_fully_approved(observation_id: int, stage: int, db: Session) -> bool:
    approvals = db.query(ObservationApproval).filter(
        ObservationApproval.observation_id == observation_id,
        ObservationApproval.stage == stage,
        ObservationApproval.action == "approved"
    ).all()
    approved_roles = {a.role_in_stage for a in approvals}

    pending_substitute = db.query(ObservationSubstitute).filter(
        ObservationSubstitute.observation_id == observation_id,
        ObservationSubstitute.is_filled == False
    ).first()
    if pending_substitute:
        return False

    required_roles = get_required_roles_for_stage(observation_id, stage, db)
    for role in required_roles:
        if role not in approved_roles:
            return False

    return True


# ─── Initialize approval chain on submission ──────────────────────────────────

def initialize_approval_chain(observation_id: int, db: Session):
    obs = db.query(Observation).filter(
        Observation.observation_id == observation_id
    ).first()

    school_level = get_school_level(obs.class_id, db)
    substitutes_needed = []

    chief = get_chief_coordinator(school_level, db)
    if chief and chief.user_id == obs.observee_id:
        substitutes_needed.append("chief_coordinator")

    peer = get_peer_coordinator(obs.class_id, db)
    if peer and peer.user_id == obs.observee_id:
        substitutes_needed.append("peer_coordinator")

    if school_level != "primary":
        subject_coord = get_subject_coordinator(obs.subject_id, db)
        if subject_coord and subject_coord.user_id == obs.observee_id:
            substitutes_needed.append("subject_coordinator")

    if substitutes_needed:
        for role in substitutes_needed:
            db.add(ObservationSubstitute(
                observation_id=observation_id,
                original_role=role,
                is_filled=False
            ))
        obs.status = "substitute_needed"
    else:
        obs.status = "stage1_in_progress"

    db.commit()
    return substitutes_needed


# ─── Assign substitute ────────────────────────────────────────────────────────

def assign_substitute(
    observation_id: int,
    original_role: str,
    substitute_user_id: int,
    principal: User,
    db: Session
):
    if principal.designation != "principal":
        raise HTTPException(status_code=403, detail="Only principal can assign substitutes")

    substitute_record = db.query(ObservationSubstitute).filter(
        ObservationSubstitute.observation_id == observation_id,
        ObservationSubstitute.original_role == original_role,
        ObservationSubstitute.is_filled == False
    ).first()

    if not substitute_record:
        raise HTTPException(status_code=404, detail="No pending substitute needed for this role")

    substitute_user = db.query(User).filter(User.user_id == substitute_user_id).first()
    if not substitute_user:
        raise HTTPException(status_code=404, detail="Substitute user not found")

    # substitute cannot be the observee
    obs = db.query(Observation).filter(
        Observation.observation_id == observation_id
    ).first()
    if substitute_user_id == obs.observee_id:
        raise HTTPException(status_code=400, detail="Substitute cannot be the observee")

    substitute_record.substitute_user_id = substitute_user_id
    substitute_record.assigned_by = principal.user_id
    substitute_record.assigned_at = datetime.utcnow()
    substitute_record.is_filled = True

    db.flush()

    remaining = db.query(ObservationSubstitute).filter(
        ObservationSubstitute.observation_id == observation_id,
        ObservationSubstitute.is_filled == False
    ).first()

    if not remaining:
        obs.status = "stage1_in_progress"

    db.commit()
    return {"message": f"Substitute assigned for {original_role}"}


# ─── Determine approver role ──────────────────────────────────────────────────

def determine_approver_role(
    approver: User,
    observation_id: int,
    obs: Observation,
    school_level: str,
    db: Session
) -> tuple:

    # check if this person is a substitute first
    substitute = db.query(ObservationSubstitute).filter(
        ObservationSubstitute.observation_id == observation_id,
        ObservationSubstitute.substitute_user_id == approver.user_id,
        ObservationSubstitute.is_filled == True
    ).first()

    if substitute:
        role = substitute.original_role
        stage = 1 if role == "chief_coordinator" else 2

        # validate observation is at correct stage for this substitute
        expected_status = "stage1_in_progress" if stage == 1 else "stage2_in_progress"
        if obs.status != expected_status:
            raise HTTPException(
                status_code=400,
                detail=f"Observation is not at the correct stage for your role. Current: {obs.status}"
            )
        return role, stage

    # check principal
    if approver.designation == "principal":
        if obs.status != "stage1_in_progress":
            raise HTTPException(
                status_code=400,
                detail=f"Observation is not at principal approval stage. Current: {obs.status}"
            )
        return "principal", 1

    # check chief coordinator
    chief = get_chief_coordinator(school_level, db)
    if chief and chief.user_id == approver.user_id:
        if obs.status != "stage1_in_progress":
            raise HTTPException(
                status_code=400,
                detail=f"Observation is not at chief coordinator stage. Current: {obs.status}"
            )
        return "chief_coordinator", 1

    # check peer coordinator
    peer = get_peer_coordinator(obs.class_id, db)
    if peer and peer.user_id == approver.user_id:
        if obs.status != "stage2_in_progress":
            raise HTTPException(
                status_code=400,
                detail=f"Observation is not at peer coordinator stage. Current: {obs.status}"
            )
        return "peer_coordinator", 2

    # check subject coordinator (secondary only)
    if school_level != "primary":
        subject_coord = get_subject_coordinator(obs.subject_id, db)
        if subject_coord and subject_coord.user_id == approver.user_id:
            if obs.status != "stage2_in_progress":
                raise HTTPException(
                    status_code=400,
                    detail=f"Observation is not at subject coordinator stage. Current: {obs.status}"
                )
            return "subject_coordinator", 2

    raise HTTPException(
        status_code=403,
        detail="You are not authorized to approve this observation"
    )


# ─── Main approve function ────────────────────────────────────────────────────

def approve_observation(
    data: ApprovalAction,
    observation_id: int,
    approver: User,
    db: Session
):
    obs = db.query(Observation).filter(
        Observation.observation_id == observation_id
    ).first()
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")

    if obs.status == "substitute_needed":
        raise HTTPException(
            status_code=400,
            detail="Principal must assign substitute reviewers before approval can proceed"
        )

    if obs.status not in ["stage1_in_progress", "stage2_in_progress"]:
        raise HTTPException(
            status_code=400,
            detail=f"Observation cannot be approved in its current status: {obs.status}"
        )

    school_level = get_school_level(obs.class_id, db)
    role_in_stage, stage = determine_approver_role(
        approver, observation_id, obs, school_level, db
    )

    # validate action permissions
    if data.action == "revision_requested" and approver.designation != "principal":
        raise HTTPException(
            status_code=403,
            detail="Only principal can request revision"
        )

    # handle revision — cancel everything, send back to draft
    if data.action == "revision_requested":
        db.query(ObservationApproval).filter(
            ObservationApproval.observation_id == observation_id
        ).delete()
        db.query(ObservationSubstitute).filter(
            ObservationSubstitute.observation_id == observation_id
        ).delete()
        obs.status = "draft"
        db.commit()
        return {"message": "Observation sent back for revision. All approvals cancelled."}

    # check this person hasn't already approved at this stage
    already_approved = db.query(ObservationApproval).filter(
        ObservationApproval.observation_id == observation_id,
        ObservationApproval.approver_id == approver.user_id,
        ObservationApproval.stage == stage
    ).first()
    if already_approved:
        raise HTTPException(
            status_code=400,
            detail="You have already acted on this observation at this stage"
        )

    # record the approval
    new_approval = ObservationApproval(
        observation_id=observation_id,
        approver_id=approver.user_id,
        stage=stage,
        role_in_stage=role_in_stage,
        action=data.action,
        comments=data.comments,
        acted_at=datetime.utcnow(),
        is_substitute=bool(
            db.query(ObservationSubstitute).filter(
                ObservationSubstitute.observation_id == observation_id,
                ObservationSubstitute.substitute_user_id == approver.user_id
            ).first()
        )
    )
    db.add(new_approval)
    db.commit()

    # check if stage is now complete
    if stage_fully_approved(observation_id, stage, db):
        if stage == 1:
            obs.status = "stage2_in_progress"
            db.commit()
        else:
            obs.status = "approved"
            db.commit()
            # trigger score calculation
            try:
                from app.services.score_service import calculate_observation_score
                calculate_observation_score(observation_id, db)
            except Exception as e:
                print(f"Score calculation failed for obs {observation_id}: {e}")

    return new_approval


# ─── Queue endpoints ──────────────────────────────────────────────────────────

def get_pending_approvals(approver: User, db: Session) -> list:
    if approver.designation == "principal":
        return db.query(Observation).filter(
            Observation.status.in_(["stage1_in_progress", "substitute_needed"])
        ).all()

    coord_assignment = db.query(CoordinatorAssignment).filter(
        CoordinatorAssignment.user_id == approver.user_id
    ).first()

    if not coord_assignment:
        return []

    if coord_assignment.coordinator_type in ["chief_primary", "chief_secondary"]:
        level = "primary" if coord_assignment.coordinator_type == "chief_primary" else "secondary"
        matching_grades = db.query(Grade).filter(
            Grade.school_level.in_(
                ["primary"] if level == "primary" else ["secondary", "higher_secondary"]
            )
        ).all()
        grade_ids = [g.grade_id for g in matching_grades]
        matching_classes = db.query(Class).filter(
            Class.grade_id.in_(grade_ids)
        ).all()
        class_ids = [c.class_id for c in matching_classes]
        return db.query(Observation).filter(
            Observation.status == "stage1_in_progress",
            Observation.class_id.in_(class_ids)
        ).all()

    if coord_assignment.coordinator_type == "peer":
        matching_classes = db.query(Class).filter(
            Class.grade_id == coord_assignment.grade_id
        ).all()
        class_ids = [c.class_id for c in matching_classes]
        return db.query(Observation).filter(
            Observation.status == "stage2_in_progress",
            Observation.class_id.in_(class_ids)
        ).all()

    if coord_assignment.coordinator_type == "subject":
        return db.query(Observation).filter(
            Observation.status == "stage2_in_progress",
            Observation.subject_id == coord_assignment.subject_id
        ).all()

    return []


def get_substitute_needed_queue(principal: User, db: Session) -> list:
    if principal.designation != "principal":
        raise HTTPException(status_code=403, detail="Only principal can view this queue")

    return db.query(ObservationSubstitute).filter(
        ObservationSubstitute.is_filled == False
    ).all()


def format_approval_response(approval: ObservationApproval, db: Session) -> dict:
    approver = db.query(User).filter(User.user_id == approval.approver_id).first()
    return {
        "approval_id": approval.approval_id,
        "observation_id": approval.observation_id,
        "approver_name": f"{approver.first_name} {approver.last_name}",
        "stage": approval.stage,
        "role_in_stage": approval.role_in_stage,
        "action": approval.action,
        "comments": approval.comments,
        "acted_at": approval.acted_at,
        "is_substitute": approval.is_substitute,
    }
