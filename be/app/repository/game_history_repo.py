from uuid import UUID
from sqlalchemy.orm import Session
from models.analytics import GameHistory as GameHistoryModel
from mapper.game_history_mapper import GameHistoryMapper
from domain.analytics.game_history import GameHistory
from .base_repo import BaseRepository

class GameHistoryRepository(BaseRepository[GameHistoryModel, GameHistory]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, GameHistoryModel, GameHistoryMapper)

    def get_by_user(self, user_id: UUID) -> list[GameHistory]:
        game_history_models = self.db_session.query(self.model_class).filter(self.model_class.user_id == user_id).all()
        return [self.mapper_class.to_domain(model) for model in game_history_models]