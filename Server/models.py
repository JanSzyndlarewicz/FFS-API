from django.db import models


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d')
    access_token = models.CharField(max_length=255, unique=True)
