from uuid import UUID
from sqlalchemy.orm import Session
from app.models.games import GameContent as GameContentModel
from app.mapper.game_contents_mapper import GameContentsMapper
from app.domain.games.game_content import GameContent
from .base_repo import BaseRepository
from typing import List, Optional

class GameContentsRepository(BaseRepository[GameContentModel, GameContent]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, GameContentModel, GameContentsMapper)

    def get_by_id(self, content_id: UUID) -> Optional[GameContent]:
        """✅ Lấy game content theo content_id (primary key)"""
        model = self.db_session.query(self.model_class)\
            .filter(self.model_class.content_id == content_id)\
            .first()
        
        if not model:
            return None
        
        return self.mapper_class.to_domain(model)

    def create(self, domain_entity: GameContent) -> GameContent:
        """✅ Tạo mới game content"""
        model = self.mapper_class.to_model(domain_entity)
        self.db_session.add(model)
        self.db_session.commit()
        self.db_session.refresh(model)
        return self.mapper_class.to_domain(model)

    def get_game_content_by_level(self, game_id: UUID, level: int) -> List[GameContent]:
        """
        Nhiệm vụ: Lấy TẤT CẢ nội dung (pool đáp án) cho game và level.
        (Dùng cho luồng 'Format Frontend').
        Trả về: List[GameContent] (domain).
        """
        game_content_models = self.db_session.query(self.model_class).filter(
            self.model_class.game_id == game_id,
            self.model_class.level == level
        ).order_by(self.model_class.content_id).all()
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
        ).order_by(self.model_class.content_id).all()
        return [self.mapper_class.to_domain(model) for model in game_content_models]
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[GameContent]:
        """✅ Lấy tất cả game contents với pagination"""
        game_content_models = self.db_session.query(self.model_class)\
            .order_by(self.model_class.content_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
        return [self.mapper_class.to_domain(model) for model in game_content_models]
    
    def count_all(self) -> int:
        """✅ Đếm tổng số game contents"""
        return self.db_session.query(self.model_class).count()

    def delete(self, content_id: UUID) -> bool:
        """✅ Xóa game content theo content_id"""
        try:
            result = self.db_session.query(self.model_class)\
                .filter(self.model_class.content_id == content_id)\
                .delete()
            self.db_session.commit()
            return result > 0
        except Exception as e:
            self.db_session.rollback()
            print(f"❌ Error deleting game content: {e}")
            return False

    def save(self, domain_entity: GameContent) -> GameContent:
        """✅ Cập nhật game content theo content_id"""
        model = self.db_session.query(self.model_class)\
            .filter(self.model_class.content_id == domain_entity.content_id)\
            .first()
        
        if not model:
            raise ValueError("Game content not found")
        
        # Update fields
        model.game_id = domain_entity.game_id
        model.level = domain_entity.level
        model.content_type = domain_entity.content_type
        model.media_path = domain_entity.media_path
        model.question_text = domain_entity.question_text
        model.correct_answer = domain_entity.correct_answer
        model.emotion = domain_entity.emotion
        model.explanation = domain_entity.explanation
        
        self.db_session.commit()
        self.db_session.refresh(model)
        
        return self.mapper_class.to_domain(model)