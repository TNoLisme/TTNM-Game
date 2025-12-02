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
            questions=data.get("questions", []), 
            level=data.get("level")
        )
        if self.repo.get_by_id(session.session_id):
            self.repo.update(session)
        else:
            self.repo.create(session)

        return {"status": "success", "data": session}

    def end_session(self, session_id: UUID) -> dict:
        session = self.repo.get_by_id(session_id)
        if session:
            session.state = "end"
            session.end_time = datetime.now()
            self.repo.update(session)
            return {"status": "success", "data": session}
        return {"status": "failed", "message": "Session not found"}