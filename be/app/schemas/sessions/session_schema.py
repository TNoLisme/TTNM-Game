from uuid import UUID
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime
from games.question_schema import QuestionSchema
from ..enum import SessionStateEnum

class SessionSchema(BaseModel):


    class SessionRequest(BaseModel):
        user_id: UUID
        game_id: UUID
        start_time: datetime = Field(default_factory=lambda: datetime(2025, 10, 25, 14, 45))
        state: SessionStateEnum
        score: int = Field(..., ge=0)
        emotion_errors: Dict[str, int]
        max_errors: int = Field(..., ge=0)
        level_threshold: int = Field(..., ge=0)
        ratio: List[float] = Field(..., min_items=1)
        time_limit: int = Field(..., ge=1)
        questions: List[QuestionSchema.QuestionRequest] = Field(..., min_items=1, max_items=10)

        @validator("time_limit")
        def time_limit_must_be_positive(cls, v):
            if v <= 0:
                raise ValueError("time_limit must be greater than 0")
            return v

    class SessionResponse(BaseModel):
        session_id: UUID
        user_id: UUID
        game_id: UUID
        start_time: datetime
        state: SessionStateEnum
        score: int
        emotion_errors: Dict[str, int]
        max_errors: int
        level_threshold: int
        ratio: List[float]
        time_limit: int
        questions: List[QuestionSchema.QuestionResponse]
        end_time: Optional[datetime] = None