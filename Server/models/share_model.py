from django.conf import settings
from django.db import models
from Server.models.file_model import File


class Share(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='shared_files')
    shared_with = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_files')
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_files')
    shared_at = models.DateTimeField(auto_now_add=True)