from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict


# class QuestionCreate(BaseModel):
#     question_type:str
#     question_text: str
#     created_by: int #userID

class QuestionBase(BaseModel):
    question_text: str
    question_type: str
    section: str
    subsection: str


class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    question_type:Optional[str]=None
    question_text: Optional[str]=None
    section: Optional[str] = None
    subsection: Optional[str] = None
    created_by: Optional[int]=None #userID

class QuestionResponse(BaseModel):
    question_id: int
    question_type:str
    question_text: str
    is_active: bool
    section: Optional[str] = None
    subsection: Optional[str] = None
    created_by: int #userID

    model_config = ConfigDict(from_attributes=True)

class QuestionOptionResponse(BaseModel):
    option_id: int
    option_grade: str
    score_value: float
    model_config=ConfigDict(from_attributes=True)


class GroupedQuestionsResponse(BaseModel):
    options: List[QuestionOptionResponse]                          # the 4 shared A+/A/B/C options
    sections: Dict[str, Dict[str, List[QuestionResponse]]]         # section -> subsection -> questions


