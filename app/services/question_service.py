from sqlalchemy.orm import Session
from collections import defaultdict

from app.models.question import QuestionBank, QuestionOption


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