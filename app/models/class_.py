from sqlalchemy import Column, Integer, String
from app.database import Base


class Class(Base):
    __tablename__ = "class"

    class_id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String, nullable=False)

