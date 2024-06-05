# auth_views.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from Server.decorators import response_logger


@require_http_methods(["POST"])
@csrf_exempt
@response_logger
def login_user(request: WSGIRequest) -> JsonResponse:
    """
    Login views. Authenticates user and logs them in. If successful, returns session key.
    In the body of the request, the username and password as key-value pairs are expected.
    :param request: request object with username and password in body of the request.
    :return: JsonResponse with status and session key if successful, error message if not.
    """
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    print(f'username: {username}, password: {password}')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)

        session_key = request.session.session_key
        session_expiry = request.session.get_expiry_date()
        return JsonResponse({'status': 'success', 'session_key': session_key, 'session_expiry': session_expiry})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid username or password'})


@require_http_methods(["POST"])
@csrf_exempt
@response_logger
def logout_user(request: WSGIRequest) -> JsonResponse:
    """
    Logout views. Logs out the user.
    :param request: request object with user to log out.
    :return: JsonResponse with status.
    """
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'User not authenticated'})


@require_http_methods(["POST"])
@csrf_exempt
@response_logger
def register_user(request: WSGIRequest) -> JsonResponse:
    """
    Register views. Registers a new user.
    In the body of the request, the username and password as key-value pairs are expected.
    Username must be unique and password must be at least 8 characters long.
    On successful registration, returns status 'success'. On failure, returns status 'error' and error message.
    :param request: request object with username and password in body of the request.
    :return: JsonResponse with status and error message if unsuccessful.
    """
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    try:
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        user = User.objects.create_user(username, password=password)
        user.save()
        return JsonResponse({'status': 'success'})
    except ValidationError as e:
        return JsonResponse({'status': 'error', 'message': str(e.message)})


@require_http_methods(["GET"])
@csrf_exempt
@response_logger
def session_info(request: WSGIRequest) -> JsonResponse:
    """
    Get session information.
    Current session key and expiry date are returned if user is authenticated.
    :param request: request object.
    :return: JsonResponse with session key and expiry date if user is authenticated, error message if not.
    """
    if request.user.is_authenticated:
        session_key = request.session.session_key
        session_expiry = request.session.get_expiry_date()
        return JsonResponse({'status': 'success', 'session_key': session_key, 'session_expiry': session_expiry})
    else:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'})
