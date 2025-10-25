from uuid import UUID
from datetime import datetime
from repository.child_progress_repo import ChildProgressRepository

class AnalyticsService:
    def __init__(self, child_progress_repo: ChildProgressRepository):
        self.repo = child_progress_repo

    def generate_summary(self, child_id: UUID) -> dict:
        analytics = self.repo.get_analytics_by_child_id(child_id)
        if analytics:
            summary = f"Progress summary for child {child_id} at {datetime.now()}"
            self.repo.save_summary(child_id, summary)
            return {"status": "success", "summary": summary}
        return {"status": "failed", "message": "No analytics data found"}