from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django_access_point.models.custom_field import CUSTOM_FIELD_TYPE, CUSTOM_FIELD_OPTIONS_STATUS
from django_access_point.utils_response import (
    success_response,
    validation_error_response,
    error_response,
    notfound_response,
    created_response,
    deleted_response,
)
from django_access_point.models.custom_field import CUSTOM_FIELD_STATUS


class CustomFieldViewSet(viewsets.GenericViewSet):
    """
    Base view class for Custom Field CRUD operations.
    Child classes must define `queryset` and `serializer_class`.
    """

    queryset = None  # Should be defined in the child class
    serializer_class = None  # Should be defined in the child class
    custom_field_options_model = None  # Should be defined in the child class

    def list(self, request, *args, **kwargs):
        """
        List all objects in the queryset.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        response_data = {"data": serializer.data}

        return success_response(response_data)

    def create(self, request, *args, **kwargs):
        """
        Create a new object.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return created_response(serializer.data)

        return validation_error_response(serializer.errors)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Retrieve a single object by primary key.
        """
        queryset = self.get_queryset()
        custom_field = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(custom_field)

        return Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Update an existing object by primary key.
        """
        queryset = self.get_queryset()
        custom_field = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(custom_field, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        Soft Delete an object by primary key.
        """
        try:
            custom_field = self.queryset.get(pk=pk)
        except ObjectDoesNotExist:
            return notfound_response("Custom Field not found.")

        custom_field.status = CUSTOM_FIELD_STATUS[0][0]
        custom_field.save()

        return deleted_response("Field deleted successfully.")

    @action(detail=False, methods=["post"], url_path="reorder-fields")
    def reorder_fields(self, request, *args, **kwargs):
        """
        Reorder fields based on the provided dictionary (id -> position).
        The dictionary provided should have field IDs as keys and their new positions as values.

        How it works: If u move field to position 3, all the fields after
        position 3 (i.e., fields with positions 3, 4, and 5) shift one position down.
        """
        new_order = request.data

        # Ensure the request body is a dictionary
        if not isinstance(new_order, dict):
            return error_response("Request body must be a dictionary with field_id as key and position as value.",
                                  status.HTTP_400_BAD_REQUEST)

        # Validate that the positions provided are positive integers
        if any(not isinstance(pos, int) or pos <= 0 for pos in new_order.values()):
            return error_response("Positions must be positive integers.", status.HTTP_400_BAD_REQUEST)

        # Fetch active fields
        active_fields = self.queryset
        active_fields_dict = {field.id: field for field in active_fields}

        # Ensure all provided field IDs are valid active field IDs
        invalid_ids = [field_id for field_id in new_order.keys() if int(field_id) not in active_fields_dict]
        if invalid_ids:
            return error_response(f"Invalid field IDs provided: {', '.join(map(str, invalid_ids))}",
                                  status.HTTP_400_BAD_REQUEST)

        # Start a transaction to ensure atomic updates
        with transaction.atomic():
            updated_fields = []

            # Loop through the dictionary and update the field_order for each field
            for field_id, new_position in new_order.items():
                field = active_fields_dict[int(field_id)]

                # Update the field order of the field
                field.field_order = new_position
                field.save()
                updated_fields.append(field)

            # After updating specific fields, re-order the remaining fields to fill any gaps
            remaining_fields = [field for field in active_fields if field not in updated_fields]

            # Sort remaining fields by their current order and update them accordingly
            for index, field in enumerate(remaining_fields, start=1):
                field.field_order = index  # Reorder remaining fields starting from 1
                field.save()

        return success_response("Fields reordered successfully.")

    @action(detail=True, methods=["get"], url_path="get-options")
    def get_options(self, request, pk=None, *args, **kwargs):
        """
        Retrieve the options for a custom field.
        """
        # Check if custom_field_options_model is defined
        self._check_custom_field_options_model()

        # Fetch the custom field options
        custom_field_options = self.custom_field_options_model.objects.filter(custom_field=pk,
                                        status=CUSTOM_FIELD_OPTIONS_STATUS[1][0]).order_by('label')

        # Format the response data
        formatted_options = [{"id": option.id, "label": option.label} for option in custom_field_options]

        return success_response(formatted_options)

    @action(detail=True, methods=["post"], url_path="update-options")
    def update_options(self, request, pk=None, *args, **kwargs):
        """
        Update options for a custom field. This will add, update, or delete options based on the request data.
        """
        # Check if custom_field_options_model is defined
        self._check_custom_field_options_model()

        # dropdown, radio, multiselect_checkbox
        FIELDS_ALLOWED = [CUSTOM_FIELD_TYPE[6][0], CUSTOM_FIELD_TYPE[7][0], CUSTOM_FIELD_TYPE[11][0]]

        try:
            custom_field = self.queryset.filter(field_type__in=FIELDS_ALLOWED).get(pk=pk)
        except ObjectDoesNotExist:
            return notfound_response("Custom Field not found. Invalid field type or field doesn't exist.")

        custom_field_options = (self.custom_field_options_model.objects.
                                filter(custom_field=pk, status=CUSTOM_FIELD_OPTIONS_STATUS[1][0]))

        # Extract provided options from the request data
        provided_options = request.data.get("options", [])

        # Create dictionary for provided options with valid IDs
        provided_option_ids = {
            str(option.get("id")): option
            for option in provided_options
            if option.get("id") is not None
        }

        # Handle new options (those without an ID)
        new_options = [
            option for option in provided_options if option.get("id") is None
        ]

        # Update existing options or soft delete options that were not provided
        for option in custom_field_options:
            option_data = provided_option_ids.pop(str(option.id), None)

            if option_data:
                # If the option data is provided, update its value
                option.label = option_data.get("label", option.label)
                option.save()
            else:
                # If no data is provided for an existing option, soft delete it
                option.status = CUSTOM_FIELD_OPTIONS_STATUS[0][0]  # Soft delete
                option.save()

        # Add new options (those not present in provided_option_ids)
        for new_option_data in new_options:
            self.custom_field_options_model.objects.create(
                custom_field=custom_field,
                label=new_option_data.get("label"),
            )

        return success_response("Options updated successfully.")

    def _check_custom_field_options_model(self):
        if not self.custom_field_options_model:
            raise ImproperlyConfigured(
                "Django Access Point: 'custom_field_options_model' is missing."
            )