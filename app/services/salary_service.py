from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime

from app.models.salary_increment_eligibility import SalaryIncrementEligibility
from app.models.observation import Observation
from app.models.score import Score
from app.models.acr import ACRReport
from app.models.academic_year_settings import AcademicYearSettings
from app.models.user import User
from app.schemas.salary import SalaryEligibilityDecision

from datetime import date

def calculate_years_of_service(joining_date) -> int:
    if not joining_date:
        return None
    today = date.today()
    years = today.year - joining_date.year
    if (today.month, today.day) < (joining_date.month, joining_date.day):
        years -= 1
    return years


def get_teacher_salary_summary(user_id: int, academic_year: str, db: Session) -> dict:
    teacher = db.query(User).filter(User.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher.designation in ["admin", "principal"]:
        raise HTTPException(status_code=400, detail="Admin and principal do not have salary increment eligibility")

    year_settings = db.query(AcademicYearSettings).filter(
        AcademicYearSettings.academic_year == academic_year
    ).first()

    # get all observations for this teacher this year
    all_obs = db.query(Observation).filter(
        Observation.observee_id == user_id,
        func.extract('year', Observation.observed_at).in_(
            [int(academic_year.split('-')[0]), int(academic_year.split('-')[1])]
        )
    ).all()

    approved_obs = [o for o in all_obs if o.status == "approved"]

  

    # get scores for approved observations
    scores = []
    
    for obs in approved_obs:
        score = db.query(Score).filter(Score.observation_id == obs.observation_id).first()
        if score and score.total_score is not None:
            scores.append(float(score.total_score))

    # print(scores)
    avg_score = round(sum(scores) / len(scores), 2) if scores else None
    lowest = round(min(scores), 2) if scores else None
    highest = round(max(scores), 2) if scores else None

    # get ACR for this year
    acr = db.query(ACRReport).filter(
        ACRReport.reported_id == user_id,
        ACRReport.academic_year == academic_year,
        ACRReport.status == "finalized"
    ).first()

    # get existing decision if any
    decision = db.query(SalaryIncrementEligibility).filter(
        SalaryIncrementEligibility.user_id == user_id,
        SalaryIncrementEligibility.academic_year == academic_year
    ).first()

    decided_by_name = None
    if decision and decision.decided_by:
        decider = db.query(User).filter(User.user_id == decision.decided_by).first()
        decided_by_name = f"{decider.first_name} {decider.last_name}" if decider else None

    attendance_percentage = None
    if acr and year_settings:
        attendance_percentage = round((acr.days_present / year_settings.total_working_days) * 100, 2)

    return {
        "user_id": teacher.user_id,
        "teacher_name": f"{teacher.first_name} {teacher.last_name}",
        "designation": teacher.designation,
        "years_of_service": calculate_years_of_service(teacher.joining_date),
        "teaching_load": teacher.teaching_load,
        "academic_year": academic_year,
        "total_observations": len(all_obs),
        "approved_observations": len(approved_obs),
        "average_score": avg_score,
        "lowest_score": lowest,
        "highest_score": highest,
        "acr_grade": acr.grade if acr else None,
        "acr_percentage": float(acr.percentage) if acr and acr.percentage else None,
        "days_present": acr.days_present if acr else None,
        "total_working_days": year_settings.total_working_days if year_settings else None,
        "attendance_percentage": attendance_percentage,
        "increment_decision": {
            "is_eligible": decision.is_eligible,
            "decided_by": decided_by_name,
            "decision_notes": decision.decision_notes,
            "decided_at": decision.decided_at,
        } if decision else None
    }


def get_all_teachers_summary(academic_year: str, db: Session) -> list:
    teachers = db.query(User).filter(
        User.designation=="teacher",
        User.is_active == True
    ).all()

    return [get_teacher_salary_summary(t.user_id, academic_year, db) for t in teachers]


def record_increment_decision(
    user_id: int,
    academic_year: str,
    data: SalaryEligibilityDecision,
    principal: User,
    db: Session
):
    if principal.designation != "principal":
        raise HTTPException(status_code=403, detail="Only principal can record increment decisions")

    teacher = db.query(User).filter(User.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher.designation in ["admin", "principal"]:
        raise HTTPException(status_code=400, detail="Admin and principal do not have salary increment eligibility")

    existing = db.query(SalaryIncrementEligibility).filter(
        SalaryIncrementEligibility.user_id == user_id,
        SalaryIncrementEligibility.academic_year == academic_year
    ).first()

    if existing:
        existing.is_eligible = data.is_eligible
        existing.decision_notes = data.decision_notes
        existing.decided_by = principal.user_id
        existing.decided_at = datetime.utcnow()
    else:
        new_decision = SalaryIncrementEligibility(
            user_id=user_id,
            academic_year=academic_year,
            is_eligible=data.is_eligible,
            decided_by=principal.user_id,
            decision_notes=data.decision_notes,
            decided_at=datetime.utcnow()
        )
        db.add(new_decision)

    db.commit()
    return get_teacher_salary_summary(user_id, academic_year, db)
