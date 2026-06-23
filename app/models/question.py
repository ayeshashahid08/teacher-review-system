from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey
from app.database import Base


class QuestionBank(Base):
    __tablename__ = "question_bank"

    question_id = Column(Integer, primary_key=True, index=True)
    question_type = Column(String, nullable=False)
    question_text = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)


class QuestionOption(Base):
    __tablename__ = "question_options"

    option_id = Column(Integer, primary_key=True, index=True)
    option_grade = Column(String, nullable=False)
    score_value = Column(Numeric, nullable=False)
