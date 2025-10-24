from uuid import UUID
from typing import List
from models.sessions.session import Session
from datetime import datetime
from report import Report

class ChildProgress:
    """
    Lưu trữ tiến trình chơi của trẻ
    """

    def __init__(
        self,
        progress_id: UUID,
        child_id: UUID,
        game_id: UUID,
        level: int,
        accuracy: float,
        avg_response_time: float,
        score: int = 0,
        last_played: datetime = None
    ):
        self._progress_id = progress_id
        self._child_id = child_id
        self._game_id = game_id
        self._level = level
        self._accuracy = accuracy
        self._avg_response_time = avg_response_time
        self._score = score
        self._last_played = last_played

    def calculate_accuracy(self, sessions: List[Session]) -> float:
        """
        Tính tỷ lệ trả lời đúng từ các phiên chơi
        """
        pass

    def update_emotion_distribution(self, sessions: List[Session]) -> None:
        """
        Cập nhật phân bố cảm xúc
        """
        pass

    def generate_report(self, report_type: str) -> "Report":
        """
        Tạo báo cáo cho phụ huynh
        """
        pass

    def check_level_advance(self, current_score: int, threshold: int) -> bool:
        """
        Kiểm tra xem có đủ điểm để lên cấp không
        """
        pass
