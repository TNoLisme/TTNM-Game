from uuid import UUID
from domain.analytics.session_history import SessionHistory
from repository.session_history_repo import SessionHistoryRepository

class SessionHistoryService:
    def __init__(self, session_history_repo: SessionHistoryRepository):
        self.repo = session_history_repo

    def record_session(self, data: dict) -> dict:
        session = SessionHistory(
            child_id=UUID(data.get("child_id")),
            game_id=UUID(data.get("game_id")),
            session_id=UUID(data.get("session_id")),
            level=data.get("level"),
            score=data.get("score")
        )
        self.repo.save_session_history(session)
        return {"status": "success", "message": f"Session {session.session_id} recorded"}

    def get_latest_session(self, child_id: UUID) -> dict:
        session = self.repo.get_latest_session(child_id)
        return {"status": "success", "data": {"session_id": str(session.session_id), "level": session.level}} if session else {"status": "failed", "message": "No session found"}