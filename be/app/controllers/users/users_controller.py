from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.services.users.users_service import UsersService
from app.schemas.users.user_schema import UserSchema
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.database import get_db
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Any

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register")
async def register(user: UserSchema.ChildRequest, db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    result = service.create_child(user.dict())
    if result.get("status") != "success":
        raise HTTPException(400, detail=result.get("message", "Đăng ký thất bại"))

    return {"status": "success", "message": "Đăng ký thành công", "data": {"user_id": result.get("user_id")}}


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(request: LoginRequest, db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    result = service.login(request.username, request.password)
    if not result["success"]:
        raise HTTPException(400, detail=result["message"])

    return result


@router.post("/forgot-password")
async def forgot_password(request: UserSchema.ForgotPasswordRequest, db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    result = service.forgot_password(request.dict())
    if result.get("status") != "success":
        raise HTTPException(400, detail=result.get("message"))

    return result


@router.post("/reset-password")
async def reset_password(request: UserSchema.ResetPasswordRequest, db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    result = service.reset_password(request.dict())
    if result.get("status") != "success":
        raise HTTPException(400, detail=result.get("message"))

    return result


@router.get("/me")
async def get_profile(user_id: UUID = Query(...), db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    profile = service.get_current_user_info(user_id)
    if not profile:
        raise HTTPException(404, detail="User not found")

    return profile


@router.put("/me")
async def update_all_in_one(payload: dict = Body(...), db=Depends(get_db)):
    user_id_str = payload.get("user_id")
    update = payload.get("update", {})

    if not user_id_str:
        raise HTTPException(400, "Thiếu user_id")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(400, "user_id sai định dạng")

    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)

    user = user_repo.get_by_id(user_id)
    child = child_repo.get_by_user_id(user_id)
    if not user or not child:
        raise HTTPException(404, "Không tìm thấy người dùng")

    # Cập nhật bảng users
    for field in ["name", "username", "email"]:
        if field in update and update[field] not in ["", None]:
            setattr(user, field, str(update[field]))

    # Cập nhật password (nếu có)
    if "password" in update and update["password"]:
        user.password = update["password"]

    # Cập nhật bảng children
    if "age" in update and update["age"] not in ["", None]:
        child.age = int(update["age"])
    if "gender" in update and update["gender"] in ["male", "female"]:
        child.gender = update["gender"]
    if "date_of_birth" in update and update["date_of_birth"]:
        child.date_of_birth = update["date_of_birth"]
    if "phone_number" in update and update["phone_number"]:
        child.phone_number = update["phone_number"].strip()

    user_repo.save(user)
    child_repo.save(child)
    db.commit()

    service = UsersService(user_repo, child_repo)
    return service.get_current_user_info(user_id)