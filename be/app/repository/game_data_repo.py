from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional
from app.models.games import GameData as GameDataModel
from app.mapper.game_data_mapper import GameDataMapper
from app.domain.games.game_data import GameData
from .base_repo import BaseRepository

class GameDataRepository(BaseRepository[GameDataModel, GameData]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, GameDataModel, GameDataMapper)

    def load_data_by_game_and_level(self, game_id: UUID, user_id: UUID, level: int) -> Optional[GameData]:
        """
        Nhiệm vụ: Tìm một 'bộ đề' (GameData) đã lưu cho user, game, level cụ thể.
        Trả về: 
         - GameData (domain) nếu tìm thấy (Cache Hit).
         - None nếu không tìm thấy (Cache Miss).
        """
        game_data_model = self.db_session.query(self.model_class).filter(
            self.model_class.game_id == game_id, 
            self.model_class.user_id == user_id, 
            self.model_class.level == level
        ).first()
        
        if not game_data_model: 
            return None 
            
        return self.mapper_class.to_domain(game_data_model)