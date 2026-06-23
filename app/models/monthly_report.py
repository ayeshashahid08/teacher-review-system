from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey, UniqueConstraint, Text
from app.database import Base


class MonthlyReport(Base):
    __tablename__ = "monthly_reports"
    __table_args__ = (UniqueConstraint("user_id", "month", "year", name="uq_user_month_year"),)

    report_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    total_observations = Column(Integer)
    average_score = Column(Numeric)
    ai_suggestions = Column(Text)
    human_suggestions = Column(Text)
    generated_at = Column(TIMESTAMP)


class ReportInsight(Base):
    __tablename__ = "report_insights"

    insight_id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("monthly_reports.report_id"), nullable=False)
    insight_text = Column(String, nullable=False)
    insight_type = Column(String, nullable=False)
    source_observation_id = Column(Integer, ForeignKey("observations.observation_id"))
