from fastapi import FastAPI

from app.admin import setup_admin
from app.core.database import Base, engine
from app.modules.auth.presentation.routes import router as auth_router


AUTH_FLOW_DESCRIPTION = """
OTP authentication sample API.

Recommended flow in Swagger:

1. Call `POST /api/v1/auth/register`
2. Call `POST /api/v1/auth/request-otp`
3. Copy `demo_otp` from the response
4. Call `POST /api/v1/auth/login`
5. Copy `access_token`
6. Click **Authorize** in Swagger UI and enter `Bearer <access_token>`
7. Call `GET /api/v1/auth/me`
"""


openapi_tags = [
    {
        "name": "auth",
        "description": "Register users, request OTP, login with OTP, and access protected user APIs.",
    },
    {
        "name": "system",
        "description": "System endpoints used to verify application health.",
    },
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="FastAPI Auth Sample",
        version="1.0.0",
        description=AUTH_FLOW_DESCRIPTION,
        openapi_tags=openapi_tags,
        swagger_ui_parameters={"persistAuthorization": True},
    )

    Base.metadata.create_all(bind=engine)
    setup_admin(app)

    @app.get(
        "/health",
        tags=["system"],
        summary="Health check",
        description="Simple endpoint to confirm the FastAPI service is running.",
    )
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth_router)
    return app


app = create_app()
