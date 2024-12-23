from rest_framework import status
from rest_framework.response import Response


def success_response(data):
    """
    Helper function to standardize success responses.
    """
    return Response(
        {"status": "success", "data": data},
        status=status.HTTP_200_OK,
    )


def validation_error_response(message):
    """
    Helper function to standardize validation error responses.
    """
    return Response(
        {"status": "validation_error", "data": message},
        status=status.HTTP_400_BAD_REQUEST,
    )


def error_response(data):
    """
    Helper function to standardize error responses.
    """
    return Response(
        {"status": "error", "data": data},
        status=status.HTTP_400_BAD_REQUEST,
    )


def created_response(data):
    """
    Helper function to standardize created responses.
    """
    return Response(
        {"status": "success", "data": data},
        status=status.HTTP_201_CREATED,
    )


def deleted_response(message):
    """
    Helper function to standardize deleted responses.
    """
    return Response(
        {"status": "success", "data": message},
        status=status.HTTP_204_NO_CONTENT,
    )


def notfound_response(message):
    """
    Helper function to standardize notfound responses.
    """
    return Response(
        {"status": "error", "data": message},
        status=status.HTTP_404_NOT_FOUND,
    )
