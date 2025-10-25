from uuid import UUID
from pydantic import BaseModel, Field

class EmotionConceptSchema(BaseModel):
    class EmotionConceptRequest(BaseModel):
        emotion: str = Field(..., max_length=50)
        level: int = Field(..., ge=1, le=10)
        title: str = Field(..., max_length=100)
        video_path: str = Field(..., max_length=255)
        image_path: str = Field(..., max_length=255)
        audio_path: str = Field(..., max_length=255)
        description: str = Field(..., max_length=1000)

    class EmotionConceptResponse(BaseModel):
        concept_id: UUID
        emotion: str
        level: int
        title: str
        video_path: str
        image_path: str
        audio_path: str
        description: str