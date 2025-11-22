from sqlalchemy import Column, UUID, String, Integer, Text, UnicodeText
from uuid import uuid4
from ..base import Base

class EmotionConcept(Base):
    __tablename__ = "emotion_concepts"

    concept_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    emotion = Column(UnicodeText(50), nullable=False)
    level = Column(Integer, nullable=False)
    title = Column(UnicodeText(100), nullable=False)
    video_path = Column(String(255))
    image_path = Column(String(255))
    audio_path = Column(String(255))
    description = Column(UnicodeText)