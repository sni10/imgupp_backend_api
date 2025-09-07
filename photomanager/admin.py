# photomanager/admin.py
from django.contrib import admin
from .models import Gallery, Image, Profile
import uuid


class ImageInline(admin.TabularInline):  # Или используйте admin.StackedInline для другого вида
    model = Image
    extra = 1  # Количество пустых форм для новых изображений


class GalleryInline(admin.TabularInline):  # Или используйте admin.StackedInline для другого вида
    model = Gallery
    extra = 3  # Количество пустых форм для новых изображений


class GalleryAdmin(admin.ModelAdmin):
    inlines = [ImageInline, ]
    change_form_template = 'admin/photomanager/galleries/change_form.html'

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        images = request.FILES.getlist('images')
        for image_file in images:
            Image.objects.create(
                gallery=form.instance,
                image=image_file,
                hashpath=uuid.uuid4().hex
            )


class ProfileAdmin(admin.ModelAdmin):
    inlines = [GalleryInline, ]
    change_form_template = 'admin/photomanager/galleries/change_form.html'


admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Image)
