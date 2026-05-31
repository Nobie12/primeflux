from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    RegisterView,
    SendEmailOTPView,
    SendOTPView,
    VerifyEmailOTPView,
    VerifyOTPView,
)

urlpatterns = [
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("otp/phone/send/", SendOTPView.as_view(), name="send_otp"),
    path("otp/phone/verify/", VerifyOTPView.as_view(), name="verify_otp"),
    path("otp/email/send/", SendEmailOTPView.as_view(), name="send_email_otp"),
    path("otp/email/verify/", VerifyEmailOTPView.as_view(), name="verify_email_otp"),
]
