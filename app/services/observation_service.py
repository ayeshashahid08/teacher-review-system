from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date, datetime

from app.models.observation import Observation
from app.models.observation_mcq_response import ObservationMCQResponse
from app.models.observation_remarks import ObservationRemarks
from app.models.user import User
from app.models.subject import Subject
from app.models.class_ import Class
from app.models.question import QuestionBank
from app.models.class_yearly_strength import ClassYearlyStrength
from app.models.teacher_assignment import TeacherAssignment
from app.models.grade import Grade

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
    observation = db.query(Observation).filter(Observation.observation_id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Not Found")
    
    if observation.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft observations can be edited")
    
    remarks = db.query(ObservationRemarks).filter(
        ObservationRemarks.observation_id == observation_id
    ).first()

    if remarks:
        if data.general_observation is not None:
            remarks.general_observation = data.general_observation
        if data.remarks_suggestions is not None:
            remarks.remarks_suggestions = data.remarks_suggestions
    else:
        remarks = ObservationRemarks(
            observation_id=observation_id,
            general_observation=data.general_observation,
            remarks_suggestions=data.remarks_suggestions
        )
        db.add(remarks)

    db.commit()
    db.refresh(remarks)
    return remarks


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
    if not remarks or remarks.general_observation is None or remarks.remarks_suggestions is None:
        raise HTTPException(status_code=400, detail="Please complete the remarks section before submitting")

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
    grade = db.query(Grade).filter(Grade.grade_id == class_.grade_id).first()
    class_display = f"Grade {grade.grade_number}{class_.division}"
    
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
        "class_name": class_display,
        "class_strength": strength_record.strength if strength_record else None,
        "students_present": obs.students_present,
        "period": obs.period,
        "topic": obs.topic,
        "status": obs.status,
        "observed_at": obs.observed_at,
        "submitted_at": obs.submitted_at,
    }
