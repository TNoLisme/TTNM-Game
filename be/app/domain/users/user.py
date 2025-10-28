from uuid import UUID
import enum
from app.domain.enum import RoleEnum
class User:
    def __init__(self, user_id: UUID, username: str, email: str, password: str, role: RoleEnum, name: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.name = name

    def update_profile(self, username: str, email: str) -> None:
        """Cập nhật thông tin hồ sơ người dùng."""
        self.username = username
        self.email = email

    def get_role(self) -> RoleEnum:
        """Trả về vai trò của người dùng."""
        return self.role
    
    def verify_password(self, plain_password: str) -> bool:
        # Giả định sử dụng hàm hash (như bcrypt) để so sánh
        from passlib.hash import bcrypt  # Cần cài: pip install passlib[bcrypt]
        return bcrypt.verify(plain_password, self.password)