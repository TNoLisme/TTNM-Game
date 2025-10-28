from fastapi import Depends, HTTPException, APIRouter
from app.services.users.users_service import UsersService
from app.schemas.users.user_schema import UserSchema
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()

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
        raise e  # Ném lại HTTPException để FastAPI xử lý đúng mã lỗi
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
    print(f"Received login request for username: {request.username}, password: {request.password}")
    
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    result = service.login(request.username, request.password)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

# Thêm mới cho quên mật khẩu
@router.post("/forgot-password")  # Đổi router thành user_router
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

@router.post("/reset-password")  # Đổi router thành user_router
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