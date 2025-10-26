from uuid import UUID
from typing import Dict
from datetime import datetime
import enum
from app.domain.analytics.child_progress import ChildProgress
from app.domain.users.user import User

class ReportTypeEnum(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class Report:
    def __init__(self, report_id: UUID, child_id: UUID, report_type: ReportTypeEnum, generated_at: datetime,
                 summary: str, data: Dict):
        self.report_id = report_id
        self.child_id = child_id
        self.report_type = report_type
        self.generated_at = generated_at
        self.summary = summary
        self.data = data

    def generate_summary(self, progress: 'ChildProgress') -> str:
        """Tạo tóm tắt báo cáo."""
        return f"Progress: {progress.accuracy}% accuracy, {len(progress.review_emotions)} emotions to review"

    def export_pdf(self) -> None:
        """Xuất báo cáo dưới dạng PDF."""
        # Placeholder
        pass

    def send_notification(self, user: 'User') -> None:
        """Gửi thông báo báo cáo."""
        # Placeholder
        pass