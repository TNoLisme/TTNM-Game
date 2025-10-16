from be.app.services import auth_service

# Đây là các hàm sẽ được gắn vào Web Framework (ví dụ: Flask/FastAPI)

def register_route(request_data: dict):
    """
    POST /api/register
    """
    # Lấy dữ liệu từ request (tùy thuộc vào framework)
    username = request_data.get('username')
    email = request_data.get('email')
    password = request_data.get('password')
    confirm_password = request_data.get('confirmPassword')
    
    if not username or not email or not password or not confirm_password:
        return {"success": False, "message": "Thiếu thông tin bắt buộc"}, 400
        
    if password != confirm_password:
        return {"success": False, "message": "Mật khẩu và xác nhận mật khẩu không khớp"}, 400
    
    # Gọi Service Layer
    result = auth_service.register_user(request_data)
    
    # Trả về kết quả
    status_code = 200 if result['success'] else 400
    return result, status_code


def login_route(request_data: dict):
    """
    POST /api/login
    """
    # Lấy dữ liệu từ request
    username = request_data.get('username')
    password = request_data.get('password')
    
    if not username or not password:
        return {"success": False, "message": "Thiếu username hoặc password"}, 400

    # Gọi Service Layer
    result = auth_service.login_user(username, password)

    # Trả về kết quả
    status_code = 200 if result['success'] else 401 # 401: Unauthorized
    return result, status_code


# Hàm route để lấy danh sách users (GET /api/users)
def get_users_route():
    from be.app.dao import user_dao
    users = user_dao.get_all_users()
    # Xóa mật khẩu khỏi danh sách trả về
    for user in users:
        if 'password' in user:
            del user['password']
    return users, 200