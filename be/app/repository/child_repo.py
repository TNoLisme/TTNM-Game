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

    def get_game_history(self, user_id: UUID) -> list[dict]:
        # Placeholder: cần join với session_history
        return []

    def get_last_level(self, user_id: UUID, game_id: UUID) -> int:
        # Placeholder: cần join với session_history
        return 1