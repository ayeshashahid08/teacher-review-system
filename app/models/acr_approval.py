from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from app.database import Base


class ACRApproval(Base):
    __tablename__ = "acr_approvals"

    approval_id = Column(Integer, primary_key=True, index=True)
    acr_id = Column(Integer, ForeignKey("acr_report.acr_id"), nullable=False)
    principal_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    action = Column(String, nullable=False)  # approved, revision_requested
    comments = Column(String, nullable=True)
    acted_at = Column(TIMESTAMP, nullable=True)
