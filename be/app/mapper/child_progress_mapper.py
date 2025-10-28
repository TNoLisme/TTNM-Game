from uuid import UUID
from datetime import datetime
from app.models.analytics.child_progress import ChildProgress as ChildProgressModel
from app.domain.analytics.child_progress import ChildProgress
from app.schemas.analytics.child_progress_schema import ChildProgressSchema  # Giả định schema

class ChildProgressMapper:
    @staticmethod
    def to_domain(child_progress_model: ChildProgressModel) -> ChildProgress:
        """Chuyển đổi từ model sang domain entity."""
        if not child_progress_model:
            return None
        return ChildProgress(
            progress_id=child_progress_model.progress_id,
            child_id=child_progress_model.child_id,
            game_id=child_progress_model.game_id,
            level=child_progress_model.level,
            accuracy=child_progress_model.accuracy,
            avg_response_time=child_progress_model.avg_response_time,
            score=child_progress_model.score,
            last_played=child_progress_model.last_played,
            ratio=child_progress_model.ratio,
            review_emotions=child_progress_model.review_emotions
        )

    @staticmethod
    def to_model(child_progress_domain: ChildProgress) -> ChildProgressModel:
        """Chuyển đổi từ domain entity sang model."""
        if not child_progress_domain:
            return None
        return ChildProgressModel(
            progress_id=child_progress_domain.progress_id,
            child_id=child_progress_domain.child_id,
            game_id=child_progress_domain.game_id,
            level=child_progress_domain.level,
            accuracy=child_progress_domain.accuracy,
            avg_response_time=child_progress_domain.avg_response_time,
            score=child_progress_domain.score,
            last_played=child_progress_domain.last_played,
            ratio=child_progress_domain.ratio,
            review_emotions=child_progress_domain.review_emotions
        )

    @staticmethod
    def to_response(child_progress_model: ChildProgressModel) -> ChildProgressSchema.ChildProgressResponse:
        """Chuyển đổi từ model sang response schema."""
        if not child_progress_model:
            return None
        return ChildProgressSchema.ChildProgressResponse(
            progress_id=child_progress_model.progress_id,
            child_id=child_progress_model.child_id,
            game_id=child_progress_model.game_id,
            level=child_progress_model.level,
            accuracy=child_progress_model.accuracy,
            avg_response_time=child_progress_model.avg_response_time,
            score=child_progress_model.score,
            last_played=child_progress_model.last_played or datetime(2025, 10, 25, 16, 8),
            ratio=child_progress_model.ratio,
            review_emotions=child_progress_model.review_emotions
        )