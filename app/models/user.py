from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    joined_at = Column(TIMESTAMP, server_default=func.now())
    years_of_service = Column(Integer)
    employment_number = Column(Integer, unique=True, nullable=False)
    CNIC = Column(String, unique=True, nullable=False)
    qualification = Column(String)
    additional_responsibilities = Column(Text)
    extra_credentials = Column(Text)
    teaching_load = Column(Integer)
    added_by = Column(Integer, ForeignKey("users.user_id"))
    must_change_password = Column(Boolean, default=True)
    
