from sqlalchemy import Column, UUID, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..base import Base

game_data_contents = Table(
    "game_data_contents",
    Base.metadata,
    Column("data_id", UUID(as_uuid=True), ForeignKey("game_data.data_id"), primary_key=True),
    Column("content_id", UUID(as_uuid=True), ForeignKey("game_content.content_id"), primary_key=True)
)

class GameData(Base):
    __tablename__ = "game_data"

    data_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.game_id"))
    level = Column(Integer, nullable=False)

    # Relationships
    game = relationship("Game", back_populates="game_data")
    contents = relationship("GameContent", secondary=game_data_contents, back_populates="game_data")