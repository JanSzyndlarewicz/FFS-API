from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from Server.decorators import response_logger
from Server.models.file_model import File
from Server.models.share_model import Share


@require_http_methods(["GET"])
@csrf_exempt
@response_logger
def get_files_in_bin(request: WSGIRequest) -> JsonResponse:
    """
    Get the list of files in the bin. Files in bin are those that have been deleted by the user.
    The JSON response will contain a list of dictionaries with the keys 'file_token' and 'filename'.
    :param request: WSGIRequest object containing metadata about the request
    :return: JsonResponse
    """
    user = request.user
    if user.is_authenticated:
        files = File.objects.filter(user=user, deleted_at__isnull=False)
        return JsonResponse(
            {'files': [{'file_token': file.access_token,
                        'filename': file.get_original_filename(),
                        'file_size': file.file.size}
                       for file in files]})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)


@require_http_methods(["PUT"])
@csrf_exempt
@response_logger
def put_file_in_bin(request: WSGIRequest, access_token: str):
    """
    Put the file with the given file_id in the bin.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: The access token of the file
    :return: JsonResponse containing the result of the deletion
    """
    try:
        if request.user.is_authenticated:
            file = File.objects.get(access_token=access_token)
            if file.user != request.user:
                return JsonResponse({'error': 'User not authorized to delete the file'}, status=403)

            if file.deleted_at:
                return JsonResponse({'error': 'File already in bin'}, status=400)

            shares = Share.objects.filter(file=file)
            for share in shares:
                share.delete()

            file.deleted_at = timezone.now()
            file.save()

            return JsonResponse({'message': 'File deleted'})
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    except File.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)


@require_http_methods(["PUT"])
@csrf_exempt
@response_logger
def recover_file(request: WSGIRequest, access_token: str):
    """
    Recover the file with the given file_id from the bin.
    :param request: WSGIRequest object containing metadata about the request
    :param access_token: The access token of the file
    :return: JsonResponse containing the result of the recovery
    """
    try:
        if request.user.is_authenticated:
            file = File.objects.get(access_token=access_token)
            if file.user != request.user:
                return JsonResponse({'error': 'User not authorized to recover the file'}, status=403)

            if not file.deleted_at:
                return JsonResponse({'error': 'File not in bin'}, status=400)

            file.deleted_at = None
            file.save()

            return JsonResponse({'message': 'File recovered'})
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    except File.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)
