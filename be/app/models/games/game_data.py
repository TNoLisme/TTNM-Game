from sqlalchemy import Column, UUID, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..base import Base
from .game_data_question import GameDataContents

class GameData(Base):
    __tablename__ = "game_data"

    data_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.game_id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    level = Column(Integer, nullable=False)

    # Relationships
    game = relationship("Game", back_populates="game_data")
    questions = relationship("Question", secondary="game_data_question", back_populates="game_data")