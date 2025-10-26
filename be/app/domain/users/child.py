from uuid import UUID
from typing import List
from datetime import datetime
import enum
from app.domain.users.user import User
from app.domain.enum import RoleEnum
from app.domain.analytics.child_progress import ChildProgress
from app.domain.sessions.session import Session
import enum
from app.domain.enum import ReportTypeEnum

class Child(User):
    def __init__(self, user_id: UUID, username: str, email: str, password: str, role: RoleEnum, name: str,
                 age: int, progress: List[ChildProgress], last_played: datetime, report_preferences: ReportTypeEnum,
                 created_at: datetime, last_login: datetime):
        super().__init__(user_id, username, email, password, role, name)
        self.age = age
        self.progress = progress
        self.last_played = last_played
        self.report_preferences = report_preferences
        self.created_at = created_at
        self.last_login = last_login

    def update_progress(self, session: Session) -> None:
        """Cập nhật tiến trình chơi."""
        for p in self.progress:
            if p.game_id == session.game_id:
                p.update_emotion_distribution(session)

    def get_stats(self, game_id: UUID) -> ChildProgress:
        """Lấy thống kê tiến trình cho một trò chơi."""
        return next((p for p in self.progress if p.game_id == game_id), None)

    def get_game_history(self) -> List[Session]:
        """Lấy lịch sử các phiên chơi."""
        # Placeholder: cần repository
        return []

    def view_reports(self, report_type: ReportTypeEnum) -> List[dict]:
        """Xem báo cáo tiến trình."""
        # Placeholder: cần repository
        return []

    def get_last_level(self, game_id: UUID) -> int:
        """Lấy level gần nhất trẻ đã chơi đến."""
        # Placeholder: cần repository
        return 1