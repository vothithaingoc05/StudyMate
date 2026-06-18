from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=100)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    avatar_url: str | None = None
    is_active: bool
    role: str = "Sinh viên"

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    message: str
    user: UserResponse


class RegisterResponse(BaseModel):
    message: str
    email: EmailStr


class VerifyEmailResponse(BaseModel):
    message: str
    verified: bool