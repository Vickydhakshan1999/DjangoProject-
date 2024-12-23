import threading
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from django_access_point.models.user import TENANT_STATUS_CHOICES, USER_STATUS_CHOICES, USER_TYPE_CHOICES
from django_access_point.serializers.auth import (
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UserOnboardSerializer,
)
from django_access_point.utils_response import (
    success_response,
    validation_error_response,
    error_response,
    notfound_response,
)
from django_access_point.utils import generate_user_token_with_expiry, validate_invite_token


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            if user is None:
                return error_response("Invalid credentials.")
            elif not user.is_user_active():
                return error_response("You don't have access to the application. Please contact admin.")
            elif hasattr(user, "tenant") and user.tenant:
                tenant = user.tenant
                if tenant.status != TENANT_STATUS_CHOICES[1][0]:
                    return error_response("You don't have access to the application. Please contact admin.")

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Send tokens as response
            return success_response(
                {"refresh_token": str(refresh), "access_token": str(access_token)}
            )

        return validation_error_response(serializer.errors)


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            # Fetch the user
            try:
                user = get_user_model().objects.filter(status=USER_STATUS_CHOICES[1][0]).get(email=email)
            except get_user_model().DoesNotExist:
                return error_response("You don't have access to the application.")

            # Generate the token and encoded user ID with expiry time
            token_payload = generate_user_token_with_expiry(user, 1)

            # Build the reset URL with the token_payload (no expiry time in the URL)
            if user.user_type == USER_TYPE_CHOICES[0][0]: # Admin User
                frontend_url = settings.FRONTEND_PORTAL_URL
            else: # Tenant User
                frontend_url = settings.FRONTEND_TENANT_URL

            reset_url = f"{frontend_url}/reset-password/{token_payload}"

            email_thread = threading.Thread(target=self.send_reset_email, args=(user, reset_url, email))
            email_thread.start()

            return success_response("Password reset email sent.")

        return validation_error_response(serializer.errors)

    def send_reset_email(self, user, reset_url, email):
        subject = "Reset Your Password"
        context = {
            "user": user,
            "reset_url": reset_url,
            "support_email": settings.PLATFORM_SUPPORT_EMAIL,
            "platform_name": settings.PLATFORM_NAME,
            "logo_url": settings.PLATFORM_LOGO_URL,
        }

        message = render_to_string("password_reset_email.html", context)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=message,  # Ensure HTML is sent
        )


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, token_payload, *args, **kwargs):
        """
        Reset Password
        """
        # Validate the invite token
        is_valid, user, message = validate_invite_token(token_payload)

        if not is_valid:
            return error_response(message)

        password = request.data.get('password')
        if not password:
            return validation_error_response({"password": ["This field is required."]})
        elif len(password) < 8:
            return validation_error_response({"password": ["Password must be at least 8 characters long."]})
        elif user.status != USER_STATUS_CHOICES[1][0]:
            return error_response("Invitation link has expired.")

        user.set_password(password)
        user.save()

        return success_response("Your password has been reset successfully. You can now log in with your new password. ")


class UserOnboardView(generics.GenericAPIView):
    serializer_class = UserOnboardSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            return success_response(
                {"user": {"email": user.email, "tenant": user.tenant.name}}
            )

        return validation_error_response(serializer.errors)
