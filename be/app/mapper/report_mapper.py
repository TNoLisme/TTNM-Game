from uuid import UUID
from datetime import datetime
from app.models.analytics.report import Report as ReportModel
from app.domain.analytics.report import Report
from app.schemas.analytics.report_schema import ReportSchema  # Giả định schema

class ReportMapper:
    @staticmethod
    def to_domain(report_model: ReportModel) -> Report:
        """Chuyển đổi từ model sang domain entity."""
        if not report_model:
            return None
        return Report(
            report_id=report_model.report_id,
            child_id=report_model.child_id,
            report_type=report_model.report_type,
            generated_at=report_model.generated_at,
            summary=report_model.summary,
            data=report_model.data
        )

    @staticmethod
    def to_model(report_domain: Report) -> ReportModel:
        """Chuyển đổi từ domain entity sang model."""
        if not report_domain:
            return None
        return ReportModel(
            report_id=report_domain.report_id,
            child_id=report_domain.child_id,
            report_type=report_domain.report_type.value,
            generated_at=report_domain.generated_at,
            summary=report_domain.summary,
            data=report_domain.data
        )

    @staticmethod
    def to_response(report_model: ReportModel) -> ReportSchema.ReportResponse:
        """Chuyển đổi từ model sang response schema."""
        if not report_model:
            return None
        return ReportSchema.ReportResponse(
            report_id=report_model.report_id,
            child_id=report_model.child_id,
            report_type=report_model.report_type,
            generated_at=report_model.generated_at or datetime(2025, 10, 25, 16, 8),
            summary=report_model.summary,
            data=report_model.data
        )