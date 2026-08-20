from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.observation import Observation
from app.models.observation_mcq_response import ObservationMCQResponse
from app.models.observation_remarks import ObservationRemarks
from app.models.question import QuestionOption
from app.models.score import Score


def calculate_grade(percentage: float) -> str:
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    else:
        return "D"


def calculate_observation_score(
    observation_id: int,
    db: Session
) -> Score:

    observation = db.query(Observation).filter(
        Observation.observation_id == observation_id
    ).first()

    if not observation:
        raise HTTPException(
            status_code=404,
            detail="Observation not found"
        )

    mcq_responses = db.query(ObservationMCQResponse).filter(
        ObservationMCQResponse.observation_id == observation_id
    ).all()

    mcq_score = 0.0

    for response in mcq_responses:
        option = db.query(QuestionOption).filter(
            QuestionOption.option_id == response.selected_option_id
        ).first()

        if option:
            mcq_score += float(option.score_value)

    remarks = db.query(ObservationRemarks).filter(
        ObservationRemarks.observation_id == observation_id
    ).first()

    ai_score = None

    if remarks and remarks.ai_descriptive_total is not None:
        ai_score = float(remarks.ai_descriptive_total)

    number_of_mcqs = len(mcq_responses)

    max_mcq_score = number_of_mcqs * 1.0
    max_descriptive_score = 5.0

    max_possible_score = max_mcq_score + max_descriptive_score

    descriptive_score = 0.0
    descriptive_score = (
        score.written_score
        if score.is_overridden
        else ai_score
)

    if ai_score is not None:
        descriptive_score = ai_score

    total_score = mcq_score + descriptive_score

    percentage = (
        (total_score / max_possible_score) * 100
        if max_possible_score > 0
        else 0
    )

    grade = calculate_grade(percentage)

    score = db.query(Score).filter(
        Score.observation_id == observation_id
    ).first()

    if score:
        score.mcq_score = mcq_score
        score.ai_score = ai_score
        score.max_possible_score = max_possible_score
        score.total_score = total_score
        score.percentage = percentage
        score.grade = grade

    else:
        score = Score(
            observation_id=observation_id,
            mcq_score=mcq_score,
            ai_score=ai_score,
            written_score=None,
            max_possible_score=max_possible_score,
            total_score=total_score,
            percentage=percentage,
            grade=grade,
            is_overridden=False,
            override_reason=None
        )

        db.add(score)

    db.commit()
    db.refresh(score)

    return score