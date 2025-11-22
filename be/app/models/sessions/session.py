from sqlalchemy import Column, UUID, TIMESTAMP, String, Integer, Enum, JSON, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, DOUBLE_PRECISION
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum
from ..base import Base
from app.models.users.user import User

class SessionStateEnum(enum.Enum):
    playing = "playing"
    pause = "pause"
    end = "end"

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.game_id"))
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)
    state = Column(Enum(SessionStateEnum), nullable=False)
    score = Column(Integer, nullable=False, default=0)
    emotion_errors = Column(JSON, nullable=False, default={})
    max_errors = Column(Integer, nullable=False)
    level_threshold = Column(Integer, nullable=False)
    ratio = Column(ARRAY(DOUBLE_PRECISION), nullable=False, default=[])
    time_limit = Column(Integer, nullable=False)
    question_ids = Column(ARRAY(PG_UUID(as_uuid=True)), nullable=False, default=[])
    level = Column(Integer, nullable=False, default=1)

    # Relationships
    user = relationship("User", back_populates="sessions")
    game = relationship("Game", back_populates="sessions")
    session_questions = relationship("SessionQuestions", back_populates="session")
    session_history = relationship("SessionHistory", back_populates="session")
    game_history = relationship("GameHistory", back_populates="session")