# photomanager/views.py
from PIL import Image as Im, ImageFilter, ImageDraw, ImageFont
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from fastapi import HTTPException
from rest_framework.pagination import PageNumberPagination
import os
import asyncio

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Image, Post
from .serializers import ProfileSerializer, ProfileListSerializer,ImageSerializer, GalleryFullSerializer

from ..tools.mysql import fetch_one

long = 60 * 60 * 24


class GalleryDetailView(APIView):
    # @method_decorator(cache_page(long))
    def get(self, request, hashpath):
        gallery = get_object_or_404(Gallery, hashpath=hashpath)
        serializer = GalleryFullSerializer(gallery)
        return Response(serializer.data)




async def post_detail_view(hashpath: str):
    post_query = "SELECT * FROM galleries WHERE hashpath = %s"
    images_query = "SELECT * FROM images WHERE gallery_id = %s"

    # Выполнение запросов параллельно
    post, images = await asyncio.gather(
        fetch_one(post_query, hashpath),
        fetch_one(images_query, hashpath)  # Предположим, что hashpath это ID галереи
    )

    if not post:
        raise HTTPException(status_code=404, detail="Gallery not found")

    # Подготовка данных
    data = {
        "title": post['title'],
        "description": post['description'],
        "images": images if images else []
    }
    return data


class ProfileDetailView(APIView):
    # @method_decorator(cache_page(long))
    def get(self, request, hashpath):
        profile = get_object_or_404(Profile, hashpath=hashpath)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


# class ProfileListView(APIView):
#     # @method_decorator(cache_page(long))
#     def get(self, request):
#         profiles = Profile.objects.all()
#         serializer = ProfileListSerializer(profiles, many=True)
#         return Response(serializer.data)


class ProfileListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 100


class ProfileListView(APIView):
    pagination_class = ProfileListPagination

    # @method_decorator(cache_page(long))
    def get(self, request):
        profiles = Profile.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(profiles, request, view=self)

        if page is not None:
            serializer = ProfileListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProfileListSerializer(profiles, many=True)
        return Response(serializer.data)


def serve_image(request, folder, filename):
    # Путь к исходному изображению
    image_path = os.path.join(settings.MEDIA_ROOT, "cache", "galleries", folder, filename)
    # Путь к изображению водяного знака
    watermark_path = os.path.join(settings.MEDIA_ROOT, "watermark.png")
    # Путь к закешированному изображению
    cache_dir = os.path.join(settings.MEDIA_ROOT, "cache", "processed", folder)
    os.makedirs(cache_dir, exist_ok=True)
    cached_image_path = os.path.join(cache_dir, filename)

    # Если закешированное изображение существует, вернуть его
    if os.path.exists(cached_image_path):
        with open(cached_image_path, "rb") as cached_image:
            return HttpResponse(cached_image.read(), content_type="image/jpeg")

    try:
        # Открытие основного изображения
        with Im.open(image_path) as img:
            # Применение размытия
            blurred = img.filter(ImageFilter.GaussianBlur(radius=1.25))

            # Открытие изображения водяного знака
            with Im.open(watermark_path) as watermark:
                # Масштабирование водяного знака, например, до 20% от ширины основного изображения
                scale_factor = 0.2
                new_width = int(blurred.width * scale_factor)
                new_height = int(watermark.height * new_width / watermark.width)
                resized_watermark = watermark.resize((new_width, new_height), Im.Resampling.LANCZOS)

                # Позиция водяного знака: в нижнем правом углу основного изображения
                position = (blurred.width - new_width, blurred.height - new_height)

                # Наложение водяного знака на изображение
                blurred.paste(resized_watermark, position, resized_watermark)

                # Сохранение измененного изображения в файл для кеширования
                blurred.save(cached_image_path, "JPEG")

                # Чтение сохраненного изображения и возврат его в ответе
                with open(cached_image_path, "rb") as cached_image:
                    return HttpResponse(cached_image.read(), content_type="image/jpeg")
    except IOError:
        return HttpResponse("Image not found or error in processing", status=404)

# def serve_image(request, folder, filename):
#     # Путь к исходному изображению
#     image_path = os.path.join(settings.MEDIA_ROOT, "cache", "galleries", folder, filename)
#     # Путь к изображению водяного знака
#     watermark_path = os.path.join(settings.MEDIA_ROOT, "watermark.png")
#
#     try:
#         # Открытие основного изображения
#         with Im.open(image_path) as img:
#             # Применение размытия
#             blurred = img.filter(ImageFilter.GaussianBlur(radius=1.25))
#
#             # Открытие изображения водяного знака
#             with Im.open(watermark_path) as watermark:
#
#                 # Масштабирование водяного знака, например, до 20% от ширины основного изображения
#                 scale_factor = 2
#                 new_width = int(blurred.width * scale_factor)
#                 new_height = int(watermark.height * new_width / watermark.width)
#                 resized_watermark = watermark.resize((new_width, new_height), Im.Resampling.LANCZOS)
#
#                 # Позиция водяного знака: в нижнем правом углу основного изображения
#                 position = (blurred.width - new_width, blurred.height - new_height)
#
#                 # Наложение водяного знака на изображение
#                 blurred.paste(resized_watermark, position, resized_watermark)
#
#                 # Сохранение измененного изображения в памяти
#                 response = HttpResponse(content_type="image/jpeg")
#                 blurred.save(response, "JPEG")
#                 return response
#     except IOError:
#         return HttpResponse("Image not found or error in processing", status=404)