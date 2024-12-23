from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from django_access_point.models.user import USER_TYPE_CHOICES, USER_STATUS_CHOICES

class Command(BaseCommand):
    help = "Creates Portal Super Admin User"

    def handle(self, *args, **options):
        name = "Admin"
        email = "admin@admin.com"
        password = "password"

        hashed_password = make_password(password)

        get_user_model().objects.create(
            name=name,
            email=email,
            password=hashed_password,
            user_type=USER_TYPE_CHOICES[0][0],
            status=USER_STATUS_CHOICES[1][0]
        )

        self.stdout.write(self.style.SUCCESS('Portal Super Admin User created successfully!'))
