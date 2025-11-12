from uuid import UUID
from sqlalchemy.orm import Session
from app.models.games import GameData as GameDataModel
from app.mapper.game_data_mapper import GameDataMapper
from app.domain.games.game_data import GameData
from .base_repo import BaseRepository

class GameDataRepository(BaseRepository[GameDataModel, GameData]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, GameDataModel, GameDataMapper)

    def load_data_by_game_and_level(self, game_id: UUID, user_id: UUID, level: int) -> GameData:
        game_data_model = self.db_session.query(self.model_class).filter(
            self.model_class.game_id == game_id, self.model_class.user_id == user_id, self.model_class.level == level
        ).first()
        if not game_data_model: 
            raise ValueError("Game data not found")
        return self.mapper_class.to_domain(game_data_model)