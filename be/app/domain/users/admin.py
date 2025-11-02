from uuid import UUID
from typing import List
from .user import User
from ..enum import RoleEnum
from .child import Child
import enum

class Admin(User):
    def __init__(self, user_id: UUID, username: str, email: str, password: str, role: RoleEnum, name: str,
                 all_child: List[Child]):
        super().__init__(user_id, username, email, password, role, name)
        self.all_child = all_child

    def manage_users(self, user_id: UUID, action: str) -> None:
        """Quản lý người dùng."""
        # Placeholder
        pass

    def manage_content(self, content: dict) -> None:
        """Quản lý nội dung game."""
        # Placeholder
        pass

    def view_all_reports(self, report_type: str) -> List[dict]:
        """Xem báo cáo của tất cả trẻ."""
        # Placeholder
        return []

    def update_system_settings(self, settings: dict) -> None:
        """Cập nhật cài đặt hệ thống."""
        # Placeholder
        pass