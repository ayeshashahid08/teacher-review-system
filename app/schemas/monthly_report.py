from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MonthlyReportGenerate(BaseModel):
    user_id: int
    month: int
    year: int


class MCQPercentage(BaseModel):
    question_id: int
    question_text: str
    response_percentage: float  # % of max possible marks this teacher scored on this question, averaged across observations


class MonthlyReportEdit(BaseModel):
    human_suggestions: Optional[str] = None


class MonthlyReportApprove(BaseModel):
    comments: Optional[str] = None


class MonthlyReportDetail(BaseModel):
    report_id: int
    teacher_name: str
    month: int
    year: int
    total_observations: int
    average_score: Optional[float] = None
    mcq_percentages: List[MCQPercentage]
    ai_suggestions: Optional[str] = None
    human_suggestions: Optional[str] = None
    status: str
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None
    pdf_path: Optional[str] = None

    class Config:
        from_attributes = True