# views.py
import uuid
from django.http import HttpResponse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
from Server.file_operations import create_tarfile_from_file_contents
from Server.models import UploadedFile
from Server.settings import MAX_FILE_SIZE


@require_http_methods(["POST"])
@csrf_exempt
def get_download_link(request, access_token: str) -> JsonResponse:
    """
    Get the download link for the file with the given file_id.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: The access token of the file
    :return: JsonResponse containing the file content if the file exists, otherwise an error message
    """
    try:
        uploaded_file = UploadedFile.objects.get(access_token=access_token)
        if uploaded_file.password:
            password = request.POST.get('password', None)
            if password and password == uploaded_file.password:
                return JsonResponse(uploaded_file.file_content, content_type='application/force-download')
            else:
                return JsonResponse({'error': 'Incorrect password'}, status=401)
        else:
            return JsonResponse(uploaded_file.file_content, content_type='application/force-download')
    except UploadedFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def upload_file(request) -> JsonResponse:
    password = request.POST.get('password', None)
    user = request.user if request.user.is_authenticated else None
    file_obj = request.FILES['file']
    if file_obj.size > MAX_FILE_SIZE:
        return JsonResponse({'error': 'File size exceeds 1GB'}, status=400)

    file_name = file_obj.name
    access_token = generate_unique_access_token()
    # Read the file content and save it to the database
    file_content = file_obj.read()

    uploaded_file = UploadedFile.objects.create(file=file_name,
                                                file_content=file_content,
                                                access_token=access_token,
                                                password=password,
                                                user=user)
    return JsonResponse({'url': f'/download/{uploaded_file.access_token}'})


def generate_unique_access_token() -> str:
    """
    Generate a unique access token for the file.
    :return: String containing the access token for the file
    """
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
def get_user_filenames(request) -> JsonResponse:
    """
    Get the list of files uploaded by the user.
    The JSON response will contain a list of dictionaries with the keys 'url' and 'filename'.
    Using the 'url' key, the user can download the file.
    :param request: WSGIRequest object containing metadata about the request
    :return: JsonResponse
    """
    user = request.user
    if user.is_authenticated:
        files = UploadedFile.objects.filter(user=user)
        return JsonResponse(
            {'files': [{'url': f'/download/{file.access_token}', 'filename': file.file.name} for file in files]})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)


def get_user_files(request):
    """
    Get the list of files uploaded by the user.
    The JSON response will contain a list of dictionaries with the keys 'url' and 'filename'.
    Using the 'url' key, the user can download the file.
    :param request: WSGIRequest object containing metadata about the request
    :return: JsonResponse
    """
    user = request.user
    if user.is_authenticated:
        files = UploadedFile.objects.filter(user=user)
        if not files:
            return JsonResponse({'error': 'No files uploaded'}, status=404)
        tar_data = create_tarfile_from_file_contents(files)
        return HttpResponse(tar_data, content_type='application/force-download')
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
