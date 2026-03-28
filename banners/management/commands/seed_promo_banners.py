import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from banners.models import PromoBanner


class Command(BaseCommand):
    help = 'Bitta demo promo banner yaratadi (agar hali bo‘lmasa). Faqat DEBUG yoki ALLOW_SEED_COMMANDS.'

    def handle(self, *args, **options):
        allow = os.environ.get('ALLOW_SEED_COMMANDS', '').lower() in ('1', 'true', 'yes')
        if not settings.DEBUG and not allow:
            raise CommandError(
                'Ishlab chiqarishda bannerni seed qilish o‘chirilgan. '
                '/admin/ dan qo‘shing yoki ALLOW_SEED_COMMANDS=1 bilan ishga tushiring.'
            )
        if PromoBanner.objects.exists():
            self.stdout.write(self.style.WARNING('Bannerlar allaqachon bor — o‘tkazib yuborildi.'))
            return

        PromoBanner.objects.create(
            title="Yozgi mavsumga 30% chegirma!",
            subtitle="Cheklangan vaqt. Sport zallarni hoziroq ko'ring.",
            cta_text="Xaritada ko'rish",
            target=PromoBanner.Target.EXPLORE,
            bg_color_start='#0078FF',
            bg_color_end='#004aad',
            sort_order=0,
            is_active=True,
        )
        self.stdout.write(self.style.SUCCESS('Demo promo banner qo‘shildi. Admin: /admin/banners/promobanner/'))
