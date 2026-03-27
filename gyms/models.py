from django.db import models
from django.utils.text import slugify


class GymCategory(models.Model):
    """
    Zal kategoriyalari — iau-backend/news/Category kabi tuzilgan.
    Misol: Fitness, Yoga, Boks, Kurash, Plavanie, MMA ...
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nomi")
    slug = models.SlugField(max_length=120, unique=True, blank=True,
                            help_text="Avtomatik to'ldiriladi")
    icon = models.CharField(
        max_length=80, blank=True, default='',
        verbose_name="Ikonka (emoji yoki key)",
        help_text="Masalan: 💪 yoki 'gym', 'yoga', 'boxing'"
    )
    description = models.TextField(blank=True, verbose_name="Tavsif")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Tartib")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Zal kategoriyasi"
        verbose_name_plural = "Zal kategoriyalari"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Gym(models.Model):

    name = models.CharField(max_length=255, verbose_name="Zal nomi")
    district = models.CharField(max_length=120, verbose_name="Tuman")
    region = models.CharField(max_length=120, blank=True, default='Toshkent viloyati', verbose_name="Viloyat")
    address = models.CharField(max_length=255, blank=True, default='', verbose_name="Manzil")
    phone = models.CharField(max_length=40, blank=True, default='', verbose_name="Telefon")

    rating = models.FloatField(default=0, verbose_name="Reyting")
    reviews_count = models.IntegerField(default=0, verbose_name="Sharhlar soni")
    description = models.TextField(blank=True, default='', verbose_name="Tavsif")

    monthly_price = models.IntegerField(default=0, verbose_name="Oylik narx (so'm)")
    entry_price = models.IntegerField(default=0, verbose_name="Kirish narxi (so'm)")
    hours = models.CharField(max_length=80, blank=True, default='', verbose_name="Ish vaqti")
    is_open = models.BooleanField(default=True, verbose_name="Ochiqmi?")

    facilities = models.JSONField(default=list, blank=True, verbose_name="Imkoniyatlar")
    sports = models.JSONField(default=list, blank=True, verbose_name="Sport turlari")
    categories = models.ManyToManyField(
        'GymCategory',
        blank=True,
        related_name='gyms',
        verbose_name="Kategoriyalar",
    )

    gradient = models.CharField(max_length=255, blank=True, default='', verbose_name="Fon gradient")
    accent_color = models.CharField(max_length=80, blank=True, default='#0078FF', verbose_name="Rang")

    lat = models.FloatField(default=0, verbose_name="Kenglik (lat)")
    lng = models.FloatField(default=0, verbose_name="Uzunlik (lng)")

    # Eski JSON field — backwards compat uchun qoldirildi (endi GymImage ishlatiladi)
    images = models.JSONField(default=list, blank=True, editable=False)

    google_maps_url = models.CharField(max_length=1000, blank=True, default='', verbose_name="Google Maps havolasi")
    yandex_maps_url = models.CharField(max_length=1000, blank=True, default='', verbose_name="Yandex Maps havolasi")
    telegram_url = models.URLField(max_length=500, blank=True, default='', verbose_name="Telegram")
    instagram_url = models.URLField(max_length=500, blank=True, default='', verbose_name="Instagram")

    liked_by = models.ManyToManyField(
        'accounts.User',
        blank=True,
        related_name='liked_gyms',
        verbose_name="Yoqtirgan foydalanuvchilar"
    )

    class Meta:
        ordering = ['-rating']
        verbose_name = "Zal (Gym)"
        verbose_name_plural = "Zallar (Gyms)"

    def __str__(self):
        return self.name


class GymImage(models.Model):
    """
    Gym uchun galereya rasmlari — iau-backend/news/NewsGalleryImage kabi tuzilgan.
    Admin panelda TabularInline orqali bevosita rasm yuklanadi.
    """
    gym = models.ForeignKey(
        Gym,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name="Zal",
    )
    image = models.ImageField(
        upload_to='gyms/gallery/',
        verbose_name="Rasm",
    )
    caption = models.CharField(max_length=255, blank=True, verbose_name="Izoh (ixtiyoriy)")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Tartib raqam")

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Zal rasmi"
        verbose_name_plural = "Zal rasmlari"

    def __str__(self):
        return f"{self.gym.name} — rasm #{self.order or self.id}"


class GymRating(models.Model):
    """Har bir foydalanuvchi bitta zalga 1 marta baho va izoh qoldirishi mumkin."""
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='user_ratings')
    user = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='gym_ratings'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Baho (1-5)",
        choices=[(i, str(i)) for i in range(1, 6)],
    )
    comment = models.TextField(
        blank=True, default='',
        verbose_name="Izoh (sharh)",
        help_text="Foydalanuvchi qoldirgan sharh matni",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('gym', 'user')
        verbose_name = "Sharh va baho"
        verbose_name_plural = "Sharhlar va baholar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} → {self.gym.name}: {self.score}★"


class GymView(models.Model):
    """Har bir unique IP bitta zalga 1 marta ko'rishni hisoblaydi."""
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='unique_views')
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('gym', 'ip_address')
        verbose_name = "Ko'rish"
        verbose_name_plural = "Ko'rishlar"

    def __str__(self):
        return f"{self.ip_address} → {self.gym.name}"
