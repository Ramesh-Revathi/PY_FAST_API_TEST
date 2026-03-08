from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.infrastructure.models import OTPCode, User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, full_name: str, email: Optional[str], phone: Optional[str], password_hash: str) -> User:
        user = User(full_name=full_name, email=email, phone=phone, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.db.scalar(statement)

    def get_by_phone(self, phone: str) -> Optional[User]:
        statement = select(User).where(User.phone == phone)
        return self.db.scalar(statement)

    def get_by_id(self, user_id: int) -> Optional[User]:
        statement = select(User).where(User.id == user_id)
        return self.db.scalar(statement)

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        normalized_identifier = identifier.strip()
        return self.get_by_email(normalized_identifier) or self.get_by_phone(normalized_identifier)


class OTPRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, user_id: int, purpose: str, code_hash: str, expires_at) -> OTPCode:
        otp_code = OTPCode(user_id=user_id, purpose=purpose, code_hash=code_hash, expires_at=expires_at)
        self.db.add(otp_code)
        self.db.commit()
        self.db.refresh(otp_code)
        return otp_code

    def invalidate_active_codes(self, user_id: int, purpose: str) -> None:
        statement = select(OTPCode).where(
            OTPCode.user_id == user_id,
            OTPCode.purpose == purpose,
            OTPCode.is_used.is_(False),
        )
        active_codes = self.db.scalars(statement).all()
        for code in active_codes:
            code.is_used = True
        self.db.commit()

    def get_latest_active_code(self, user_id: int, purpose: str) -> Optional[OTPCode]:
        statement = (
            select(OTPCode)
            .where(
                OTPCode.user_id == user_id,
                OTPCode.purpose == purpose,
                OTPCode.is_used.is_(False),
            )
            .order_by(OTPCode.created_at.desc())
        )
        return self.db.scalar(statement)

    def mark_as_used(self, otp_code: OTPCode) -> None:
        otp_code.is_used = True
        self.db.add(otp_code)
        self.db.commit()
