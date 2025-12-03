from sqlalchemy import Column, UUID, ForeignKey, Boolean, Integer, TIMESTAMP, UnicodeText
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy import Float
from ..base import Base

class SessionQuestions(Base):
    __tablename__ = "session_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"))
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"))
    user_answer = Column(UnicodeText, nullable=False)
    correct_answer = Column(UnicodeText, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    check_hint = Column(Boolean, nullable=False)
    cv_confidence = Column(Float)
    timestamp = Column(TIMESTAMP, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="session_questions")
    question = relationship("Question", back_populates="session_questions")