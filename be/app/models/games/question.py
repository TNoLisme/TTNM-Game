from sqlalchemy import Column, UUID, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..base import Base

question_answer_options = Table(
    "question_answer_options",
    Base.metadata,
    Column("question_id", UUID(as_uuid=True), ForeignKey("questions.question_id"), primary_key=True),
    Column("content_id", UUID(as_uuid=True), ForeignKey("game_content.content_id"), primary_key=True)
)

class Question(Base):
    __tablename__ = "questions"

    question_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.game_id"))
    level = Column(Integer, nullable=False)
    content_id = Column(UUID(as_uuid=True), ForeignKey("game_content.content_id"))
    correct_answer = Column(String(50), nullable=False)

    # Relationships
    game = relationship("Game", back_populates="questions")
    content = relationship("GameContent", back_populates="questions")
    answer_options = relationship("GameContent", secondary=question_answer_options, back_populates="answer_options")
    session_questions = relationship("SessionQuestions", back_populates="question")