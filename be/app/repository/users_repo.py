from uuid import UUID
from sqlalchemy.orm import Session
from models.users import User as UserModel
from mapper.users_mapper import UsersMapper
from domain.users.user import User
from typing import Optional
from .base_repo import BaseRepository

class UsersRepository(BaseRepository[UserModel, User]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, UserModel, UsersMapper)

    def get_by_username(self, username: str) -> Optional[User]:
        user_model = self.db_session.query(self.model_class).filter(self.model_class.username == username).first()
        return self.mapper_class.to_domain(user_model)