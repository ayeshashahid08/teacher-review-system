from sqlalchemy import Column, Integer, String, ForeignKey, Text
from app.database import Base


class ObservationRemarks(Base):
    __tablename__ = "observation_remarks"

    observation_id = Column(Integer, ForeignKey("observations.observation_id"), primary_key=True)
    general_observation = Column(Text)
    remarks_suggestions = Column(Text)
