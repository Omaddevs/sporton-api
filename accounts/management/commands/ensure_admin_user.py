from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create default admin user for notifications (dev)'

    def handle(self, *args, **options):
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

