from uuid import UUID
from datetime import datetime
from app.models.games.game_data import GameData as GameDataModel
from app.domain.games.game_data import GameData
from app.mapper.game_contents_mapper import GameContentsMapper
from app.schemas.games.game_data_schema import GameDataSchema  # Cập nhật từ schema mới
from typing import List, Dict

class GameDataMapper:
    @staticmethod
    def to_domain(game_data_model: GameDataModel) -> GameData:
        """Chuyển đổi từ model sang domain entity."""
        if not game_data_model:
            return None
        contents = [GameContentsMapper.to_domain(content) for content in game_data_model.contents]
        return GameData(
            data_id=game_data_model.data_id,
            game_id=game_data_model.game_id,
            level=game_data_model.level,
            contents=[c.__dict__ for c in contents]  # Chuyển thành Dict
        )

    @staticmethod
    def to_model(game_data_domain: GameData) -> GameDataModel:
        """Chuyển đổi từ domain entity sang model."""
        if not game_data_domain:
            return None
        game_data_model = GameDataModel(
            data_id=game_data_domain.data_id,
            game_id=game_data_domain.game_id,
            level=game_data_domain.level
        )
        # Cập nhật contents (cần repository để lưu relationship)
        return game_data_model

    @staticmethod
    def to_response(game_data_model: GameDataModel) -> GameDataSchema.GameDataResponse:
        """Chuyển đổi từ model sang response schema."""
        if not game_data_model:
            return None
        return GameDataSchema.GameDataResponse(
            data_id=game_data_model.data_id,
            game_id=game_data_model.game_id,
            level=game_data_model.level,
            contents=[c.__dict__ for c in game_data_model.contents],  # Chuyển thành Dict
            correct_answers=[],  # Giả định từ domain
            options=[],  # Giả định từ domain
            created_at=datetime(2025, 10, 25, 16, 20)
        )