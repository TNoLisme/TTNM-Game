from uuid import UUID
from sqlalchemy.orm import Session
from typing import List
from app.models.games import Game as GameModel
from app.mapper.games_mapper import GamesMapper
from app.domain.games.game import Game
from .base_repo import BaseRepository

class GamesRepository(BaseRepository[GameModel, Game]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, GameModel, GamesMapper)

    def get_all(self) -> List[Game]:
        """Lấy tất cả games."""
        models = self.db_session.query(self.model_class).all()
        return [self.mapper_class.to_domain(model) for model in models]

    def save(self, game: Game) -> Game:
        """Lưu hoặc cập nhật game."""
        model = self.mapper_class.to_model(game)
        merged = self.db_session.merge(model)
        self.db_session.commit()
        self.db_session.refresh(merged)
        return self.mapper_class.to_domain(merged)