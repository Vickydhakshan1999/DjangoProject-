import threading
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from django_access_point.models.custom_field import CUSTOM_FIELD_STATUS
from django_access_point.models.user import USER_TYPE_CHOICES, USER_STATUS_CHOICES
from django_access_point.mixins.user import UserProfileMixin
from django_access_point.views.custom_field import CustomFieldViewSet
from django_access_point.views.crud import CrudViewSet
from django_access_point.views.helpers_crud import (custom_field_values_related_name, _get_custom_field_queryset,
                                                     _prefetch_custom_field_values, _format_custom_field_submitted_values)
from django_access_point.excel_report import ExcelReportGenerator

from .models import UserCustomField, UserCustomFieldOptions, UserCustomFieldValue
from .serializers import UserSerializer, UserCustomFieldSerializer


class PlatformUser(CrudViewSet, UserProfileMixin):
    queryset = get_user_model().objects.filter(user_type=USER_TYPE_CHOICES[0][0]).exclude(
        status=USER_STATUS_CHOICES[0][0])
    list_fields = {"id": "ID", "status": "Status", "name": "Name", "email": "Email Address", "phone_no": "Phone No"}
    detail_fields = {"status": "Status", "name": "Name", "email": "Email Address", "phone_no": "Phone No"}
    list_search_fields = ["name", "email", "phone_no"]
    serializer_class = UserSerializer
    custom_field_model = UserCustomField
    custom_field_value_model = UserCustomFieldValue
    custom_field_options_model = UserCustomFieldOptions

    def after_save(self, request, instance):
        """
        Handle after save.
        """
        # After user saved, invite user to setup profile
        frontend_url = settings.FRONTEND_PORTAL_URL

        # Create a new thread to send the email asynchronously
        email_thread = threading.Thread(target=self.send_invite_user_email, args=(instance, frontend_url))
        email_thread.start()

    @action(detail=False, methods=['post'], url_path='complete-profile-setup/(?P<token_payload>.+)',
            permission_classes=[AllowAny])
    def complete_profile_setup_action(self, request, token_payload, *args, **kwargs):
        return self.complete_profile_setup(request, token_payload, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='generate-user-report')
    def generate_user_report(self, request, *args, **kwargs):
        """
        Generate User Report.
        """
        # Queryset to fetch active platform users
        users_queryset = self.queryset.order_by("-created_at")
        # Get User Custom Fields
        active_custom_fields = _get_custom_field_queryset(self.custom_field_model)

        # PreFetch User Custom Field Values
        users_queryset = _prefetch_custom_field_values(
            users_queryset, active_custom_fields, self.custom_field_value_model
        )

        def get_headers():
            headers = ["Name", "Email Address"]

            # Custom Field Headers
            for field in active_custom_fields:
                headers.append(field.label)

            return headers

        # Define row data for each user, including custom fields
        def get_row_data(user):
            row = [user.name, user.email]

            # Custom Field Values
            if active_custom_fields:
                if hasattr(user, custom_field_values_related_name):
                    custom_field_submitted_values = getattr(user, custom_field_values_related_name).all()
                    formatted_custom_field_submitted_values = _format_custom_field_submitted_values(
                        custom_field_submitted_values,
                        self.custom_field_options_model
                    )

                    # Append each custom field value to the row
                    for field in active_custom_fields:
                        row.append(formatted_custom_field_submitted_values.get(field.id, ""))

            return row

        # Create Excel report generator instance
        report_generator = ExcelReportGenerator(
            title="Platform User Report",
            queryset=users_queryset,
            get_headers=get_headers,
            get_row_data=get_row_data
        )

        # Generate and return the report as an HTTP response
        return report_generator.generate_report()


class PlatformUserCustomField(CustomFieldViewSet):
    queryset = UserCustomField.objects.filter(status=CUSTOM_FIELD_STATUS[1][0]).order_by("field_order")
    serializer_class = UserCustomFieldSerializer
    custom_field_options_model = UserCustomFieldOptions


class TenantUser(CrudViewSet, UserProfileMixin):
    queryset = get_user_model().objects.filter(user_type=USER_TYPE_CHOICES[1][0]).exclude(
        status=USER_STATUS_CHOICES[0][0])
    list_fields = {"id": "ID", "status": "Status", "name": "Name", "email": "Email Address", "phone_no": "Phone No"}
    detail_fields = {"status": "Status", "name": "Name", "email": "Email Address", "phone_no": "Phone No"}
    list_search_fields = ["name", "email", "phone_no"]
    serializer_class = UserSerializer
    custom_field_model = UserCustomField
    custom_field_value_model = UserCustomFieldValue
    custom_field_options_model = UserCustomFieldOptions

    def after_save(self, request, instance):
        """
        Handle after save.
        """
        # After user saved, invite user to setup profile
        frontend_url = settings.FRONTEND_TENANT_URL

        # Create a new thread to send the email asynchronously
        email_thread = threading.Thread(target=self.send_invite_user_email, args=(instance, frontend_url))
        email_thread.start()

    @action(detail=False, methods=['post'], url_path='complete-profile-setup/(?P<token_payload>.+)',
            permission_classes=[AllowAny])
    def complete_profile_setup_action(self, request, token_payload, *args, **kwargs):
        return self.complete_profile_setup(request, token_payload, *args, **kwargs)


class TenantUserCustomField(CustomFieldViewSet):
    queryset = UserCustomField.objects.filter(status=CUSTOM_FIELD_STATUS[1][0]).order_by("field_order")
    serializer_class = UserCustomFieldSerializer
    custom_field_options_model = UserCustomFieldOptions