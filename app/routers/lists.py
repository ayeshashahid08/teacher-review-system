from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.subject import Subject
from app.models.class_ import Class
from app.models.question import QuestionBank
from app.models.acr import ACRReport
from app.schemas.user import UserPublicResponse, UserFullResponse
from app.models.teacher_assignment import TeacherAssignment
from app.services.acr_service import format_acr_response
from app.services.observation_service import format_observation_response
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
    from app.models.grade import Grade
    classes = db.query(Class).all()
    result = []
    for c in classes:
        grade = db.query(Grade).filter(Grade.grade_id == c.grade_id).first()
        result.append({
            "class_id": c.class_id,
            "grade_number": grade.grade_number,
            "division": c.division,
            "school_level": grade.school_level,
            "display_name": f"Grade {grade.grade_number}{c.division}"
        })
    return result


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
        User.designation=="teacher",
        User.is_active == True
    ).all()

@router.get("/users/teachers/dropdown")
def get_teachers_dropdown(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    teachers = db.query(User).filter(
        User.designation == "teacher",
        User.is_active == True
    ).all()
    return [
        {
            "user_id": t.user_id,
            "display_name": f"{t.first_name} {t.last_name}"
        }
        for t in teachers
    ]



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


@router.get("/users/{user_id}")
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.designation in ["admin", "principal"]:
        return UserFullResponse.model_validate(user)
    else:
        return UserPublicResponse.model_validate(user)
    

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
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.grade import Grade
    assignments = db.query(TeacherAssignment).filter(
        TeacherAssignment.user_id == user_id,
        TeacherAssignment.subject_id == subject_id
    ).all()

    if not assignments:
        raise HTTPException(status_code=404, detail="No classes found for this teacher and subject")

    result = []
    for a in assignments:
        class_ = db.query(Class).filter(Class.class_id == a.class_id).first()
        grade = db.query(Grade).filter(Grade.grade_id == class_.grade_id).first()
        result.append({
            "class_id": class_.class_id,
            "grade_number": grade.grade_number,
            "division": class_.division,
            "school_level": grade.school_level,
            "display_name": f"Grade {grade.grade_number}{class_.division}"
        })
    return result

@router.get("/my-acr")
def get_my_acr(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reports = db.query(ACRReport).filter(
        ACRReport.reported_id == current_user.user_id,
        ACRReport.status == "approved"
    ).all()
    return [format_acr_response(r, db) for r in reports]

@router.get("/my-drafts")
def get_my_drafts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    drafts = db.query(Observation).filter(
        Observation.observer_id == current_user.user_id,
        Observation.status == "draft"
    ).all()
    return [format_observation_response(obs, db) for obs in drafts]


@router.get("/reports-submitted-by-me")
def get_my_acr_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reports = db.query(ACRReport).filter(
        ACRReport.reporter_id == current_user.user_id
    ).all()
    return [format_acr_response(r, db) for r in reports]