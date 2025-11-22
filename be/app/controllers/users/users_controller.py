from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.services.users.users_service import UsersService
from app.schemas.users.user_schema import UserSchema
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.database import get_db
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Any
from app.middleware.auth_middleware import create_session_token

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register")
async def register(user: UserSchema.ChildRequest, db=Depends(get_db)):
    print("Received user data from Pydantic:", user.dict())
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    try:
        result = service.create_child({
            "username": user.username,
            "email": user.email,
            "password": user.password,
            "name": user.name,
            "age": user.age,
            "report_preferences": user.report_preferences if user.report_preferences else None,
            "gender": user.gender,
            "date_of_birth": user.date_of_birth,
            "phone_number": user.phone_number,
            "role": user.role
        })

        print("run đến đây 1")
        if result.get("status") != "success":
            print("❌ Registration failed:", result)
            raise HTTPException(status_code=400, detail=result.get("message", "Đăng ký thất bại"))

    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        print("⚠️ Exception when creating child:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

    return {"status": "success", "message": "Đăng ký thành công", "data": {"user_id": result.get("user_id")}}


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(request: LoginRequest, db=Depends(get_db)):
    """
    ⭐ CHUẨN HÓA LOGIN RESPONSE
    Luôn trả về: {success, message, user, access_token}
    """
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🔐 LOGIN ATTEMPT")
    print(f"   Username: {request.username}")
    print(f"   Password: {'*' * len(request.password)}")
    
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)
    
    result = service.login(request.username, request.password)
    
    if not result["success"]:
        print(f"❌ Login failed: {result['message']}")
        raise HTTPException(status_code=400, detail=result["message"])

    # Lấy user từ database
    user = user_repo.get_by_username(request.username)
    if not user:
        print(f"❌ User not found in database after successful login")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    access_token = create_session_token(user.user_id, user.role)
    
    print(f"✅ LOGIN SUCCESSFUL")
    print(f"   User ID: {user.user_id}")
    print(f"   Username: {user.username}")
    print(f"   Role: {user.role}")
    print(f"   Token: {access_token[:30]}...")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    response = {
        "success": True,
        "message": result.get("message", "Đăng nhập thành công"),
        "user": {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "accountType": user.role.value if hasattr(user.role, 'value') else str(user.role)
        },
        "access_token": access_token  # ⭐ KEY QUAN TRỌNG
    }
    
    # Debug: Log response structure
    print(f"📤 RESPONSE STRUCTURE:")
    print(f"   Keys: {list(response.keys())}")
    print(f"   access_token exists: {('access_token' in response)}")
    print(f"   access_token value: {response['access_token'][:30]}...")
    
    return response


@router.post("/forgot-password")
async def forgot_password(request: UserSchema.ForgotPasswordRequest, db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    try:
        result = service.forgot_password(request.dict())
        if result.get("status") != "success":
            raise HTTPException(status_code=400, detail=result.get("message", "Gửi OTP thất bại"))
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        print("⚠️ Exception in forgot_password:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")


@router.post("/reset-password")
async def reset_password(request: UserSchema.ResetPasswordRequest, db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    try:
        result = service.reset_password(request.dict())
        if result.get("status") != "success":
            raise HTTPException(status_code=400, detail=result.get("message", "Đặt lại mật khẩu thất bại"))
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        print("⚠️ Exception in reset_password:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")


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