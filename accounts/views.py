import os

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import GoogleLoginSerializer, LoginSerializer, RegisterSerializer, ProfileUpdateSerializer

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

User = get_user_model()


def user_to_payload(user):
    return {
        'id': user.id,
        'username': user.username,
        'fullName': user.full_name or user.get_full_name(),
        'email': user.email,
        'provider': user.provider,
        'avatar': None,
    }


def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'user': user_to_payload(user),
                **tokens_for_user(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response(
            {
                'user': user_to_payload(user),
                **tokens_for_user(user),
            },
            status=status.HTTP_200_OK,
        )


class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_token_str = serializer.validated_data['id_token']

        client_id_from_req = serializer.validated_data.get('client_id')
        client_id = client_id_from_req or os.environ.get('GOOGLE_OAUTH_CLIENT_ID') or ''
        
        if not client_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Set GOOGLE_OAUTH_CLIENT_ID env var or pass client_id in request for Google login.")

        try:
            decoded = google_id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                audience=client_id,
            )
        except Exception as e:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(str(e))

        email = decoded.get('email') or ''
        full_name = decoded.get('name') or decoded.get('given_name') or ''
        google_sub = decoded.get('sub') or None

        if not email or not google_sub:
            raise ValueError('Invalid Google token payload.')

        user = User.objects.filter(provider='google', google_sub=google_sub).first()

        if not user:
            # Create new user (ensure unique username)
            base_username = email.split('@')[0] or 'google_user'
            candidate = base_username
            i = 1
            while User.objects.filter(username=candidate).exists():
                i += 1
                candidate = f'{base_username}{i}'

            user = User.objects.create_user(
                username=candidate,
                email=email,
                password=None,
                full_name=full_name,
                provider='google',
                google_sub=google_sub,
            )
        else:
            user.provider = 'google'
            user.full_name = full_name or user.full_name
            user.email = user.email or email
            user.google_sub = google_sub
            user.save()

        return Response(
            {
                'user': user_to_payload(user),
                **tokens_for_user(user),
            },
            status=status.HTTP_200_OK,
        )

class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = ProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.update(request.user, serializer.validated_data)
        return Response({'user': user_to_payload(request.user)}, status=status.HTTP_200_OK)

class AdminUsersListView(APIView):
    """Admin uchun: barcha ro'yxatdan o'tgan foydalanuvchilar ro'yxati."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser or request.user.username == 'admin'):
            return Response({'detail': 'Ruxsat yo\'q'}, status=403)
        users = User.objects.all().order_by('username').values('id', 'username', 'full_name', 'email')
        return Response({'users': list(users)})

from django.shortcuts import render

# Create your views here.
