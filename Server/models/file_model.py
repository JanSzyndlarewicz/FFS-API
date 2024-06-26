from django.conf import settings
from django.db import models


class File(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d')
    access_token = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def get_original_filename(self):
        return self.file.name.split('/')[-1]
