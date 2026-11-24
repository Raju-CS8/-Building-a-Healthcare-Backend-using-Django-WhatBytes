"""
Custom API Exception Handler for consistent, informative error responses.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            'success': False,
            'status_code': response.status_code,
            'error': exc.__class__.__name__,
            'message': 'An error occurred while processing your request.',
            'details': response.data
        }

        # Provide cleaner message if available
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_data['message'] = str(response.data['detail'])
            elif 'non_field_errors' in response.data:
                custom_data['message'] = str(response.data['non_field_errors'][0])
        elif isinstance(response.data, list) and len(response.data) > 0:
            custom_data['message'] = str(response.data[0])

        response.data = custom_data

    return response
