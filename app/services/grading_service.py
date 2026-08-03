from sqlalchemy.orm import Session
# adjust this import to whatever file ACROverallGradeCriteria actually lives in
from app.models.acr import ACROverallGradeCriteria


def get_grade_for_percentage(percentage: float, db: Session) -> str:
    criteria = db.query(ACROverallGradeCriteria).filter(
        ACROverallGradeCriteria.min_percentage <= percentage
    ).order_by(ACROverallGradeCriteria.min_percentage.desc()).first()

    return criteria.grade if criteria else "Below Expectation"