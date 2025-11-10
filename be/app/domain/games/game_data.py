# app/domain/game_data.py
from uuid import UUID
from typing import List, Dict, Optional
from app.domain.games.game_content import GameContent

class GameData:
    def __init__(self, data_id: UUID, game_id: UUID, user_id: UUID, level: int, contents: List[GameContent]):
        self.data_id = data_id
        self.game_id = game_id
        self.user_id = user_id
        self.level = level
        self.contents = contents  # danh sách GameContent

    @classmethod
    def load_data_by_game_and_level(cls, game_id: UUID, user_id: UUID, level: int, contents: List[GameContent]) -> 'GameData':
        return cls(UUID("456f1234-e89b-12d3-a456-426614174000"), game_id, user_id, level, contents)

    def validate_data(self) -> bool:
        return len(self.contents) >= 50

    def get_random_contents(self, count: int) -> List[GameContent]:
        """Lấy ngẫu nhiên n câu hỏi (mỗi câu gồm 1 nội dung chính)."""
        if len(self.contents) < count:
            raise ValueError("Not enough contents")
        return self.contents[:count]
