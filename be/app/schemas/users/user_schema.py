
            
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.domain.enum import RoleEnum, ReportTypeEnum, GenderEnum

class UserSchema:
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
            use_enum_values = True

    class ChildRequest(UserRequest):
        age: int = Field(..., ge=3)  # Chỉ yêu cầu >= 3
        report_preferences: Optional[ReportTypeEnum] = None
        gender: GenderEnum
        date_of_birth: datetime  # Thống nhất tên với backend
        phone_number: str = Field(..., min_length=10, max_length=20)

        @validator("age")
        def age_must_be_valid(cls, v):
            if v < 3:
                raise ValueError("age must be greater 3")
            return v

        class Config:
            use_enum_values = True

    class ChildResponse(UserResponse):
        age: int
        progress: Optional[List[dict]] = None
        last_played: Optional[datetime] = None
        report_preferences: Optional[ReportTypeEnum] = None
        created_at: datetime = Field(default_factory=lambda: datetime(2025, 10, 25, 14, 45))
        last_login: Optional[datetime] = None
        gender: GenderEnum
        date_of_birth: datetime
        phone_number: str

        class Config:
            use_enum_values = True

    class AdminRequest(UserRequest):
        pass

    class AdminResponse(UserResponse):
        all_child: Optional[List["UserSchema.ChildResponse"]] = None

        class Config:
            use_enum_values = True
            use_enum_values = True

    class AdminRequest(UserRequest):
        pass

    class AdminResponse(UserResponse):
        all_child: Optional[List["UserSchema.ChildResponse"]] = None

        class Config:
            use_enum_values = True