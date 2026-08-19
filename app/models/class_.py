from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.database import Base


class Class(Base):
    __tablename__ = "classes"
    __table_args__ = (UniqueConstraint("grade_id", "division", name="uq_grade_division"),)

    class_id = Column(Integer, primary_key=True, index=True)
    grade_id = Column(Integer, ForeignKey("grades.grade_id"), nullable=False)
    division = Column(String, nullable=False)
