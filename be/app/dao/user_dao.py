# Dữ liệu người dùng cố định (Mô phỏng tài khoản Admin)
# Sửa logic truy cập DB thực tế khi có DB

MOCK_USERS = [
    {
        "id": "admin",
        "username": "admin",
        "email": "admin@ttnm.com",
        "password": "admin",
        "fullName": "admin",
        "accountType": "admin",
    }
]

def find_user_by_username(username: str):
    """
    Tìm kiếm người dùng theo username trong DB.
    """
    for user in MOCK_USERS:
        if user["username"] == username:
            return user.copy()
    return None

def find_user_by_email(email: str):
    """
    Tìm kiếm người dùng theo email trong DB.
    """
    for user in MOCK_USERS:
        if user["email"] == email:
            return user.copy()
    return None

def create_new_user(user_data: dict):
    """
    Lưu người dùng mới vào DB.
    """
    if find_user_by_username(user_data.get('username')) or find_user_by_email(user_data.get('email')):
        return None # Đã tồn tại
        
    # Tạo ID ngẫu nhiên đơn giản
    import uuid
    new_user = {
        "id": str(uuid.uuid4()),
        "username": user_data.get('username'),
        "email": user_data.get('email'),
        "password": user_data.get('password'),
        "fullName": user_data.get('fullName'),
        "accountType": user_data.get('accountType', 'user'),
    }

    MOCK_USERS.append(new_user)
    return new_user.copy()

def get_all_users():
    """
    Lấy tất cả người dùng.
    """
    return [user.copy() for user in MOCK_USERS]