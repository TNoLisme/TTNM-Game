from uuid import UUID
from typing import List

class GameHistory:
    def __init__(self, history_id: UUID, user_id: UUID, session_id: UUID, game_id: UUID,
                 score: int, level: int):
        self.history_id = history_id
        self.user_id = user_id
        self.session_id = session_id
        self.game_id = game_id
        self.score = score
        self.level = level

    @classmethod
    def load_history_by_user(cls, user_id: UUID) -> List['GameHistory']:
        """Tải lịch sử chơi theo user_id."""
        # Placeholder: cần repository
        return []

    @classmethod
    def load_history_by_session(cls, session_id: UUID) -> 'GameHistory':
        """Tải lịch sử chơi theo session_id."""
        # Placeholder: cần repository
        return cls(UUID("pqr67890-e89b-12d3-a456-426614174000"), UUID("123e4567-e89b-12d3-a456-426614174000"), session_id, UUID("987fcdeb-12a3-4d56-7890-1234567890ab"), 50, 1)