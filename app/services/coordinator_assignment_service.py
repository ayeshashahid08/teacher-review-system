from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.coordinator_assignment import CoordinatorAssignment
from app.models.user import User
from app.models.class_ import Class
from app.models.grade import Grade
from app.models.subject import Subject
from app.schemas.coordinator_assignment import CoordinatorAssignmentCreate

VALID_TYPES = ["chief_primary", "chief_secondary", "peer", "subject"]


def create_coordinator_assignment(
    data: CoordinatorAssignmentCreate,
    creator: User,
    db: Session
):
    if creator.designation not in ["admin", "principal"]:
        raise HTTPException(status_code=403, detail="Only admin or principal can manage coordinator assignments")

    if data.coordinator_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"coordinator_type must be one of {VALID_TYPES}")

    user = db.query(User).filter(User.user_id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.designation not in ["teacher"]:
        raise HTTPException(status_code=400, detail="Only teachers can be assigned coordinator roles")
    if data.coordinator_type == "peer" and not data.grade_id:
        raise HTTPException(status_code=400, detail="grade_id is required for peer coordinator")

    if data.coordinator_type == "subject" and not data.subject_id:
        raise HTTPException(status_code=400, detail="subject_id is required for subject coordinator")

    if data.coordinator_type in ["chief_primary", "chief_secondary"] and (data.grade_id or data.subject_id):
        raise HTTPException(status_code=400, detail="Chief coordinators don't need class or subject assignment")

    existing = db.query(CoordinatorAssignment).filter(
        CoordinatorAssignment.coordinator_type == data.coordinator_type,
        CoordinatorAssignment.grade_id == data.grade_id,
        CoordinatorAssignment.subject_id == data.subject_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A coordinator is already assigned for this role. Remove them first."
        )

    new_assignment = CoordinatorAssignment(
        user_id=data.user_id,
        coordinator_type=data.coordinator_type,
        grade_id=data.grade_id,
        subject_id=data.subject_id
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return format_coordinator_response(new_assignment, db)


def get_all_coordinator_assignments(db: Session):
    assignments = db.query(CoordinatorAssignment).all()
    return [format_coordinator_response(a, db) for a in assignments]


def delete_coordinator_assignment(assignment_id: int, deleter: User, db: Session):
    if deleter.designation not in ["admin", "principal"]:
        raise HTTPException(status_code=403, detail="Only admin or principal can manage coordinator assignments")

    assignment = db.query(CoordinatorAssignment).filter(
        CoordinatorAssignment.assignment_id == assignment_id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(assignment)
    db.commit()
    return {"message": "Coordinator assignment removed successfully"}


def format_coordinator_response(assignment: CoordinatorAssignment, db: Session) -> dict:
    user = db.query(User).filter(User.user_id == assignment.user_id).first()

    class_display = None
    if assignment.grade_id:
        class_ = db.query(Class).filter(Class.grade_id == assignment.grade_id).first()
        if class_:
            grade = db.query(Grade).filter(Grade.grade_id == class_.grade_id).first()
            class_display = f"Grade {grade.grade_number}{class_.division}"

    subject_name = None
    if assignment.subject_id:
        subject = db.query(Subject).filter(Subject.subject_id == assignment.subject_id).first()
        subject_name = subject.subject_name if subject else None

    return {
        "assignment_id": assignment.assignment_id,
        "user_id": assignment.user_id,
        "coordinator_name": f"{user.first_name} {user.last_name}",
        "coordinator_type": assignment.coordinator_type,
        "class_display": class_display,
        "subject_name": subject_name,
    }
