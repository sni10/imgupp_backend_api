# photomanager/models.py
import datetime
import os
from django.conf import settings
from django.db import models
import hashlib
import time
import uuid
from django.core.exceptions import SuspiciousFileOperation


# Create your models here.
def image_upload_path(instance, filename):
    _, ext = os.path.splitext(filename)
    # Создаем путь на основе hashpath фотосета и оригинального имени файла
    path = os.path.join('origins', 'galleries', instance.gallery.hashpath, f"{instance.hashpath}{ext}")

    return path


class Folder(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    birthplace = models.CharField(max_length=100, blank=True, null=True)
    hair_color = models.CharField(max_length=50, blank=True, null=True)
    height = models.CharField(max_length=15, blank=True, null=True)
    bust_size = models.CharField(max_length=10, blank=True, null=True)
    measurements = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hashpath = models.CharField(max_length=64, unique=True, blank=False, default=uuid.uuid4)

    def __str__(self):
        return f"{self.name}"


class Post(models.Model):
    folder = models.ForeignKey(Folder, related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hashpath = models.CharField(max_length=64, unique=True, blank=False, default=uuid.uuid4)

    def __str__(self):
        return f"{self.title}"


class Image(models.Model):
    gallery = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_path, max_length=500)
    caption = models.CharField(max_length=255, blank=True)
    hashpath = models.CharField(max_length=64, unique=True, blank=False, default=uuid.uuid4)

    def __str__(self):
        return f"{self.gallery.title}: {self.caption}"