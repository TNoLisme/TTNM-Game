from uuid import UUID
from datetime import datetime
from app.domain.sessions.session import Session
from app.repository.sessions_repo import SessionsRepository

class SessionsService:
    def __init__(self, db: Session):
        self.repo = SessionsRepository(db)

    def start_session(self, data: dict) -> Session:
        session = Session(
            user_id=UUID(data.get("user_id")),
            game_id=UUID(data.get("game_id")),
            start_time=datetime.now(),
            state=data.get("state"),
            score=0,
            emotion_errors={"sợ hãi": 0, "buồn bã": 0, "tức giận": 0, "ghê tởm": 0, "ngạc nhiên": 0, "vui vẻ": 0},
            max_errors=data.get("max_errors"),
            level_threshold=data.get("level_threshold"),
            ratio=[],
            time_limit=data.get("time_limit"),
            questions=data.get("questions", []),
            level=data.get("level")
        )
        self.repo.create(session)

        return session

    def end_session(self, session_id: UUID) -> Session:
        session = self.repo.get_by_id(session_id)
        if session:
            session.state = "end"
            session.end_time = datetime.now()
            self.repo.update(session)
            return session
        return None
    
    def get_latest_session(self, user_id: UUID, game_id: UUID) -> Session:
        session = self.repo.get_latest_session(user_id, game_id)
        return session if session else None
    
    def get_by_id(self, session_id: UUID) -> Session | None:
        session = self.repo.get_by_id(session_id)
        return session if session else None
    
    def create(self, session: Session) -> Session:
        session = self.repo.create(session)
        return session if session else None

    def update(self, session: Session) -> Session:
        session = self.repo.update(session)
        return session if session else None 