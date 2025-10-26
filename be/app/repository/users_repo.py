# app/repository/users_repo.py
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.users.user import User as UserModel  # Import tuyệt đối
from app.mapper.users_mapper import UsersMapper
from app.domain.users.user import User
from typing import Optional, List
from .base_repo import BaseRepository

class UsersRepository(BaseRepository[UserModel, User]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, UserModel, UsersMapper)
    
    def get_all(self):
        user_models = self.db_session.query(self.model_class).all()
        return [self.mapper_class.to_domain(user) for user in user_models]

    def get_by_username(self, username: str) -> Optional[User]:
        user_model = self.db_session.query(self.model_class).filter(self.model_class.username == username).first()
        return self.mapper_class.to_domain(user_model)

    def get_all_users(self) -> List[User]:
        user_models = self.db_session.query(self.model_class).all()
        return [self.mapper_class.to_domain(user) for user in user_models]

    def get_by_username_and_password(self, username: str, password: str) -> Optional[User]:
        user_model = self.db_session.query(self.model_class) \
            .filter(self.model_class.username == username) \
            .filter(self.model_class.password == password) \
            .first()
        return self.mapper_class.to_domain(user_model)