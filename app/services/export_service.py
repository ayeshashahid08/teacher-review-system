import csv
import io
import os
import zipfile
from datetime import date, datetime

from openpyxl import Workbook
from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased

# Adjust these import paths to match your project
from app.models.user import User
from app.models.academic_year_settings import AcademicYearSettings
from app.models.acr import ACRReport, ACRResponse, ACRGradeCriteria, ACROverallGradeCriteria
from app.models.acr_approval import ACRApproval
from app.models.monthly_report import MonthlyReport, ReportInsight
from app.models.observation import Observation
from app.models.observation_mcq_response import ObservationMCQResponse
from app.models.observation_remarks import ObservationRemarks
from app.models.observation_substitute import ObservationSubstitute
from app.models.question import QuestionBank, QuestionOption
from app.models.score import Score
from app.models.teacher_assignment import TeacherAssignment
from app.models.subject import Subject
from app.models.class_ import Class
from app.models.grade import Grade

# Month the academic year starts (4 = April, 8 = August)
ACADEMIC_YEAR_START_MONTH = 8

EXCLUDED_COLUMNS = {"password_hash"}


def parse_academic_year(academic_year: str):
    """'2025-2026' -> (date(2025, 4, 1), date(2026, 3, 31))"""
    try:
        start_year, end_year = [int(p) for p in academic_year.split("-")]
    except ValueError:
        raise ValueError("Academic year must look like 2025-2026")
    if end_year != start_year + 1:
        raise ValueError("Academic year must span consecutive years, e.g. 2025-2026")

    start = date(start_year, ACADEMIC_YEAR_START_MONTH, 1)
    end = date.fromordinal(date(end_year, ACADEMIC_YEAR_START_MONTH, 1).toordinal() - 1)
    return start, end


def _full_name(user):
    return f"{user.first_name} {user.last_name}"


# ---------- per-table filters: each takes (query, academic_year) ----------

def _settings_filter(q, ay):
    return q.filter(AcademicYearSettings.academic_year == ay)


def _acr_filter(q, ay):
    return q.filter(ACRReport.academic_year == ay)


def _acr_child_filter(model):
    """Tables keyed by acr_id (responses, approvals) are filtered via their ACR."""
    def _filter(q, ay):
        return (
            q.join(ACRReport, model.acr_id == ACRReport.acr_id)
            .filter(ACRReport.academic_year == ay)
        )
    return _filter


def _observation_filter(q, ay):
    start, end = parse_academic_year(ay)
    return q.filter(Observation.observed_at >= start, Observation.observed_at <= end)


def _observation_child_filter(model):
    """Tables keyed by observation_id are filtered through observed_at."""
    def _filter(q, ay):
        start, end = parse_academic_year(ay)
        return (
            q.join(Observation, model.observation_id == Observation.observation_id)
            .filter(Observation.observed_at >= start, Observation.observed_at <= end)
        )
    return _filter


def _month_index_bounds(ay):
    start, end = parse_academic_year(ay)
    return start.year * 12 + start.month, end.year * 12 + end.month


def _monthly_filter(q, ay):
    lo, hi = _month_index_bounds(ay)
    month_index = MonthlyReport.year * 12 + MonthlyReport.month
    return q.filter(month_index >= lo, month_index <= hi)


def _insight_filter(q, ay):
    lo, hi = _month_index_bounds(ay)
    month_index = MonthlyReport.year * 12 + MonthlyReport.month
    return (
        q.join(MonthlyReport, ReportInsight.report_id == MonthlyReport.report_id)
        .filter(month_index >= lo, month_index <= hi)
    )


# Raw tables filtered to the selected academic year. Key = file / sheet name.
YEAR_EXPORTS = {
    "academic_year_settings":    (AcademicYearSettings, _settings_filter),
    "acr_reports":               (ACRReport, _acr_filter),
    "acr_responses":             (ACRResponse, _acr_child_filter(ACRResponse)),
    "acr_approvals":             (ACRApproval, _acr_child_filter(ACRApproval)),
    "observations":              (Observation, _observation_filter),
    "observation_mcq_responses": (ObservationMCQResponse, _observation_child_filter(ObservationMCQResponse)),
    "observation_remarks":       (ObservationRemarks, _observation_child_filter(ObservationRemarks)),
    "observation_substitutes":   (ObservationSubstitute, _observation_child_filter(ObservationSubstitute)),
    "observation_scores":        (Score, _observation_child_filter(Score)),
    "monthly_reports":           (MonthlyReport, _monthly_filter),
    "report_insights":           (ReportInsight, _insight_filter),
}

# Tables exported in full, regardless of year
FULL_SNAPSHOTS = {
    "users": User,
    "subjects": Subject,
    "grades": Grade,
    "classes": Class,
    "question_bank": QuestionBank,
    "question_options": QuestionOption,
    "teacher_assignments": TeacherAssignment,
    "acr_grade_criteria": ACRGradeCriteria,
    "acr_overall_grade_criteria": ACROverallGradeCriteria,
}


# ---------- generic helpers ----------

def _columns(model):
    return [c.key for c in model.__table__.columns if c.key not in EXCLUDED_COLUMNS]


def _model_to_row(obj, columns):
    row = []
    for col in columns:
        value = getattr(obj, col)
        if isinstance(value, (datetime, date)):
            value = value.isoformat()
        row.append(value)
    return row


def _iso(value):
    return value.isoformat() if value else None


# ---------- readable (joined) sheets: observations ----------

def _observation_details(db: Session, academic_year: str):
    """One row per observation: names, subject, class, score, grade and remarks."""
    start, end = parse_academic_year(academic_year)
    Observer, Observee = aliased(User), aliased(User)

    rows = (
        db.query(Observation, Observer, Observee, Subject, Class, Grade, Score, ObservationRemarks)
        .join(Observer, Observation.observer_id == Observer.user_id)
        .join(Observee, Observation.observee_id == Observee.user_id)
        .join(Subject, Observation.subject_id == Subject.subject_id)
        .join(Class, Observation.class_id == Class.class_id)
        .join(Grade, Class.grade_id == Grade.grade_id)
        .outerjoin(Score, Score.observation_id == Observation.observation_id)
        .outerjoin(ObservationRemarks, ObservationRemarks.observation_id == Observation.observation_id)
        .filter(Observation.observed_at >= start, Observation.observed_at <= end)
        .order_by(Observation.observed_at, Observation.observation_id)
        .all()
    )

    cols = [
        "observation_id", "observed_at", "status", "observer", "observee",
        "subject", "class", "school_level", "period", "topic", "students_present",
        "mcq_score", "ai_score", "written_score", "total_score",
        "max_possible_score", "percentage", "grade", "is_overridden", "override_reason",
        "general_observation", "remarks_suggestions",
    ]
    out = []
    for obs, observer, observee, subject, klass, grade, score, remarks in rows:
        out.append([
            obs.observation_id, _iso(obs.observed_at), obs.status,
            _full_name(observer), _full_name(observee),
            subject.subject_name, f"Grade {grade.grade_number}-{klass.division}", grade.school_level,
            obs.period, obs.topic, obs.students_present,
            score.mcq_score if score else None,
            score.ai_score if score else None,
            score.written_score if score else None,
            score.total_score if score else None,
            score.max_possible_score if score else None,
            score.percentage if score else None,
            score.grade if score else None,
            score.is_overridden if score else None,
            score.override_reason if score else None,
            remarks.general_observation if remarks else None,
            remarks.remarks_suggestions if remarks else None,
        ])
    return cols, out


def _mcq_details(db: Session, academic_year: str):
    """One row per answered question: question text, chosen grade and score."""
    start, end = parse_academic_year(academic_year)

    rows = (
        db.query(ObservationMCQResponse, QuestionBank, QuestionOption)
        .join(Observation, ObservationMCQResponse.observation_id == Observation.observation_id)
        .join(QuestionBank, ObservationMCQResponse.question_id == QuestionBank.question_id)
        .join(QuestionOption, ObservationMCQResponse.selected_option_id == QuestionOption.option_id)
        .filter(Observation.observed_at >= start, Observation.observed_at <= end)
        .order_by(ObservationMCQResponse.observation_id, QuestionBank.question_id)
        .all()
    )

    cols = ["observation_id", "section", "subsection", "question",
            "selected_grade", "score_value", "max_points", "explanation"]
    out = [
        [r.observation_id, q.section, q.subsection, q.question_text,
         o.option_grade, o.score_value, q.max_points, r.explanation]
        for r, q, o in rows
    ]
    return cols, out


# ---------- readable (joined) sheets: ACR ----------

def _latest_approvals(db: Session, academic_year: str) -> dict:
    """acr_id -> most recent ACRApproval for that ACR."""
    rows = (
        db.query(ACRApproval)
        .join(ACRReport, ACRApproval.acr_id == ACRReport.acr_id)
        .filter(ACRReport.academic_year == academic_year)
        .order_by(ACRApproval.acted_at.asc().nullsfirst(), ACRApproval.approval_id.asc())
        .all()
    )
    return {a.acr_id: a for a in rows}  # later rows overwrite earlier ones


def _acr_details(db: Session, academic_year: str):
    """One row per ACR: who was reported on, who reported, attendance, marks, grade, latest approval."""
    Reported, Reporter = aliased(User), aliased(User)
    latest = _latest_approvals(db, academic_year)

    rows = (
        db.query(ACRReport, Reported, Reporter, AcademicYearSettings.total_working_days)
        .join(Reported, ACRReport.reported_id == Reported.user_id)
        .join(Reporter, ACRReport.reporter_id == Reporter.user_id)
        .join(AcademicYearSettings, ACRReport.academic_year == AcademicYearSettings.academic_year)
        .filter(ACRReport.academic_year == academic_year)
        .order_by(Reported.first_name, Reported.last_name)
        .all()
    )

    cols = [
        "acr_id", "academic_year", "reported_name", "reported_employment_number",
        "reported_designation", "reporter_name", "days_present", "total_working_days",
        "attendance_percentage", "total_marks", "percentage", "grade",
        "status", "submitted_at",
        "latest_approval_action", "latest_approval_comments", "latest_approval_at",
    ]
    out = []
    for acr, reported, reporter, working_days in rows:
        attendance = None
        if acr.days_present is not None and working_days:
            attendance = round(acr.days_present / working_days * 100, 2)
        approval = latest.get(acr.acr_id)
        out.append([
            acr.acr_id, acr.academic_year,
            _full_name(reported), reported.employment_number, reported.designation,
            _full_name(reporter),
            acr.days_present, working_days, attendance,
            acr.total_marks, acr.percentage, acr.grade,
            acr.status, _iso(acr.submitted_at),
            approval.action if approval else None,
            approval.comments if approval else None,
            _iso(approval.acted_at) if approval else None,
        ])
    return cols, out


def _acr_response_details(db: Session, academic_year: str):
    """One row per ACR answer: teacher, question text, marks and per-question grade."""
    Reported = aliased(User)

    rows = (
        db.query(ACRResponse, Reported, QuestionBank, ACRGradeCriteria.grade)
        .join(ACRReport, ACRResponse.acr_id == ACRReport.acr_id)
        .join(Reported, ACRReport.reported_id == Reported.user_id)
        .join(QuestionBank, ACRResponse.acr_question_id == QuestionBank.question_id)
        .outerjoin(
            ACRGradeCriteria,
            and_(
                ACRGradeCriteria.acr_question_id == ACRResponse.acr_question_id,
                ACRResponse.acr_response_marks >= ACRGradeCriteria.min_marks,
                ACRResponse.acr_response_marks <= ACRGradeCriteria.max_marks,
            ),
        )
        .filter(ACRReport.academic_year == academic_year)
        .order_by(Reported.first_name, Reported.last_name, QuestionBank.question_id)
        .all()
    )

    cols = ["acr_id", "reported_name", "section", "subsection", "question",
            "marks_awarded", "max_points", "question_grade"]
    out = [
        [r.acr_id, _full_name(u), q.section, q.subsection,
         q.question_text, r.acr_response_marks, q.max_points, grade]
        for r, u, q, grade in rows
    ]
    return cols, out


def _acr_approval_details(db: Session, academic_year: str):
    """Full approval history: one row per principal action, with names."""
    Reported, Principal = aliased(User), aliased(User)

    rows = (
        db.query(ACRApproval, ACRReport, Reported, Principal)
        .join(ACRReport, ACRApproval.acr_id == ACRReport.acr_id)
        .join(Reported, ACRReport.reported_id == Reported.user_id)
        .join(Principal, ACRApproval.principal_id == Principal.user_id)
        .filter(ACRReport.academic_year == academic_year)
        .order_by(Reported.first_name, Reported.last_name, ACRApproval.acted_at)
        .all()
    )

    cols = ["approval_id", "acr_id", "reported_name", "principal_name",
            "action", "comments", "acted_at"]
    out = [
        [a.approval_id, a.acr_id, _full_name(reported), _full_name(principal),
         a.action, a.comments, _iso(a.acted_at)]
        for a, acr, reported, principal in rows
    ]
    return cols, out


# ---------- collection ----------

def collect_data(db: Session, academic_year: str) -> dict:
    """Returns {name: (columns, rows)} for every sheet."""
    data = {}

    # Readable sheets first so they appear first in the zip / workbook
    data["observation_details"] = _observation_details(db, academic_year)
    data["observation_mcq_details"] = _mcq_details(db, academic_year)
    data["acr_details"] = _acr_details(db, academic_year)
    data["acr_response_details"] = _acr_response_details(db, academic_year)
    data["acr_approval_details"] = _acr_approval_details(db, academic_year)

    for name, (model, year_filter) in YEAR_EXPORTS.items():
        cols = _columns(model)
        rows = year_filter(db.query(model), academic_year).all()
        data[name] = (cols, [_model_to_row(o, cols) for o in rows])

    for name, model in FULL_SNAPSHOTS.items():
        cols = _columns(model)
        data[name] = (cols, [_model_to_row(o, cols) for o in db.query(model).all()])

    return data


def collect_pdf_paths(db: Session, academic_year: str) -> list:
    """Paths of generated monthly report PDFs for the year."""
    reports = _monthly_filter(db.query(MonthlyReport), academic_year).all()
    return [r.pdf_path for r in reports if r.pdf_path]


# ---------- builders ----------

def build_zip(data: dict, pdf_paths: list = None) -> io.BytesIO:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, (cols, rows) in data.items():
            text = io.StringIO()
            writer = csv.writer(text)
            writer.writerow(cols)
            writer.writerows(rows)
            # utf-8-sig so Excel opens Urdu/special characters correctly
            zf.writestr(f"{name}.csv", text.getvalue().encode("utf-8-sig"))

        for path in pdf_paths or []:
            if os.path.isfile(path):
                zf.write(path, arcname=f"monthly_report_pdfs/{os.path.basename(path)}")
    buffer.seek(0)
    return buffer


def build_xlsx(data: dict) -> io.BytesIO:
    wb = Workbook()
    wb.remove(wb.active)
    for name, (cols, rows) in data.items():
        ws = wb.create_sheet(title=name[:31])  # Excel sheet name limit
        ws.append(cols)
        for row in rows:
            ws.append(row)
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer