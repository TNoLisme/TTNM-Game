from uuid import UUID
from sqlalchemy.orm import Session
from app.models.games.game_data_question import GameDataContents as GameDataContentsModel
from app.mapper.game_data_question_mapper import GameDataContentsMapper
from app.domain.games.game_data_question import GameDataContents as GameDataContentsDomain
from typing import Optional, List
from .base_repo import BaseRepository

class GameDataContentsRepository(BaseRepository[GameDataContentsModel, GameDataContentsDomain]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, GameDataContentsModel, GameDataContentsMapper)

    def get_question_ids_by_data_id(self, data_id: UUID) -> List[UUID]:
        """
        Nhiệm vụ: Lấy danh sách 'question_id' dựa trên 'data_id' (bộ đề).
        (Dùng cho luồng Cache Hit).
        Trả về: List[UUID] các question_id.
        """
        results = self.db_session.query(self.model_class.question_id)\
            .filter(self.model_class.data_id == data_id)\
            .all()
        
        return [result[0] for result in results]

    def create(self, domain_entity: GameDataContentsDomain) -> GameDataContentsDomain:
        """
        Nhiệm vụ: Tạo mới một entry trong bảng map. 
        (Ghi đè 'create' của BaseRepository vì bảng này không cần 'refresh').
        Trả về: Domain object đã được gửi vào.
        """
        model = self.mapper_class.to_model(domain_entity)
        self.db_session.add(model)
        self.db_session.commit()
        return domain_entity