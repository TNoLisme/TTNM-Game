# schemas/games/game_data_contents_schema.py
from pydantic import BaseModel
from typing import Optional

class GameDataContentsSchema(BaseModel):
    class GameDataContentsRequest(BaseModel):
        data_id: str
        content_id: str

        class Config:
            from_attributes = True

    class GameDataContentsResponse(BaseModel):
        data_id: str
        content_id: str

        class Config:
            from_attributes = True