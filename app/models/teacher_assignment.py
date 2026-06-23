from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base


class TeacherAssignment(Base):
    __tablename__ = "teacher_assignments"

    assignment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    class_id = Column(Integer, ForeignKey("class.class_id"), nullable=False)
