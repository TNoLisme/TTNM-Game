from uuid import UUID
from datetime import datetime
from app.models.games.game_data import GameData as GameDataModel
from app.domain.games.game_data import GameData
from app.mapper.questions_mapper import QuestionsMapper
from app.schemas.games.game_data_schema import GameDataSchema  # Cập nhật từ schema mới
from typing import List, Dict

class GameDataMapper:
    @staticmethod
    def to_domain(game_data_model: GameDataModel) -> GameData:
        """Chuyển đổi từ model sang domain entity."""
        if not game_data_model:
            return None
        questions_domain = []
        if game_data_model.questions: # Đảm bảo đã load
            questions_domain = [QuestionsMapper.to_domain(q) for q in game_data_model.questions]
        
        return GameData(
            data_id=game_data_model.data_id,
            game_id=game_data_model.game_id,
            user_id=game_data_model.user_id,
            level=game_data_model.level,
            questions=questions_domain # Gán vào 'questions' (Domain)
        )

    @staticmethod
    def to_model(game_data_domain: GameData) -> GameDataModel:
        """Chuyển đổi từ domain entity sang model."""
        if not game_data_domain:
            return None
        game_data_model = GameDataModel(
            data_id=game_data_domain.data_id,
            game_id=game_data_domain.game_id,
            user_id=game_data_domain.user_id,
            level=game_data_domain.level
        )
        if game_data_domain.questions:
            game_data_model.questions = [QuestionsMapper.to_model(q_domain) for q_domain in game_data_domain.questions]
        # Cập nhật contents (cần repository để lưu relationship)
        return game_data_model

    @staticmethod
    def to_response(game_data_model: GameDataModel) -> GameDataSchema.GameDataResponse:
        """Chuyển đổi từ model sang response schema."""
        if not game_data_model:
            return None
        questions_response = []
        if game_data_model.questions:
            questions_response = [QuestionsMapper.to_response(q) for q in game_data_model.questions]
        return GameDataSchema.GameDataResponse(
            data_id=game_data_model.data_id,
            game_id=game_data_model.game_id,
            user_id=game_data_model.user_id,
            level=game_data_model.level,
            contents=questions_response,
            correct_answers=[],  # Giả định từ domain
            created_at=datetime(2025, 10, 25, 16, 20)
        )