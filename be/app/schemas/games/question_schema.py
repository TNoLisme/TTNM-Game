from uuid import UUID
from pydantic import BaseModel, Field
from typing import List
from .game_contents_schema import GameContentsSchema

class QuestionSchema(BaseModel):
    class QuestionRequest(BaseModel):
        game_id: UUID
        level: int = Field(..., ge=1, le=10)
        content: GameContentsSchema.GameContentRequest
        answer_options: List[GameContentsSchema.GameContentRequest] = Field(..., min_items=2, max_items=4)
        correct_answer: str = Field(..., max_length=100)

    class QuestionResponse(BaseModel):
        question_id: UUID
        game_id: UUID
        level: int
        content: GameContentsSchema.GameContentResponse
        answer_options: List[GameContentsSchema.GameContentResponse]
        correct_answer: str