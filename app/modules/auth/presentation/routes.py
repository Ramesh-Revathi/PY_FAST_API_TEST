from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.auth.application.services import AuthService
from app.modules.auth.domain.schemas import LoginRequest, OTPRequest, OTPResponse, RegisterRequest, RegisterResponse, TokenResponse, UserResponse
from app.modules.auth.infrastructure.repositories import UserRepository


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    return user


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    description="Create a new user account using email or phone and a password.",
    responses={
        201: {"description": "User registered successfully."},
        400: {"description": "Email or phone is missing."},
        409: {"description": "Email or phone is already registered."},
    },
)
def register(
    payload: RegisterRequest = Body(
        ...,
        openapi_examples={
            "registerWithEmail": {
                "summary": "Register with email and phone",
                "value": {
                    "full_name": "Ramesh Kumar",
                    "email": "ramesh@example.com",
                    "phone": "+919999999999",
                    "password": "StrongPass@123",
                },
            }
        },
    ),
    service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    user = service.register_user(payload)
    return RegisterResponse(message="User registered successfully.", user=UserResponse.model_validate(user))


@router.post(
    "/request-otp",
    response_model=OTPResponse,
    summary="Request login OTP",
    description="Generate a one-time password for the user identified by email or phone.",
    responses={
        200: {"description": "OTP generated successfully."},
        404: {"description": "User not found."},
    },
)
def request_otp(
    payload: OTPRequest = Body(
        ...,
        openapi_examples={
            "requestOtpWithEmail": {
                "summary": "Request OTP using email",
                "value": {"identifier": "ramesh@example.com"},
            },
            "requestOtpWithPhone": {
                "summary": "Request OTP using phone",
                "value": {"identifier": "+919999999999"},
            },
        },
    ),
    service: AuthService = Depends(get_auth_service),
) -> OTPResponse:
    otp_value = service.request_login_otp(payload)
    return OTPResponse(
        message="OTP generated successfully.",
        expires_in_minutes=settings.otp_expire_minutes,
        demo_otp=otp_value if settings.expose_demo_otp else None,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with OTP",
    description="Validate the OTP and return a bearer token for protected APIs.",
    responses={
        200: {"description": "Login successful."},
        400: {"description": "Invalid OTP, expired OTP, or OTP not requested."},
        404: {"description": "User not found."},
    },
)
def login(
    payload: LoginRequest = Body(
        ...,
        openapi_examples={
            "loginWithOtp": {
                "summary": "Login using OTP",
                "value": {
                    "identifier": "ramesh@example.com",
                    "otp": "123456",
                },
            }
        },
    ),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    token, user = service.login_with_otp(payload)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Protected endpoint. Use the bearer token from the login API in Swagger Authorize.",
    responses={401: {"description": "Authentication required or token is invalid."}},
)
def me(current_user=Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
