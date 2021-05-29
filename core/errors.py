from typing import TYPE_CHECKING

from django.template.response import TemplateResponse

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def bad_request(request: 'HttpRequest', exception: Exception = None) -> 'HttpResponse':
    """Handle a 400 error."""
    status = 400
    return TemplateResponse(
        request,
        template='error.html',
        context={'status': f'{status}', 'status_text': 'Bad request'},
        status=status,
    )


def permission_denied(request: 'HttpRequest', exception: Exception = None) -> 'HttpResponse':
    """Handle a 403 error."""
    status = 403
    return TemplateResponse(
        request,
        template='error.html',
        context={'status': f'{status}', 'status_text': 'Permission denied'},
        status=status,
    )


def not_found(request: 'HttpRequest', exception: Exception = None) -> 'HttpResponse':
    """Handle a 404 error."""
    status = 404
    return TemplateResponse(
        request,
        template='error.html',
        context={'status': f'{status}', 'status_text': 'Page not found'},
        status=status,
    )


def error(request: 'HttpRequest', exception: Exception = None) -> 'HttpResponse':
    """Handle a 500 error."""
    status = 500
    return TemplateResponse(
        request,
        template='error.html',
        context={'status': f'{status}', 'status_text': 'An error occurred'},
        status=status,
    )
