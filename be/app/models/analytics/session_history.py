from sqlalchemy import Column, UUID, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..base import Base

class SessionHistory(Base):
    __tablename__ = "session_history"

    session_history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.user_id"))
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.game_id"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"))
    level = Column(Integer, nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)
    score = Column(Integer, nullable=False)

    # Relationships
    child = relationship("Child", back_populates="session_history")
    game = relationship("Game")
    session = relationship("Session", back_populates="session_history")
