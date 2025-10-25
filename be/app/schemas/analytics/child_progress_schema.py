from uuid import UUID
from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime

class ChildProgressSchema(BaseModel):
    class ChildProgressRequest(BaseModel):
        child_id: UUID
        game_id: UUID
        level: int = Field(..., ge=1, le=10)
        accuracy: float = Field(..., ge=0.0, le=1.0)
        avg_response_time: float = Field(..., ge=0.0)
        score: int = Field(..., ge=0)
        last_played: datetime = Field(default_factory=lambda: datetime(2025, 10, 25, 14, 45))
        ratio: List[float] = Field(..., min_items=1)
        review_emotions: List[UUID]

        @validator("accuracy")
        def accuracy_must_be_valid(cls, v):
            if v < 0.0 or v > 1.0:
                raise ValueError("accuracy must be between 0.0 and 1.0")
            return v

    class ChildProgressResponse(BaseModel):
        progress_id: UUID
        child_id: UUID
        game_id: UUID
        level: int
        accuracy: float
        avg_response_time: float
        score: int
        last_played: datetime
        ratio: List[float]
        review_emotions: List[UUID]