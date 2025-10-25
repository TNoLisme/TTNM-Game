from sqlalchemy import Column, UUID, Integer, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..base import Base

class GameHistory(Base):
    __tablename__ = "game_history"

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"))
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.game_id"))
    score = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)

    # Relationships
    user = relationship("User", back_populates="game_history")
    session = relationship("Session", back_populates="game_history")
    game = relationship("Game")