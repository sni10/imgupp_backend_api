from django.db import models
from django.utils import timezone
import uuid

# Create your models here.


class DownloadLink(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    # Связь с пользователем (если нужно)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def is_valid(self):
        """Проверяет, активна ли ссылка и не истек ли её срок."""
        return self.is_active and self.expires_at > timezone.now()
