from uuid import UUID
from datetime import datetime
from app.models.games.game import Game as GameModel, GameTypeEnum
from app.domain.games.game import Game, GameClick, GameCV, GameRecognizeEmotion, GameSituationEmotion, GameFaceBuilder, GameWhoIsWho, GameExpressEmotion, GameSituationExpress
from app.schemas.games.game_schema import GameSchema  # Giả định schema
from typing import Optional

class GamesMapper:
    @staticmethod
    def to_domain(game_model: GameModel) -> Game:
        """Chuyển đổi từ model sang domain entity."""
        game_type_value = getattr(game_model.game_type, "value", None)
        if not game_model:
            return None
        

        if game_type_value == "GameClick":
            return GameClick(
                game_id=game_model.game_id,
                game_type=game_model.game_type,
                name=game_model.name,
                level=game_model.level,
                difficulty_level=game_model.difficulty_level,
                max_errors=game_model.max_errors,
                level_threshold=game_model.level_threshold,
                time_limit=game_model.time_limit,
                type_question="multiple_choice",  # Giả định
                options=[]
            )
        elif game_type_value == "GameCV":
            return GameCV(
                game_id=game_model.game_id,
                game_type=game_model.game_type,
                name=game_model.name,
                level=game_model.level,
                difficulty_level=game_model.difficulty_level,
                max_errors=game_model.max_errors,
                level_threshold=game_model.level_threshold,
                time_limit=game_model.time_limit,
                cv_model={},  # Giả định
                camera_stream={}
            )
        return None  # Xử lý các loại khác nếu cần

    @staticmethod
    def to_model(game_domain: Game) -> GameModel:
        """Chuyển đổi từ domain entity sang model."""
        if not game_domain:
            return None
        game_model = GameModel(
            game_id=game_domain.game_id,
            game_type=getattr(game_domain, "game_type", "GameClick"),
            name=game_domain.name,
            level=game_domain.level,
            difficulty_level=game_domain.difficulty_level,
            max_errors=game_domain.max_errors,
            level_threshold=game_domain.level_threshold,
            time_limit=game_domain.time_limit
        )
        return game_model

    @staticmethod
    def to_response(game_model: GameModel) -> GameSchema.GameResponse:
        """Chuyển đổi từ model sang response schema."""
        if not game_model:
            return None
        return GameSchema.GameResponse(
            game_id=game_model.game_id,
            game_type=game_model.game_type,
            name=game_model.name,
            level=game_model.level,
            difficulty_level=game_model.difficulty_level,
            max_errors=game_model.max_errors,
            level_threshold=game_model.level_threshold,
            time_limit=game_model.time_limit,
            created_at=datetime(2025, 10, 25, 16, 8)
        )