
from be.app.dao import user_dao 

def register_user(user_details: dict):
    """
    Xử lý logic đăng ký người dùng mới.
    """
    username = user_details.get('username')
    email = user_details.get('email')
    password = user_details.get('password')
    
    # 1. Kiểm tra username/email đã tồn tại
    if user_dao.find_user_by_username(username):
        return {"success": False, "message": "Username đã tồn tại."}
    
    if user_dao.find_user_by_email(email):
        return {"success": False, "message": "Email đã tồn tại."}

    # 2. Lưu người dùng vào CSDL
    new_user = user_dao.create_new_user(user_details)
    
    if new_user:
        # Xóa mật khẩu trước khi trả về
        del new_user['password']
        return {"success": True, "message": "Đăng ký thành công!", "user": new_user}
    else:
        # Trường hợp này chỉ xảy ra nếu có lỗi tạo ID hoặc lỗi khác trong DAO
        return {"success": False, "message": "Lỗi không xác định khi đăng ký."}


def login_user(username: str, password: str):
    """
    Xử lý logic đăng nhập.
    """
    user = user_dao.find_user_by_username(username)

    # 1. Kiểm tra tồn tại người dùng
    if not user:
        return {"success": False, "message": "Tên đăng nhập không tồn tại."}

    # 2. So sánh mật khẩu (Logic đơn giản: so sánh chuỗi)
    if user["password"] == password:
        # Đăng nhập thành công
        del user['password'] # Xóa mật khẩu trước khi trả về
        return {"success": True, "message": "Đăng nhập thành công!", "user": user}
    else:
        # Sai mật khẩu
        return {"success": False, "message": "Mật khẩu không đúng."}