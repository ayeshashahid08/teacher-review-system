from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from collections import defaultdict

from app.models.monthly_report import MonthlyReport
from app.models.observation import Observation
from app.models.observation_mcq_response import ObservationMCQResponse
from app.models.observation_remarks import ObservationRemarks
from app.models.question import QuestionBank, QuestionOption
from app.models.score import Score
from app.models.user import User

from app.schemas.monthly_report import MonthlyReportGenerate, MonthlyReportEdit
from app.services.ai_feedback_service import generate_ai_feedback_with_retry


def calculate_mcq_percentages(
    db: Session,
    observation_ids: list[int],
):
    mcq_rows = db.query(ObservationMCQResponse).filter(
        ObservationMCQResponse.observation_id.in_(observation_ids)
    ).all()

    per_question_scores = defaultdict(list)

    for row in mcq_rows:
        option = db.query(QuestionOption).filter(
            QuestionOption.option_id == row.selected_option_id
        ).first()

        if option is not None:
            per_question_scores[row.question_id].append(
                float(option.score_value)
            )

    results = []

    for question_id, values in per_question_scores.items():
        question = db.query(QuestionBank).filter(
            QuestionBank.question_id == question_id
        ).first()

        if not values:
            continue

        average_score = sum(values) / len(values)

        results.append({
            "question_id": question_id,
            "question_text": (
                question.question_text
                if question
                else "Unknown"
            ),
            "response_percentage": round(
                average_score * 100,
                2,
            ),
        })

    return results

def generate_monthly_report(data: MonthlyReportGenerate, db: Session) -> MonthlyReport:
    observations = db.query(Observation).filter(
        Observation.observee_id == data.user_id,
        Observation.status == "approved",
    ).all()

    # keep only observations that fall in the requested month/year
    observations = [
        o for o in observations
        if o.observed_at.month == data.month and o.observed_at.year == data.year
    ]

    if not observations:
        raise HTTPException(status_code=400, detail="No approved observations found for this teacher in this month")

    observation_ids = [o.observation_id for o in observations]

    # ---- average total score across the month ----
    scores = db.query(Score).filter(Score.observation_id.in_(observation_ids)).all()
    total_scores = [float(s.total_score) for s in scores if s.total_score is not None]
    average_score = sum(total_scores) / len(total_scores) if total_scores else None

    # Per-question MCQ percentage across the month
    mcq_percentages = calculate_mcq_percentages(
    db,
    observation_ids,
)   
    # ---- remarks text for AI feedback ----
    remarks_rows = db.query(ObservationRemarks).filter(
        ObservationRemarks.observation_id.in_(observation_ids)
    ).all()
    remarks_summary = "\n".join(
        f"- general_observation: {r.general_observation or ''} | remarks_suggestions: {r.remarks_suggestions or ''}"
        for r in remarks_rows
    ) or "No written remarks recorded this month."

    mcq_summary = "\n".join(
        f"{item['question_text']}: {item['response_percentage']}%" for item in mcq_percentages
    ) or "No MCQ responses recorded this month."

    ai_feedback = generate_ai_feedback_with_retry(mcq_summary, remarks_summary)

    # ---- upsert the MonthlyReport row ----
    report = db.query(MonthlyReport).filter(
        MonthlyReport.user_id == data.user_id,
        MonthlyReport.month == data.month,
        MonthlyReport.year == data.year,
    ).first()

    if report and report.status == "approved":
        raise HTTPException(status_code=400, detail="This month's report is already approved and cannot be regenerated")

    if report:
        report.total_observations = len(observations)
        report.average_score = average_score
        report.ai_suggestions = ai_feedback
        report.generated_at = datetime.utcnow()
        report.status = "pending_approval"
    else:
        report = MonthlyReport(
            user_id=data.user_id,
            month=data.month,
            year=data.year,
            total_observations=len(observations),
            average_score=average_score,
            ai_suggestions=ai_feedback,
            generated_at=datetime.utcnow(),
            status="pending_approval",
        )
        db.add(report)

    db.commit()
    db.refresh(report)

    # stash mcq_percentages on the instance for the formatter to reuse without re-querying
    report._mcq_percentages_cache = mcq_percentages
    return report


def edit_monthly_report(report_id: int, data: MonthlyReportEdit, principal: User, db: Session) -> MonthlyReport:
    report = db.query(MonthlyReport).filter(MonthlyReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.status == "approved":
        raise HTTPException(status_code=400, detail="Approved reports cannot be edited")

    if data.human_suggestions is not None:
        report.human_suggestions = data.human_suggestions

    db.commit()
    db.refresh(report)
    return report


def approve_monthly_report(report_id: int, principal: User, db: Session) -> MonthlyReport:
    report = db.query(MonthlyReport).filter(MonthlyReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.status == "approved":
        raise HTTPException(status_code=400, detail="Report is already approved")

    report.status = "approved"
    report.approved_by = principal.user_id
    report.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(report)
    return report


def get_report_with_percentages(report_id: int, db: Session) -> dict:
    report = db.query(MonthlyReport).filter(MonthlyReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    teacher = db.query(User).filter(User.user_id == report.user_id).first()
    approver = db.query(User).filter(User.user_id == report.approved_by).first() if report.approved_by else None

    observations = db.query(Observation).filter(
        Observation.observee_id == report.user_id,
        Observation.status == "approved",
    ).all()
    observation_ids = [
        o.observation_id for o in observations
        if o.observed_at.month == report.month and o.observed_at.year == report.year
    ]

    mcq_percentages = calculate_mcq_percentages(
    db,
    observation_ids,
)
    return {
        "report_id": report.report_id,
        "teacher_name": f"{teacher.first_name} {teacher.last_name}",
        "month": report.month,
        "year": report.year,
        "total_observations": report.total_observations,
        "average_score": float(report.average_score) if report.average_score is not None else None,
        "mcq_percentages": mcq_percentages,
        "ai_suggestions": report.ai_suggestions,
        "human_suggestions": report.human_suggestions,
        "status": report.status,
        "approved_by_name": f"{approver.first_name} {approver.last_name}" if approver else None,
        "approved_at": report.approved_at,
        "generated_at": report.generated_at,
        "pdf_path": report.pdf_path,
    }