from django.db import models

from django_access_point.models.user import TenantBase, UserBase
from django_access_point.models.custom_field import CustomFieldBase, CustomFieldOptionsBase, CustomFieldValueBase


class Tenant(TenantBase):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200, blank=True)

class User(UserBase):
    phone_no = models.CharField(max_length=100)

class UserCustomField(CustomFieldBase):
    pass

class UserCustomFieldOptions(CustomFieldOptionsBase):
    custom_field = models.ForeignKey(UserCustomField, on_delete=models.CASCADE)


class UserCustomFieldValue(CustomFieldValueBase):
    submission = models.ForeignKey(User, related_name="custom_field_values", on_delete=models.CASCADE)
    custom_field = models.ForeignKey(UserCustomField, on_delete=models.CASCADE)
