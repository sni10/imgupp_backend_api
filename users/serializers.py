from PIL import Image as PilImage  # Исправление №1
import os
from django.conf import settings
from rest_framework import serializers
from .models import UserSubscription, SubscriptionPlan

def get_thumbnail(image_path):
    # Определяем базовую директорию для оригинальных изображений
    original_dir = os.path.join(settings.MEDIA_ROOT, image_path)

    # Определяем путь для сохранения уменьшенного изображения
    parts = image_path.split('/')
    filename = parts[-1]
    # Добавляем префикс 'thumb_' к имени файла
    cached_filename = "thumb_" + f"{settings.CACHE_IMG_SIZE}" + filename
    cached_dir = os.path.join(settings.MEDIA_ROOT, "cached_images", *parts[:-1], cached_filename)

    if not os.path.exists(cached_dir):
        os.makedirs(os.path.dirname(cached_dir), exist_ok=True)
        with PilImage.open(original_dir) as img:
            img.thumbnail(settings.CACHE_IMG_SIZE)
            img.save(cached_dir, "JPEG")

    # Возвращаем относительный путь от MEDIA_ROOT
    relative_path = os.path.join("cached_images", *parts[:-1], cached_filename)
    return relative_path


class UserSubscriptionSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()  # Исправление №3

    class Meta:
        model = Image
        fields = ['image', 'caption', 'hashpath', 'thumbnail_url']

    def get_thumbnail_url(self, obj):
        img = obj.image.name
        thumbnail_path = get_thumbnail(img)
        path = img.replace('\\', '/')

        # Формируем полный URL, используя MEDIA_URL и относительный путь к уменьшенному изображению
        parts = path.split('/')
        photoset = parts[-2]
        filename = parts[-1]

        strip = settings.HTTP_HOST + '/api/img' + f"/galleries/{photoset}/{filename}"

        return strip

    def to_representation(self, instance):
        # Получаем стандартное представление данных
        ret = super().to_representation(instance)

        # Модифицируем значение 'hashpath' здесь, если нужно
        # Например, мы хотим добавить какой-то префикс к 'hashpath'

        image_path = ret['image']
        # Определяем базовую директорию для оригинальных изображений
        # Если image_path начинается с MEDIA_URL, убираем эту часть
        if image_path.startswith(settings.MEDIA_URL):
            image_path = image_path[len(settings.MEDIA_URL):]  # Удаляем '/media/' из пути

        # Теперь image_path можно использовать с MEDIA_ROOT без дублирования '/media/'
        original_dir = os.path.join(settings.MEDIA_ROOT, image_path)

        # Формируем полный URL, используя MEDIA_URL и относительный путь к уменьшенному изображению
        parts = image_path.split('/')
        photoset = parts[-2]
        filename = parts[-1]

        # Добавляем префикс 'thumb_' к имени файла
        cached_filename = "thumb_" + f"{settings.CACHE_IMG_SIZE}" + filename
        cached_dir = os.path.join(settings.MEDIA_ROOT, "cached_images", *parts[:-1], cached_filename)

        if not os.path.exists(cached_dir):
            os.makedirs(os.path.dirname(cached_dir), exist_ok=True)

            with PilImage.open(original_dir) as img:
                img.thumbnail(settings.CACHE_IMG_SIZE)
                img.save(cached_dir, "JPEG")

        strip = settings.HTTP_HOST + '/api/img' + f"/galleries/{photoset}/{filename}"
        # Возвращаем измененные данные
        ret['image'] = strip

        return ret

class SubscriptionPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'duration', 'price']
