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

    # ================================
    # SIÊU HÀM: LƯU + CẬP NHẬT = 1 PHÁT
    # ================================
    def save(self, user: UserDomain) -> UserDomain:
        """LƯU HOẶC CẬP NHẬT – KHÔNG BAO GIỜ LỖI REFRESH!"""
        user_model = self.mapper_class.to_model(user)
        
        # DÙNG merge() → TỰ ĐỘNG GẮN LẠI VÀO SESSION
        merged = self.db_session.merge(user_model)
        self.db_session.commit()
        
        # CHỈ REFRESH merged object → AN TOÀN 100%
        self.db_session.refresh(merged)
        return self.mapper_class.to_domain(merged)

    # ================================
    # CÁC HÀM LẤY DỮ LIỆU
    # ================================
    def get_by_id(self, user_id: UUID) -> Optional[UserDomain]:
        user_model = self.db_session.query(self.model_class).filter_by(user_id=user_id).first()
        return self.mapper_class.to_domain(user_model) if user_model else None

    def get_all(self) -> List[UserDomain]:
        return [self.mapper_class.to_domain(m) for m in self.db_session.query(self.model_class).all()]

    def get_by_username(self, username: str) -> Optional[UserDomain]:
        print(f"[REPO] Tìm username: {username}")
        user_model = self.db_session.query(self.model_class).filter_by(username=username).first()
        print(f"[REPO] Tìm thấy: {user_model}")
        return self.mapper_class.to_domain(user_model) if user_model else None

    def get_by_email(self, email: str) -> Optional[UserDomain]:
        user_model = self.db_session.query(self.model_class)\
            .filter(self.model_class.email.ilike(email.strip().lower())).first()
        return self.mapper_class.to_domain(user_model) if user_model else None

    def get_by_username_and_password(self, username: str, password: str) -> Optional[UserDomain]:
        user_model = self.db_session.query(self.model_class)\
            .filter(self.model_class.username == username)\
            .filter(self.model_class.password == password)\
            .first()
        print(f"[LOGIN] User: {username} → {user_model}")
        return self.mapper_class.to_domain(user_model) if user_model else None

    # Alias để dễ gọi
    get_user_by_id = get_by_id
    get_all_users = get_all