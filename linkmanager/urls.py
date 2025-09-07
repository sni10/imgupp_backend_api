from django.urls import path
from .views import CreateLinkView, RetrieveLinkView

urlpatterns = [
    path('links/create/', CreateLinkView.as_view(), name='create_link'),
    path('links/<uuid:uuid>/', RetrieveLinkView.as_view(), name='retrieve_link'),
]
