from uuid import UUID
from sqlalchemy.orm import Session
from app.models.games import GameContent as GameContentModel
from app.mapper.game_contents_mapper import GameContentsMapper
from app.domain.games.game_content import GameContent
from .base_repo import BaseRepository
from typing import List

class GameContentsRepository(BaseRepository[GameContentModel, GameContent]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, GameContentModel, GameContentsMapper)

    def get_game_content_by_level(self, game_id: UUID, level: int) -> List[GameContent]:
        """
        Nhiệm vụ: Lấy TẤT CẢ nội dung (pool đáp án) cho game và level.
        (Dùng cho luồng 'Format Frontend').
        Trả về: List[GameContent] (domain).
        """
        game_content_models = self.db_session.query(self.model_class).filter(
            self.model_class.game_id == game_id,
            self.model_class.level == level
        ).all()
        return [self.mapper_class.to_domain(model) for model in game_content_models]
    
    def get_game_content_by_emotion_and_level(self, game_id: UUID, level: int, emotion: str) -> List[GameContent]:
        """
        Nhiệm vụ: Lấy TẤT CẢ nội dung theo cảm xúc, game, level.
        (Dùng cho luồng 'Cache Miss' để chọn câu hỏi).
        Trả về: List[GameContent] (domain).
        """
        game_content_models = self.db_session.query(self.model_class).filter(
            self.model_class.game_id == game_id,
            self.model_class.level == level,
            self.model_class.emotion == emotion
        ).all()
        return [self.mapper_class.to_domain(model) for model in game_content_models]
    