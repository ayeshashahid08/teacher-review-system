from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user, require_role
from app.models.user import User
from app.schemas.salary import SalaryEligibilityDecision
from app.services.salary_service import (
    get_teacher_salary_summary,
    get_all_teachers_summary,
    record_increment_decision,
)

router = APIRouter(prefix="/salary", tags=["Salary Increment"])


@router.get("/summary/{academic_year}")
def get_all_summaries(
    academic_year: str,
    current_user: User = Depends(require_role(["principal"])),
    db: Session = Depends(get_db)
):
    return get_all_teachers_summary(academic_year, db)


@router.get("/summary/{academic_year}/{user_id}")
def get_one_summary(
    academic_year: str,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_teacher_salary_summary(user_id, academic_year, db)


@router.post("/decision/{academic_year}/{user_id}")
def make_decision(
    academic_year: str,
    user_id: int,
    data: SalaryEligibilityDecision,
    current_user: User = Depends(require_role(["principal"])),
    db: Session = Depends(get_db)
):
    return record_increment_decision(user_id, academic_year, data, current_user, db)
