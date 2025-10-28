# app/repository/games/game_data_contents_repo.py
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.games.game_data_contents import GameDataContents
from app.mapper.game_data_contents_mapper import GameDataContentsMapper
from app.domain.games.game_data_contents import GameDataContents as GameDataContentsDomain
from typing import Optional, List
from .base_repo import BaseRepository

class GameDataContentsRepository(BaseRepository[GameDataContents, GameDataContentsDomain]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, GameDataContents, GameDataContentsMapper)

    def get_by_data_id(self, data_id: str) -> Optional[GameDataContentsDomain]:
        model = self.db_session.query(self.model_class).filter(self.model_class.data_id == data_id).first()
        return self.mapper_class.to_domain(model)

    def get_by_content_id(self, content_id: str) -> Optional[GameDataContentsDomain]:
        model = self.db_session.query(self.model_class).filter(self.model_class.content_id == content_id).first()
        return self.mapper_class.to_domain(model)

    def get_all_by_game_id(self, game_id: str) -> List[GameDataContentsDomain]:
        models = self.db_session.query(self.model_class).join(GameDataContents.game_data).filter(GameDataContents.game_data.game_id == game_id).all()
        return [self.mapper_class.to_domain(model) for model in models]