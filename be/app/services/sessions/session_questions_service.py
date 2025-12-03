from uuid import UUID
from app.domain.sessions.session_questions import SessionQuestions
from app.repository.session_questions_repo import SessionQuestionsRepository
from app.domain.sessions.session import Session

class SessionQuestionsService:
    def __init__(self, db: Session):
        self.repo = SessionQuestionsRepository(db)

    def get_session_by_id(self, session_id: UUID) -> list[SessionQuestions]:
        result = self.repo.get_session_by_id(session_id)
        return result if result else None
    
    def create(self, session_question: SessionQuestions):
        result = self.repo.create(session_question)
        return result if result else None
    
    def save(self, session_question: SessionQuestions):
        result = self.repo.save(session_question)
        return result if result else None