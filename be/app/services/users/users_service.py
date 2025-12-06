from uuid import UUID, uuid4
from app.domain.users.user import User
from app.domain.users.child import Child
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.domain.enum import RoleEnum, GenderEnum
from datetime import datetime
import time
import random
import string
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

# Global dict tạm thời cho OTP
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
            role=RoleEnum[data.get("role").upper()] if data.get("role") else RoleEnum.admin,
            name=data.get("name")
        )

        self.user_repo.save(user)
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
        self.user_repo.save(user)

        child = Child(
            user_id=str(user_id),
            age=data.get("age"),
            last_played=None,
            report_preferences=data.get("report_preferences"),
            created_at=datetime.utcnow(),
            last_login=None,
            gender=data.get("gender"),
            date_of_birth=data.get("date_of_birth"),
            phone_number=data.get("phone_number")
        )
        saved_child = self.child_repo.save(child)
        print("CHILD SAVED:", saved_child.__dict__)
        return {"status": "success", "message": "Child created", "user_id": str(user_id)}
    
    def login(self, username: str, password: str) -> dict:
        """✅ LOGIN - KHÔNG CÓ TOKEN"""
        user = self.user_repo.get_by_username_and_password(username, password)
        
        if not user:
            return {"success": False, "message": "Sai tên đăng nhập hoặc mật khẩu."}

        # Lấy thông tin child nếu là child
        child_data = None
        if user.role == RoleEnum.child:
            child_data = self.child_repo.get_by_user_id(user.user_id)

        return {
            "success": True,
            "message": "Đăng nhập thành công",
            "user": {
                "user_id": str(user.user_id),
                "username": user.username,
                "fullName": user.name,
                "name": user.name,
                "email": user.email,
                "accountType": user.role.value,
                "role": user.role.value,
                "age": child_data.age if child_data else None,
                "gender": child_data.gender.value if child_data and child_data.gender else None,
                "phone_number": child_data.phone_number if child_data else None
            }
        }
    
    def forgot_password(self, data: dict) -> dict:
        email = data.get("email")
        user = self.user_repo.get_by_email(email)
        if not user:
            return {"status": "failed", "message": "Email not found"}

        otp = ''.join(random.choices(string.digits, k=6))
        expiry = time.time() + 600

        otp_storage[email] = {'otp': otp, 'expiry': expiry}
        print(f"[DEMO] OTP generated for {email}: {otp}")

        try:
            msg = MIMEText(f"Xin chào {user.name},\n\nMã OTP của bạn là: {otp}\n\nMã này hết hạn sau 10 phút.\n\nTrân trọng,\nEmoGarden Team")
            msg['Subject'] = 'Mã OTP Đặt Lại Mật Khẩu - EmoGarden'
            msg['From'] = os.getenv("EMAIL_USER")
            msg['To'] = email

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
                server.send_message(msg)
            print(f"[EMAIL] OTP sent to {email} successfully")
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send OTP to {email}: {e}")
            return {"status": "failed", "message": "Gửi OTP thất bại, thử lại sau"}

        return {"status": "success", "message": "OTP đã gửi đến email của bạn"}

    def reset_password(self, data: dict) -> dict:
        email = data.get("email")
        otp = data.get("otp")
        new_password = data.get("new_password")

        stored = otp_storage.get(email)
        if not stored:
            return {"status": "failed", "message": "No OTP found for this email. Request new one."}

        if stored['otp'] != otp or time.time() > stored['expiry']:
            del otp_storage[email]
            return {"status": "failed", "message": "Invalid or expired OTP"}

        user = self.user_repo.get_by_email(email)
        if user:
            user.password = new_password
            self.user_repo.save(user)
            del otp_storage[email]
            return {"status": "success", "message": "Password reset successfully"}
        return {"status": "failed", "message": "User not found"}

    def get_current_user_info(self, user_id: UUID) -> dict:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        base_info = {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "role": user.role.value
        }
        
        if user.role == RoleEnum.child:
            child = self.child_repo.get_by_user_id(str(user_id))
            if child:
                base_info.update({
                    "age": child.age,
                    "gender": child.gender.value if child.gender else None,
                    "phone_number": child.phone_number
                })
        
        return base_info

    def update_profile(self, user_id: UUID, data: dict) -> dict:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "User not found"}

        # UPDATE USER
        for key, value in data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        self.user_repo.save(user)

        # UPDATE CHILD NẾU LÀ CHILD
        if user.role == RoleEnum.child:
            child = self.child_repo.get_by_user_id(user_id)
            if child:
                child_data = {k: v for k, v in data.items() if k in ["age", "phone_number", "gender", "report_preferences"]}
                if child_data:
                    for key, value in child_data.items():
                        if key == "gender":
                            setattr(child, key, GenderEnum[value.upper()])
                        else:
                            setattr(child, key, value)
                    self.child_repo.save(child)
                    print("CHILD UPDATED IN SERVICE:", child.__dict__)
            else:
                print("[WARNING] Child not found for update!")

        return {"success": True, "message": "Cập nhật thành công"}