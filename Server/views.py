# views.py
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
from Server.decorators import response_logger
from Server.file_operations import create_tarfile_in_memory, encrypt_file, get_file_from_path, \
    generate_unique_access_token
from Server.models import File, Share
from Server.settings import MAX_FILE_SIZE


@require_http_methods(["GET"])
@csrf_exempt
@response_logger
def get_file(request, access_token: str) -> HttpResponse:
    """
    Get the download link for the file with the given file_id.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: The access token of the file
    :return: JsonResponse containing the file content if the file exists, otherwise an error message
    """
    try:
        uploaded_file = File.objects.get(access_token=access_token)
        if uploaded_file.password:
            path, content = get_file_from_path(uploaded_file.file.path)
            encrypted_file = encrypt_file(path, content, uploaded_file.password)
            response = HttpResponse(encrypted_file, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=' + path + '.zip'
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
def upload_file(request) -> JsonResponse:
    """
    Upload a file to the server.
    :param request: WSGIRequest object containing metadata about the request and the file to upload
    :return: JsonResponse containing the URL to download the file
    """
    password = request.POST.get('password', None)
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
def delete_file(request, access_token: str):
    """
    Delete the file with the given file_id.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: The access token of the file
    :return: JsonResponse containing the result of the deletion
    """
    try:
        file = File.objects.get(access_token=access_token)
        file.delete()
        return JsonResponse({'message': 'File deleted'})
    except File.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)


@require_http_methods(["GET", "POST", "DELETE"])
@csrf_exempt
@response_logger
def file_view(request, access_token: str = None) -> HttpResponse:
    if request.method == 'GET':
        return get_file(request, access_token)
    elif request.method == 'POST' and access_token is None:
        return upload_file(request)
    elif request.method == 'DELETE':
        return delete_file(request, access_token)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@require_http_methods(["POST"])
@csrf_exempt
@response_logger
def share_file(request, access_token: str, username: str):
    if request.user.is_authenticated:
        try:
            file = File.objects.get(access_token=access_token)
            shared_with = User.objects.get(username=username)
            Share.objects.create(file=file, shared_with=shared_with, shared_by=request.user)
            return JsonResponse({'message': 'File shared successfully'})
        except File.DoesNotExist:
            return JsonResponse({'error': 'File not found'}, status=404)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)


@require_http_methods(["GET"])
@csrf_exempt
@response_logger
def get_shared_files(request: WSGIRequest) -> JsonResponse:
    """
    Get the list of files shared with the user.
    The JSON response will contain a list of dictionaries with the keys 'file_token' and 'filename'.
    Using the 'file_token' key, the user can reference the file.
    :param request: WSGIRequest object containing metadata about the request
    :return: JsonResponse containing the list of shared files
    """
    if request.user.is_authenticated:
        shared_files = Share.objects.filter(shared_with=request.user)
        return JsonResponse({'files': [{'file_token': file.file.access_token,
                                        'filename': file.file.get_original_filename()} for file in shared_files]})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)


@require_http_methods(["DELETE"])
@csrf_exempt
@response_logger
def delete_share(request: WSGIRequest, access_token: str, shared_with: str) -> JsonResponse:
    """
    Delete the share with the given access token and shared_with user.
    Access token is the file access token and shared_with is the username
    of the user with whom the file is shared.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: unique access token of the file
    :param shared_with: username of the user with whom the file is shared
    :return: JsonResponse containing the result of the deletion
    """
    if request.user.is_authenticated:
        try:
            id_of_user = User.objects.get(username=shared_with)
            shared_file = Share.objects.get(file__access_token=access_token, shared_with=id_of_user)
            if shared_file.shared_by != request.user:
                return JsonResponse({'error': 'User not authorized to delete the share'}, status=403)
            shared_file.delete()
            return JsonResponse({'message': 'File unshared successfully'})
        except Share.DoesNotExist:
            return JsonResponse({'error': 'File not found'}, status=404)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)


@require_http_methods(["GET", "POST", "DELETE"])
@csrf_exempt
@response_logger
def share_view(request: WSGIRequest, access_token: str = None, shared_with: str = None) -> JsonResponse:
    if request.method == 'POST' and access_token is not None and shared_with is not None:
        return share_file(request, access_token, shared_with)
    elif request.method == 'GET' and access_token is None and shared_with is None:
        return get_shared_files(request)
    elif request.method == 'DELETE' and access_token is not None and shared_with is not None:
        return delete_share(request, access_token, shared_with)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@require_http_methods(["GET"])
@ensure_csrf_cookie
@response_logger
def get_csrf_token(request: WSGIRequest) -> JsonResponse:
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})


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
        files = File.objects.filter(user=user)
        return JsonResponse(
            {'files': [{'file_token': file.access_token, 'filename': file.get_original_filename()} for file in files]})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)


@require_http_methods(["GET"])
@csrf_exempt
@response_logger
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
        files = File.objects.filter(user=user)
        if not files:
            return JsonResponse({'error': 'No files uploaded'}, status=404)
        tar_data = create_tarfile_in_memory([file.file.path for file in files])
        return HttpResponse(tar_data, content_type='application/force-download')
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
