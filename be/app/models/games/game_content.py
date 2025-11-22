
from sqlalchemy import Column, UUID, Integer, String, Enum, Text, ForeignKey, UnicodeText
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum
from ..base import Base

class ContentTypeEnum(enum.Enum):
    text = "text"
    image = "image"
    video = "video"
    audio = "audio"

class GameContent(Base):
    __tablename__ = "game_content"

    content_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.game_id"))
    level = Column(Integer, nullable=False)
    content_type = Column(Enum(ContentTypeEnum), nullable=False)
    media_path = Column(String(255))
    question_text = Column(UnicodeText)
    correct_answer = Column(UnicodeText(50))
    emotion = Column(UnicodeText(50))
    explanation = Column(UnicodeText)

    # Relationships
    game = relationship("Game", back_populates="game_contents")
    questions = relationship("Question", back_populates="content")
