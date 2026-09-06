from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from app.database import Base


class ObservationApproval(Base):
    __tablename__ = "observation_approval"

    approval_id = Column(Integer, primary_key=True, index=True)
    observation_id = Column(Integer, ForeignKey("observations.observation_id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    stage = Column(Integer, nullable=False)  # 1 or 2
    role_in_stage = Column(String, nullable=False)
    # principal, chief_coordinator, peer_coordinator, subject_coordinator
    action = Column(String, nullable=False)
    # approved, revision_requested (only principal can revision_request)
    comments = Column(String, nullable=True)
    acted_at = Column(TIMESTAMP, nullable=True)
    is_substitute = Column(Boolean, default=False)
