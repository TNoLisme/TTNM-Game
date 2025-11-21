# app/repository/session_questions_repo.py
from uuid import UUID
from sqlalchemy.orm import Session, joinedload # <-- THÊM joinedload
from app.models.sessions import SessionQuestions as SessionQuestionsModel
from app.mapper.session_questions_mapper import SessionQuestionsMapper
from app.domain.sessions.session_questions import SessionQuestions
from .base_repo import BaseRepository
# (Import thêm)
from app.models.games.question import Question as QuestionModel
from app.models.games.game_content import GameContent

class SessionQuestionsRepository(BaseRepository[SessionQuestionsModel, SessionQuestions]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, SessionQuestionsModel, SessionQuestionsMapper)

    def get_session_by_id(self, session_id: UUID) -> list[SessionQuestions]:
        # === SỬA: Thêm joinedload để load 'question' và 'question.content' ===
        session_question_models = self.db_session.query(self.model_class)\
            .options(
                joinedload(SessionQuestionsModel.question)
                .joinedload(QuestionModel.content)
            )\
            .filter(self.model_class.session_id == session_id)\
            .all()
        # === HẾT SỬA ===
        return [self.mapper_class.to_domain(model) for model in session_question_models]
    
    def get_by_session_and_question(self, session_id: UUID, question_id: UUID) -> SessionQuestions:
        """ Lấy một câu hỏi cụ thể trong session """
        model = self.db_session.query(self.model_class)\
            .options(
                joinedload(SessionQuestionsModel.question)
                .joinedload(QuestionModel.content)
            )\
            .filter(
                self.model_class.session_id == session_id,
                self.model_class.question_id == question_id
            )\
            .first()
        return self.mapper_class.to_domain(model)

    def save(self, sq: SessionQuestions) -> SessionQuestions:
        """ Lưu hoặc cập nhật session question """
        model = self.mapper_class.to_model(sq)
        merged = self.db_session.merge(model)
        self.db_session.commit()
        self.db_session.refresh(merged)
        
        # Load lại với đầy đủ relationship để trả về domain
        reloaded_model = self.db_session.query(self.model_class)\
            .options(
                joinedload(SessionQuestionsModel.question)
                .joinedload(QuestionModel.content)
            )\
            .filter(self.model_class.id == merged.id)\
            .first()  
        return self.mapper_class.to_domain(reloaded_model)