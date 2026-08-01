from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone_number: str | None = Field(default=None, max_length=30)
    teacher_voice: Literal["female", "male"] = "female"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthUserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    teacher_voice: str
    role: str


class LoginResponse(TokenResponse):
    message: str = "Login successful"
    user: AuthUserResponse


class RegisterResponse(BaseModel):
    message: str = "User registered successfully"
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: AuthUserResponse


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone_number: str | None
    role: str
    teacher_voice: str
    created_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}
