from abc import ABC, abstractmethod
from uuid import UUID
from enum import Enum

class RoleEnum(str, Enum):
    CHILD = "child"
    ADMIN = "admin"

class User(ABC):
    """
    Abstract base class cho tất cả người dùng.
    """

    def __init__(self, user_id: UUID, username: str, email: str, password: str, role: RoleEnum, name: str):
        self._user_id = user_id
        self._username = username
        self._email = email
        self._password = password  # Nên mã hóa trước khi lưu
        self._role = role
        self._name = name

    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        """Xác thực đăng nhập"""
        pass

    @abstractmethod
    def logout(self) -> None:
        """Đăng xuất người dùng"""
        pass

    @abstractmethod
    def update_profile(self, username: str, email: str) -> None:
        """Cập nhật thông tin hồ sơ"""
        pass

    @abstractmethod
    def get_role(self) -> RoleEnum:
        """Trả về role của người dùng"""
        pass
