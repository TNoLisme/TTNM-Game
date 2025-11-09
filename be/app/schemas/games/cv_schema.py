from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class ScenarioResponse(BaseModel):
    id: str  # Changed from UUID to str for easier JSON serialization
    title: str
    description: str
    target_emotion: str
    instruction: str
    hint: Optional[str] = None
    image_path: Optional[str] = None
    explanation: Optional[str] = None
    level: Optional[int] = 1  # Level của scenario


class ScenariosResponse(BaseModel):
    scenarios: List[ScenarioResponse]


class StartSessionRequest(BaseModel):
    user_id: str
    game_type: str = "GameCV"


class StartSessionResponse(BaseModel):
    session_id: UUID
    message: str


class SaveResultRequest(BaseModel):
    session_id: UUID
    scenario_id: UUID
    target_emotion: str
    detected_emotion: Optional[str]
    success: bool
    time_taken: int


class SaveResultResponse(BaseModel):
    message: str

