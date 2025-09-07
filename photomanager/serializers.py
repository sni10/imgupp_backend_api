from PIL import Image as PilImage  # Исправление №1
import os
from django.conf import settings
from rest_framework import serializers
from .models import Profile, Gallery, Image


def get_url(image_path, thumb_img=0):
    folder, filename = gen_cache(image_path, thumb_img)
    url = settings.HTTP_HOST + '/api/img' + '/' + folder + '/' + filename

    return url


def gen_cache(image_path, thumb_img):
    parts = image_path.split('/')
    folder = parts[-2]
    filename = parts[-1]

    size = settings.CACHE_IMG_SIZE
    original_dir = os.path.join(settings.MEDIA_ROOT, "origins", "galleries", folder, filename)

    if thumb_img:
        filename = "thumb_" + filename
        size = settings.CACHE_THUMB_SIZE

    cached_dir = os.path.join(settings.MEDIA_ROOT, "cache", "galleries", folder, filename)

    if not os.path.exists(cached_dir):
        os.makedirs(os.path.dirname(cached_dir), exist_ok=True)

        with PilImage.open(original_dir) as img:
            img.thumbnail(size)
            img.save(cached_dir, "JPEG")

    return folder, filename


class ImageSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    uuid = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Image
        fields = ['caption', 'uuid', 'thumbnail_url', 'image_url']

    def get_uuid(self, obj):
        hashpath = obj.hashpath
        return hashpath

    def get_thumbnail_url(self, obj):
        thumbnail_url = get_url(obj.image.name, 1)
        return thumbnail_url

    def get_image_url(self, obj):
        origin_url = get_url(obj.image.name)
        return origin_url


class GalleryFullSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = ['title', 'description', 'hashpath', 'images']

    def get_images(self, obj):
        images = obj.images.all()
        return ImageSerializer(images, many=True, context=self.context).data  # Обратите внимание на передачу context


class GalleryPrevSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = ['title', 'description', 'hashpath', 'image_url', 'thumbnail_url']

    def get_image_url(self, obj):
        images = obj.images.all()
        images = ImageSerializer(images, many=True, context=self.context).data  # Обратите внимание на передачу context

        result = images[5]['image_url']

        return result

    def get_thumbnail_url(self, obj):
        images = obj.images.all()
        images = ImageSerializer(images, many=True, context=self.context).data  # Обратите внимание на передачу context

        result = images[5]['thumbnail_url']

        return result


class ProfileListSerializer(serializers.ModelSerializer):
    galleries = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['name', 'description', 'hashpath', 'birthplace', 'measurements', 'galleries']

    def get_galleries(self, obj):
        galleries = obj.galleries.all()
        result = GalleryPrevSerializer(galleries, many=True, context=self.context).data  # Обратите внимание на передачу context

        if ( len(result) > 0 ):
            return result[0]

        return []


class ProfileSerializer(serializers.ModelSerializer):
    galleries = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['name', 'description', 'hashpath', 'birthplace', 'measurements', 'galleries']

    def get_galleries(self, obj):
        galleries = obj.galleries.all()
        return GalleryPrevSerializer(galleries, many=True, context=self.context).data  # Обратите внимание на передачу context
