from uuid import UUID
from app.domain.users.user import User
from app.repository.users_repo import UsersRepository

class UsersService:
    def __init__(self, user_repo: UsersRepository):
        self.repo = user_repo

    def create_user(self, data: dict) -> dict:
        user = User(
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
            role=data.get("role"),
            name=data.get("name")
        )
        self.repo.save_user(user)
        return {"status": "success", "message": f"User {user.username} created", "user_id": str(user.user_id)}

    def get_user_by_id(self, user_id: UUID) -> dict:
        user = self.repo.get_user_by_id(user_id)
        if user:
            return {"status": "success", "data": {
                "username": user.username,
                "email": user.email,
                "role": user.role
            }}
        return {"status": "failed", "message": "User not found"}

    def update_user(self, user_id: UUID, data: dict) -> dict:
        user = self.repo.get_user_by_id(user_id)
        if user:
            user.username = data.get("username", user.username)
            self.repo.update_user(user)
            return {"status": "success", "message": f"User {user_id} updated"}
        return {"status": "failed", "message": "User not found"}