from uuid import UUID
from app.models.users.user import User as UserModel
from app.domain.users.admin import Admin
from app.mapper.child_mapper import ChildMapper
from app.schemas.users.user_schema import UserSchema
from app.domain.enum import RoleEnum

class AdminMapper:
    @staticmethod
    def to_domain(user_model: UserModel, children: list = None) -> Admin:
        """Chuyển đổi từ model sang Admin domain entity"""
        if not user_model:
            return None
        
        # Chỉ chuyển nếu role là admin
        if user_model.role != RoleEnum.admin:
            raise ValueError("User is not an admin")
        
        # Chuyển children nếu có
        all_child = []
        if children:
            all_child = [ChildMapper.to_domain(child) for child in children]
        
        return Admin(
            user_id=user_model.user_id,
            username=user_model.username,
            email=user_model.email,
            password=user_model.password,
            role=user_model.role,
            name=user_model.name,
            all_child=all_child
        )

    @staticmethod
    def to_model(admin_domain: Admin) -> UserModel:
        """Chuyển đổi từ Admin domain entity sang model"""
        if not admin_domain:
            return None
        
        return UserModel(
            user_id=admin_domain.user_id,
            username=admin_domain.username,
            email=admin_domain.email,
            password=admin_domain.password,
            role=RoleEnum.admin,
            name=admin_domain.name
        )

    @staticmethod
    def to_response(admin_domain: Admin) -> UserSchema.AdminResponse:
        """Chuyển đổi từ Admin domain sang response schema"""
        if not admin_domain:
            return None
        
        return UserSchema.AdminResponse(
            user_id=admin_domain.user_id,
            username=admin_domain.username,
            email=admin_domain.email,
            role=admin_domain.role,
            name=admin_domain.name,
            all_child=[ChildMapper.to_response(c) for c in admin_domain.all_child] if admin_domain.all_child else []
        )

    @staticmethod
    def to_response_from_model(user_model: UserModel, children: list = None) -> UserSchema.AdminResponse:
        """Chuyển đổi trực tiếp từ model sang response"""
        if not user_model:
            return None
        
        children_response = []
        if children:
            children_response = [ChildMapper.to_response(c) for c in children]
        
        return UserSchema.AdminResponse(
            user_id=user_model.user_id,
            username=user_model.username,
            email=user_model.email,
            role=user_model.role,
            name=user_model.name,
            all_child=children_response
        )