# schemas/games/question_answer_options_schema.py
from pydantic import BaseModel
from typing import Optional
class QuestionAnswerOptionsSchema(BaseModel):
    class QuestionAnswerOptionsRequest(BaseModel):
        question_id: str
        content_id: str

        class Config:
            from_attributes = True

    class QuestionAnswerOptionsResponse(BaseModel):
        question_id: str
        content_id: str

        class Config:
            from_attributes = True