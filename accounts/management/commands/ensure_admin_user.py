import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Lokal uchun default admin (faqat DEBUG yoki ALLOW_ENSURE_ADMIN=1).'

    def handle(self, *args, **options):
        if not settings.DEBUG and os.environ.get('ALLOW_ENSURE_ADMIN') != '1':
            raise CommandError(
                'Ishlab chiqarishda default admin yaratish bloklangan. '
                'python manage.py createsuperuser ishlating yoki ALLOW_ENSURE_ADMIN=1.'
            )
        User = get_user_model()
        username = 'admin'
        password = 'admin123'

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'full_name': 'Admin',
                'provider': 'email',
                'is_staff': True,
                'is_superuser': True,
                'email': 'admin@example.com',
            },
        )

        if not user.password:
            user.set_password(password)
            user.save()

        if created:
            self.stdout.write(self.style.SUCCESS('Admin user created. Password: admin123'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin user already exists.'))

