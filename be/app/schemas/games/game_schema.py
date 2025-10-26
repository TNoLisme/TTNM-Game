from uuid import UUID
from pydantic import BaseModel, Field, validator
from ...domain.enum import GameTypeEnum

class GameSchema(BaseModel):

    class GameRequest(BaseModel):
        game_type: GameTypeEnum
        name: str = Field(..., max_length=100)
        level: int = Field(..., ge=1, le=10)
        difficulty_level: int = Field(..., ge=1, le=5)
        max_errors: int = Field(..., ge=0)
        level_threshold: int = Field(..., ge=0)
        time_limit: int = Field(..., ge=1)

        @validator("time_limit")
        def time_limit_must_be_positive(cls, v):
            if v <= 0:
                raise ValueError("time_limit must be greater than 0")
            return v

    class GameResponse(BaseModel):
        game_id: UUID
        game_type: GameTypeEnum
        name: str
        level: int
        difficulty_level: int
        max_errors: int
        level_threshold: int
        time_limit: int