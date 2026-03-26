from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Frontend uses `fullName` + `username` and a simplified provider model.
    """

    provider = models.CharField(
        max_length=16,
        default='email',
        choices=[('email', 'email'), ('google', 'google')],
    )
    full_name = models.CharField(max_length=255, blank=True, default='')
    google_sub = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

