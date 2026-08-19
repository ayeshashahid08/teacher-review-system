from sqlalchemy import Column, Integer, String, UniqueConstraint
from app.database import Base


class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = (UniqueConstraint("grade_number", name="uq_grade_number"),)

    grade_id = Column(Integer, primary_key=True, index=True)
    grade_number = Column(Integer, nullable=False)
    school_level = Column(String, nullable=False)
