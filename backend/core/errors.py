from typing import TYPE_CHECKING, Optional, Union

from django.http import JsonResponse
from django.template.response import TemplateResponse
from rest_framework import status

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse
    from rest_framework.request import Request


def bad_request(
    request: Union['HttpRequest', 'Request'], exception: Optional[Exception] = None
) -> Union['HttpResponse', JsonResponse]:
    """Handle a 400 error."""
    _status = status.HTTP_400_BAD_REQUEST
    if request.path.startswith('/api/'):
        data = {'error': 'Bad Request'}
        return JsonResponse(data, status=_status)
    return TemplateResponse(
        request,
        template='error.html',
        context={'status': f'{_status}', 'status_text': 'Bad request'},
        status=_status,
    )


def permission_denied(
    request: Union['HttpRequest', 'Request'], exception: Optional[Exception] = None
) -> Union['HttpResponse', JsonResponse]:
    """Handle a 403 error."""
    _status = status.HTTP_403_FORBIDDEN
    if request.path.startswith('/api/'):
        data = {'error': 'Forbidden'}
        return JsonResponse(data, status=_status)
    return TemplateResponse(
        request,
        template='error.html',
        context={'status': f'{_status}', 'status_text': 'Permission denied'},
        status=_status,
    )


def not_found(
    request: Union['HttpRequest', 'Request'], exception: Optional[Exception] = None
) -> Union['HttpResponse', JsonResponse]:
    """Handle a 404 error."""
    _status = status.HTTP_404_NOT_FOUND
    if request.path.startswith('/api/'):
        data = {'error': 'Not Found'}
        return JsonResponse(data, status=_status)
    return TemplateResponse(
        request,
        template='error.html',
        context={'status': f'{_status}', 'status_text': 'Page not found'},
        status=_status,
    )


def server_error(
    request: Union['HttpRequest', 'Request'], exception: Optional[Exception] = None
) -> Union['HttpResponse', JsonResponse]:
    """Handle a 500 error."""
    _status = status.HTTP_500_INTERNAL_SERVER_ERROR
    if request.path.startswith('/api/'):
        data = {'error': 'Server Error'}
        return JsonResponse(data, status=_status)
    return TemplateResponse(
        request,
        template='error.html',
        context={'status': f'{_status}', 'status_text': 'An error occurred'},
        status=_status,
    )


error_views = {
    '400': bad_request,
    '403': permission_denied,
    '404': not_found,
    '500': server_error,
}


def error(
    request: Union['HttpRequest', 'Request'],
    error_code: int,
) -> Union['HttpResponse', JsonResponse]:
    view = error_views.get(str(error_code))
    return view(request)
