from sqlalchemy import Column, Integer, Boolean, Numeric, String, ForeignKey
from app.database import Base


class Score(Base):
    __tablename__ = "scores"

    observation_id = Column(Integer, ForeignKey("observations.observation_id"), primary_key=True)
    mcq_score = Column(Numeric)
    ai_score = Column(Numeric)
    written_score = Column(Numeric)
    total_score = Column(Numeric)
    is_overridden = Column(Boolean, default=False)
    override_reason = Column(String)
