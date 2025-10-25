from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from models.analytics import SessionHistory as SessionHistoryModel
from mapper.session_history_mapper import SessionHistoryMapper
from domain.analytics.session_history import SessionHistory
from .base_repo import BaseRepository

class SessionHistoryRepository(BaseRepository[SessionHistoryModel, SessionHistory]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, SessionHistoryModel, SessionHistoryMapper)

    def get_last_level(self, child_id: UUID, game_id: UUID) -> int:
        session_history_model = self.db_session.query(self.model_class).filter(
            self.model_class.child_id == child_id, self.model_class.game_id == game_id
        ).order_by(self.model_class.start_time.desc()).first()
        return session_history_model.level if session_history_model else 1