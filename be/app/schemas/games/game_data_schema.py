from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict

class GameDataSchema:
    class GameDataRequest(BaseModel):
        game_id: UUID
        level: int = Field(..., ge=1, le=10)
        contents: List[Dict] = Field(..., min_items=50)

    class GameDataResponse(BaseModel):
        data_id: UUID
        game_id: UUID
        level: int
        contents: List[Dict]
        correct_answers: List[str] = []
        options: List[str] = []
        created_at: datetime = Field(default_factory=lambda: datetime(2025, 10, 25, 16, 20))

    class Config:
        from_attributes = True