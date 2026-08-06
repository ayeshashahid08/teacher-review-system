from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey
from app.database import Base


class QuestionBank(Base):
    __tablename__ = "question_bank"

    question_id = Column(Integer, primary_key=True, index=True)
    question_type = Column(String, nullable=False)
    question_text = Column(String, nullable=False)
    section = Column(String, nullable=True)       # e.g. "Academics", "Teacher-Student Relationship"
    subsection = Column(String, nullable=True)    # e.g. "In Class Performance", "Performance Beyond Class"
    max_points = Column(Numeric, nullable=False, default=1)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)


class QuestionOption(Base):
    __tablename__ = "question_options"

    option_id = Column(Integer, primary_key=True, index=True)
    option_grade = Column(String, nullable=False)   # "A+", "A", "B", "C"
    score_value = Column(Numeric, nullable=False)   # 1.0, 0.75, 0.5, 0.25