from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@require_http_methods(["POST"])
@csrf_exempt
def login_view(request):
    username = request.headers.get('username', None)
    password = request.headers.get('password', None)
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid username or password'})


@require_http_methods(["POST"])
@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'status': 'success'})


@require_http_methods(["POST"])
@csrf_exempt
def register_view(request):
    username = request.headers.get('username', None)
    password = request.headers.get('password', None)
    try:
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        user = User.objects.create_user(username, password=password)
        user.save()
        return JsonResponse({'status': 'success'})
    except ValidationError as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
