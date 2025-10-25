from sqlalchemy import Column, UUID, Integer, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base
import enum

class ReportTypeEnum(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class Child(Base):
    __tablename__ = "children"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    age = Column(Integer)
    last_played = Column(TIMESTAMP)
    report_preferences = Column(Enum(ReportTypeEnum))
    created_at = Column(TIMESTAMP, nullable=False)
    last_login = Column(TIMESTAMP)

    # Relationships
    progress = relationship("ChildProgress", back_populates="child")
    session_history = relationship("SessionHistory", back_populates="child")
    reports = relationship("Report", back_populates="child")