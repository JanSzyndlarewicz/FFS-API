from django.conf import settings
from django.db import models


class File(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d')
    access_token = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def get_original_filename(self):
        return self.file.name.split('/')[-1]


class Share(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='shared_files')
    shared_with = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_files')
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_files')
    shared_at = models.DateTimeField(auto_now_add=True)
