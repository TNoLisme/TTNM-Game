# models/games/game_data_contents.py
from sqlalchemy import Column, String, ForeignKey
from ..base import Base

class GameDataContents(Base):
    __tablename__ = "game_data_contents"
    __table_args__ = {'extend_existing': True}
    data_id = Column(String(36), ForeignKey("game_data.data_id"), primary_key=True)
    content_id = Column(String(36), ForeignKey("game_content.content_id"), primary_key=True)