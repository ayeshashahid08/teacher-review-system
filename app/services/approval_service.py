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
from app.models.subject import Subject
from app.schemas.approval import ApprovalAction


# ─── Helper: get school level for a class ───────────────────────────────────

def get_school_level(class_id: int, db: Session) -> str:
    class_ = db.query(Class).filter(Class.class_id == class_id).first()
    grade = db.query(Grade).filter(Grade.grade_id == class_.grade_id).first()
    return grade.school_level  # primary, secondary, higher_secondary


# ─── Helper: find chief coordinator for a section ────────────────────────────

def get_chief_coordinator(school_level: str, db: Session) -> User:
    coord_type = "chief_primary" if school_level == "primary" else "chief_secondary"
    assignment = db.query(CoordinatorAssignment).filter(
        CoordinatorAssignment.coordinator_type == coord_type
    ).first()
    if not assignment:
        raise HTTPException(status_code=500,
                          detail=f"No {coord_type} coordinator assigned in system")
    return db.query(User).filter(User.user_id == assignment.user_id).first()


# ─── Helper: find peer coordinator for a class ───────────────────────────────

def get_peer_coordinator(class_id: int, db: Session) -> User:
    assignment = db.query(CoordinatorAssignment).filter(
        CoordinatorAssignment.coordinator_type == "peer",
        CoordinatorAssignment.class_id == class_id
    ).first()
    if not assignment:
        raise HTTPException(status_code=500,
                          detail="No peer coordinator assigned for this class")
    return db.query(User).filter(User.user_id == assignment.user_id).first()


# ─── Helper: find subject coordinator ────────────────────────────────────────

def get_subject_coordinator(subject_id: int, db: Session) -> User:
    assignment = db.query(CoordinatorAssignment).filter(
        CoordinatorAssignment.coordinator_type == "subject",
        CoordinatorAssignment.subject_id == subject_id
    ).first()
    if not assignment:
        return None  # not every subject has one
    return db.query(User).filter(User.user_id == assignment.user_id).first()


# ─── Helper: check if all required approvals for a stage are done ────────────

def stage_fully_approved(observation_id: int, stage: int, db: Session) -> bool:
    approvals = db.query(ObservationApproval).filter(
        ObservationApproval.observation_id == observation_id,
        ObservationApproval.stage == stage,
        ObservationApproval.action == "approved"
    ).all()

    approved_roles = {a.role_in_stage for a in approvals}

    pending = db.query(ObservationSubstitute).filter(
        ObservationSubstitute.observation_id == observation_id,
        ObservationSubstitute.is_filled == False
    ).first()

    if pending:
        return False

    substitutes = db.query(ObservationSubstitute).filter(
        ObservationSubstitute.observation_id == observation_id,
        ObservationSubstitute.is_filled == True
    ).all()

    required_roles = get_required_roles_for_stage(observation_id, stage, db)

    for role in required_roles:
        is_covered = role in approved_roles
        if not is_covered:
            return False

    return True


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
            return ["peer_coordinator", "subject_coordinator"]


# ─── Main: called when observation is submitted ───────────────────────────────

def initialize_approval_chain(observation_id: int, db: Session):
    obs = db.query(Observation).filter(
        Observation.observation_id == observation_id
    ).first()

    observee = db.query(User).filter(User.user_id == obs.observee_id).first()
    school_level = get_school_level(obs.class_id, db)

    substitutes_needed = []

    # check if observee is chief coordinator
    chief = get_chief_coordinator(school_level, db)
    if chief and chief.user_id == obs.observee_id:
        substitutes_needed.append("chief_coordinator")

    # check if observee is peer coordinator
    peer = get_peer_coordinator(obs.class_id, db)
    if peer and peer.user_id == obs.observee_id:
        substitutes_needed.append("peer_coordinator")

    # check if observee is subject coordinator (secondary only)
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


# ─── Main: principal assigns substitute ──────────────────────────────────────

def assign_substitute(
    observation_id: int,
    original_role: str,
    substitute_user_id: int,
    principal: User,
    db: Session
):
    if principal.designation != "principal":
        raise HTTPException(status_code=403,
                          detail="Only principal can assign substitutes")

    substitute_record = db.query(ObservationSubstitute).filter(
        ObservationSubstitute.observation_id == observation_id,
        ObservationSubstitute.original_role == original_role,
        ObservationSubstitute.is_filled == False
    ).first()

    if not substitute_record:
        raise HTTPException(status_code=404,
                          detail="No pending substitute needed for this role")

    substitute_user = db.query(User).filter(
        User.user_id == substitute_user_id
    ).first()
    if not substitute_user:
        raise HTTPException(status_code=404, detail="Substitute user not found")

    substitute_record.substitute_user_id = substitute_user_id
    substitute_record.assigned_by = principal.user_id
    substitute_record.assigned_at = datetime.utcnow()
    substitute_record.is_filled = True
    db.flush() 
    # check if all substitutes are now filled
    remaining = db.query(ObservationSubstitute).filter(
        ObservationSubstitute.observation_id == observation_id,
        ObservationSubstitute.is_filled == False
    ).first()

    # if not remaining:
    #     obs = db.query(Observation).filter(
    #         Observation.observation_id == observation_id
    #     ).first()
    #     obs.status = "stage1_in_progress"

    # db.commit()
    # return {"message": f"Substitute assigned for {original_role}"}
    if not remaining:
        obs = db.query(Observation).filter(
            Observation.observation_id == observation_id
        ).first()
        print(f"No remaining substitutes. Current obs status: {obs.status}")
        obs.status = "stage1_in_progress"
        print(f"Updated obs status to: {obs.status}")
    else:
        print(f"Still has remaining unfilled substitutes")

    db.commit()
    
    # verify after commit
    obs_check = db.query(Observation).filter(
        Observation.observation_id == observation_id
    ).first()
    print(f"Status after commit: {obs_check.status}")
    
    return {"message": f"Substitute assigned for {original_role}"}


# ─── Main: approve observation ────────────────────────────────────────────────

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

    school_level = get_school_level(obs.class_id, db)

    # determine what role this approver plays in this observation
    role_in_stage, stage = determine_approver_role(
        approver, observation_id, obs, school_level, db
    )

    # validate action permissions
    if data.action == "revision_requested" and approver.designation != "principal":
        raise HTTPException(
            status_code=403,
            detail="Only principal can request revision"
        )

    if data.action == "revision_requested":
        # cancel all existing approvals and send back to draft
        db.query(ObservationApproval).filter(
            ObservationApproval.observation_id == observation_id
        ).delete()
        obs.status = "draft"
        db.commit()
        return {"message": "Observation sent back for revision"}

    # check this person hasn't already approved
    already_approved = db.query(ObservationApproval).filter(
        ObservationApproval.observation_id == observation_id,
        ObservationApproval.approver_id == approver.user_id,
        ObservationApproval.stage == stage
    ).first()
    if already_approved:
        raise HTTPException(status_code=400,
                          detail="You have already acted on this observation")

    # record the approval
    new_approval = ObservationApproval(
        observation_id=observation_id,
        approver_id=approver.user_id,
        stage=stage,
        role_in_stage=role_in_stage,
        action=data.action,
        comments=data.comments,
        acted_at=datetime.utcnow()
    )
    db.add(new_approval)
    db.commit()

    # check if this stage is now complete
    if stage_fully_approved(observation_id, stage, db):
        if stage == 1:
            obs.status = "stage2_in_progress"
        else:
            obs.status = "approved"
        db.commit()

    return new_approval


def determine_approver_role(
    approver: User,
    observation_id: int,
    obs: Observation,
    school_level: str,
    db: Session
) -> tuple:
    """Returns (role_in_stage, stage_number)"""

    # check if this person is a substitute
    substitute = db.query(ObservationSubstitute).filter(
        ObservationSubstitute.observation_id == observation_id,
        ObservationSubstitute.substitute_user_id == approver.user_id,
        ObservationSubstitute.is_filled == True
    ).first()

    if substitute:
        role = substitute.original_role
        stage = 1 if role == "chief_coordinator" else 2
        return role, stage

    # check principal
    if approver.designation == "principal":
        if obs.status == "stage1_in_progress":
            return "principal", 1
        raise HTTPException(status_code=400,
                          detail="Observation is not at principal approval stage")

    # check chief coordinator
    chief = get_chief_coordinator(school_level, db)
    if chief and chief.user_id == approver.user_id:
        if obs.status == "stage1_in_progress":
            return "chief_coordinator", 1
        raise HTTPException(status_code=400,
                          detail="Observation is not at chief coordinator stage")

    # check peer coordinator
    peer = get_peer_coordinator(obs.class_id, db)
    if peer and peer.user_id == approver.user_id:
        if obs.status == "stage2_in_progress":
            return "peer_coordinator", 2
        raise HTTPException(status_code=400,
                          detail="Observation is not at peer coordinator stage")

    # check subject coordinator (secondary only)
    if school_level != "primary":
        subject_coord = get_subject_coordinator(obs.subject_id, db)
        if subject_coord and subject_coord.user_id == approver.user_id:
            if obs.status == "stage2_in_progress":
                return "subject_coordinator", 2
            raise HTTPException(status_code=400,
                              detail="Observation is not at subject coordinator stage")

    raise HTTPException(status_code=403,
                      detail="You are not authorized to approve this observation")


# ─── Queue endpoints ──────────────────────────────────────────────────────────

def get_pending_approvals(approver: User, db: Session) -> list:
    if approver.designation == "principal":
        return db.query(Observation).filter(
            Observation.status.in_(["stage1_in_progress", "substitute_needed"])
        ).all()

    # find what coordinator role this person has
    coord_assignment = db.query(CoordinatorAssignment).filter(
        CoordinatorAssignment.user_id == approver.user_id
    ).first()

    if not coord_assignment:
        return []

    if coord_assignment.coordinator_type in ["chief_primary", "chief_secondary"]:
        school_level = "primary" if coord_assignment.coordinator_type == "chief_primary" else "secondary"
        # get all classes in this section
        classes = db.query(Class).join(Grade).filter(
            Grade.school_level.in_(
                ["primary"] if school_level == "primary"
                else ["secondary", "higher_secondary"]
            )
        ).all()
        class_ids = [c.class_id for c in classes]
        return db.query(Observation).filter(
            Observation.status == "stage1_in_progress",
            Observation.class_id.in_(class_ids)
        ).all()

    if coord_assignment.coordinator_type == "peer":
        return db.query(Observation).filter(
            Observation.status == "stage2_in_progress",
            Observation.class_id == coord_assignment.class_id
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
