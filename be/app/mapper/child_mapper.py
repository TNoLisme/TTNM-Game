from uuid import UUID
from datetime import datetime
from app.models.users.child import Child as ChildModel
from app.domain.users.child import Child
from app.mapper.child_progress_mapper import ChildProgressMapper
from app.schemas.users.user_schema import UserSchema  # Sửa import
from app.domain.enum import ReportTypeEnum, RoleEnum, GenderEnum

class ChildMapper:
    @staticmethod
    def to_domain(child_model: ChildModel) -> Child:
        """Chuyển đổi từ model sang domain entity."""
        if not child_model:
            return None
        report_pref_value = (
            child_model.report_preferences.value
            if isinstance(child_model.report_preferences, ReportTypeEnum)
            else str(child_model.report_preferences)
            if child_model.report_preferences else None
        )
        gender_value = (
            child_model.gender.value
            if isinstance(child_model.gender, GenderEnum)
            else str(child_model.gender)
            if child_model.gender else None
        )

        return Child(
            user_id=str(child_model.user_id),
            age=child_model.age,
            progress=[ChildProgressMapper.to_domain(p) for p in child_model.progress] if child_model.progress else [],
            last_played=child_model.last_played,
            report_preferences=ReportTypeEnum(report_pref_value) if report_pref_value else None,
            created_at=child_model.created_at,
            last_login=child_model.last_login,
            gender=GenderEnum(gender_value) if gender_value else None,
            date_of_birth=child_model.date_of_birth,
            phone_number=child_model.phone_number
        )

    @staticmethod
    def to_model(child_domain: Child) -> ChildModel:
        """Chuyển đổi từ domain entity sang model."""
        if not child_domain:
            return None
        return ChildModel(
            user_id=UUID(child_domain.user_id),
            age=child_domain.age,
            last_played=child_domain.last_played,
            report_preferences=child_domain.report_preferences.value if child_domain.report_preferences else None,
            created_at=child_domain.created_at,
            last_login=child_domain.last_login,
            gender=child_domain.gender.value if child_domain.gender else None,
            date_of_birth=child_domain.date_of_birth,
            phone_number=child_domain.phone_number,
            progress=child_domain.progress
        )

    @staticmethod
    def to_response(child_model: ChildModel) -> UserSchema.ChildResponse:
        """Chuyển đổi từ model sang response schema."""
        if not child_model:
            return None
        return UserSchema.ChildResponse(
            user_id=child_model.user_id,
            username=child_model.username,
            email=child_model.email,
            role=child_model.role,
            name=child_model.name,
            age=child_model.age,
            progress=[ChildProgressMapper.to_response(p) for p in child_model.progress] if child_model.progress else None,
            last_played=child_model.last_played,
            report_preferences=child_model.report_preferences,
            created_at=child_model.created_at or datetime(2025, 10, 25, 16, 8),
            last_login=child_model.last_login or datetime(2025, 10, 25, 16, 8),
            gender=child_model.gender,
            date_of_birth=child_model.date_of_birth,
            phone_number=child_model.phone_number
        )