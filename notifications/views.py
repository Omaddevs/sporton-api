from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification, NotificationRecipient
from .serializers import AdminSendSerializer, NotificationListSerializer

User = get_user_model()


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(request.user.is_staff or request.user.is_superuser or request.user.username == 'admin')


class NotificationsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(recipients__user=request.user).distinct().order_by('-created_at')
        serializer = NotificationListSerializer(qs, many=True, context={'request': request})
        unread_count = NotificationRecipient.objects.filter(user=request.user, is_read=False).count()
        # Frontend wants newest first.
        return Response(
            {
                'items': serializer.data,
                'count': len(serializer.data),
                'unreadCount': unread_count,
            },
            status=status.HTTP_200_OK,
        )


class NotificationsMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ids = request.data.get('ids', None)
        now = timezone.now()

        recs = NotificationRecipient.objects.filter(user=request.user)
        if ids:
            recs = recs.filter(notification_id__in=ids)

        recs = recs.filter(is_read=False)
        recs.update(is_read=True, read_at=now)
        unread_count = NotificationRecipient.objects.filter(user=request.user, is_read=False).count()
        return Response({'ok': True, 'unreadCount': unread_count}, status=status.HTTP_200_OK)


class NotificationsDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ids = request.data.get('ids', None)
        recs = NotificationRecipient.objects.filter(user=request.user)
        if ids:
            recs = recs.filter(notification_id__in=ids)
        recs.delete()
        
        unread_count = NotificationRecipient.objects.filter(user=request.user, is_read=False).count()
        return Response({'ok': True, 'unreadCount': unread_count}, status=status.HTTP_200_OK)


class AdminSendNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = AdminSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        title = serializer.validated_data.get('title') or 'Bildirishnoma'
        message = serializer.validated_data['message']

        notification = Notification.objects.create(
            title=title,
            message=message,
            from_user=request.user if request.user.is_authenticated else None,
        )

        send_to = serializer.validated_data.get('send_to', 'all')
        selected_usernames = (serializer.validated_data.get('selected_usernames') or '').strip()
        selected_user_ids = serializer.validated_data.get('selected_user_ids') or []

        if send_to == 'selected':
            usernames = [u.strip() for u in selected_usernames.split(',') if u.strip()]
            # Username bilan ham, id bilan ham yuborish mumkin (ikkalasi birga bo'lsa birlashtiramiz).
            users_qs = User.objects.none()
            if usernames:
                users_qs = users_qs | User.objects.filter(username__in=usernames)
            if selected_user_ids:
                users_qs = users_qs | User.objects.filter(id__in=selected_user_ids)
            users = users_qs.distinct()
        else:
            users = User.objects.all()

        users = users.order_by('id')

        # recipients: NotificationRecipient per-user
        recipients = [NotificationRecipient(notification=notification, user=u) for u in users]
        NotificationRecipient.objects.bulk_create(
            recipients,
            batch_size=200,
            ignore_conflicts=True
        )

        return Response(
            {
                'ok': True,
                'notificationId': notification.id,
                'sentTo': users.count(),
            },
            status=status.HTTP_201_CREATED,
        )

from django.shortcuts import render

# Create your views here.
