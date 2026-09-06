from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.schemas.coordinator_assignment import CoordinatorAssignmentCreate
from app.services.coordinator_assignment_service import (
    create_coordinator_assignment,
    get_all_coordinator_assignments,
    delete_coordinator_assignment,
)

router = APIRouter(prefix="/coordinator-assignments", tags=["Coordinator Assignments"])


@router.post("/")
def create(
    data: CoordinatorAssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_coordinator_assignment(data, current_user, db)


@router.get("/")
def get_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_all_coordinator_assignments(db)


@router.delete("/{assignment_id}")
def delete(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_coordinator_assignment(assignment_id, current_user, db)
