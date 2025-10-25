from uuid import UUID
from datetime import datetime
from typing import Optional

class SessionHistory:
    def __init__(self, session_history_id: UUID, child_id: UUID, game_id: UUID, session_id: UUID,
                 level: int, start_time: datetime, end_time: Optional[datetime], score: int):
        self.session_history_id = session_history_id
        self.child_id = child_id
        self.game_id = game_id
        self.session_id = session_id
        self.level = level
        self.start_time = start_time
        self.end_time = end_time
        self.score = score

    @classmethod
    def load_latest_session(cls, user_id: UUID, game_id: UUID) -> 'SessionHistory':
        """Tải phiên chơi gần nhất."""
        # Placeholder: cần repository
        return cls(UUID("mno34567-e89b-12d3-a456-426614174000"), user_id, game_id, UUID("abc12345-e89b-12d3-a456-426614174000"), 1, datetime.now(), None, 0)

    def get_last_level(self, user_id: UUID, game_id: UUID) -> int:
        """Lấy level gần nhất mà trẻ đã chơi đến."""
        # Placeholder: cần repository
        return self.level