from datetime import datetime
from typing import List
from uuid import UUID
from user import User, RoleEnum
from models.sessions.session import Session
from models.progress.child_progress import ChildProgress
from models.progress.report import Report
from enum import Enum

class ReportTypeEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class Child(User):
    """
    Class Child kế thừa từ User.
    """

    def __init__(self, age: int, progress: List[ChildProgress] = None,
                 last_played: datetime = None,
                 report_preferences: ReportTypeEnum = ReportTypeEnum.DAILY,
                 created_at: datetime = None,
                 last_login: datetime = None,
                 **kwargs):
        super().__init__(role=RoleEnum.CHILD, **kwargs)
        self._age = age
        self._progress = progress or []
        self._last_played = last_played
        self._report_preferences = report_preferences
        self._created_at = created_at
        self._last_login = last_login

    def update_progress(self, session: Session) -> None:
        """Cập nhật tiến trình dựa trên phiên chơi"""
        pass

    def get_stats(self, game_id: UUID) -> ChildProgress:
        """Lấy thống kê tiến trình cho 1 trò chơi"""
        pass

    def get_game_history(self) -> List[Session]:
        """Lấy lịch sử các phiên chơi"""
        pass

    def view_reports(self, report_type: ReportTypeEnum) -> List[Report]:
        """Xem báo cáo tiến trình của trẻ"""
        pass
