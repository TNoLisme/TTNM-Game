from uuid import UUID
from pydantic import BaseModel, Field

class GameHistorySchema(BaseModel):
    class GameHistoryRequest(BaseModel):
        user_id: UUID
        session_id: UUID
        game_id: UUID
        score: int = Field(..., ge=0)
        level: int = Field(..., ge=1, le=10)

    class GameHistoryResponse(BaseModel):
        history_id: UUID
        user_id: UUID
        session_id: UUID
        game_id: UUID
        score: int
        level: int