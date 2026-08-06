from sqlalchemy import Column, Integer, ForeignKey, Text, Numeric
from app.database import Base


class ObservationRemarks(Base):
    __tablename__ = "observation_remarks"

    observation_id = Column(Integer, ForeignKey("observations.observation_id"), primary_key=True)

    # human-filled — 3 separate inputs
    strengths = Column(Text)
    areas_of_improvement = Column(Text)
    suggestions_recommendations = Column(Text)

    # AI-rated — reads all 3 together, scores each 0-3
    ai_strengths_score = Column(Numeric)
    ai_improvement_score = Column(Numeric)
    ai_suggestions_score = Column(Numeric)
    ai_descriptive_total = Column(Numeric)   # sum of the three, out of 9
    ai_rationale = Column(Text)