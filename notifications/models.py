from django.conf import settings
from django.db import models


class Notification(models.Model):
    title = models.CharField(max_length=120, default='Bildirishnoma')
    message = models.TextField()
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sent_notifications',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '1. Yuborish uchun Xabar'
        verbose_name_plural = '1. Yuborish uchun Xabarlar'

    def __str__(self):
        return f'{self.title} ({self.id})'


class NotificationRecipient(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_items')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['notification', 'user'], name='unique_notification_recipient'),
        ]
        verbose_name = '2. Qabul qiluvchi (Kim o\'qidi?)'
        verbose_name_plural = '2. Qabul qiluvchilar (Hisobot)'

    def __str__(self):
        return f'{self.user_id} -> {self.notification_id} ({self.is_read})'


