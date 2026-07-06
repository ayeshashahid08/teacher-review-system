from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, UniqueConstraint
from app.database import Base


class ACRReport(Base):
    __tablename__ = "acr_report"
    __table_args__ = (UniqueConstraint("reported_id", "academic_year", name="uq_reported_academic_year"),)

    acr_id = Column(Integer, primary_key=True, index=True)
    academic_year = Column(String, ForeignKey("academic_year_settings.academic_year"), nullable=False)
    reported_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    days_present = Column(Integer)
    total_marks = Column(Integer)
    percentage = Column(Numeric)
    grade = Column(String)
    status = Column(String, default="draft")


class ACRResponse(Base):
    __tablename__ = "acr_responses"

    acr_id = Column(Integer, ForeignKey("acr_report.acr_id"), primary_key=True)
    acr_question_id = Column(Integer, ForeignKey("question_bank.question_id"), primary_key=True)
    acr_response_marks = Column(Integer, nullable=False)


class ACRGradeCriteria(Base):
    __tablename__ = "acr_grade_criteria"

    criteria_id = Column(Integer, primary_key=True, index=True)
    acr_question_id = Column(Integer, ForeignKey("question_bank.question_id"), nullable=False)
    min_marks = Column(Integer, nullable=False)
    max_marks = Column(Integer, nullable=False)
    grade = Column(String, nullable=False)


class ACROverallGradeCriteria(Base):
    __tablename__ = "acr_overall_grade_criteria"

    criteria_id = Column(Integer, primary_key=True, index=True)
    min_percentage = Column(Numeric, nullable=False)
    max_percentage = Column(Numeric, nullable=False)
    grade = Column(String, nullable=False)
