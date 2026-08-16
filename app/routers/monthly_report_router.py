from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from app.database import get_db
from app.schemas.monthly_report import MonthlyReportGenerate, MonthlyReportEdit, MonthlyReportDetail
from app.services.monthly_report_service import (
    generate_monthly_report,
    edit_monthly_report,
    approve_monthly_report,
    get_report_with_percentages,
)
from app.services.pdf_service import generate_monthly_report_pdf
from app.models.monthly_report import MonthlyReport
from app.services.auth_service import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/monthly-reports", tags=["Monthly Reports"])


@router.post("/generate", response_model=MonthlyReportDetail)
def generate(
    data: MonthlyReportGenerate,
    principal: User = Depends(require_role(["principal"])),
    db: Session = Depends(get_db)
):
    report = generate_monthly_report(data, db)
    return get_report_with_percentages(report.report_id, db)

@router.get("/my")
def get_my_monthly_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.monthly_report import MonthlyReport
    return db.query(MonthlyReport).filter(MonthlyReport.user_id == current_user.user_id, MonthlyReport.status == "approved").all()



@router.get("/{report_id}", response_model=MonthlyReportDetail)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(MonthlyReport).filter(MonthlyReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    role = current_user.designation
    is_owner = current_user.user_id == report.user_id

    if role == "principal":
        pass  # principal can always view
    elif role == "coordinator":
        pass  # chief coordinator can view, but every write endpoint below excludes this role
    elif is_owner:
        if report.status != "approved":
            raise HTTPException(status_code=403, detail="Report is not yet approved")
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this report")

    return get_report_with_percentages(report_id, db)


@router.put("/{report_id}", response_model=MonthlyReportDetail)
def edit_report(
    report_id: int,
    data: MonthlyReportEdit,
    principal: User = Depends(require_role(["principal"])),
    db: Session = Depends(get_db)
):
    edit_monthly_report(report_id, data, principal, db)
    return get_report_with_percentages(report_id, db)


@router.post("/{report_id}/approve", response_model=MonthlyReportDetail)
def approve(
    report_id: int,
    principal: User = Depends(require_role(["principal"])),
    db: Session = Depends(get_db)
):
    report = approve_monthly_report(report_id, principal, db)

    report_data = get_report_with_percentages(report_id, db)
    pdf_path = generate_monthly_report_pdf(report_data)
    report.pdf_path = pdf_path
    db.commit()

    return get_report_with_percentages(report_id, db)


@router.get("/{report_id}/pdf")
def download_pdf(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(MonthlyReport).filter(MonthlyReport.report_id == report_id).first()
    if not report or not report.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not available")

    role = current_user.designation
    is_owner = current_user.user_id == report.user_id
    if role not in ("principal", "coordinator") and not (is_owner and report.status == "approved"):
        raise HTTPException(status_code=403, detail="Not authorized to view this report")

    return FileResponse(report.pdf_path, media_type="application/pdf", filename=f"report_{report_id}.pdf")