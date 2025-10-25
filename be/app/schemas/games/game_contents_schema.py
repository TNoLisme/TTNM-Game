from uuid import UUID
from pydantic import BaseModel, Field, validator
from typing import Optional

class GameContentsSchema(BaseModel):
    class GameContentRequest(BaseModel):
        game_id: UUID
        level: int = Field(..., ge=1, le=10)
        content_type: str = Field(..., max_length=50)
        media_path: str = Field(..., max_length=255)
        question_text: str = Field(..., max_length=500)
        correct_answer: str = Field(..., max_length=100)
        emotion: Optional[str] = Field(None, max_length=50)
        explanation: Optional[str] = Field(None, max_length=1000)

        @validator("media_path")
        def media_path_must_be_valid(cls, v):
            if not v.startswith(("http://", "https://", "/")):
                raise ValueError("media_path must be a valid URL or relative path")
            return v

    class GameContentResponse(BaseModel):
        content_id: UUID
        game_id: UUID
        level: int
        content_type: str
        media_path: str
        question_text: str
        correct_answer: str
        emotion: Optional[str]
        explanation: Optional[str]