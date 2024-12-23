import json
from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django_access_point.models.custom_field import CUSTOM_FIELD_TYPE, CUSTOM_FIELD_RULES
from django_access_point.serializers.validations import validate


class CrudSerializer(serializers.ModelSerializer):
    """
    Base serializer class for CRUD operations.
    """

    class Meta:
        model = None  # This should be defined in the child class
        fields = None  # This should be defined in the child class
        custom_field_model = None  # This should be defined in the child class
        custom_field_value_model = None  # This should be defined in the child class

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

    def validate(self, data):
        # Access the context here, after the serializer is initialized
        self.custom_field_model = self.context.get("custom_field_model", None)
        self.custom_field_value_model = self.context.get("custom_field_value_model", None)

        if self.custom_field_model:
            custom_fields_data = {}
            custom_field_errors = {}

            for key, value in self.initial_data.items():
                if key.startswith("custom_field_"):
                    # Extract the custom field ID from the key (assuming format is custom_field_<id>)
                    custom_field_id = key.split("_")[2]  # Example: custom_field_1, custom_field_2
                    custom_fields_data[custom_field_id] = {"field_type": "", "value": value}

            _req_custom_fields_id = list(custom_fields_data.keys()) # custom fields received from request
            _req_active_custom_fields_id = list() # active custom fields configured

            active_custom_fields = self.context.get("custom_field_queryset", None)

            for custom_field in active_custom_fields:
                _custom_field_id = str(custom_field.id)
                _req_active_custom_fields_id.append(_custom_field_id)
                if _custom_field_id not in _req_custom_fields_id:
                    custom_field_errors["custom_field_" + _custom_field_id] = "This field is required."
                else:
                    custom_field_label = custom_field.label
                    custom_field_type = custom_field.field_type
                    custom_field_validation_rule = custom_field.validation_rule
                    custom_field_value = custom_fields_data[_custom_field_id].get("value", "")

                    custom_fields_data[_custom_field_id]["field_type"] = custom_field_type

                    field_error = self.validate_custom_field_data(
                        _custom_field_id,
                        custom_field_label,
                        custom_field_type,
                        custom_field_validation_rule,
                        custom_field_value,
                    )

                    if field_error and len(field_error) != 0:
                        custom_field_errors.update(field_error)

            # If there are fields on the request which are not mapped to custom field, raise validation errors
            invalid_custom_fields = [item for item in _req_custom_fields_id if item not in _req_active_custom_fields_id]
            if len(invalid_custom_fields) > 0:
                raise ValidationError("Remove fields from the request that are not mapped to a custom field.")

            # If there are any custom field validation errors, raise validation errors
            if custom_field_errors:
                raise ValidationError(custom_field_errors)

            # Add custom fields data to the validated data if there are no errors
            data["custom_fields"] = custom_fields_data

        return data

    def validate_custom_field_data(
        self, field_id, field_label, field_type, field_validation_rule, field_value
    ):
        validation_errors = {}

        # If field has validation 'required'
        if CUSTOM_FIELD_RULES[0][0] in field_validation_rule and field_validation_rule["required"]:
            error = validate.is_empty(field_value)
            if error:
                validation_errors["custom_field_" + field_id] = f"{field_label} may not be blank."
                return validation_errors

        # If field has validation 'minlength'
        if CUSTOM_FIELD_RULES[1][0] in field_validation_rule and field_value:
            minlength = field_validation_rule["minlength"]
            error = validate.minlength(field_value, minlength, field_type)
            if error:
                validation_errors["custom_field_" + field_id] = f"{field_label} must contain at least {minlength} characters."
                return validation_errors

        # If field has validation 'maxlength'
        if CUSTOM_FIELD_RULES[2][0] in field_validation_rule and field_value:
            maxlength = field_validation_rule["maxlength"]
            error = validate.maxlength(field_value, maxlength, field_type)
            if error:
                validation_errors["custom_field_" + field_id] = f"{field_label} should not be greater than {maxlength} characters."
                return validation_errors

        # If field has validation 'min' - for 'number' field
        if CUSTOM_FIELD_RULES[3][0] in field_validation_rule and field_value:
            min_value = field_validation_rule["min"]
            error = validate.min_value(field_value, min_value)
            if error:
                validation_errors["custom_field_" + field_id] = f"{field_label} should be equal or greater than {min_value}."
                return validation_errors

        # If field has validation 'max' - for 'number' field
        if CUSTOM_FIELD_RULES[4][0] in field_validation_rule and field_value:
            max_value = field_validation_rule["max"]
            error = validate.max_value(field_value, max_value)
            if error:
                validation_errors["custom_field_" + field_id] = f"{field_label} should be equal or less than {max_value}."
                return validation_errors

        # If field has validation 'email'
        if CUSTOM_FIELD_RULES[5][0] in field_validation_rule and field_value and field_validation_rule["email"]:
            error = validate.is_email(field_value)
            if error:
                validation_errors["custom_field_" + field_id] = f"{field_label} is invalid."
                return validation_errors

        # If field has validation 'url'
        if CUSTOM_FIELD_RULES[6][0] in field_validation_rule and field_value and field_validation_rule["url"]:
            error = validate.is_url(field_value)
            if error:
                validation_errors["custom_field_" + field_id] = f"{field_label} is invalid."
                return validation_errors

        # If field has validation 'unique'
        if CUSTOM_FIELD_RULES[6][0] in field_validation_rule and field_value and field_validation_rule["unique"]:
            error = validate.is_unique(field_value)
            if error:
                validation_errors["custom_field_" + field_id] = f"{field_label} already exists."
                return validation_errors

        return validation_errors

    def create(self, validated_data):
        # Extract custom fields data from validated data
        custom_fields_data = validated_data.pop("custom_fields", {})

        instance = self.Meta.model.objects.create(**validated_data)

        # Save custom fields (if applicable)
        self.create_custom_field_data(instance, custom_fields_data)

        return instance

    def create_custom_field_data(self, instance, custom_fields_data):
        custom_fields = []

        for field_id, field_data in custom_fields_data.items():
            custom_field_entry = dict(submission=instance, custom_field_id=field_id)

            if field_data["field_type"] == CUSTOM_FIELD_TYPE[6][0]: #dropdown
                custom_field_entry["dropdown_field"] = json.dumps(field_data["value"])
            elif field_data["field_type"] == CUSTOM_FIELD_TYPE[7][0]: #radio
                custom_field_entry["radio_field"] = field_data["value"]
            elif field_data["field_type"] == CUSTOM_FIELD_TYPE[11][0]: #multiselect_checkbox
                custom_field_entry["multiselect_checkbox_field"] = json.dumps(field_data["value"])
            else:
                custom_field_entry["text_field"] = field_data["value"]

            custom_fields.append(custom_field_entry)

        if custom_fields:
            self.custom_field_value_model.objects.bulk_create(
                [self.custom_field_value_model(**data) for data in custom_fields]
            )
