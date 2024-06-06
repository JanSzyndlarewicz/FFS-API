# utils_views.py
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from Server.utils.decorators import response_logger


@require_http_methods(["GET"])
@ensure_csrf_cookie
@response_logger
def get_csrf_token(request: WSGIRequest) -> JsonResponse:
    """
    Get the CSRF token. This view is used to get the CSRF token from the server.
    Method is not currently used in the frontend.
    :param request: WSGIRequest object containing metadata about the request
    :return: JsonResponse containing the CSRF token
    """
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})


