from uuid import UUID
from sqlalchemy.orm import Session
from app.models.users import Child as ChildModel
from app.mapper.child_mapper import ChildMapper
from app.domain.users.child import Child
from typing import Optional
from .base_repo import BaseRepository


class ChildRepository(BaseRepository[ChildModel, Child]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, ChildModel, ChildMapper)

    # ================================
    # SIÊU HÀM: LƯU + CẬP NHẬT = 1 PHÁT
    # ================================
    def save(self, child: Child) -> Child:
        child_model = self.mapper_class.to_model(child)
        merged = self.db_session.merge(child_model)
        self.db_session.commit()
        self.db_session.refresh(merged)
        return self.mapper_class.to_domain(merged)

    # ================================
    # LẤY CHILD THEO USER_ID
    # ================================
    def get_by_user_id(self, user_id: UUID) -> Optional[Child]:
        child_model = self.db_session.query(self.model_class)\
            .filter_by(user_id=str(user_id)).first()
        return self.mapper_class.to_domain(child_model) if child_model else None

    # ================================
    # LẤY LỊCH SỬ CHƠI
    # ================================
    def get_game_history(self, user_id: UUID) -> list[dict]:
        from app.models.analytics.session_history import SessionHistory
        from app.models.analytics.game_history import GameHistory
        
        history = (
            self.db_session.query(SessionHistory, GameHistory)
            .join(GameHistory, SessionHistory.session_history_id == GameHistory.history_id)
            .filter(SessionHistory.child_id == user_id)
            .all()
        )
        return [
            {"session_id": str(s.session_id), "score": g.score, "level": g.level}
            for s, g in history
        ]

    # ================================
    # LẤY LEVEL CUỐI CÙNG
    # ================================
    def get_last_level(self, user_id: UUID, game_id: UUID) -> int:
        from app.models.analytics.session_history import SessionHistory
        last = (
            self.db_session.query(SessionHistory)
            .filter(SessionHistory.child_id == user_id, SessionHistory.game_id == game_id)
            .order_by(SessionHistory.end_time.desc())
            .first()
        )
        return last.level if last else 1

    # ================================
    # LẤY THEO SĐT
    # ================================
    def get_by_phone_number(self, phone_number: str) -> Optional[Child]:
        child_model = self.db_session.query(self.model_class)\
            .filter_by(phone_number=phone_number).first()
        return self.mapper_class.to_domain(child_model) if child_model else None