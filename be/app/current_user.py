# app/current_user.py
from typing import Optional, Union
from app.domain.users.user import User
from app.domain.users.child import Child

# Biến global lưu user hiện tại (Child hoặc Admin)
current_user: Optional[Union[User, Child]] = None

def set_current_user(user: Union[User, Child]) -> None:
    """Đặt user hiện tại sau khi login"""
    global current_user
    current_user = user

def get_current_user() -> Optional[Union[User, Child]]:
    """Lấy user hiện tại"""
    global current_user
    return current_user

def is_child() -> bool:
    """Kiểm tra có phải Child không"""
    return isinstance(get_current_user(), Child)

def is_admin() -> bool:
    """Kiểm tra có phải Admin không"""
    user = get_current_user()
    return user is not None and getattr(user, 'role', None) == 'admin'

def logout() -> None:
    """Đăng xuất"""
    global current_user
    current_user = None