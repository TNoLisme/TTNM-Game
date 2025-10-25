from uuid import UUID
from sqlalchemy.orm import Session
from models.analytics import Report as ReportModel
from mapper.report_mapper import ReportMapper
from domain.analytics.report import Report
from .base_repo import BaseRepository

class ReportRepository(BaseRepository[ReportModel, Report]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, ReportModel, ReportMapper)

    def get_by_child(self, child_id: UUID) -> list[Report]:
        report_models = self.db_session.query(self.model_class).filter(self.model_class.child_id == child_id).all()
        return [self.mapper_class.to_domain(model) for model in report_models]