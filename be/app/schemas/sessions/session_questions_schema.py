from uuid import UUID
from pydantic import BaseModel, Field, validator
from typing import Dict
from datetime import datetime
from app.schemas.games.question_schema import QuestionSchema


class SessionQuestionsSchema(BaseModel):
    class SessionQuestionsRequest(BaseModel):
        session_id: UUID
        question: QuestionSchema.QuestionRequest
        user_answer: Dict = Field(...)
        correct_answer: Dict = Field(...)
        is_correct: bool
        response_time_ms: int = Field(..., ge=0)
        check_hint: bool
        cv_confidence: float = Field(..., ge=0.0, le=1.0)
        timestamp: datetime = Field(default_factory=lambda: datetime(2025, 10, 25, 14, 45))

        @validator("response_time_ms")
        def response_time_must_be_positive(cls, v):
            if v < 0:
                raise ValueError("response_time_ms must be non-negative")
            return v

    class SessionQuestionsResponse(BaseModel):
        id: UUID
        session_id: UUID
        question: QuestionSchema.QuestionResponse
        user_answer: Dict
        correct_answer: Dict
        is_correct: bool
        response_time_ms: int
        check_hint: bool
        cv_confidence: float
        timestamp: datetime