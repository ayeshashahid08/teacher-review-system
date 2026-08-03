from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class PasswordResetRequest(Base):
    __tablename__ = "password_reset_requests"

    request_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    reason = Column(String)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
