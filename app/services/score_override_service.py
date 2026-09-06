from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.score import Score
from app.models.user import User
from app.schemas.score import ScoreOverrideInput

from app.services.score_service import calculate_grade

def override_score(
    observation_id: int,
    data: ScoreOverrideInput,
    principal: User,
    db: Session
) -> Score:

    score = db.query(Score).filter(
        Score.observation_id == observation_id
    ).first()

    if not score:
        raise HTTPException(
            status_code=404,
            detail="Score not found for this observation"
        )

    if data.written_score < 0 or data.written_score > 5:
        raise HTTPException(
            status_code=400,
            detail="Written score must be between 0 and 5"
        )


    score.written_score = data.written_score

    score.is_overridden = True

    score.override_reason = data.override_reason

    descriptive_score = data.written_score

    mcq_score = float(score.mcq_score or 0)

    total_score = mcq_score + descriptive_score

    score.total_score = total_score

    max_possible_score = float(score.max_possible_score or 0)

    if max_possible_score > 0:
        percentage = (
            total_score / max_possible_score
        ) * 100
    else:
        percentage = 0

    score.percentage = percentage

    score.grade = calculate_grade(percentage)

    db.commit()
    db.refresh(score)

    return score