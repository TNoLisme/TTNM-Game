from uuid import UUID
from app.domain.sessions.session_questions import SessionQuestions
from app.repository.session_questions_repo import SessionQuestionsRepository

class SessionQuestionsService:
    def __init__(self, session_questions_repo: SessionQuestionsRepository):
        self.repo = session_questions_repo

    def record_answer(self, data: dict) -> dict:
        session_question = SessionQuestions(
            session_id=UUID(data.get("session_id")),
            question=data.get("question"),
            user_answer=data.get("user_answer"),
            correct_answer=data.get("correct_answer"),
            is_correct=data.get("is_correct"),
            response_time_ms=data.get("response_time_ms"),
            check_hint=data.get("check_hint"),
            cv_confidence=data.get("cv_confidence")
        )
        self.repo.save_session_question(session_question)
        return {"status": "success", "message": f"Answer for session {session_question.session_id} recorded"}

    def get_question_result(self, session_id: UUID) -> dict:
        results = self.repo.get_questions_by_session(session_id)
        return {"status": "success", "data": [{"is_correct": r.is_correct} for r in results]} if results else {"status": "failed", "message": "No results found"}