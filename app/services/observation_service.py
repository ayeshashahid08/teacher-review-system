from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date, datetime

from app.models.observation import Observation
from app.models.observation_mcq_response import ObservationMCQResponse
from app.models.observation_remarks import ObservationRemarks
from app.models.user import User
from app.models.subject import Subject
from app.models.class_ import Class
from app.models.question import QuestionBank, QuestionOption
from app.models.class_yearly_strength import ClassYearlyStrength
from app.models.score import Score
from app.schemas.score import ScoreOverrideInput
from app.models.teacher_assignment import TeacherAssignment
from app.services.descriptive_ai_rating_service import rate_descriptive_section
from app.services.grading_service import get_grade_for_percentage

from app.core.security import decode_access_token

from app.schemas.observation import (
    ObservationDraftCreate,
    ObservationDetailsUpdate,
    MCQResponseInput,
    RemarksInput,
)


def start_observation_draft(data: ObservationDraftCreate, observer_id: int, db: Session) -> Observation:
    observer = db.query(User).filter(User.user_id == observer_id).first()
    if observer.designation == "admin":
        raise HTTPException(status_code=403, detail="Admin cannot take observations")
    
    observee = db.query(User).filter(User.user_id == data.observee_id).first()
    if not observee:
        raise HTTPException(status_code=404, detail="Observee not found")
    if observee.designation in ["admin", "principal"]:
        raise HTTPException(status_code=403, detail="Admin and principal cannot be observed")
    
    if observer_id == data.observee_id:
        raise HTTPException(status_code=400, detail="You cannot observe yourself")

    assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.user_id == data.observee_id,
        TeacherAssignment.subject_id == data.subject_id,
        TeacherAssignment.class_id == data.class_id
    ).first()
    if not assignment:
        raise HTTPException(status_code=400, detail="This teacher is not assigned to this subject and class combination")

    new_observation = Observation(
        observer_id=observer_id,
        observee_id=data.observee_id,
        subject_id=data.subject_id,
        class_id=data.class_id,
        observed_at=date.today(),
        status="draft"
    )
    db.add(new_observation)
    db.commit()
    db.refresh(new_observation)
    return new_observation
    


def update_observation_details(observation_id: int, data: ObservationDetailsUpdate, db: Session) -> Observation:
    observation = db.query(Observation).filter(Observation.observation_id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Not Found")
    
    if observation.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft observations can be edited")

    if data.students_present is not None:
        observation.students_present = data.students_present
    if data.period is not None:
        observation.period = data.period
    if data.topic is not None:
        observation.topic = data.topic

    db.commit()
    db.refresh(observation)
    return observation



def save_mcq_response(observation_id: int, data: MCQResponseInput, db: Session) -> ObservationMCQResponse:
    observation = db.query(Observation).filter(Observation.observation_id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Not Found")
    
    if observation.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft observations can be edited")

    question = db.query(QuestionBank).filter(
        QuestionBank.question_id == data.question_id,
        QuestionBank.question_type == "observation",
        QuestionBank.is_active == True
    ).first()
    if not question:
        raise HTTPException(status_code=400, detail="Invalid question for observation form")
    
    
    response = db.query(ObservationMCQResponse).filter(
        ObservationMCQResponse.observation_id == observation_id,
        ObservationMCQResponse.question_id == data.question_id
    ).first()

    if response:
        response.selected_option_id = data.selected_option_id
        response.explanation = data.explanation
    else:
        response = ObservationMCQResponse(
            observation_id=observation_id,
            question_id=data.question_id,
            selected_option_id=data.selected_option_id,
            explanation=data.explanation
        )
        db.add(response)

    db.commit()
    db.refresh(response)
    return response

def save_remarks(observation_id: int, data: RemarksInput, db: Session) -> ObservationRemarks:
    remarks = db.query(ObservationRemarks).filter(
        ObservationRemarks.observation_id == observation_id
    ).first()

    if remarks:
        if data.strengths is not None:
            remarks.strengths = data.strengths
        if data.areas_of_improvement is not None:
            remarks.areas_of_improvement = data.areas_of_improvement
        if data.suggestions_recommendations is not None:
            remarks.suggestions_recommendations = data.suggestions_recommendations
    else:
        remarks = ObservationRemarks(
            observation_id=observation_id,
            strengths=data.strengths,
            areas_of_improvement=data.areas_of_improvement,
            suggestions_recommendations=data.suggestions_recommendations,
        )
        db.add(remarks)

    db.commit()
    db.refresh(remarks)

    # Once all 3 fields are present, ask the AI to rate them.
    # Re-runs on every edit so the rating always reflects the latest text.
    if remarks.strengths and remarks.areas_of_improvement and remarks.suggestions_recommendations:
        rating = rate_descriptive_section(
            remarks.strengths, remarks.areas_of_improvement, remarks.suggestions_recommendations
        )
        remarks.ai_strengths_score = rating["strengths_score"]
        remarks.ai_improvement_score = rating["improvement_score"]
        remarks.ai_suggestions_score = rating["suggestions_score"]
        remarks.ai_descriptive_total = rating["total_score"]
        remarks.ai_rationale = rating["rationale"]
        db.commit()
        db.refresh(remarks)

    return remarks

def compute_observation_score(observation_id: int, db: Session) -> Score:
    mcq_responses = db.query(ObservationMCQResponse).filter(
        ObservationMCQResponse.observation_id == observation_id
    ).all()

    mcq_points_earned = 0.0
    for response in mcq_responses:
        option = db.query(QuestionOption).filter(
            QuestionOption.option_id == response.selected_option_id
        ).first()
        if option:
            mcq_points_earned += float(option.score_value)

    num_mcqs = db.query(QuestionBank).filter(
        QuestionBank.question_type == "observation",
        QuestionBank.is_active == True
    ).count()

    remarks = db.query(ObservationRemarks).filter(
        ObservationRemarks.observation_id == observation_id
    ).first()
    descriptive_score = float(remarks.ai_descriptive_total) if remarks and remarks.ai_descriptive_total is not None else 0.0

    max_possible = (num_mcqs * 1) + 9   # 1 pt per MCQ + 9 for the descriptive section
    total_earned = mcq_points_earned + descriptive_score
    percentage = (total_earned / max_possible) * 100 if max_possible else 0

    grade = get_grade_for_percentage(percentage, db)

    score = db.query(Score).filter(Score.observation_id == observation_id).first()
    if not score:
        score = Score(observation_id=observation_id)
        db.add(score)

    score.mcq_score = mcq_points_earned
    score.ai_score = descriptive_score
    score.max_possible_score = max_possible
    score.total_score = total_earned
    score.percentage = round(percentage, 2)
    score.grade = grade

    db.commit()
    db.refresh(score)
    return score

def override_observation_score(observation_id: int, data: ScoreOverrideInput, principal: User, db: Session) -> Score:
    score = db.query(Score).filter(Score.observation_id == observation_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="No score exists yet for this observation — submit it first")

    obs = db.query(Observation).filter(Observation.observation_id == observation_id).first()
    if not obs or obs.status not in ("submitted", "pending_chief_coordinator", "pending_peer_coordinator", "approved"):
        raise HTTPException(status_code=400, detail="Observation must be submitted before its score can be overridden")

    score.written_score = data.written_score
    score.is_overridden = True
    score.override_reason = data.override_reason

    # descriptive component now comes from the principal's override instead of the AI score
    total_earned = score.mcq_score + score.written_score
    percentage = (total_earned / score.max_possible_score) * 100 if score.max_possible_score else 0

    score.total_score = total_earned
    score.percentage = round(percentage, 2)
    score.grade = get_grade_for_percentage(percentage, db)

    db.commit()
    db.refresh(score)
    return score

def get_full_observation_state(observation_id: int, db: Session) -> dict:
    target_obs = db.query(Observation).filter(Observation.observation_id == observation_id).first()
    if not target_obs:
        raise HTTPException(status_code=404, detail="Observation not found")

    obs_mcq_responses = db.query(ObservationMCQResponse).filter(
        ObservationMCQResponse.observation_id == observation_id
    ).all()

    obs_text_response = db.query(ObservationRemarks).filter(
        ObservationRemarks.observation_id == observation_id
    ).first()

    return {"observation": target_obs, "mcq_responses": obs_mcq_responses, "remarks": obs_text_response}


def submit_observation(observation_id: int, db: Session) -> Observation:
    obs = db.query(Observation).filter(Observation.observation_id == observation_id).first()
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")

    if obs.period is None or obs.topic is None or obs.students_present is None:
        raise HTTPException(status_code=400, detail="Please complete all observation details before submitting")

    remarks = db.query(ObservationRemarks).filter(
        ObservationRemarks.observation_id == observation_id
    ).first()
    if (not remarks or remarks.strengths is None or remarks.areas_of_improvement is None
            or remarks.suggestions_recommendations is None):
        raise HTTPException(status_code=400, detail="Please complete strengths, areas of improvement, and suggestions before submitting")
    if remarks.ai_descriptive_total is None:
        raise HTTPException(status_code=400, detail="AI rating for the descriptive section is not ready yet")

    total_ques = db.query(QuestionBank).filter(
        QuestionBank.question_type == "observation",
        QuestionBank.is_active == True
    ).count()

    answered_ques = db.query(ObservationMCQResponse).filter(
        ObservationMCQResponse.observation_id == observation_id
    ).count()

    if total_ques != answered_ques:
        raise HTTPException(status_code=400, detail="Please answer all questions before submitting")

    obs.status = "submitted"
    obs.submitted_at = datetime.utcnow()
    db.commit()
    db.refresh(obs)

    compute_observation_score(observation_id, db)  # writes mcq_score, ai_score, total_score, percentage, grade to Score

    return obs
    
def get_academic_year(obs: Observation) ->str:
    month = obs.observed_at.month
    year = obs.observed_at.year
    if month >= 1 and month <= 7:
        academic_year = str(year-1)+ '-' +str(year)
    else:
        academic_year = str(year)+'-' +str(year+1) 
    return academic_year

def format_observation_response(obs: Observation, db: Session) -> dict:
    observer = db.query(User).filter(User.user_id == obs.observer_id).first()
    observee = db.query(User).filter(User.user_id == obs.observee_id).first()
    subject = db.query(Subject).filter(Subject.subject_id == obs.subject_id).first()
    class_ = db.query(Class).filter(Class.class_id == obs.class_id).first()

    
    academic_year = get_academic_year(obs)
    strength_record = db.query(ClassYearlyStrength).filter(
        ClassYearlyStrength.class_id == obs.class_id,
        ClassYearlyStrength.academic_year == academic_year
    ).first()

    return {
        "observation_id": obs.observation_id,
        "observer_name": f"{observer.first_name} {observer.last_name}",
        "observee_name": f"{observee.first_name} {observee.last_name}",
        "subject_name": subject.subject_name,
        "class_name": class_.class_name,
        "class_strength": strength_record.strength if strength_record else None,
        "students_present": obs.students_present,
        "period": obs.period,
        "topic": obs.topic,
        "status": obs.status,
        "observed_at": obs.observed_at,
        "submitted_at": obs.submitted_at,
    }
