from django_access_point.models.custom_field import CUSTOM_FIELD_RULES_FILE_FORMAT_ALLOWED


def get_text_box_field_validation_rule_schema():
    # Get Text Box field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "unique": false,
        "minlength": 2,
        "maxlength": 10
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "unique": {"type": "boolean"},
            "minlength": {"type": "integer", "minimum": 1},
            "maxlength": {"type": "integer", "minimum": 1},
        },
        "required": ["required", "unique", "minlength", "maxlength"],
        "additionalProperties": False
    }
    return schema


def get_website_url_field_validation_rule_schema():
    # Get Website URL field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "unique": false,
        "url": true - should be always true
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "unique": {"type": "boolean"},
            "url": {"type": "boolean"}
        },
        "required": ["required", "unique", "url"],
        "additionalProperties": False
    }
    return schema


def get_textarea_field_validation_rule_schema():
    # Get TextArea field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "minlength": 2,
        "maxlength": 10
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "minlength": {"type": "integer", "minimum": 1},
            "maxlength": {"type": "integer", "minimum": 1},
        },
        "required": ["required", "minlength", "maxlength"],
        "additionalProperties": False
    }
    return schema


def get_number_field_validation_rule_schema():
    # Get Number field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "unique": false,
        "min": 2,
        "max": 10,
        "number": true - should be always true
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "unique": {"type": "boolean"},
            "min": {"type": "integer", "minimum": 1},
            "max": {"type": "integer", "minimum": 1},
            "number": {"type": "boolean"},
            "decimal": {"type": "boolean"},
            "decimal_places": {"type": "integer", "minimum": 0},
        },
        "required": ["required", "unique", "min", "max", "number", "decimal", "decimal_places"],
        "additionalProperties": False
    }
    return schema


def get_phone_no_field_validation_rule_schema():
    # Get Phone no field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "unique": false,
        "minlength": 2,
        "maxlength": 10,
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "unique": {"type": "boolean"},
            "minlength": {"type": "integer", "minimum": 1},
            "maxlength": {"type": "integer", "minimum": 1}
        },
        "required": ["required", "unique", "minlength", "maxlength"],
        "additionalProperties": False
    }
    return schema


def get_dynamic_dropdown_field_validation_rule_schema():
    # Get Dynamic Dropdown field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "max_selection": 2
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "max_selection": {"type": "integer", "minimum": 1},
            "option_api_url": {"type": "string"},
        },
        "required": ["required", "max_selection"],
        "additionalProperties": False
    }
    return schema


def get_email_field_validation_rule_schema():
    # Get Email field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "unique": false,
        "email": true - should be always true
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "unique": {"type": "boolean"},
            "email": {"type": "boolean"},
        },
        "required": ["required", "unique", "email"],
        "additionalProperties": False
    }
    return schema


def get_dropdown_field_validation_rule_schema():
    # Get Dropdown field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "max_selection": 2
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "max_selection": {"type": "integer", "minimum": 1},
        },
        "required": ["required", "max_selection"],
        "additionalProperties": False
    }
    return schema


def get_radio_field_validation_rule_schema():
    # Get Radio field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "unique": false,
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "unique": {"type": "boolean"},
        },
        "required": ["required", "unique"],
        "additionalProperties": False
    }
    return schema


def get_date_field_validation_rule_schema():
    # Get Date field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "unique": false,
        "date": true, - should be always true
        "date_format": 'm-d-Y',
    }

    Allowed Date Format: refer 'CUSTOM_FIELD_RULES_DATE_FORMAT_ALLOWED' utils
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "unique": {"type": "boolean"},
            "date": {"type": "boolean"},
            "date_format": {"type": "string"},
        },
        "required": ["required", "unique", "date", "date_format"],
        "additionalProperties": False
    }
    return schema


def get_time_field_validation_rule_schema():
    # Get Time field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "unique": false,
        "time": true, - should be always true
        "time_format": '12'
    }

    Allowed Time Format: refer 'CUSTOM_FIELD_RULES_TIME_FORMAT_ALLOWED' utils
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "unique": {"type": "boolean"},
            "time": {"type": "boolean"},
            "time_format": {"type": "string"},
        },
        "required": ["required", "unique", "time", "time_format"],
        "additionalProperties": False
    }
    return schema


def get_short_textarea_field_validation_rule_schema():
    # Get Short TextArea field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "minlength": 2,
        "maxlength": 10
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "minlength": {"type": "integer", "minimum": 1},
            "maxlength": {"type": "integer", "minimum": 1},
        },
        "required": ["required", "minlength", "maxlength"],
        "additionalProperties": False
    }
    return schema


def get_file_field_validation_rule_schema():
    # Get File field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "file": true, - should be always true
        "file_max_size_mb": 2, - 2MB (value should be added in MB)
        "file_extensions_allowed": [],
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "file": {"type": "boolean"},
            "file_max_size_mb": {"type": "number", "minimum": 0, "multipleOf": 0.1},
            "file_extensions_allowed": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": CUSTOM_FIELD_RULES_FILE_FORMAT_ALLOWED
                }
            }
        },
        "required": ["required", "file", "file_max_size_mb", "file_extensions_allowed"],
        "additionalProperties": False
    }
    return schema


def get_multiselect_checkbox_field_validation_rule_schema():
    # Get MultiSelect Checkbox field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "max_selection": 2
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "max_selection": {"type": "integer", "minimum": 1},
        },
        "required": ["required", "max_selection"],
        "additionalProperties": False
    }
    return schema


def get_hidden_field_validation_rule_schema():
    # Get Hidden field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "unique": false,
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "unique": {"type": "boolean"},
        },
        "required": ["required", "unique"],
        "additionalProperties": False
    }
    return schema


def get_image_field_validation_rule_schema():
    # Get Image field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "image": true, - should be always true
        "file_max_size_mb": 2, - 2MB (value should be added in MB)
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
            "image": {"type": "boolean"},
            "file_max_size_mb": {"type": "number", "minimum": 0, "multipleOf": 0.1},
        },
        "required": ["required", "image", "file_max_size_mb"],
        "additionalProperties": False
    }
    return schema


def get_signature_field_validation_rule_schema():
    # Get Signature field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "minlength": 2,
        "maxlength": 10
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
        },
        "required": ["required"],
        "additionalProperties": False
    }
    return schema


def get_location_field_validation_rule_schema():
    # Get location field Validation Rules Schema
    """
    Sample Valid Schema:
    {
        "required": true,
        "minlength": 2,
        "maxlength": 10
    }
    """
    schema = {
        "type": "object",
        "properties": {
            "required": {"type": "boolean"},
        },
        "required": ["required"],
        "additionalProperties": False
    }
    return schema
