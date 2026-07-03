from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from app.database import Base


class ObservationApproval(Base):
    __tablename__ = "observation_approval"

    approval_id = Column(Integer, primary_key=True, index=True)
    observation_id = Column(Integer, ForeignKey("observations.observation_id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    stage = Column(String, nullable=False) # principal, chief coordinator...
    action = Column(String, nullable=False)
    comments = Column(String)
    acted_at = Column(TIMESTAMP)
