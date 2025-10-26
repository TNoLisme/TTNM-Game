from sqlalchemy import Column, String, Enum, UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..base import Base
from app.domain.enum import RoleEnum

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum, native_enum=False), nullable=False)
    name = Column(String(100), nullable=False)

    # Relationships
    sessions = relationship("Session", back_populates="user")
    game_history = relationship("GameHistory", back_populates="user")
