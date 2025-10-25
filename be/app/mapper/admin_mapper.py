from uuid import UUID
from datetime import datetime
from models.users.admin import Admin as AdminModel
from domain.users.admin import Admin, RoleEnum
from schemas.users.user_schema import UserSchema  # Giả định schema

class AdminMapper:
    @staticmethod
    def to_domain(admin_model: AdminModel) -> Admin:
        """Chuyển đổi từ model sang domain entity."""
        if not admin_model:
            return None
        return Admin(
            user_id=admin_model.user_id,
            username=admin_model.username,
            email=admin_model.email,
            password=admin_model.password,
            role=RoleEnum(admin_model.role),
            name=admin_model.name,
            all_child=[]  # Placeholder, cần load từ repository
        )

    @staticmethod
    def to_model(admin_domain: Admin) -> AdminModel:
        """Chuyển đổi từ domain entity sang model."""
        if not admin_domain:
            return None
        return AdminModel(
            user_id=admin_domain.user_id,
            username=admin_domain.username,
            email=admin_domain.email,
            password=admin_domain.password,
            role=admin_domain.role.value,
            name=admin_domain.name
        )

    @staticmethod
    def to_response(admin_model: AdminModel) -> UserSchema.AdminResponse:
        """Chuyển đổi từ model sang response schema."""
        if not admin_model:
            return None
        return UserSchema.AdminResponse(
            user_id=admin_model.user_id,
            username=admin_model.username,
            email=admin_model.email,
            role=admin_model.role,
            name=admin_model.name,
            all_child=None  # Giả định all_child là tùy chọn
        )