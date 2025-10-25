from sqlalchemy import Column, UUID, String, Enum
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum
from ..base import Base

class RoleEnum(enum.Enum):
    child = "child"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    name = Column(String(100), nullable=False)

    # Relationships
    sessions = relationship("Session", back_populates="user")
    game_history = relationship("GameHistory", back_populates="user")
