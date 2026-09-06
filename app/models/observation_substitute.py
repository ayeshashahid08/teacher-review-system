from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from app.database import Base


class ObservationSubstitute(Base):
    __tablename__ = "observation_substitutes"

    id = Column(Integer, primary_key=True, index=True)
    observation_id = Column(Integer, ForeignKey("observations.observation_id"), nullable=False)
    original_role = Column(String, nullable=False)
    # 'chief_coordinator', 'peer_coordinator', 'subject_coordinator'
    substitute_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    # null until principal assigns someone
    assigned_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    assigned_at = Column(TIMESTAMP, nullable=True)
    is_filled = Column(Boolean, default=False)
    # false = waiting for principal to assign, true = substitute assigned
