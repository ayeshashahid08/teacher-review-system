from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.database import Base


class CoordinatorAssignment(Base):
    __tablename__ = "coordinator_assignments"
    __table_args__ = (
        UniqueConstraint("user_id", "coordinator_type", "grade_id", "subject_id",
                        name="uq_coordinator_assignment"),
    )

    assignment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    coordinator_type = Column(String, nullable=False,
                             ) # chief_primary, chief_secondary, peer, subject
    grade_id = Column(Integer, ForeignKey("classes.class_id"), nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=True)
