from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.question import GroupedQuestionsResponse
from app.services.question_service import get_questions_grouped
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("", response_model=GroupedQuestionsResponse)
def get_questions(
    question_type: str = "observation",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_questions_grouped(question_type, db)