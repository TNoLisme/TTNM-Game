from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import date
from app.domain.enum import RoleEnum, ReportTypeEnum, GenderEnum

# === BASE ===
class UserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: RoleEnum
    name: str = Field(..., max_length=100)

    @validator("password")
    def password_must_contain_special(cls, v):
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("password must contain at least one special character")
        return v

    class Config:
        use_enum_values = True

class UserResponse(BaseModel):
    user_id: UUID
    username: str
    email: str
    role: RoleEnum
    name: str

    class Config:
        from_attributes = True
        use_enum_values = True

# === CHILD ===
class ChildRequest(UserRequest):
    age: int = Field(..., ge=3)
    report_preferences: Optional[ReportTypeEnum] = None
    gender: GenderEnum
    date_of_birth: date
    phone_number: str = Field(..., min_length=10, max_length=20)

    class Config:
        use_enum_values = True

class ChildResponse(UserResponse):
    age: int
    progress: Optional[List[dict]] = None
    last_played: Optional[date] = None
    report_preferences: Optional[ReportTypeEnum] = None
    created_at: date = Field(default_factory=date.today)
    last_login: Optional[date] = None
    gender: GenderEnum
    date_of_birth: date
    phone_number: str

    class Config:
        from_attributes = True
        use_enum_values = True

# === ADMIN ===
class AdminRequest(UserRequest):
    pass

class AdminResponse(UserResponse):
    all_child: Optional[List[ChildResponse]] = None

    class Config:
        use_enum_values = True

# === AUTH ===
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)

    @validator("new_password")
    def password_must_contain_special(cls, v):
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("password must contain at least one special character")
        return v

# === PROFILE ===
class ProfileResponse(BaseModel):
    user: UserResponse
    child: Optional[ChildResponse] = None

    class Config:
        from_attributes = True
        use_enum_values = True

# === UPDATE ===
class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: Optional[str] = None

    class Config:
        extra = "ignore"
        use_enum_values = True

class ChildProfileUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    report_preferences: Optional[ReportTypeEnum] = None

    class Config:
        extra = "ignore"
        use_enum_values = True

# === EXPORT ===
UserSchema = type('UserSchema', (), {
    'UserRequest': UserRequest,
    'UserResponse': UserResponse,
    'ChildRequest': ChildRequest,
    'ChildResponse': ChildResponse,
    'AdminRequest': AdminRequest,
    'AdminResponse': AdminResponse,
    'ForgotPasswordRequest': ForgotPasswordRequest,
    'ResetPasswordRequest': ResetPasswordRequest,
    'ProfileResponse': ProfileResponse,
    'UserProfileUpdate': UserProfileUpdate,
    'ChildProfileUpdate': ChildProfileUpdate,
})
