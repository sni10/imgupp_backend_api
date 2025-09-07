from rest_framework import serializers
from .models import DownloadLink


class DownloadLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadLink
        fields = ['uuid', 'expires_at', 'is_active']
        # Здесь можно добавить дополнительные поля, если необходимо
