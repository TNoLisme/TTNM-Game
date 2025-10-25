from uuid import UUID
import enum

class RoleEnum(enum.Enum):
    child = "child"
    admin = "admin"

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