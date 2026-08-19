from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class ClassYearlyStrength(Base):
    __tablename__ = "class_yearly_strength"

    class_id = Column(Integer, ForeignKey("classes.class_id"), primary_key=True)
    academic_year = Column(String, ForeignKey("academic_year_settings.academic_year"), primary_key=True)
    strength = Column(Integer, nullable=False)
