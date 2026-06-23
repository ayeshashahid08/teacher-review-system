from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class ObservationMCQResponse(Base):
    __tablename__ = "observation_mcq_responses"

    observation_id = Column(Integer, ForeignKey("observations.observation_id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("question_bank.question_id"), primary_key=True)
    selected_option_id = Column(Integer, ForeignKey("question_options.option_id"), nullable=False)
    explanation = Column(String)
