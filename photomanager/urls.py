# urls.py
from django.urls import path
from .views import ProfileDetailView, ProfileListView, serve_image

urlpatterns = [

    # path('gallery/<str:hashpath>', GalleryDetailView.as_view()),

    # path('profile/<str:hashpath>', ProfileDetailView.as_view()),

    # path('profiles', ProfileListView.as_view()),

    # path('<path:image_path>', serve_image, name='serve_image'),
    # path('<str:folder>/<str:filename>', serve_image, name='serve_image'),
    # http://127.0.0.1:8000/
    # /api
    # /img
    # /7f699ea93b3ff306148e/7f699ea93b3ff306148e.jpg


]

