# Create your views here.
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DownloadLink
from .serializers import DownloadLinkSerializer


class CreateLinkView(APIView):
    def post(self, request, *args, **kwargs):
        # Устанавливаем срок действия ссылки на 1 час от текущего времени
        expires_at = timezone.now() + timedelta(hours=1)
        link = DownloadLink.objects.create(expires_at=expires_at)
        serializer = DownloadLinkSerializer(link)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrieveLinkView(APIView):
    def get(self, request, uuid, *args, **kwargs):
        link = get_object_or_404(DownloadLink, uuid=uuid)
        if link.is_valid():
            serializer = DownloadLinkSerializer(link)
            return Response(serializer.data)
        else:
            return Response({"message": "Ссылка недействительна или истек срок действия."}, status=404)
