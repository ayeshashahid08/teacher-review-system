from sqlalchemy import Column, Integer, String
from app.database import Base


class Subject(Base):
    __tablename__ = "subjects"

    subject_id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String, nullable=False)
