from rest_framework.views import exception_handler as _exception_handler


def exception_handler(exc, context):
    response = _exception_handler(exc, context)
    if response is not None:
        response.data = {'error': response.data, 'status_code': response.status_code}
    return response
