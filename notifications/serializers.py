from rest_framework import serializers

from .models import Notification, NotificationRecipient


class NotificationListSerializer(serializers.ModelSerializer):
    isRead = serializers.SerializerMethodField()
    readAt = serializers.SerializerMethodField()
    fromUser = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'createdAt', 'isRead', 'readAt', 'fromUser']

    def get_isRead(self, obj):
        user = self.context.get('request').user
        rec = NotificationRecipient.objects.filter(notification=obj, user=user).only('is_read').first()
        return bool(rec and rec.is_read)

    def get_readAt(self, obj):
        user = self.context.get('request').user
        rec = NotificationRecipient.objects.filter(notification=obj, user=user).only('read_at').first()
        return rec.read_at if rec else None

    def get_fromUser(self, obj):
        if not obj.from_user:
            return None
        return {'id': obj.from_user_id, 'username': obj.from_user.username}


class AdminSendSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120, required=False, default='Bildirishnoma')
    message = serializers.CharField()
    send_to = serializers.ChoiceField(
        choices=[('all', 'all'), ('selected', 'selected')],
        required=False,
        default='all',
    )
    # Comma-separated usernames (AbstractUser.username)
    selected_usernames = serializers.CharField(required=False, allow_blank=True, default='')
    # Optional numeric ids (frontend hozircha ishlatmaydi, lekin backendni kengaytirish uchun qoldirdik)
    selected_user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
    )

    def validate(self, attrs):
        send_to = attrs.get('send_to', 'all')
        if send_to == 'selected':
            usernames = (attrs.get('selected_usernames') or '').strip()
            ids = attrs.get('selected_user_ids') or []
            if not usernames and not ids:
                raise serializers.ValidationError(
                    {'selected_usernames': 'Tanlash rejimida kamida 1 ta user ko\'rsatilishi kerak.'}
                )
        return attrs

