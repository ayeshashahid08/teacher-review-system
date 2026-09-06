from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.academic_year_settings import AcademicYearSettings
from app.models.user import User
from app.schemas.academic_year import AcademicYearSettingCreate


def create_ac_year_setting(data: AcademicYearSettingCreate, creater: User, db: Session):
    if creater.designation not in ["admin", "principal"]:
        raise HTTPException(status_code=403, detail="Only admin or principal can manage academic year settings")

    existing = db.query(AcademicYearSettings).filter(
        AcademicYearSettings.academic_year == data.academic_year
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Academic year already exists")

    new_setting = AcademicYearSettings(
        academic_year=data.academic_year,
        total_working_days=data.total_working_days
    )
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    return new_setting


def get_all_ac_year_settings(db: Session):
    return db.query(AcademicYearSettings).all()


def get_ac_year_setting(academic_year: str, db: Session):
    setting = db.query(AcademicYearSettings).filter(
        AcademicYearSettings.academic_year == academic_year
    ).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Academic year not found")
    return setting

def update_ac_year_setting(academic_year: str, data: AcademicYearSettingCreate, updater: User, db: Session):
    if updater.designation not in ["admin", "principal"]:
        raise HTTPException(status_code=403, detail="Only admin or principal can manage academic year settings")

    setting = db.query(AcademicYearSettings).filter(
        AcademicYearSettings.academic_year == academic_year
    ).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Academic year not found")

    if data.total_working_days < 1 or data.total_working_days > 365:
        raise HTTPException(status_code=400, detail="Total working days must be between 1 and 365")

    setting.total_working_days = data.total_working_days
    db.commit()
    db.refresh(setting)
    return setting




def delete_ac_year_setting(academic_year: str, deleter: User, db: Session):
    if deleter.designation not in ["admin", "principal"]:
        raise HTTPException(status_code=403, detail="Only admin or principal can manage academic year settings")

    setting = db.query(AcademicYearSettings).filter(
        AcademicYearSettings.academic_year == academic_year
    ).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Academic year not found")

    from app.models.acr import ACRReport
    from app.models.salary_increment_eligibility import SalaryIncrementEligibility
    from app.models.class_yearly_strength import ClassYearlyStrength

    acr_exists = db.query(ACRReport).filter(
        ACRReport.academic_year == academic_year
    ).first()
    if acr_exists:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete academic year that has ACR reports linked to it"
        )

    eligibility_exists = db.query(SalaryIncrementEligibility).filter(
        SalaryIncrementEligibility.academic_year == academic_year
    ).first()
    if eligibility_exists:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete academic year that has salary eligibility records linked to it"
        )

    db.delete(setting)
    db.commit()
    return {"message": f"Academic year {academic_year} deleted successfully"}