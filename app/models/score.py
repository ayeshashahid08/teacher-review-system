from sqlalchemy import Column, Integer, Boolean, Numeric, String, ForeignKey
from app.database import Base


class Score(Base):
    __tablename__ = "scores"

    observation_id = Column(Integer, ForeignKey("observations.observation_id"), primary_key=True)
    mcq_score = Column(Numeric)            # sum of earned MCQ points (out of num_questions x 1)
    ai_score = Column(Numeric)             # AI's descriptive total, copied from ObservationRemarks.ai_descriptive_total (out of 9)
    written_score = Column(Numeric)        # principal's manual override of the descriptive score, only used if is_overridden=True, 
    #not built yet
    max_possible_score = Column(Numeric)   # (num_mcqs x 1) + 9
    total_score = Column(Numeric)
    percentage = Column(Numeric)
    grade = Column(String)
    is_overridden = Column(Boolean, default=False)
    override_reason = Column(String)
