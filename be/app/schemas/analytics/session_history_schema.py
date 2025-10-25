from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SessionHistorySchema(BaseModel):
    class SessionHistoryRequest(BaseModel):
        child_id: UUID
        game_id: UUID
        session_id: UUID
        level: int = Field(..., ge=1, le=10)
        start_time: datetime = Field(default_factory=lambda: datetime(2025, 10, 25, 14, 45))
        end_time: Optional[datetime] = None
        score: int = Field(..., ge=0)

    class SessionHistoryResponse(BaseModel):
        session_history_id: UUID
        child_id: UUID
        game_id: UUID
        session_id: UUID
        level: int
        start_time: datetime
        end_time: Optional[datetime] = None
        score: int