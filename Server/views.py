# views.py
import os
import uuid
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from Server.models import UploadedFile


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
    if request.method == 'POST' and request.FILES['file']:
        password = request.headers.get('password', '')  # Get the password from the request
        uploaded_file = UploadedFile.objects.create(file=request.FILES['file'],
                                                    access_token=generate_unique_access_token(),
                                                    password=password)  # Save the password to the database
        return JsonResponse({'url': f'/download/{uploaded_file.access_token}'})
    else:
        return JsonResponse({'error': 'Invalid request'})


def generate_unique_access_token() -> str:
    if UploadedFile.objects.filter(access_token=uuid.uuid4().hex).exists():
        return generate_unique_access_token()
    return uuid.uuid4().hex


@ensure_csrf_cookie
def get_csrf_token(request):
    # Zwraca token CSRF w odpowiedzi JSON
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})
