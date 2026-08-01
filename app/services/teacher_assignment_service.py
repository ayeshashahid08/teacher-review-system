from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import func

from app.models.teacher_assignment import TeacherAssignment
from app.models.user import User
from app.models.subject import Subject
from app.models.class_ import Class
from app.schemas.teacher_assignment import TeacherAssignmentCreate


def create_assignment(data: TeacherAssignmentCreate, assignment_creater: User, db: Session):
    if assignment_creater.designation != "admin" :
        raise HTTPException(status_code=403, detail="Only admin can assign teachers")

    existing = db.query(TeacherAssignment).filter(
        TeacherAssignment.user_id == data.user_id,
        TeacherAssignment.subject_id == data.subject_id,
        TeacherAssignment.class_id == data.class_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="This assignment already exists")

    new_assignment = TeacherAssignment(
        user_id=data.user_id,
        subject_id=data.subject_id,
        class_id=data.class_id,
        classes_per_week= data.classes_per_week
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    recalculate_teaching_load(data.user_id, db)
    return new_assignment


def get_assignments_for_user(user_id: int, db: Session):
    assignments = db.query(TeacherAssignment).filter(
        TeacherAssignment.user_id == user_id
    ).all()
    return assignments


def delete_assignment(assignment_id: int, db: Session):
    assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.assignment_id == assignment_id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(assignment)
    db.commit()
    recalculate_teaching_load(assignment.user_id, db)
    return {"message": "Assignment deleted"}


def format_assignment_response(assignment: TeacherAssignment, db: Session) -> dict:
    teacher = db.query(User).filter(User.user_id == assignment.user_id).first()
    subject = db.query(Subject).filter(Subject.subject_id == assignment.subject_id).first()
    class_ = db.query(Class).filter(Class.class_id == assignment.class_id).first()

    return {
        "assignment_id": assignment.assignment_id,
        "teacher_name": f"{teacher.first_name} {teacher.last_name}",
        "subject_name": subject.subject_name,
        "class_name": class_.class_name,
    }



def recalculate_teaching_load(user_id: int, db: Session):
    total = db.query(func.sum(TeacherAssignment.classes_per_week)).filter(
        TeacherAssignment.user_id == user_id
    ).scalar() or 0
    
    user = db.query(User).filter(User.user_id == user_id).first()
    user.teaching_load = total
    db.commit()

