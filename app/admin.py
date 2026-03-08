from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.config import settings
from app.core.database import engine
from app.modules.auth.infrastructure.models import OTPCode, User


class AdminAuth(AuthenticationBackend):
    def __init__(self) -> None:
        super().__init__(secret_key=settings.admin_secret_key)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if username == settings.admin_username and password == settings.admin_password:
            request.session.update({"admin_authenticated": True})
            return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("admin_authenticated"))


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"
    column_list = [User.id, User.full_name, User.email, User.phone, User.is_active, User.created_at]
    column_searchable_list = [User.full_name, User.email, User.phone]
    column_sortable_list = [User.id, User.full_name, User.created_at]
    form_excluded_columns = [User.password_hash, User.otp_codes]
    can_create = False


class OTPCodeAdmin(ModelView, model=OTPCode):
    name = "OTP Code"
    name_plural = "OTP Codes"
    icon = "fa-solid fa-key"
    column_list = [OTPCode.id, OTPCode.user_id, OTPCode.purpose, OTPCode.is_used, OTPCode.expires_at, OTPCode.created_at]
    column_searchable_list = [OTPCode.purpose]
    column_sortable_list = [OTPCode.id, OTPCode.user_id, OTPCode.expires_at, OTPCode.created_at]
    can_create = False


def setup_admin(app) -> Admin:
    admin = Admin(app=app, engine=engine, authentication_backend=AdminAuth(), title="App DB Admin")
    admin.add_view(UserAdmin)
    admin.add_view(OTPCodeAdmin)
    return admin