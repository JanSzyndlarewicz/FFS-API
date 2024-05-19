# views.py
import os
import uuid
from django.http import HttpResponse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
from Server.models import UploadedFile


@require_http_methods(["GET"])
@csrf_exempt
def get_download_link(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(access_token=file_id)
        if uploaded_file.password:
            password = request.headers.get('password', None)
            if password and password == uploaded_file.password:
                return get_file(uploaded_file.file.path)
            else:
                return JsonResponse({'error': 'Incorrect password'}, status=401)
        else:
            return get_file(uploaded_file.file.path)
    except UploadedFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)


def get_file(file_path: str) -> HttpResponse:
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    else:
        return JsonResponse({'error': 'File not found'}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def upload_file(request):
    password = request.headers.get('password', None)
    print(request.user.is_authenticated)
    user = request.user if request.user.is_authenticated else None
    uploaded_file = UploadedFile.objects.create(file=request.FILES['file'],
                                                access_token=generate_unique_access_token(),
                                                password=password,
                                                user=user)
    return JsonResponse({'url': f'/download/{uploaded_file.access_token}'})


def generate_unique_access_token() -> str:
    if UploadedFile.objects.filter(access_token=uuid.uuid4().hex).exists():
        return generate_unique_access_token()
    return uuid.uuid4().hex


@require_http_methods(["GET"])
@ensure_csrf_cookie
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})


@require_http_methods(["GET"])
@csrf_exempt
def get_user_files(request):
    user = request.user
    if user.is_authenticated:
        files = UploadedFile.objects.filter(user=user)
        return JsonResponse(
            {'files': [{'url': f'/download/{file.access_token}', 'filename': file.file.name} for file in files]})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
