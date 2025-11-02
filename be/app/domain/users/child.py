
from uuid import UUID
from typing import List
from datetime import datetime
import enum
from .user import User
from ..enum import RoleEnum
from ..analytics.child_progress import ChildProgress
from ..sessions.session import Session
import enum
from datetime import date
from ..enum import ReportTypeEnum, GenderEnum


class Child(User):
    def __init__(self, user_id: str, age: int, last_played: date, report_preferences: ReportTypeEnum,
                 created_at: date, last_login: date, gender: GenderEnum, date_of_birth: date, phone_number: str, progress: List['ChildProgress'] = None):
        self.user_id = user_id
        self.age = age
        self.last_played = last_played
        self.report_preferences = report_preferences
        self.created_at = created_at
        self.last_login = last_login
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.phone_number = phone_number
        self.progress = progress or []

    def validate(self):
        if not self.user_id or not self.phone_number:
            raise ValueError("User ID and phone number are required")
    

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