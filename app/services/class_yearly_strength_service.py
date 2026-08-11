from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.class_yearly_strength import ClassYearlyStrength
from app.models.class_ import Class
from app.models.academic_year_settings import AcademicYearSettings
from app.models.user import User
from app.schemas.class_yearly_strength import ClassYearlyStrengthCreate


def create_strength(data: ClassYearlyStrengthCreate, creator: User, db: Session):
    if creator.designation not in ["admin", "principal"]:
        raise HTTPException(status_code=403, detail="Only admin or principal can manage class strength")

    class_ = db.query(Class).filter(Class.class_id == data.class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")

    academic_year = db.query(AcademicYearSettings).filter(
        AcademicYearSettings.academic_year == data.academic_year
    ).first()
    if not academic_year:
        raise HTTPException(status_code=404, detail="Academic year not found. Create it first.")

    existing = db.query(ClassYearlyStrength).filter(
        ClassYearlyStrength.class_id == data.class_id,
        ClassYearlyStrength.academic_year == data.academic_year
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Strength already set for this class and year")

    new_strength = ClassYearlyStrength(
        class_id=data.class_id,
        academic_year=data.academic_year,
        strength=data.strength
    )
    db.add(new_strength)
    db.commit()
    db.refresh(new_strength)
    return format_strength_response(new_strength, db)


def get_all_strengths(db: Session):
    strengths = db.query(ClassYearlyStrength).all()
    return [format_strength_response(s, db) for s in strengths]


def get_strengths_by_year(academic_year: str, db: Session):
    strengths = db.query(ClassYearlyStrength).filter(
        ClassYearlyStrength.academic_year == academic_year
    ).all()
    if not strengths:
        raise HTTPException(status_code=404, detail="No strength records found for this year")
    return [format_strength_response(s, db) for s in strengths]


def update_strength(class_id: int, academic_year: str, strength: int, updater: User, db: Session):
    if updater.designation not in ["admin", "principal"]:
        raise HTTPException(status_code=403, detail="Only admin or principal can manage class strength")

    if strength < 1 or strength > 200:
        raise HTTPException(status_code=400, detail="Strength must be between 1 and 200")

    existing = db.query(ClassYearlyStrength).filter(
        ClassYearlyStrength.class_id == class_id,
        ClassYearlyStrength.academic_year == academic_year
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Strength record not found")

    existing.strength = strength
    db.commit()
    db.refresh(existing)
    return format_strength_response(existing, db)


def delete_strength(class_id: int, academic_year: str, deleter: User, db: Session):
    if deleter.designation not in ["admin", "principal"]:
        raise HTTPException(status_code=403, detail="Only admin or principal can manage class strength")

    existing = db.query(ClassYearlyStrength).filter(
        ClassYearlyStrength.class_id == class_id,
        ClassYearlyStrength.academic_year == academic_year
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Strength record not found")

    db.delete(existing)
    db.commit()
    return {"message": "Strength record deleted successfully"}


def format_strength_response(strength: ClassYearlyStrength, db: Session) -> dict:
    class_ = db.query(Class).filter(Class.class_id == strength.class_id).first()
    return {
        "class_id": strength.class_id,
        "class_name": class_.class_name if class_ else None,
        "academic_year": strength.academic_year,
        "strength": strength.strength,
    }
