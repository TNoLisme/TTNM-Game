from uuid import UUID
from typing import List, Dict
from repository.game_data_repo import GameDataRepository
from domain.games.game_data import GameData
from schemas.games.game_data_schema import GameDataSchema

class GameDataService:
    def __init__(self, game_data_repo: GameDataRepository):
        self.game_data_repo = game_data_repo

    def create_game_data(self, data: GameDataSchema.GameDataRequest) -> dict:
        """Tạo dữ liệu game mới."""
        game_data = GameData(
            data_id=UUID("456f1234-e89b-12d3-a456-426614174000"),  # Giả định UUID
            game_id=data.game_id,
            level=data.level,
            contents=data.contents
        )
        if not game_data.validate_data(data.dict()):
            return {"status": "failed", "message": "Invalid data: contents must have at least 50 items"}
        self.game_data_repo.save(game_data)
        return {"status": "success", "data_id": str(game_data.data_id)}

    def get_game_data_by_game_and_level(self, game_id: UUID, level: int) -> dict:
        """Lấy dữ liệu game theo game_id và level."""
        try:
            game_data = self.game_data_repo.load_data_by_game_and_level(game_id, level)
            return {"status": "success", "data": {
                "data_id": str(game_data.data_id),
                "game_id": str(game_data.game_id),
                "level": game_data.level,
                "contents": game_data.contents
            }}
        except ValueError as e:
            return {"status": "failed", "message": str(e)}

    def get_random_contents(self, game_id: UUID, level: int, count: int) -> dict:
        """Lấy ngẫu nhiên nội dung cho câu hỏi."""
        try:
            game_data = self.game_data_repo.load_data_by_game_and_level(game_id, level)
            random_contents = game_data.get_random_contents(count)
            return {"status": "success", "contents": random_contents}
        except ValueError as e:
            return {"status": "failed", "message": str(e)}