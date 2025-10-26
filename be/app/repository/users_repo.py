# app/repository/users_repo.py
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.users.user import User as UserModel  # Import tuyệt đối
from app.mapper.users_mapper import UsersMapper
from app.domain.users.user import User as UserDomain
from typing import Optional, List
from .base_repo import BaseRepository

class UsersRepository(BaseRepository[UserModel, UserDomain]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, UserModel, UsersMapper)
    
    def get_all(self):
        user_models = self.db_session.query(self.model_class).all()
        return [self.mapper_class.to_domain(user) for user in user_models]

    def get_by_username(self, username: str) -> UserDomain:
        user = self.db_session.query(UserDomain).filter_by(username=username).first()
        return UsersMapper.to_domain(user)

    def get_by_email(self, email: str) -> UserDomain:
        user = self.db_session.query(UserDomain).filter_by(email=email).first()
        return UsersMapper.to_domain(user)

    def get_all_users(self) -> List[UserDomain]:
        user_models = self.db_session.query(self.model_class).all()
        return [self.mapper_class.to_domain(user) for user in user_models]

    def get_by_username_and_password(self, username: str, password: str) -> Optional[UserDomain]:
        user_model = self.db_session.query(self.model_class) \
            .filter(self.model_class.username == username) \
            .filter(self.model_class.password == password) \
            .first()
        return self.mapper_class.to_domain(user_model)