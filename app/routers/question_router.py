from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.question import GroupedQuestionsResponse,  QuestionCreate, QuestionUpdate, QuestionResponse
from app.services.question_service import(
    get_questions_grouped,
    create_question,
    get_question,
    update_question,
    delete_question,
    restore_question,
)
from app.services.auth_service import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("", response_model=GroupedQuestionsResponse)
def get_questions(
    question_type: str = "observation",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_questions_grouped(question_type, db)



# CREATE QUESTION
# ADMIN / PRINCIPAL ONLY
# -------------------------

@router.post(
    "",
    response_model=QuestionResponse
)
def create(
    data: QuestionCreate,
    current_user: User = Depends(
        require_role(["admin", "principal"])
    ),
    db: Session = Depends(get_db)
):
    return create_question(data, current_user, db)

# -------------------------
# DELETE QUESTION
# ADMIN / PRINCIPAL ONLY
# -------------------------

@router.delete(
    "/{question_id}"
)
def delete(
    question_id: int,
    current_user: User = Depends(
        require_role(["admin", "principal"])
    ),
    db: Session = Depends(get_db)
):
    delete_question(question_id, db)

    return {
        "message": "Question deleted successfully"
    }

# -------------------------
# RESTORE QUESTION
# ADMIN / PRINCIPAL ONLY
# -------------------------

@router.patch(
    "/{question_id}/restore",
    response_model=QuestionResponse
)
def restore(
    question_id: int,
    current_user: User = Depends(
        require_role(["admin", "principal"])
    ),
    db: Session = Depends(get_db)
):
    return restore_question(question_id, db)

@router.patch("/{question_id}/update", response_model=QuestionResponse)
def update(
    question_id: int, 
    data: QuestionUpdate,
    current_user: User = Depends(require_role(["admin", "principal"])),
    db: Session = Depends(get_db)):
    return update_question(
        question_id=question_id,
        data=data,
        db=db
    )



