from uuid import UUID, uuid4
from app.domain.users.user import User
from app.domain.users.child import Child
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.domain.enum import RoleEnum, GenderEnum, ReportTypeEnum
from datetime import datetime
from app.schemas.users.user_schema import UserSchema

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