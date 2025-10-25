from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from models.sessions import Session as SessionModel
from mapper.sessions_mapper import SessionsMapper
from domain.sessions.session import Session, SessionStateEnum
from repository.questions_repo import QuestionsRepository
from .base_repo import BaseRepository

class SessionsRepository(BaseRepository[SessionModel, Session]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, SessionModel, SessionsMapper)
        self.questions_repo = QuestionsRepository(db_session)

    def start_session(self, user_id: UUID, game_id: UUID) -> Session:
        questions = self.questions_repo.get_random_contents(game_id, 1, 10)
        session = Session(
            session_id=UUID("abc12345-e89b-12d3-a456-426614174000"),
            user_id=user_id,
            game_id=game_id,
            start_time=datetime.now(),
            state=SessionStateEnum.playing,
            score=0,
            emotion_errors={},
            max_errors=3,
            level_threshold=100,
            ratio=[],
            time_limit=300,
            questions=questions
        )
        return self.create(session)

    def load_state(self, session_id: UUID) -> dict:
        session_model = self.db_session.query(self.model_class).filter(self.model_class.session_id == session_id).first()
        if session_model:
            return {"state": session_model.state.value, "score": session_model.score}
        return {}