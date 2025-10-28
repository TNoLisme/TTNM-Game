from uuid import UUID
from datetime import datetime
from app.domain.analytics.report import Report
from app.repository.report_repo import ReportRepository

class ReportService:
    def __init__(self, report_repo: ReportRepository):
        self.repo = report_repo

    def generate_report(self, child_id: UUID, report_type: str) -> dict:
        report = Report(child_id=child_id, report_type=report_type, summary=f"Report for {child_id} at {datetime.now()}")
        self.repo.save_report(report)
        return {"status": "success", "report_id": str(report.report_id), "summary": report.summary}

    def get_report(self, report_id: UUID) -> dict:
        report = self.repo.get_report_by_id(report_id)
        return {"status": "success", "data": {"summary": report.summary}} if report else {"status": "failed", "message": "Report not found"}