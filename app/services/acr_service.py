from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import date, datetime

from app.models.acr import ACRReport, ACRResponse, ACRGradeCriteria, ACROverallGradeCriteria
from app.models.user import User
from app.models.question import QuestionBank
from app.models.academic_year_settings import AcademicYearSettings

from app.schemas.acr import AcrCreate, AcrResponseInput


def get_current_academic_year() -> str:
    today = date.today()
    month = today.month
    year = today.year
    if month >= 1 and month <= 7:
        return str(year - 1) + "-" + str(year)
    else:
        return str(year) + "-" + str(year + 1)


def start_acr(data: AcrCreate, reporter_id: int, db: Session):
    academic_year = get_current_academic_year()

    reporter = db.query(User).filter(User.user_id == reporter_id).first()
    reported = db.query(User).filter(User.user_id == data.reported_id).first()

    if not reported:
        raise HTTPException(status_code=404, detail="Teacher not found")

    # nobody fills their own ACR
    if reporter_id == data.reported_id:
        raise HTTPException(status_code=400, detail="You cannot fill your own ACR report")

    # principal's ACR cannot be made by anyone
    if reported.designation == "principal" or reported.designation == "admin" :
        raise HTTPException(status_code=403, detail="Principal and admin does not have an ACR report")

    # chief coordinator's ACR can only be filled by principal
    if reported.designation == "chief_coordinator" and reporter.designation != "principal":
        raise HTTPException(status_code=403, detail="Only principal can fill chief coordinator's ACR")

    # regular teachers' ACR can only be filled by chief coordinator
    if reported.designation in ["teacher", "coordinator", "peer_coordinator"] and reporter.designation != "chief_coordinator":
        raise HTTPException(status_code=403, detail="Only chief coordinator can fill teacher ACR reports")

    existing = db.query(ACRReport).filter(
        ACRReport.reported_id == data.reported_id,
        ACRReport.academic_year == academic_year
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="ACR already exists for this teacher this year")

    new_acr = ACRReport(
        academic_year=academic_year,
        reported_id=data.reported_id,
        reporter_id=reporter_id,
        days_present=data.days_present,
        status="draft",
    )
    db.add(new_acr)
    db.commit()
    db.refresh(new_acr)
    return new_acr


def save_acr_response(acr_id: int, reporter_id: int, data: AcrResponseInput, db: Session):
    acr = db.query(ACRReport).filter(ACRReport.acr_id == acr_id).first()
    if not acr:
        raise HTTPException(status_code=404, detail="ACR report not found")
    if acr.reporter_id != reporter_id:
        raise HTTPException(status_code=403, detail="You can only modify your own ACR reports")

    question = db.query(QuestionBank).filter(
        QuestionBank.question_id == data.acr_question_id,
        QuestionBank.question_type == "acr",
        QuestionBank.is_active == True
    ).first()
    if not question:
        raise HTTPException(status_code=400, detail="Invalid question for ACR form")
    
    max_marks_row = db.query(ACRGradeCriteria).filter(ACRGradeCriteria.acr_question_id == data.acr_question_id, ACRGradeCriteria.grade == "A+").first()
    if max_marks_row and data.acr_response_marks > max_marks_row.max_marks:
        raise HTTPException(
            status_code=400,
            detail=f"Marks cannot exceed maximum of {max_marks_row.max_marks}"
        )

    existing = db.query(ACRResponse).filter(
        ACRResponse.acr_id == acr_id,
        ACRResponse.acr_question_id == data.acr_question_id
    ).first()
    if existing:
        existing.acr_response_marks = data.acr_response_marks
    else:
        new_response = ACRResponse(
            acr_id=acr_id,
            acr_question_id=data.acr_question_id,
            acr_response_marks=data.acr_response_marks,
        )
        db.add(new_response)

    db.commit()
    recalculate_acr_report(acr_id, db)
    return {"message": "saved"}


def recalculate_acr_report(acr_id: int, db: Session):
    acr = db.query(ACRReport).filter(ACRReport.acr_id == acr_id).first()
    if not acr:
        raise HTTPException(status_code=404, detail="ACR report not found")

    total_obtained = db.query(func.sum(ACRResponse.acr_response_marks)).filter(
        ACRResponse.acr_id == acr_id
    ).scalar() or 0

    max_possible = db.query(func.sum(ACRGradeCriteria.max_marks)).filter(ACRGradeCriteria.grade == "A+").scalar() or 1
    percentage = round((total_obtained / max_possible) * 100, 2)

    grade_row = db.query(ACROverallGradeCriteria).filter(
        ACROverallGradeCriteria.min_percentage <= percentage,
        ACROverallGradeCriteria.max_percentage >= percentage
    ).first()

    grade = grade_row.grade if grade_row else "Ungraded"

    acr = db.query(ACRReport).filter(ACRReport.acr_id == acr_id).first()
    acr.total_marks = total_obtained
    acr.percentage = percentage
    acr.grade = grade
    db.commit()


def finalize_acr(acr_id: int, reporter_id: int, db: Session):
    acr = db.query(ACRReport).filter(ACRReport.acr_id == acr_id).first()
    if not acr:
        raise HTTPException(status_code=404, detail="ACR report not found")
    if acr.reporter_id != reporter_id:
        raise HTTPException(status_code=403, detail="You can only modify your own ACR reports")
    

    total_questions = db.query(QuestionBank).filter(
        QuestionBank.question_type == "acr",
        QuestionBank.is_active == True
    ).count()

    answered_questions = db.query(ACRResponse).filter(
        ACRResponse.acr_id == acr_id
    ).count()

    if answered_questions < total_questions:
        raise HTTPException(status_code=400, detail="Please fill in marks for all questions before finalizing")

    acr.status = "finalized"
    acr.submitted_at = datetime.utcnow()
    db.commit()
    db.refresh(acr)
    return acr


def get_acr_full_state(acr_id: int, db: Session) -> dict:
    acr = db.query(ACRReport).filter(ACRReport.acr_id == acr_id).first()
    if not acr:
        raise HTTPException(status_code=404, detail="ACR report not found")

    responses = db.query(ACRResponse).filter(
        ACRResponse.acr_id == acr_id
    ).all()

    return {
        "acr_report": acr,
        "responses": responses,
    }


def format_acr_response(acr: ACRReport, db: Session) -> dict:
    reported = db.query(User).filter(User.user_id == acr.reported_id).first()
    reporter = db.query(User).filter(User.user_id == acr.reporter_id).first()

    year_settings = db.query(AcademicYearSettings).filter(
        AcademicYearSettings.academic_year == acr.academic_year
    ).first()

    return {
        "acr_id": acr.acr_id,
        "academic_year": acr.academic_year,
        "reported_name": f"{reported.first_name} {reported.last_name}",
        "reporter_name": f"{reporter.first_name} {reporter.last_name}",
        "days_present": acr.days_present,
        "total_working_days": year_settings.total_working_days if year_settings else None,
        "total_marks": acr.total_marks,
        "percentage": float(acr.percentage) if acr.percentage else None,
        "grade": acr.grade,
        "status": acr.status,
        "submitted_at": acr.submitted_at,
    }
