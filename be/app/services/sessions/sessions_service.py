from uuid import UUID
from datetime import datetime
from app.domain.sessions.session import Session
from app.repository.sessions_repo import SessionsRepository

class SessionsService:
    def __init__(self, session_repo: SessionsRepository):
        self.repo = session_repo

    def start_session(self, data: dict) -> dict:
        session = Session(
            user_id=UUID(data.get("user_id")),
            game_id=UUID(data.get("game_id")),
            start_time=datetime.now(),
            state=data.get("state"),
            score=0,
            emotion_errors={},
            max_errors=data.get("max_errors"),
            level_threshold=data.get("level_threshold"),
            ratio=[],
            time_limit=data.get("time_limit"),
            questions=data.get("questions", [])
        )
        self.repo.save_session(session)
        return {"status": "success", "message": f"Session {session.session_id} started", "session_id": str(session.session_id)}

    def end_session(self, session_id: UUID) -> dict:
        session = self.repo.get_session_by_id(session_id)
        if session:
            session.state = "end"
            session.end_time = datetime.now()
            self.repo.update_session(session)
            return {"status": "success", "message": f"Session {session_id} ended"}
        return {"status": "failed", "message": "Session not found"}