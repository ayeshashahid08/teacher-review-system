from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

from app.services.auth_service import get_current_user
from app.models.user import User

from app.schemas.acr import AcrCreate, AcrResponseInput, ACRReportResponse  
from app.services.acr_service import start_acr, save_acr_response, recalculate_acr_report, finalize_acr, get_acr_full_state, format_acr_response

router = APIRouter(prefix="/acr", tags=["ACR Report"])

@router.post("/start-draft", response_model= ACRReportResponse)
def create_draft(data: AcrCreate, reporter: User = Depends(get_current_user), db: Session = Depends(get_db)):
    acr = start_acr(data, reporter.user_id , db)
    return format_acr_response(acr, db)

@router.post("/{acr_id}/response")
def save_response(acr_id: int, data:AcrResponseInput ,current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    save_acr_response(acr_id, current_user.user_id, data, db)
    return {"message": "saved"}

@router.post("/{acr_id}/finalize")
def finalise(acr_id: int,current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recalculate_acr_report(acr_id, db)
    return finalize_acr(acr_id, current_user.user_id, db)

@router.get("/{acr_id}/full-state")
def get_full_state(acr_id: int, db:Session = Depends(get_db)):
    state = get_acr_full_state(acr_id, db)
    return {
    "acr_report": format_acr_response(state["acr_report"], db),
    "responses": state["responses"]
    }