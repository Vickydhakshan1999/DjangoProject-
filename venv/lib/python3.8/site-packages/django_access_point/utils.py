import base64
import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from datetime import timedelta

try:
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    from django.db.models.loading import get_model

def get_tenant_model():
    """Returns the tenant model."""
    return get_model(settings.TENANT_MODEL)

def generate_user_token_with_expiry(user, expiry_duration_hours=24):
    """
    Generate a token for the user that includes an expiry time encoded in it.
    """
    # Generate the default token for the user
    token = default_token_generator.make_token(user)

    # Encode the user ID using base64 for safe URL inclusion
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    # Set expiry time (e.g., 24 hours from now)
    expiry_time = (timezone.now() + timedelta(hours=expiry_duration_hours)).timestamp()

    # Combine the user ID and expiry time into a payload
    payload = {
        'uidb64': uidb64,
        'token': token,
        'expiry_time': expiry_time
    }

    # Serialize the payload and base64 encode it to create a secure token
    token_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

    return token_payload

def validate_invite_token(token_payload):
    """
    Validates the invite token.
    """
    try:
        # Decode the token_payload from the URL
        decoded_payload = base64.urlsafe_b64decode(token_payload).decode()
        payload = json.loads(decoded_payload)

        # Extract values from the payload
        uidb64 = payload.get('uidb64')
        token = payload.get('token')
        expiry_time = payload.get('expiry_time')

        if not uidb64 or not token or not expiry_time:
            return False, None, "Invalid token data."

        # Decode the user ID from the URL
        uid = force_str(urlsafe_base64_decode(uidb64))

        # Retrieve the user based on the decoded ID
        user = get_user_model().objects.get(pk=uid)

        # Check if the token is valid
        if not default_token_generator.check_token(user, token):
            return False, None, "Invalid invitation link."

        # Check if the token has expired by comparing with the expiry time
        if timezone.now().timestamp() > expiry_time:
            return False, None, "Invitation link has expired."

        return True, user, ""

    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist, KeyError, json.JSONDecodeError) as e:
        # Log the exception for debugging purposes, or handle it accordingly
        return False, None, "Invalid or expired invitation link. Error: {}".format(str(e))
