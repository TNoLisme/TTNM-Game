from sqlalchemy import Column, UUID, Integer, Enum, TIMESTAMP, ForeignKey, String, Date
from sqlalchemy.orm import relationship
from ..base import Base
import enum
from app.domain.enum import GenderEnum


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
    gender = Column(Enum(GenderEnum, native_enum=False), nullable=False) # Giới tính
    date_of_birth = Column(Date, nullable=False)                         # Ngày sinh
    # Giả định phone_number là duy nhất và bắt buộc nhập
    phone_number = Column(String(20), unique=True, nullable=False)

    # Relationships
    progress = relationship("ChildProgress", back_populates="child")
    session_history = relationship("SessionHistory", back_populates="child")
    reports = relationship("Report", back_populates="child")