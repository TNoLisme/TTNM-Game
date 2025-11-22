from uuid import UUID
from sqlalchemy.orm import Session
from app.models.users.user import User as UserModel
from app.models.users.child import Child as ChildModel
from app.mapper.users_mapper import UsersMapper
from app.mapper.child_mapper import ChildMapper
from app.domain.users.user import User as UserDomain
from app.domain.users.child import Child
from typing import List, Optional
from .base_repo import BaseRepository

class AdminRepository(BaseRepository[UserModel, UserDomain]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, UserModel, UsersMapper)

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserDomain]:
        """Lấy danh sách tất cả users với pagination"""
        limit = max(0, min(limit, 1000))
        user_models = (self.db_session.query(self.model_class)
            .order_by(self.model_class.user_id)  # đảm bảo thứ tự cố định
            .offset(skip).limit(limit).all())
        return [self.mapper_class.to_domain(user) for user in user_models]

    def get_all_children(self, skip: int = 0, limit: int = 100) -> List[Child]:
        """Lấy danh sách tất cả children với pagination"""
        limit = max(0, min(limit, 1000))
        child_models = (self.db_session.query(ChildModel)
            .order_by(ChildModel.child_id)  # thay bằng khóa thích hợp nếu khác
            .offset(skip).limit(limit).all())
        return [ChildMapper.to_domain(child) for child in child_models]

    def delete_user(self, user_id: UUID) -> bool:
        """Xóa user theo ID (xóa tất cả child liên quan). Rollback nếu lỗi."""
        try:
            user = self.db_session.query(self.model_class)\
                .filter(self.model_class.user_id == user_id).first()
            if not user:
                return False

            # Xóa tất cả child liên quan
            children = self.db_session.query(ChildModel)\
                .filter(ChildModel.user_id == user_id).all()
            for child in children:
                self.db_session.delete(child)

            self.db_session.delete(user)
            self.db_session.commit()
            return True
        except Exception:
            self.db_session.rollback()
            raise

    def update_user_role(self, user_id: UUID, new_role: str) -> Optional[UserDomain]:
        """Cập nhật role của user (với validation cơ bản)."""
        # TODO: thay bằng danh sách role thực tế của ứng dụng
        ALLOWED_ROLES = {"user", "admin", "moderator"}

        if new_role not in ALLOWED_ROLES:
            raise ValueError("Invalid role")

        try:
            user = self.db_session.query(self.model_class)\
                .filter(self.model_class.user_id == user_id).first()
            if not user:
                return None
            user.role = new_role
            self.db_session.commit()
            self.db_session.refresh(user)
            return self.mapper_class.to_domain(user)
        except Exception:
            self.db_session.rollback()
            raise

    def count_users(self) -> int:
        """Đếm tổng số users"""
        return self.db_session.query(self.model_class).count()

    def count_children(self) -> int:
        """Đếm tổng số children"""
        return self.db_session.query(ChildModel).count()

    def search_users_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[UserDomain]:
        """Tìm kiếm users theo tên"""
        user_models = self.db_session.query(self.model_class)\
            .filter(self.model_class.name.ilike(f"%{name}%"))\
            .offset(skip).limit(limit).all()
        return [self.mapper_class.to_domain(user) for user in user_models]