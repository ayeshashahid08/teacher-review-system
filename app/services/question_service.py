from sqlalchemy.orm import Session
from collections import defaultdict
from fastapi import HTTPException


from app.models.question import QuestionBank, QuestionOption
from app.models.user import User
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
)


def get_questions_grouped(question_type: str, db: Session) -> dict:
    questions = db.query(QuestionBank).filter(
        QuestionBank.question_type == question_type,
        QuestionBank.is_active == True
    ).all()

    options = db.query(QuestionOption).all()

    sections = defaultdict(lambda: defaultdict(list))
    for q in questions:
        section_key = q.section or "General"
        subsection_key = q.subsection or "General"
        sections[section_key][subsection_key].append(q)

    # convert nested defaultdicts to plain dicts so FastAPI/Pydantic serializes cleanly
    sections_plain = {
        section: dict(subsections) for section, subsections in sections.items()
    }

    return {
        "options": options,
        "sections": sections_plain,
    }


def create_question(
    data: QuestionCreate,
    current_user: User,
    db: Session
) -> QuestionBank:

    question = QuestionBank(
        question_text=data.question_text,
        question_type=data.question_type,
        section=data.section,
        subsection=data.subsection,
        is_active=True,
        created_by=current_user.user_id
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question


def get_question(
    question_id: int,
    db: Session
) -> QuestionBank:

    question = db.query(QuestionBank).filter(
        QuestionBank.question_id == question_id,
        QuestionBank.is_active == True
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    return question


def update_question(
    question_id: int,
    data: QuestionUpdate,
    db: Session
) -> QuestionBank:

    question = db.query(QuestionBank).filter(
        QuestionBank.question_id == question_id,
        QuestionBank.is_active == True
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(question, field, value)

    db.commit()
    db.refresh(question)

    return question


def delete_question(
    question_id: int,
    db: Session
) -> None:

    question = db.query(QuestionBank).filter(
        QuestionBank.question_id == question_id,
        QuestionBank.is_active == True
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    # Soft delete
    question.is_active = False

    db.commit()


def restore_question(
    question_id: int,
    db: Session
) -> QuestionBank:

    question = db.query(QuestionBank).filter(
        QuestionBank.question_id == question_id,
        QuestionBank.is_active == False
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Inactive question not found"
        )

    question.is_active = True

    db.commit()
    db.refresh(question)

    return question