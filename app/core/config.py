from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Auth Sample"
    database_url: str = "sqlite:///./app.db"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    otp_expire_minutes: int = 5
    expose_demo_otp: bool = True
    admin_username: str = "admin"
    admin_password: str = "admin123"
    admin_secret_key: str = "change-admin-session-secret"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
