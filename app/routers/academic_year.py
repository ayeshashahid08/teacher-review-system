from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.schemas.academic_year import AcademicYearSettingCreate
from app.services.academic_year_service import (
    create_ac_year_setting,
    get_all_ac_year_settings,
    get_ac_year_setting,
    delete_ac_year_setting,
)

router = APIRouter(prefix="/academic-year", tags=["Academic Year Settings"])


@router.post("/")
def create_setting(
    data: AcademicYearSettingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_ac_year_setting(data, current_user, db)


@router.get("/")
def get_all_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_all_ac_year_settings(db)


@router.get("/{academic_year}")
def get_setting(
    academic_year: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_ac_year_setting(academic_year, db)


@router.delete("/{academic_year}")
def delete_setting(
    academic_year: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_ac_year_setting(academic_year, current_user, db)
