from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text
from app.database import Base


class SalaryIncrementEligibility(Base):
    __tablename__ = "salary_increment_eligibility"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    academic_year = Column(String, primary_key=True, nullable=False)
    is_eligible = Column(Boolean)
    decided_by = Column(Integer, ForeignKey("users.user_id"))
    decision_notes = Column(Text)
    decided_at = Column(TIMESTAMP)
