# urls.py
from django.urls import path
from .views import ProfileDetailView, ProfileListView, serve_image, GalleryDetailView

urlpatterns = [
    path('profiles', ProfileListView.as_view(), name='profile-list'),
    path('profile/<str:hashpath>', ProfileDetailView.as_view(), name='profile-detail'),
    path('gallery/<str:hashpath>', GalleryDetailView.as_view(), name='gallery-detail'),

    # Serve images with folder/filename structure
    # URL format: /api/img/<folder>/<filename>
    path('<str:folder>/<str:filename>', serve_image, name='serve-image'),
]

