from sqlalchemy import Column, UUID, Integer, Float, TIMESTAMP, Text, ForeignKey
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
    # SQL Server không hỗ trợ ARRAY, dùng Text (JSON string) thay thế
    ratio = Column(Text, nullable=False, default='[]')  # JSON array of floats
    review_emotions = Column(Text, nullable=False, default='[]')  # JSON array of emotion UUIDs

    # Relationships
    child = relationship("Child", back_populates="progress")
    game = relationship("Game")