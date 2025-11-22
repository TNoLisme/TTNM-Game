# models/games/game_data_contents.py
from sqlalchemy import Column, String, ForeignKey, UUID
from uuid import uuid4
from ..base import Base

class GameDataContents(Base):
    __tablename__ = "game_data_question"
    __table_args__ = {'extend_existing': True}
    data_id = Column(UUID(as_uuid=True), ForeignKey("game_data.data_id"), primary_key=True, default=uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"), primary_key=True, default=uuid4) 