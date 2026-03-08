from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, generate_otp, hash_otp, hash_password, verify_otp
from app.modules.auth.domain.schemas import LoginRequest, OTPRequest, RegisterRequest
from app.modules.auth.infrastructure.models import User
from app.modules.auth.infrastructure.repositories import OTPRepository, UserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.otp_repository = OTPRepository(db)

    def register_user(self, payload: RegisterRequest) -> User:
        if not payload.email and not payload.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either email or phone is required.",
            )

        if payload.email and self.user_repository.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

        if payload.phone and self.user_repository.get_by_phone(payload.phone):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already registered.")

        return self.user_repository.create(
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            password_hash=hash_password(payload.password),
        )

    def request_login_otp(self, payload: OTPRequest) -> str:
        user = self.user_repository.get_by_identifier(payload.identifier)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        otp_value = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=settings.otp_expire_minutes)

        self.otp_repository.invalidate_active_codes(user.id, purpose="login")
        self.otp_repository.create(
            user_id=user.id,
            purpose="login",
            code_hash=hash_otp(otp_value),
            expires_at=expires_at,
        )

        return otp_value

    def login_with_otp(self, payload: LoginRequest) -> tuple[str, User]:
        user = self.user_repository.get_by_identifier(payload.identifier)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        otp_record = self.otp_repository.get_latest_active_code(user.id, purpose="login")
        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active OTP found. Please request a new OTP.",
            )

        if otp_record.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired.")

        if not verify_otp(payload.otp, otp_record.code_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP.")

        self.otp_repository.mark_as_used(otp_record)
        access_token = create_access_token(str(user.id))
        return access_token, user
