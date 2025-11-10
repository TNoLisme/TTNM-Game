
from sqlalchemy import Column, UUID, Integer, String, Enum, Text, ForeignKey
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
    question_text = Column(Text)
    correct_answer = Column(String(50))
    emotion = Column(String(50))
    explanation = Column(Text)

    # Relationships
    game = relationship("Game", back_populates="game_contents")
    game_data = relationship("GameData", secondary="game_data_contents", back_populates="contents")
    questions = relationship("Question", back_populates="content")
