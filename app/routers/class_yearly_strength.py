from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.schemas.class_yearly_strength import ClassYearlyStrengthCreate
from app.services.class_yearly_strength_service import (
    create_strength,
    get_all_strengths,
    get_strengths_by_year,
    update_strength,
    delete_strength,
)

router = APIRouter(prefix="/class-strength", tags=["Class Yearly Strength"])


@router.post("/")
def create(
    data: ClassYearlyStrengthCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_strength(data, current_user, db)


@router.get("/")
def get_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_all_strengths(db)


@router.get("/{academic_year}")
def get_by_year(
    academic_year: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_strengths_by_year(academic_year, db)


@router.patch("/{class_id}/{academic_year}")
def update(
    class_id: int,
    academic_year: str,
    strength: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_strength(class_id, academic_year, strength, current_user, db)


@router.delete("/{class_id}/{academic_year}")
def delete(
    class_id: int,
    academic_year: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_strength(class_id, academic_year, current_user, db)
