from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from core.apps.accounts.views import health_check_views

from .views.auth_views import (
    LoginView,
    LogoutView,
    RegisterView,
    SendEmailOTPView,
    SendOTPView,
    VerifyEmailOTPView,
    VerifyOTPView,
)
from .views.profile import UserView

urlpatterns = [
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/otp/phone/send/", SendOTPView.as_view(), name="send_otp"),
    path("auth/otp/phone/verify/", VerifyOTPView.as_view(), name="verify_otp"),
    path("auth/otp/email/send/", SendEmailOTPView.as_view(), name="send_email_otp"),
    path("auth/otp/email/verify/", VerifyEmailOTPView.as_view(), name="verify_email_otp"),
    path("profile/", UserView.as_view(), name="profile"),
    path("health/", health_check_views.health_check, name="health_check"),
]
