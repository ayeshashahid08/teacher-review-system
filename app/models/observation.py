from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, ForeignKey
from app.database import Base


class Observation(Base):
    __tablename__ = "observations"

    observation_id = Column(Integer, primary_key=True, index=True)
    observer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    observee_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    class_id = Column(Integer, ForeignKey("class.class_id"), nullable=False)
    students_present = Column(Integer)
    period = Column(Integer)
    topic = Column(String)
    observed_at = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    submitted_at = Column(TIMESTAMP)
