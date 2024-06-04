# share_views.py
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from Server.decorators import response_logger
from Server.models.file_model import File
from Server.models.share_model import Share


@require_http_methods(["GET", "POST", "DELETE"])
@csrf_exempt
@response_logger
def share_view(request: WSGIRequest, access_token: str = None, shared_with: str = None) -> JsonResponse:
    """
    View for sharing files. It handles sharing, getting shared files and deleting shares.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: unique access token of the file
    :param shared_with: username of the user with whom the file is shared
    :return: JsonResponse
    """
    if request.method == 'POST' and access_token is not None and shared_with is not None:
        return share_file(request, access_token, shared_with)
    elif request.method == 'GET' and access_token is None and shared_with is None:
        return get_shared_files(request)
    elif request.method == 'DELETE' and access_token is not None and shared_with is not None:
        return delete_share(request, access_token, shared_with)
    elif request.method == 'DELETE' and access_token is not None and shared_with is None:
        return delete_all_shares_of_file(request, access_token)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@require_http_methods(["POST"])
@csrf_exempt
@response_logger
def share_file(request: WSGIRequest, access_token: str, username: str) -> JsonResponse:
    """
    Share a file with the given access token with the user with the given username.
    It creates a Share object with the file and the user.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: unique access token of the file
    :param username: username of the user with whom the file is shared
    :return: JsonResponse containing the result of the sharing operation
    """
    if request.user.is_authenticated:
        try:
            file = File.objects.get(access_token=access_token)
            if file.user != request.user:
                return JsonResponse({'error': 'User not authorized to share the file'}, status=403)

            if file.user.username == username:
                return JsonResponse({'error': 'Cannot share file with yourself'}, status=400)

            if User.objects.filter(username=username).count() == 0:
                return JsonResponse({'error': 'User not found'}, status=404)

            if Share.objects.filter(file=file, shared_with=User.objects.get(username=username)).exists():
                return JsonResponse({'error': 'File already shared with the user'}, status=400)

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
                                        'filename': file.file.get_original_filename(),
                                        'file_size': file.file.file.size,
                                        'owner': file.shared_by.username
                                        } for file in shared_files]})
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


@require_http_methods(["DELETE"])
@csrf_exempt
@response_logger
def delete_all_shares_of_file(request: WSGIRequest, access_token: str) -> JsonResponse:
    """
    Delete all shares of a file with the given access token.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: unique access token of the file
    """
    if request.user.is_authenticated:
        try:
            file = File.objects.get(access_token=access_token)
            if file.user != request.user:
                return JsonResponse({'error': 'User not authorized to delete the shares'}, status=403)
            shares = Share.objects.filter(file=file)
            for share in shares:
                share.delete()
            return JsonResponse({'message': 'Shares deleted successfully'})
        except File.DoesNotExist:
            return JsonResponse({'error': 'File not found'}, status=404)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
