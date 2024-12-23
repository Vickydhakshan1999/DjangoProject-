from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django_access_point.models.user import USER_STATUS_CHOICES
from django_access_point.utils import generate_user_token_with_expiry, validate_invite_token
from django_access_point.utils_response import success_response, error_response, validation_error_response

class UserProfileMixin:
    """
    Mixin to handle common profile setup and invitation email logic for both PlatformUser and TenantUser.
    """

    def complete_profile_setup(self, request, token_payload, *args, **kwargs):
        """
        Complete Profile Setup with a token that includes expiry time.
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
        elif user.status != USER_STATUS_CHOICES[3][0]:
            return error_response("Invitation link has expired.")

        user.status = USER_STATUS_CHOICES[1][0]
        user.set_password(password)
        user.save()

        return success_response("Profile setup completed successfully.")

    def send_invite_user_email(self, user, frontend_url):
        """
        Send the invitation email to the user with a unique token and expiry time encoded.
        """
        name = user.name
        email = user.email

        # Generate the token and encoded user ID with expiry time
        token_payload = generate_user_token_with_expiry(user, 1)

        # Build the invite URL with the token_payload (no expiry time in the URL)
        invite_url = f"{frontend_url}/profile-setup/{token_payload}"

        # Prepare the email context
        context = {
            "user_name": name,
            "invite_url": invite_url,
            "support_email": settings.PLATFORM_SUPPORT_EMAIL,
            "platform_name": settings.PLATFORM_NAME,
            "logo_url": settings.PLATFORM_LOGO_URL,
        }

        # Render the email content (HTML)
        subject = "Invitation to Complete Your Profile"
        message = render_to_string("profile_invite_email.html", context)

        # Send the email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=message,  # Ensure HTML is sent
        )

        return success_response("Invitation email sent.")
