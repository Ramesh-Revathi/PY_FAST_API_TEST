from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, examples=["Ramesh Kumar"])
    email: Optional[EmailStr] = Field(default=None, examples=["ramesh@example.com"])
    phone: Optional[str] = Field(default=None, min_length=10, max_length=20, examples=["+919999999999"])
    password: str = Field(..., min_length=8, max_length=128, examples=["StrongPass@123"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Ramesh Kumar",
                "email": "ramesh@example.com",
                "phone": "+919999999999",
                "password": "StrongPass@123",
            }
        }
    )

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.strip()


class OTPRequest(BaseModel):
    identifier: str = Field(..., min_length=3, max_length=120)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identifier": "ramesh@example.com",
            }
        }
    )


class LoginRequest(BaseModel):
    identifier: str = Field(..., min_length=3, max_length=120)
    otp: str = Field(..., min_length=4, max_length=10)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identifier": "ramesh@example.com",
                "otp": "123456",
            }
        }
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: Optional[EmailStr]
    phone: Optional[str]
    is_active: bool
    created_at: datetime


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse


class OTPResponse(BaseModel):
    message: str
    expires_in_minutes: int
    demo_otp: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
