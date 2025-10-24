from uuid import UUID
from datetime import datetime
from typing import Dict
from models.users.user import User
from child_progress import ChildProgress

class Report:
    """
    Lưu trữ báo cáo tiến trình của trẻ
    """

    def __init__(
        self,
        report_id: UUID,
        child_id: UUID,
        report_type: str,
        generated_at: datetime,
        summary: str,
        data: Dict
    ):
        self._report_id = report_id
        self._child_id = child_id
        self._report_type = report_type
        self._generated_at = generated_at
        self._summary = summary
        self._data = data

    def generate_summary(self, progress: ChildProgress) -> str:
        """
        Tạo tóm tắt báo cáo
        """
        pass

    def export_pdf(self) -> None:
        """
        Xuất báo cáo dưới dạng PDF
        """
        pass

    def send_notification(self, user: "User") -> None:
        """
        Gửi thông báo báo cáo qua email hoặc app
        """
        pass
