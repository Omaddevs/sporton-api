from django.urls import path

from .views import GoogleLoginView, LoginView, RegisterView, ProfileUpdateView, AdminUsersListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('google/', GoogleLoginView.as_view(), name='google_login'),
    path('me/', ProfileUpdateView.as_view(), name='profile_me'),
    path('users/', AdminUsersListView.as_view(), name='admin_users_list'),
]
