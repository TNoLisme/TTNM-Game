from uuid import UUID
from pydantic import BaseModel, Field
from typing import List
from .game_contents_schema import GameContentsSchema

class QuestionSchema(BaseModel):
    class QuestionRequest(BaseModel):
        game_id: UUID
        level: int = Field(..., ge=1, le=10)
        content: GameContentsSchema.GameContentRequest

    class QuestionResponse(BaseModel):
        question_id: UUID
        game_id: UUID
        level: int
        content: GameContentsSchema.GameContentResponse
        correct_answer: str