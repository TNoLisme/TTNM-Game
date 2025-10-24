from uuid import UUID
from datetime import datetime
from typing import Dict, Optional

class Session:
    """
    Entity lưu trữ thông tin phiên chơi
    """

    def __init__(
        self,
        session_id: UUID,
        user_id: UUID,
        game_id: UUID,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        state: str = "playing",
        score: int = 0,
        answers: Optional[Dict[str, str]] = None,
        emotion_errors: Optional[Dict[str, int]] = None
    ):
        self._session_id = session_id
        self._user_id = user_id
        self._game_id = game_id
        self._start_time = start_time
        self._end_time = end_time
        self._state = state
        self._score = score
        self._answers = answers or {}
        self._emotion_errors = emotion_errors or {}

    def start_session(self, user_id: UUID, game_id: UUID) -> None:
        """
        Bắt đầu phiên chơi mới
        """
        pass

    def end_session(self) -> None:
        """
        Kết thúc phiên chơi, lưu trạng thái
        """
        pass

    def save_state(self, session_state: "Session") -> None:
        """
        Lưu trạng thái phiên
        """
        pass

    def load_state(self, session_id: UUID) -> dict:
        """
        Tải trạng thái phiên theo session_id
        """
        pass
