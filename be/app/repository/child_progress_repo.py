from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.analytics import ChildProgress as ChildProgressModel
from app.mapper.child_progress_mapper import ChildProgressMapper
from app.domain.analytics.child_progress import ChildProgress
from .base_repo import BaseRepository

class ChildProgressRepository(BaseRepository[ChildProgressModel, ChildProgress]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, ChildProgressModel, ChildProgressMapper)

    def get_progress(self, child_id: UUID, game_id: UUID) -> ChildProgress:
        model = self.db_session.query(self.model_class) \
            .filter(self.model_class.child_id == child_id, self.model_class.game_id == game_id) \
            .first()
        if model:
            print("user đã có tiến trình: ", model.ratio, " and ", model.child_id)
            return self.mapper_class.to_domain(model)

        print("user chưa có tiến trình, tạo mới")
        new_progress = self.create_default_progress(child_id, game_id)
        return self.create(new_progress)

    def create_default_progress(self, child_id: UUID, game_id: UUID) -> ChildProgress:
        default_ratio = [0.1667, 0.1667, 0.1667, 0.1667, 0.1667, 0.1665]
        return ChildProgress(
            progress_id=uuid4(),
            child_id=child_id,
            game_id=game_id,
            level=1,
            accuracy=0.0,
            avg_response_time=0.0,
            score=0,
            last_played=datetime.utcnow(),
            ratio=default_ratio,
            review_emotions=[]
        )

    def create(self, progress: ChildProgress) -> ChildProgress:
        """Insert mới vào DB"""
        try:
            model = self.mapper_class.to_model(progress)
            self.db_session.add(model)
            self.db_session.commit()
            self.db_session.refresh(model)
            return self.mapper_class.to_domain(model)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"[ChildProgressRepository] Failed to create progress: {e}")
            raise

    def update(self, progress: ChildProgress) -> ChildProgress:
        try:
            existing = self.db_session.query(self.model_class) \
                .filter(self.model_class.progress_id == progress.progress_id) \
                .first()
            if not existing:
                raise ValueError(f"Progress {progress.progress_id} không tồn tại để update.")

            model = self.mapper_class.to_model(progress)
            for attr, value in model.__dict__.items():
                if attr.startswith("_"):
                    continue
                setattr(existing, attr, value)
            self.db_session.add(existing)
            self.db_session.commit()
            self.db_session.refresh(existing)
            return self.mapper_class.to_domain(existing)
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"[ChildProgressRepository] Failed to update progress: {e}")
            raise
