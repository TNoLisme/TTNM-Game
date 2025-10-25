from sqlalchemy import Column, String, Integer, Enum, UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum
from ..base import Base

class GameTypeEnum(enum.Enum):
    GameClick = "GameClick"
    GameCV = "GameCV"

class Game(Base):
    __tablename__ = "games"

    game_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    game_type = Column(Enum(GameTypeEnum), nullable=False)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)
    difficulty_level = Column(Integer, nullable=False)
    max_errors = Column(Integer, nullable=False, default=3)
    level_threshold = Column(Integer, nullable=False)
    time_limit = Column(Integer, nullable=False)

    # Relationships
    game_contents = relationship("GameContent", back_populates="game")
    game_data = relationship("GameData", back_populates="game")
    sessions = relationship("Session", back_populates="game")
    questions = relationship("Question", back_populates="game")