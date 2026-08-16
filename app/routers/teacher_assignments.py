from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.teacher_assignment import TeacherAssignmentCreate, TeacherAssignmentResponse
from app.services.teacher_assignment_service import (
    create_assignment,
    get_assignments_for_user,
    delete_assignment,
    format_assignment_response,
)
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(tags=["Teacher Assignments"])


@router.post("/teacher-assignments", response_model=TeacherAssignmentResponse)
def assignment_create(
    data: TeacherAssignmentCreate,
    assignment_creater: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_assignment = create_assignment(data, assignment_creater, db)
    return format_assignment_response(new_assignment, db)


@router.get("/teacher-assignments/{user_id}")
def get_all_assignments(
    user_id: int,
    db: Session = Depends(get_db)
):
    assignments = get_assignments_for_user(user_id, db)
    return [format_assignment_response(a, db) for a in assignments]


@router.delete("/teacher-assignments/{assignment_id}")
def assignment_delete(
    assignment_id: int,
    assignment_deleter: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_assignment(assignment_id, assignment_deleter, db)
