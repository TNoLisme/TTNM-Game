from uuid import UUID
from sqlalchemy.orm import Session
from app.models.analytics import ChildProgress as ChildProgressModel
from app.mapper.child_progress_mapper import ChildProgressMapper
from app.domain.analytics.child_progress import ChildProgress
from .base_repo import BaseRepository

class ChildProgressRepository(BaseRepository[ChildProgressModel, ChildProgress]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, ChildProgressModel, ChildProgressMapper)

    def load_progress(self, child_id: UUID, game_id: UUID) -> ChildProgress:
        child_progress_model = self.db_session.query(self.model_class).filter(
            self.model_class.child_id == child_id, self.model_class.game_id == game_id
        ).first()
        if not child_progress_model:
            raise ValueError("Progress not found")
        return self.mapper_class.to_domain(child_progress_model)