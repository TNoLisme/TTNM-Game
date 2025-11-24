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

    # ==================== User Management ====================
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserDomain]:
        limit = max(0, min(limit, 1000))
        user_models = (self.db_session.query(self.model_class)
            .order_by(self.model_class.user_id)
            .offset(skip).limit(limit).all())
        return [self.mapper_class.to_domain(user) for user in user_models]

    def count_users(self) -> int:
        return self.db_session.query(self.model_class).count()

    def get_user_by_id(self, user_id: UUID) -> Optional[UserDomain]:
        user_model = self.db_session.query(self.model_class)\
            .filter(self.model_class.user_id == user_id).first()
        return self.mapper_class.to_domain(user_model) if user_model else None

    def get_user_by_username(self, username: str) -> Optional[UserDomain]:
        user_model = self.db_session.query(self.model_class)\
            .filter(self.model_class.username == username).first()
        return self.mapper_class.to_domain(user_model) if user_model else None

    def get_user_by_email(self, email: str) -> Optional[UserDomain]:
        user_model = self.db_session.query(self.model_class)\
            .filter(self.model_class.email == email).first()
        return self.mapper_class.to_domain(user_model) if user_model else None

    def add_user(self, user: UserDomain) -> UserDomain:
        try:
            user_model = UserModel(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                password=user.password,  # Không hash theo yêu cầu
                role=user.role.value,
                name=user.name
            )
            self.db_session.add(user_model)
            self.db_session.commit()
            self.db_session.refresh(user_model)
            return self.mapper_class.to_domain(user_model)
        except Exception:
            self.db_session.rollback()
            raise

    def update_user(self, user: UserDomain) -> UserDomain:
        try:
            user_model = self.db_session.query(self.model_class)\
                .filter(self.model_class.user_id == user.user_id).first()
            
            if not user_model:
                raise ValueError(f"User with id {user.user_id} not found")
            
            # Update các field theo SQL schema
            user_model.username = user.username
            user_model.email = user.email
            user_model.name = user.name
            user_model.role = user.role.value
            user_model.password = user.password  # Không hash
            
            self.db_session.commit()
            self.db_session.refresh(user_model)
            return self.mapper_class.to_domain(user_model)
        except Exception:
            self.db_session.rollback()
            raise

    def delete_user(self, user_id: UUID) -> bool:
        try:
            user = self.db_session.query(self.model_class)\
                .filter(self.model_class.user_id == user_id).first()
            if not user:
                return False

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

    def search_users_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[UserDomain]:
        user_models = self.db_session.query(self.model_class)\
            .filter(self.model_class.name.ilike(f"%{name}%"))\
            .offset(skip).limit(limit).all()
        return [self.mapper_class.to_domain(user) for user in user_models]

    # ==================== Child Management ====================
    def get_all_children(self, skip: int = 0, limit: int = 100) -> List[Child]:
        limit = max(0, min(limit, 1000))
        child_models = (self.db_session.query(ChildModel)
            .order_by(ChildModel.user_id)
            .offset(skip).limit(limit).all())
        return [ChildMapper.to_domain(child) for child in child_models]

    def count_children(self) -> int:
        return self.db_session.query(ChildModel).count()

    def get_child_by_id(self, user_id: UUID) -> Optional[Child]:
        child_model = self.db_session.query(ChildModel)\
            .filter(ChildModel.user_id == user_id).first()
        return ChildMapper.to_domain(child_model) if child_model else None

    def add_child(self, child: Child) -> Child:
        try:
            child_model = ChildModel(
                user_id=child.user_id,
                age=child.age,
                last_played=child.last_played,
                report_preferences=child.report_preferences,
                created_at=child.created_at,
                last_login=child.last_login
            )
            self.db_session.add(child_model)
            self.db_session.commit()
            self.db_session.refresh(child_model)
            return ChildMapper.to_domain(child_model)
        except Exception:
            self.db_session.rollback()
            raise

    def update_child(self, child: Child) -> Child:
        try:
            child_model = self.db_session.query(ChildModel)\
                .filter(ChildModel.user_id == child.user_id).first()
            
            if not child_model:
                raise ValueError(f"Child with user_id {child.user_id} not found")
            
            # Update fields theo SQL schema
            child_model.age = child.age
            child_model.last_played = child.last_played
            child_model.report_preferences = child.report_preferences
            child_model.last_login = child.last_login
            # created_at không update vì đã có giá trị ban đầu
            
            self.db_session.commit()
            self.db_session.refresh(child_model)
            return ChildMapper.to_domain(child_model)
        except Exception:
            self.db_session.rollback()
            raise

    def delete_child(self, user_id: UUID) -> bool:
        try:
            child = self.db_session.query(ChildModel)\
                .filter(ChildModel.user_id == user_id).first()
            if not child:
                return False
            
            self.db_session.delete(child)
            self.db_session.commit()
            return True
        except Exception:
            self.db_session.rollback()
            raise