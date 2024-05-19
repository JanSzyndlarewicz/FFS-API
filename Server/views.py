# views.py
import os
import uuid
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from Server.models import UploadedFile
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def get_download_link(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(access_token=file_id)
        if uploaded_file.password:  # Check if file is password-protected
            # Get the password from request headers
            password = request.headers.get('password', '')
            if password and password == uploaded_file.password:
                # Password correct, allow download
                file_path = uploaded_file.file.path
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        response = HttpResponse(f.read(), content_type='application/force-download')
                        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
                        return response
                else:
                    return JsonResponse({'error': 'File not found'}, status=404)
            else:
                # Incorrect password or no password provided
                return JsonResponse({'error': 'Incorrect password'}, status=401)
        else:
            # File not password-protected, allow download
            file_path = uploaded_file.file.path
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/force-download')
                    response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
                    return response
            else:
                return JsonResponse({'error': 'File not found'}, status=404)
    except UploadedFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)


def upload_file(request):
    password = request.headers.get('password', '')  # Get the password from the request
    user = request.user if request.user.is_authenticated else None
    uploaded_file = UploadedFile.objects.create(file=request.FILES['file'],
                                                access_token=generate_unique_access_token(),
                                                password=password,  # Save the password to the database
                                                user=user)  # Associate the file with the logged in user if there is one
    return JsonResponse({'url': f'/download/{uploaded_file.access_token}'})


def generate_unique_access_token() -> str:
    if UploadedFile.objects.filter(access_token=uuid.uuid4().hex).exists():
        return generate_unique_access_token()
    return uuid.uuid4().hex


@ensure_csrf_cookie
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.headers.get('username', '')
        password = request.headers.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid username or password'})


@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'status': 'success'})


@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        username = request.headers.get('username', '')
        password = request.headers.get('password', '')
        try:
            user = User.objects.create_user(username, password=password)
            user.save()
            return JsonResponse({'status': 'success'})
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


def get_user_files(request):
    user = request.user
    if user.is_authenticated:
        files = UploadedFile.objects.filter(user=user)
        return JsonResponse(
            {'files': [{'url': f'/download/{file.access_token}', 'filename': file.file.name} for file in files]})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
