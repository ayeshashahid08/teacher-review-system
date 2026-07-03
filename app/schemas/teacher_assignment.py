from pydantic import BaseModel


class TeacherAssignmentCreate(BaseModel):
    user_id: int
    subject_id: int
    class_id: int


class TeacherAssignmentResponse(BaseModel):
    assignment_id: int
    teacher_name: str
    subject_name: str
    class_name: str

    class Config:
        from_attributes = True
