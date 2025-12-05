from sqlalchemy import Column, UUID, Enum, TIMESTAMP, Text, JSON, ForeignKey, UnicodeText
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum
from ..base import Base

class ReportTypeEnum(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.user_id"))
    report_type = Column(Enum(ReportTypeEnum), nullable=False)
    generated_at = Column(TIMESTAMP, nullable=False)
    summary = Column(UnicodeText, nullable=False)
    data = Column(JSON, nullable=False)

    # Relationships
    child = relationship("Child", back_populates="reports")