from uuid import UUID
from datetime import datetime
from app.models.users.user import User as UserModel
from app.domain.enum import RoleEnum
from app.domain.users.user import User as UserDomain
from app.schemas.users.user_schema import UserSchema

class UsersMapper:
    @staticmethod
    def to_domain(user_model: UserModel) -> UserDomain:
        """Chuyển đổi từ model sang domain entity."""
        if not user_model:
            return None

        # Xử lý an toàn khi role có thể là string hoặc Enum
        role_value = (
            user_model.role.value
            if isinstance(user_model.role, RoleEnum)
            else str(user_model.role)
        )

        return UserDomain(
            user_id=user_model.user_id,
            username=user_model.username,
            email=user_model.email,
            password=user_model.password,
            role=RoleEnum(role_value),
            name=user_model.name
        )

    @staticmethod
    def to_model(user_domain: UserDomain) -> UserModel:
        """Chuyển đổi từ domain entity sang model."""
        if not user_domain:
            return None
        return UserModel(
            user_id=user_domain.user_id,
            username=user_domain.username,
            email=user_domain.email,
            password=user_domain.password,
            role=user_domain.role.value,
            name=user_domain.name
        )

    @staticmethod
    def to_response(user_model: UserModel) -> UserSchema.UserResponse:
        """Chuyển đổi từ model sang response schema."""
        if not user_model:
            return None
        return UserSchema.UserResponse(
            user_id=user_model.user_id,
            username=user_model.username,
            email=user_model.email,
            role=str(user_model.role.value if isinstance(user_model.role, RoleEnum) else user_model.role),
            name=user_model.name
        )
