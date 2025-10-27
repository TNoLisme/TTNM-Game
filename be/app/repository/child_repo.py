from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.users import Child as ChildModel
from app.mapper.child_mapper import ChildMapper
from app.domain.users.child import Child
from .base_repo import BaseRepository

class ChildRepository(BaseRepository[ChildModel, Child]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, ChildModel, ChildMapper)

    def save(self, child: Child) -> Child:
        """Lưu một Child vào cơ sở dữ liệu"""
        try:
            # Dùng mapper để chuyển domain → model
            child_model = self.mapper_class.to_model(child)
            
            # Thêm vào DB và commit
            self.db_session.add(child_model)
            self.db_session.commit()
            self.db_session.refresh(child_model)

            # Trả lại domain object
            return self.mapper_class.to_domain(child_model)
        except Exception as e:
            self.db_session.rollback()
            raise Exception(f"Failed to save child: {str(e)}")
        

    def get_by_phone_number(self, phone_number: str) -> Child:
        child = self.db_session.query(ChildModel).filter_by(phone_number=phone_number).first()
        return self.mapper_class.to_domain(child)

    def get_game_history(self, user_id: UUID) -> list[dict]:
        # Join với session_history và game_history
        from app.models.analytics.session_history import SessionHistory
        from app.models.analytics.game_history import GameHistory
        history = (
            self.db_session.query(SessionHistory, GameHistory)
            .join(GameHistory, SessionHistory.session_history_id == GameHistory.history_id)
            .filter(SessionHistory.child_id == user_id)
            .all()
        )
        return [{"session_id": str(s.session_id), "score": g.score} for s, g in history]

    def get_last_level(self, user_id: UUID, game_id: UUID) -> int:
        from app.models.analytics.session_history import SessionHistory
        last_session = (
            self.db_session.query(SessionHistory)
            .filter(SessionHistory.child_id == user_id, SessionHistory.game_id == game_id)
            .order_by(SessionHistory.end_time.desc())
            .first()
        )
        return last_session.level if last_session else 1
    
    def get_by_user_id(self, user_id: UUID) -> Child:
        """Lấy thông tin Child dựa trên user_id."""
        child = self.db_session.query(ChildModel).filter_by(user_id=user_id).first()
        return self.mapper_class.to_domain(child) if child else None