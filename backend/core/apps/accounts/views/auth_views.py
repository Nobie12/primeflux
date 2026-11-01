from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from core.apps.accounts.models import User
from core.apps.accounts.serializers.auth import (
    RegisterSerializer,
    SendEmailOTPSerializer,
    SendOTPSerializer,
    TokenObtainPairSerializer,
    VerifyEmailOTPSerializer,
    VerifyOTPSerializer,
)
from core.core_functions.services.otp import OTPService


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "user created successfully. You can now login"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """
    No post method needed!
    SimpleJWT handles the validation and token response.
    """

    serializer_class = TokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)

            token.blacklist()

            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

        except KeyError:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SendOTPView(APIView):
    """Endpoint to trigger SMS OTP to the user's phone."""

    def post(self, request, *args, **kwargs):
        serializer = SendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data["phone"]
        success, message = OTPService.send_otp(phone)

        if not success:
            return Response({"detail": message}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        return Response({"detail": message}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """Endpoint to verify the 6-digit code and mark user as verified."""

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data["phone"]
        otp = serializer.validated_data["otp"]

        success, message = OTPService.verify_otp(phone, otp)
        if not success:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)

        # IMPORTANT: Mark the user as verified in the DB
        User.objects.filter(phone=phone).update(is_phone_verified=True)

        return Response({"detail": message}, status=status.HTTP_200_OK)


class SendEmailOTPView(APIView):
    """Endpoint to snd  OTP to a specific email."""

    def post(self, request, *args, **kwargs):
        serializer = SendEmailOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_404_BAD_REQUEST)

        email = serializer.validated_data["email"]

        success, message = OTPService.send_email_otp(email)

        if not success:
            return Response({"detail": message}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        return Response({"detail": message}, status=status.HTTP_200_OK)


class VerifyEmailOTPView(APIView):
    """Endpoint to verify the 6-digit code and mark user as verified."""

    def post(self, request, *args, **kwargs):
        serializer = VerifyEmailOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_404_BAD_REQUEST)

        otp = serializer.validated_data["otp"]
        email = serializer.validated_data["email"]

        success, message = OTPService.verify_email_otp(email, otp)

        if not success:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.filter(email=email).update(is_email_verified=True)
        return Response({"detail": message}, status=status.HTTP_200_OK)
