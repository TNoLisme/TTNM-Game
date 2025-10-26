from uuid import UUID
from datetime import datetime
from app.models.analytics.session_history import SessionHistory as SessionHistoryModel
from app.domain.analytics.session_history import SessionHistory
from app.schemas.analytics.session_history_schema import SessionHistorySchema  # Giả định schema

class SessionHistoryMapper:
    @staticmethod
    def to_domain(session_history_model: SessionHistoryModel) -> SessionHistory:
        """Chuyển đổi từ model sang domain entity."""
        if not session_history_model:
            return None
        return SessionHistory(
            session_history_id=session_history_model.session_history_id,
            child_id=session_history_model.child_id,
            game_id=session_history_model.game_id,
            session_id=session_history_model.session_id,
            level=session_history_model.level,
            start_time=session_history_model.start_time,
            end_time=session_history_model.end_time,
            score=session_history_model.score
        )

    @staticmethod
    def to_model(session_history_domain: SessionHistory) -> SessionHistoryModel:
        """Chuyển đổi từ domain entity sang model."""
        if not session_history_domain:
            return None
        return SessionHistoryModel(
            session_history_id=session_history_domain.session_history_id,
            child_id=session_history_domain.child_id,
            game_id=session_history_domain.game_id,
            session_id=session_history_domain.session_id,
            level=session_history_domain.level,
            start_time=session_history_domain.start_time,
            end_time=session_history_domain.end_time,
            score=session_history_domain.score
        )

    @staticmethod
    def to_response(session_history_model: SessionHistoryModel) -> SessionHistorySchema.SessionHistoryResponse:
        """Chuyển đổi từ model sang response schema."""
        if not session_history_model:
            return None
        return SessionHistorySchema.SessionHistoryResponse(
            session_history_id=session_history_model.session_history_id,
            child_id=session_history_model.child_id,
            game_id=session_history_model.game_id,
            session_id=session_history_model.session_id,
            level=session_history_model.level,
            start_time=session_history_model.start_time,
            end_time=session_history_model.end_time,
            score=session_history_model.score
        )