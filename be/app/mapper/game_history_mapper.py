from uuid import UUID
from models.analytics.game_history import GameHistory as GameHistoryModel
from domain.analytics.game_history import GameHistory
from schemas.analytics.game_history_schema import GameHistorySchema  # Giả định schema

class GameHistoryMapper:
    @staticmethod
    def to_domain(game_history_model: GameHistoryModel) -> GameHistory:
        """Chuyển đổi từ model sang domain entity."""
        if not game_history_model:
            return None
        return GameHistory(
            history_id=game_history_model.history_id,
            user_id=game_history_model.user_id,
            session_id=game_history_model.session_id,
            game_id=game_history_model.game_id,
            score=game_history_model.score,
            level=game_history_model.level
        )

    @staticmethod
    def to_model(game_history_domain: GameHistory) -> GameHistoryModel:
        """Chuyển đổi từ domain entity sang model."""
        if not game_history_domain:
            return None
        return GameHistoryModel(
            history_id=game_history_domain.history_id,
            user_id=game_history_domain.user_id,
            session_id=game_history_domain.session_id,
            game_id=game_history_domain.game_id,
            score=game_history_domain.score,
            level=game_history_domain.level
        )

    @staticmethod
    def to_response(game_history_model: GameHistoryModel) -> GameHistorySchema.GameHistoryResponse:
        """Chuyển đổi từ model sang response schema."""
        if not game_history_model:
            return None
        return GameHistorySchema.GameHistoryResponse(
            history_id=game_history_model.history_id,
            user_id=game_history_model.user_id,
            session_id=game_history_model.session_id,
            game_id=game_history_model.game_id,
            score=game_history_model.score,
            level=game_history_model.level
        )