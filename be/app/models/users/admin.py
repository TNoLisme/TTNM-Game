from typing import List
from user import User, RoleEnum
from child import Child
from models.progress.report import Report
from models.sessions.game_content import GameContent
from uuid import UUID

class Admin(User):
    """
    Class Admin kế thừa từ User.
    """

    def __init__(self, all_child: List[Child] = None, **kwargs):
        super().__init__(role=RoleEnum.ADMIN, **kwargs)
        self._all_child = all_child or []

    def manage_users(self, user_id: UUID, action: str) -> None:
        """
        Quản lý người dùng: tạo, sửa, xóa
        """
        pass

    def manage_content(self, content: GameContent) -> None:
        """
        Quản lý nội dung game: thêm, sửa, xóa
        """
        pass

    def view_all_reports(self, report_type: str) -> List[Report]:
        """
        Xem báo cáo của tất cả trẻ
        """
        pass

    def update_system_settings(self, settings: dict) -> None:
        """
        Cập nhật các cài đặt hệ thống
        """
        pass
