from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers

from django_access_point.models.custom_field import CUSTOM_FIELD_TYPE


class CustomFieldSerializer(serializers.ModelSerializer):
    """
    Base serializer class for Custom Field.
    Child classes must define `model` and `fields`.
    """

    class Meta:
        model = None  # Should be defined in the child class
        fields = [
            "id",
            "label",
            "slug",
            "field_type",
            "field_size",
            "placeholder",
            "field_order",
            "custom_class_name",
            "validation_rule",
            "is_unique",
            "content",
            "content_size",
            "content_alignment",
            "show_on_table",
        ]

    def __init__(self, *args, **kwargs):
        # Ensure that the 'model' and 'fields' are set in the child class Meta
        if not hasattr(self.Meta, "model"):
            raise ImproperlyConfigured(
                "Django Access Point: The 'model' attribute must be defined in the child class Meta."
            )
        if not hasattr(self.Meta, "fields"):
            raise ImproperlyConfigured(
                "Django Access Point: The 'fields' attribute must be defined in the child class Meta."
            )

        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if (
            instance.field_type == CUSTOM_FIELD_TYPE[13][0]
            or instance.field_type == CUSTOM_FIELD_TYPE[14][0]
        ):
            # for Heading & Paragraph fields
            representation.pop("validation_rule", None)
            representation.pop("is_unique", None)
            representation.pop("show_on_table", None)
        else:
            representation.pop("content", None)
            representation.pop("content_size", None)
            representation.pop("content_alignment", None)
            representation.pop("show_on_table", None)

        return representation
