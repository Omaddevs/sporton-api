from django.db import models


class PromoBanner(models.Model):
    """Bosh sahifa va boshqa joylar uchun aksiya / promo karusel bannerlari."""

    class Target(models.TextChoices):
        NONE = 'none', "Hech qayerga"
        EXPLORE = 'explore', 'Xarita (Explore)'
        FAVORITE = 'favorite', 'Sevimlilar'
        HOME = 'home', 'Bosh sahifa'
        EXTERNAL = 'external', 'Tashqi havola'

    title = models.CharField(max_length=200, verbose_name='Sarlavha')
    subtitle = models.CharField(max_length=400, blank=True, default='', verbose_name='Pod sarlavha')
    cta_text = models.CharField(max_length=80, default="Ko'rish", verbose_name='Tugma matni')
    image = models.ImageField(
        upload_to='banners/',
        blank=True,
        null=True,
        verbose_name='O‘ng tomondagi rasm',
        help_text='Ixtiyoriy. Bo‘lmasa faqat matn va gradient ko‘rinadi.',
    )
    bg_color_start = models.CharField(
        max_length=32,
        default='#0078FF',
        verbose_name='Gradient boshlanishi (hex)',
    )
    bg_color_end = models.CharField(
        max_length=32,
        default='#004aad',
        verbose_name='Gradient tugashi (hex)',
    )
    target = models.CharField(
        max_length=20,
        choices=Target.choices,
        default=Target.NONE,
        verbose_name='Tugma bosilganda',
    )
    link_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
        verbose_name='Tashqi havola',
        help_text="Faqat «Tashqi havola» tanlanganida ishlatiladi.",
    )
    sort_order = models.PositiveIntegerField(default=0, verbose_name='Tartib', db_index=True)
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name = 'Promo banner'
        verbose_name_plural = 'Promo bannerlar'

    def __str__(self):
        return self.title
