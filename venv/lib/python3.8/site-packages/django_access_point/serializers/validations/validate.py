import re
from datetime import datetime
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from django_access_point.models.custom_field import CUSTOM_FIELD_TYPE, CUSTOM_FIELD_RULES_DATE_FORMAT_ALLOWED, \
    CUSTOM_FIELD_RULES_TIME_FORMAT_ALLOWED


def is_empty(value):
    """
    Check if value exists or not
    """
    return not bool(value)


def minlength(value, minlength, field_type):
    """
    Check if value is not less than the minimum characters set.
    Handles text, textarea, and phone numbers.
    """
    if field_type == CUSTOM_FIELD_TYPE[6][0]:
        value = ''.join(re.findall(r'\d+', value))

    return len(value) < minlength


def maxlength(value, maxlength, field_type):
    """
    Check if value is not greater than the maximum characters set.
    Handles text, textarea, and phone numbers.
    """
    # Handle phone numbers: strip non-numeric characters
    if field_type == CUSTOM_FIELD_TYPE[6][0]:
        value = ''.join(re.findall(r'\d+', value))

    return len(value) > maxlength


def is_url(value):
    """
    Check if value is a valid URL.
    """
    if value.startswith('www.'):
        value = 'http://' + value

    url_validator = URLValidator(schemes=['http', 'https'])

    try:
        url_validator(value)
        return False  # No error
    except ValidationError:
        return True  # Error if URL is invalid


def is_unique(value, field_key, field_type, submission_id=None):
    """
    Check if value doesn't exist already.
    """
    # Placeholder for uniqueness validation logic
    return False  # Assume no error for now


def is_number(value):
    """
    Check if value is a number.
    """
    return not value.isnumeric()


def min_value(value, min_value):
    """
    Check if value is greater or equal to the minimum value.
    """
    try:
        return float(value) < float(min_value)
    except ValueError:
        return True


def max_value(value, max_value):
    """
    Check if value is less than or equal to the maximum value.
    """
    try:
        return float(value) > float(max_value)
    except ValueError:
        return True


def is_email(value):
    """
    Check if value is a valid email.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return not re.match(pattern, value)


def is_date(value, date_format_allowed):
    """
    Check if value is valid date.
    """
    try:
        date_format = CUSTOM_FIELD_RULES_DATE_FORMAT_ALLOWED[date_format_allowed]
        datetime.strptime(value, date_format)
        return False  # No error
    except ValueError:
        return True  # Error if invalid date format


def min_max_selection(value, max_selection_allowed, validate_min, validate_max):
    """
    Check if length of the value matches the max selection allowed & has minimum 1 if the field is required.
    """
    value_length = len(value)

    if validate_min and value_length == 0:
        return 1  # Error: Minimum selection required
    elif validate_max and value_length > max_selection_allowed:
        return 2  # Error: Exceeds max selection allowed
    return 0  # No error


def is_file(field_key, req):
    """
    Check if value is a valid file.
    """
    uploaded_file = req.FILES.get(field_key)
    return uploaded_file is None  # True if no file uploaded


def file_extension(uploaded_file, file_extensions_allowed):
    """
    Check if file extension is allowed.
    """
    extension = uploaded_file.name.split('.')[-1].lower()

    # Handle case where "jpg" extension is used but should be "jpeg"
    if extension == "jpg":
        extension = "jpeg"

    return extension not in file_extensions_allowed


def file_size(uploaded_file, max_file_size_allowed):
    """
    Check if file size does not exceed the allowed file size limit.
    """
    max_upload_size = max_file_size_allowed * 1024 * 1024  # Convert MB to bytes
    return uploaded_file.size > max_upload_size


def is_time(value, time_format_allowed):
    """
    Check if value is valid time.
    """
    try:
        time_format = CUSTOM_FIELD_RULES_TIME_FORMAT_ALLOWED[time_format_allowed]
        datetime.strptime(value, time_format)
        return False  # No error
    except ValueError:
        return True  # Error if invalid time format
