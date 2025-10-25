from sqlalchemy import Column, UUID, Integer, Float, TIMESTAMP, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, DOUBLE_PRECISION
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..base import Base

class ChildProgress(Base):
    __tablename__ = "child_progress"

    progress_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.user_id"))
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.game_id"))
    level = Column(Integer, nullable=False)
    accuracy = Column(Float, nullable=False)
    avg_response_time = Column(Float, nullable=False)
    score = Column(Integer, nullable=False)
    last_played = Column(TIMESTAMP, nullable=False)
    ratio = Column(ARRAY(DOUBLE_PRECISION), nullable=False, default=[])
    review_emotions = Column(ARRAY(PG_UUID(as_uuid=True)), nullable=False, default=[])

    # Relationships
    child = relationship("Child", back_populates="progress")
    game = relationship("Game")