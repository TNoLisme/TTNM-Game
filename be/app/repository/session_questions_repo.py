from uuid import UUID
from sqlalchemy.orm import Session
from models.sessions import SessionQuestions as SessionQuestionsModel
from mapper.session_questions_mapper import SessionQuestionsMapper
from domain.sessions.session_questions import SessionQuestions
from .base_repo import BaseRepository

class SessionQuestionsRepository(BaseRepository[SessionQuestionsModel, SessionQuestions]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, SessionQuestionsModel, SessionQuestionsMapper)

    def get_by_session(self, session_id: UUID) -> list[SessionQuestions]:
        session_question_models = self.db_session.query(self.model_class).filter(self.model_class.session_id == session_id).all()
        return [self.mapper_class.to_domain(model) for model in session_question_models]