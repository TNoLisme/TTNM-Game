from uuid import UUID, uuid4
from app.domain.users.user import User
from app.domain.users.child import Child
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.domain.enum import RoleEnum, GenderEnum, ReportTypeEnum
from datetime import datetime
from app.schemas.users.user_schema import UserSchema
import time  # Thêm cho expiry
import random  # Thêm cho OTP
import string  # Thêm cho OTP
import smtplib  # Thêm cho gửi email
from email.mime.text import MIMEText  # Thêm cho message email
from dotenv import load_dotenv  # Thêm để load .env
import os  # Thêm cho os.getenv

load_dotenv()  # Load .env ngay đầu file

# Global dict tạm thời cho OTP (cho demo, mất khi server restart)
otp_storage = {}

class UsersService:
    def __init__(self, user_repo: UsersRepository, child_repo: ChildRepository):
        self.user_repo = user_repo
        self.child_repo = child_repo

    def create_user(self, data: dict) -> dict:
        existing_user_by_username = self.user_repo.get_by_username(data.get("username"))
        if existing_user_by_username:
            return {"status": "failed", "message": "Username already exists"}

        existing_user_by_email = self.user_repo.get_by_email(data.get("email"))
        if existing_user_by_email:
            return {"status": "failed", "message": "Email already exists"}

        user = User(
            user_id=uuid4(),
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
            role=RoleEnum[data.get("role").upper()] if data.get("role") else RoleEnum.ADMIN,
            name=data.get("name")
        )

        self.user_repo.save_user(user)
        return {"status": "success", "message": f"User {user.username} created", "user_id": str(user.user_id)}

    def create_child(self, data: dict) -> dict:
        print("Data in create_child:", data)
        existing_user_by_username = self.user_repo.get_by_username(data.get("username"))
        if existing_user_by_username:
            return {"status": "failed", "message": "Username already exists"}

        existing_user_by_email = self.user_repo.get_by_email(data.get("email"))
        if existing_user_by_email:
            return {"status": "failed", "message": "Email already exists"}

        user_id = uuid4()

        user = User(
            user_id=user_id,
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
            role=RoleEnum.child,
            name=data.get("name")
        )
        self.user_repo.save_user(user)

        child = Child(
            user_id=str(user_id),
            age=data.get("age"),
            last_played=None,
            report_preferences=ReportTypeEnum(data.get("report_preferences")) if data.get("report_preferences") else None,
            created_at=datetime.utcnow(),
            last_login=None,
            gender=GenderEnum(data.get("gender")) if data.get("gender") else None,
            date_of_birth=data.get("date_of_birth"),
            phone_number=data.get("phone_number")
        )
        self.child_repo.save(child)
        print("Tạo child thành công ở đây.")
        return {"status": "success", "message": f"Child created", "user_id": str(child.user_id)}
    
    def login(self, username: str, password: str) -> dict:
        """Kiểm tra đăng nhập dựa trên username và password."""
        user = self.user_repo.get_by_username_and_password(username, password)
        if user:
            return {
                "success": True,
                "message": "Đăng nhập thành công",
                "user": {
                    "username": user.username,
                    "fullName": user.name,
                    "accountType": user.role.value
                }
            }
        return {"success": False, "message": "Sai tên đăng nhập hoặc mật khẩu."}
    
        # Thêm mới cho quên mật khẩu (gửi email thật)
    def forgot_password(self, data: dict) -> dict:
        email = data.get("email")
        user = self.user_repo.get_by_email(email)
        if not user:
            return {"status": "failed", "message": "Email not found"}

        # Tạo OTP random 6 chữ số
        otp = ''.join(random.choices(string.digits, k=6))
        expiry = time.time() + 600  # 10 phút (600 giây)

        # Lưu tạm vào global dict (key: email)
        otp_storage[email] = {'otp': otp, 'expiry': expiry}
        print(f"[DEMO] OTP generated for {email}: {otp} (expires at {expiry})")  # Giữ print cho demo

        # Gửi email thật qua Gmail
        try:
            msg = MIMEText(f"Xin chào {user.name},\n\nMã OTP của bạn là: {otp}\n\nMã này hết hạn sau 10 phút.\n\nTrân trọng,\nEmoGarden Team")
            msg['Subject'] = 'Mã OTP Đặt Lại Mật Khẩu - EmoGarden'
            msg['From'] = os.getenv("EMAIL_USER")
            msg['To'] = email

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
                server.send_message(msg)
            print(f"[EMAIL] OTP sent to {email} successfully")  # Log thành công
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send OTP to {email}: {e}")
            return {"status": "failed", "message": "Gửi OTP thất bại, thử lại sau"}

        return {"status": "success", "message": "OTP đã gửi đến email của bạn"}

    def reset_password(self, data: dict) -> dict:
        email = data.get("email")
        otp = data.get("otp")
        new_password = data.get("new_password")

        # Lấy OTP từ global dict
        stored = otp_storage.get(email)
        if not stored:
            return {"status": "failed", "message": "No OTP found for this email. Request new one."}

        # Verify OTP và expiry
        if stored['otp'] != otp or time.time() > stored['expiry']:
            del otp_storage[email]  # Xóa nếu sai
            return {"status": "failed", "message": "Invalid or expired OTP"}

        # Cập nhật password (plain text, dùng repo update)
        user = self.user_repo.get_by_email(email)
        if user:
            user.password = new_password  # Plain text
            self.user_repo.update_user(user)  # Gọi update_user hiện có
            del otp_storage[email]  # Xóa OTP sau khi thành công
            return {"status": "success", "message": "Password reset successfully"}
        return {"status": "failed", "message": "User not found"}