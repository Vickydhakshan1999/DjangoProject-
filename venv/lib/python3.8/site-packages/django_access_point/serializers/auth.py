from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from django_access_point.models.user import USER_TYPE_CHOICES, USER_STATUS_CHOICES
from django_access_point.utils import get_tenant_model

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Authenticate the user
        user = authenticate(email=email, password=password)

        attrs["user"] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        You can optionally add logic here to validate email existence.
        This avoids disclosing whether the email exists in the system.
        """
        return value


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value


class UserOnboardSerializer(serializers.Serializer):
    tenant_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def validate_email(self, value):
        user_model = get_user_model()
        if user_model.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        tenant_name = validated_data.get("tenant_name")
        email = validated_data.get("email")
        password = validated_data.get("password")

        # Hash the password before saving
        hashed_password = make_password(password)

        # Create the user first
        user = get_user_model().objects.create(
            email=email,
            password=hashed_password,
            user_type=USER_TYPE_CHOICES[1][0],
            status=USER_STATUS_CHOICES[1][0]
        )

        # Create the tenant and assign the user as the owner
        tenant = get_tenant_model().objects.create(
            name=tenant_name,
            owner=user
        )

        user.tenant = tenant
        user.save()

        return user
