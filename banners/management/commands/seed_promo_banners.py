from django.core.management.base import BaseCommand

from banners.models import PromoBanner


class Command(BaseCommand):
    help = 'Bitta demo promo banner yaratadi (agar hali bo‘lmasa).'

    def handle(self, *args, **options):
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
