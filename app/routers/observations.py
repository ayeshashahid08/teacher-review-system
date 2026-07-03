from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.observation import (
    ObservationDraftCreate,
    ObservationDetailsUpdate,
    MCQResponseInput,
    RemarksInput,
)
from app.services.observation_service import (
    start_observation_draft,
    update_observation_details,
    save_mcq_response,
    save_remarks,
    get_full_observation_state,
    submit_observation,
    format_observation_response,
)
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/observations", tags=["Observations"])


@router.post("/start-draft")
def create_draft(
    data: ObservationDraftCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obser = start_observation_draft(data, current_user.user_id, db)
    return format_observation_response(obser, db)


@router.put("/{observation_id}/details")
def update_details(
    observation_id: int,
    data: ObservationDetailsUpdate,
    db: Session = Depends(get_db)
):
    updated_obser = update_observation_details(observation_id, data, db)
    return format_observation_response(updated_obser, db)


@router.post("/{observation_id}/mcq-response")
def add_mcq_response(
    observation_id: int,
    data: MCQResponseInput,
    db: Session = Depends(get_db)
):
    save_mcq_response(observation_id, data, db)
    return {"message": "saved"}


@router.patch("/{observation_id}/remarks")
def update_remarks(
    observation_id: int,
    data: RemarksInput,
    db: Session = Depends(get_db)
):
    save_remarks(observation_id, data, db)
    return {"message": "saved"}


@router.get("/{observation_id}/full-state")
def get_draft_state(
    observation_id: int,
    db: Session = Depends(get_db)
):
    return get_full_observation_state(observation_id, db)


@router.post("/{observation_id}/submit")
def submit(
    observation_id: int,
    db: Session = Depends(get_db)
):
    submitted_obser = submit_observation(observation_id, db)
    return format_observation_response(submitted_obser, db)
