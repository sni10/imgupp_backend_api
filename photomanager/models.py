# photomanager/models.py
import datetime
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import hashlib
import time
import uuid
from django.core.exceptions import SuspiciousFileOperation


def generate_hashpath():
    """Generate a unique hashpath using UUID4"""
    return uuid.uuid4().hex


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    hashpath = models.CharField(max_length=32, unique=True, default=generate_hashpath)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Profile of {self.user.username}"


class Gallery(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    hashpath = models.CharField(max_length=32, unique=True, default=generate_hashpath)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='galleries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Gallery: {self.title or 'Untitled'}"
    
    class Meta:
        verbose_name_plural = "Galleries"


def image_upload_path(instance, filename):
    _, ext = os.path.splitext(filename)
    # Создаем путь на основе hashpath фотосета и оригинального имени файла
    path = os.path.join('origins', 'galleries', instance.gallery.hashpath, f"{instance.hashpath}{ext}")

    return path


class Image(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=image_upload_path, max_length=500)
    hashpath = models.CharField(max_length=32, unique=True, default=generate_hashpath)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image: {self.title or self.image.name}"


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