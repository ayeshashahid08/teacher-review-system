from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.academic_year_settings import AcademicYearSettings
from app.services.auth_service import require_role   # adjust to your actual file name
from app.services import export_service

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/academic-year-export/{academic_year}")
def download_academic_year(
    academic_year: str,
    format: str = Query("zip", pattern="^(zip|xlsx)$"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "principal"])),
):
    try:
        export_service.parse_academic_year(academic_year)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    exists = db.query(AcademicYearSettings).filter(
        AcademicYearSettings.academic_year == academic_year
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Academic year not found")

    data = export_service.collect_data(db, academic_year)

    if format == "xlsx":
        buffer = export_service.build_xlsx(data)
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        pdfs = export_service.collect_pdf_paths(db, academic_year)
        buffer = export_service.build_zip(data, pdfs)
        media = "application/zip"

    filename = f"academic_year_{academic_year}.{format}"
    return StreamingResponse(
        buffer,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )