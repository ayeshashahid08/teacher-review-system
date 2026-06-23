from sqlalchemy import Column, String, Integer
from app.database import Base


class AcademicYearSettings(Base):
    __tablename__ = "academic_year_settings"

    academic_year = Column(String, primary_key=True)
    total_working_days = Column(Integer, nullable=False)
