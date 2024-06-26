# file_views.py
import os
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from Server.utils.decorators import response_logger
from Server.utils.file_operations import encrypt_file, get_file_from_path, \
    generate_unique_access_token, create_tarfile_in_memory
from Server.models.file_model import File
from Server.settings import MAX_FILE_SIZE


@require_http_methods(["GET", "POST", "DELETE"])
@csrf_exempt
@response_logger
def file_view(request: WSGIRequest, access_token: str = None) -> HttpResponse:
    """
    View for file operations. The operations supported are GET, POST, and DELETE.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: The access token of the file
    :return: HttpResponse
    """
    if request.method == 'GET':
        return get_file(request, access_token)
    elif request.method == 'POST' and access_token is None:
        return upload_file(request)
    elif request.method == 'DELETE':
        return delete_file(request, access_token)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@require_http_methods(["GET"])
@csrf_exempt
@response_logger
def get_file(request: WSGIRequest, access_token: str) -> HttpResponse:
    """
    Get the download link for the file with the given file_id. The file is downloaded if it exists.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: The access token of the file
    :return: JsonResponse containing the file content if the file exists, otherwise an error message
    """
    try:
        uploaded_file = File.objects.get(access_token=access_token)
        if uploaded_file.deleted_at:
            return JsonResponse({'error': 'File has been removed'}, status=404)

        if uploaded_file.password:
            path, content = get_file_from_path(uploaded_file.file.path)
            encrypted_file, encrypted_file_path = encrypt_file(uploaded_file.file.path, uploaded_file.password)
            response = HttpResponse(encrypted_file, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=' + path + '.zip'
            os.remove(encrypted_file_path)
            return response
        else:
            path, content = get_file_from_path(uploaded_file.file.path)
            response = HttpResponse(content, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=' + path
            return response

    except File.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
@response_logger
def upload_file(request: WSGIRequest) -> JsonResponse:
    """
    Upload a file to the server. The file is stored in the 'file' key of the request.
    :param request: WSGIRequest object containing metadata about the request and the file to upload
    :return: JsonResponse containing the URL to download the file
    """
    password = request.headers.get('password', None)
    user = request.user if request.user.is_authenticated else None
    file_obj = request.FILES['file']
    if file_obj.size > MAX_FILE_SIZE:
        return JsonResponse({'error': 'File size exceeds 1GB'}, status=400)

    uploaded_file = File.objects.create(file=request.FILES['file'],
                                        access_token=generate_unique_access_token(),
                                        password=password,
                                        user=user)

    return JsonResponse({'url': f'/file/{uploaded_file.access_token}/'})


@require_http_methods(["DELETE"])
@csrf_exempt
@response_logger
def delete_file(request: WSGIRequest, access_token: str) -> JsonResponse:
    """
    Delete the file with the given file_id. The file is permanently deleted.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: The access token of the file
    :return: JsonResponse containing the result of the deletion
    """
    try:
        file = File.objects.get(access_token=access_token)
        os.remove(file.file.path)
        file.delete()
        return JsonResponse({'message': 'File deleted'})
    except File.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)


@require_http_methods(["GET"])
@csrf_exempt
@response_logger
def get_user_filenames(request: WSGIRequest) -> JsonResponse:
    """
    Get the list of files uploaded by the user.
    The JSON response will contain a list of dictionaries with the keys 'file_token' and 'filename'.
    Using the 'file_token' key, the user can reference the file.
    :param request: WSGIRequest object containing metadata about the request
    :return: JsonResponse
    """
    user = request.user
    if user.is_authenticated:
        files = File.objects.filter(user=user, deleted_at=None)
        response = []
        for file in files:
            try:
                response.append({'file_token': file.access_token, 'filename': file.get_original_filename()})
            except FileNotFoundError:
                file.delete()
        return JsonResponse({'files': response})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)


@require_http_methods(["GET"])
@csrf_exempt
@response_logger
def get_user_files(request: WSGIRequest) -> HttpResponse:
    """
    Get the list of files uploaded by the user.
    The JSON response will contain a list of dictionaries with the keys 'url' and 'filename'.
    Using the 'url' key, the user can download the file.
    :param request: WSGIRequest object containing metadata about the request
    :return: JsonResponse
    """
    user = request.user
    if user.is_authenticated:
        files = File.objects.filter(user=user)
        if not files:
            return JsonResponse({'error': 'No files uploaded'}, status=404)
        tar_data = create_tarfile_in_memory([file.file.path for file in files])
        return HttpResponse(tar_data, content_type='application/force-download')
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
