# models/games/question_answer_options.py
from sqlalchemy import Column, String, ForeignKey
from ..base import Base

class QuestionAnswerOptions(Base):
    __tablename__ = "question_answer_options"
    __table_args__ = {'extend_existing': True}
    

    question_id = Column(String(36), ForeignKey("questions.question_id"), primary_key=True)
    content_id = Column(String(36), ForeignKey("game_content.content_id"), primary_key=True)