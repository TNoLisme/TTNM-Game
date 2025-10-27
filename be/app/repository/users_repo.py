from uuid import UUID
from sqlalchemy.orm import Session
from app.models.users.user import User as UserModel
from app.mapper.users_mapper import UsersMapper
from app.domain.users.user import User as UserDomain
from typing import Optional, List
from .base_repo import BaseRepository

class UsersRepository(BaseRepository[UserModel, UserDomain]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, UserModel, UsersMapper)
    
    def save_user(self, user: UserDomain) -> UserDomain:
        """Lưu một đối tượng User vào cơ sở dữ liệu."""
        user_model = self.mapper_class.to_model(user)
        self.db_session.add(user_model)
        try:
            self.db_session.commit()
            self.db_session.refresh(user_model)
            return self.mapper_class.to_domain(user_model)
        except Exception as e:
            self.db_session.rollback()
            raise ValueError(f"Lỗi khi lưu user: {e}")
        finally:
            self.db_session.expire_all() # Làm mới session

    def update_user(self, user: UserDomain) -> UserDomain:
        """Cập nhật thông tin của một User trong cơ sở dữ liệu."""
        existing_user = self.db_session.query(self.model_class).filter_by(user_id=user.user_id).first()
        if existing_user:
            user_model = self.mapper_class.to_model(user)
            for key, value in vars(user_model).items():
                if key not in ['user_id', '_sa_instance_state']:
                    setattr(existing_user, key, value)
            self.db_session.commit()
            self.db_session.refresh(existing_user)
            return self.mapper_class.to_domain(existing_user)
        raise ValueError("User not found")

    def get_user_by_id(self, user_id: UUID) -> Optional[UserDomain]:
        """Lấy thông tin User dựa trên user_id."""
        user_model = self.db_session.query(self.model_class).filter_by(user_id=user_id).first()
        return self.mapper_class.to_domain(user_model) if user_model else None

    def get_all(self) -> List[UserDomain]:
        """Lấy tất cả các User."""
        user_models = self.db_session.query(self.model_class).all()
        return [self.mapper_class.to_domain(user) for user in user_models]

    def get_by_username(self, username: str) -> Optional[UserDomain]:
        """Lấy User dựa trên username."""
        print(f"Querying username: {username}")  # Log để kiểm tra
        user_model = self.db_session.query(self.model_class).filter_by(username=username).first()
        print(f"Found user: {user_model}")  # Log kết quả
        return self.mapper_class.to_domain(user_model)

    def get_by_email(self, email: str) -> Optional[UserDomain]:
        """Lấy User dựa trên email."""
        user_model = self.db_session.query(self.model_class).filter_by(email=email).first()
        return self.mapper_class.to_domain(user_model)

    def get_all_users(self) -> List[UserDomain]:
        """Lấy tất cả các User."""
        return self.get_all()

    def get_by_username_and_password(self, username: str, password: str) -> Optional[UserDomain]:
        """Lấy User dựa trên username và password."""
        user_model = self.db_session.query(self.model_class) \
            .filter(self.model_class.username == username) \
            .filter(self.model_class.password == password) \
            .first()
        return self.mapper_class.to_domain(user_model)
    
