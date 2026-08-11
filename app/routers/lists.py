from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.subject import Subject
from app.models.class_ import Class
from app.models.question import QuestionBank
from app.schemas.user import UserPublicResponse, UserFullResponse
from app.models.teacher_assignment import TeacherAssignment
router = APIRouter(tags=["Lists"])


@router.get("/subjects")
def get_subjects(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Subject).all()


@router.get("/classes")
def get_classes(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Class).all()



@router.get("/users")
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    users = db.query(User).filter(User.is_active == True).all()

    if current_user.designation in ["admin", "principal"]:
        return [UserFullResponse.model_validate(u) for u in users]
    else:
        return [UserPublicResponse.model_validate(u) for u in users]


@router.get("/users/teachers")
def get_teachers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(User).filter(
        User.designation.in_(["teacher", "peer_coordinator", "chief_coordinator"]),
        User.is_active == True
    ).all()


@router.get("/question-bank/observation")
def get_observation_questions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(QuestionBank).filter(
        QuestionBank.question_type == "observation",
        QuestionBank.is_active == True
    ).all()


@router.get("/question-bank/acr")
def get_acr_questions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(QuestionBank).filter(
        QuestionBank.question_type == "acr",
        QuestionBank.is_active == True
    ).all()


@router.get("/question-options")
def get_question_options(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.question import QuestionOption
    return db.query(QuestionOption).all()


@router.get("/observations/my")
def get_my_observations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.observation import Observation
    return db.query(Observation).filter(
        Observation.observee_id == current_user.user_id, Observation.status == "approved"
    ).all()


@router.get("/observations/submitted-by-me")
def get_observations_submitted_by_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.observation import Observation
    return db.query(Observation).filter(
        Observation.observer_id == current_user.user_id
    ).all()


@router.get("/users/{user_id}", response_model = UserPublicResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/{user_id}/subjects")
def get_subjects_for_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignments = db.query(TeacherAssignment).filter(
        TeacherAssignment.user_id == user_id
    ).all()

    if not assignments:
        raise HTTPException(status_code=404, detail="No assignments found for this teacher")

    subject_ids = [a.subject_id for a in assignments]
    subjects = db.query(Subject).filter(Subject.subject_id.in_(subject_ids)).all()
    return subjects


@router.get("/users/{user_id}/classes")
def get_classes_for_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignments = db.query(TeacherAssignment).filter(
        TeacherAssignment.user_id == user_id
    ).all()

    if not assignments:
        raise HTTPException(status_code=404, detail="No assignments found for this teacher")

    class_ids = [a.class_id for a in assignments]
    classes = db.query(Class).filter(Class.class_id.in_(class_ids)).all()
    return classes
