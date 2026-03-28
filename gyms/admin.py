from django import forms
from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from django.utils.html import format_html
import re

from sporton_backend.admin_mixins import SuperuserDeleteOnlyMixin, SuperuserOnlyModelAdminMixin
from .models import Gym, GymCategory, GymImage, GymRating, GymView


# ── GymCategory admin (news Category kabi) ───────────────────────────────────

@admin.register(GymCategory)
class GymCategoryAdmin(SuperuserOnlyModelAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'icon', 'name', 'slug', 'gym_count', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    def gym_count(self, obj):
        return obj.gyms.count()
    gym_count.short_description = 'Zallar soni'


# ── GymImage Inline (iau-backend NewsGalleryImageInline kabi) ─────────────────

class GymImageInline(admin.TabularInline):
    model = GymImage
    extra = 1          # 1 ta bo'sh qator (news kabi) — "Add another" bilan ko'paytirishingiz mumkin
    max_num = 20       # maksimal 20 ta rasm

    def has_add_permission(self, request, obj=None):
        return bool(request.user.is_active and request.user.is_superuser)

    def has_change_permission(self, request, obj=None):
        return bool(request.user.is_active and request.user.is_superuser)

    def has_delete_permission(self, request, obj=None):
        return bool(request.user.is_active and request.user.is_superuser)
    fields = ('image', 'caption', 'order', 'preview')
    readonly_fields = ('preview',)
    ordering = ('order', 'id')
    show_change_link = False

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:70px;border-radius:6px;border:2px solid #dbeffe;" />',
                obj.image.url,
            )
        return "—"
    preview.short_description = "Ko'rinish"


# ── GymAdminForm ──────────────────────────────────────────────────────────────

class GymAdminForm(forms.ModelForm):
    sports_text = forms.CharField(
        required=False,
        label='Sport turlari',
        help_text='Vergul bilan yozing: gym,running,pilates',
    )
    facilities_text = forms.CharField(
        required=False,
        label='Imkoniyatlar',
        help_text='Vergul bilan yozing: shower,parking,wifi,locker,ac,cardio,strength,sauna,pool,cafe',
    )

    monthly_price = forms.CharField(
        required=False,
        label="Oylik narx (so'm)",
        help_text="Misol: 400000 yoki 400.000 yoki 400,000 yoki 400 000",
    )
    entry_price = forms.CharField(
        required=False,
        label="Kirish narxi (so'm)",
        help_text="Misol: 50000 yoki 50.000",
    )

    telegram_url = forms.CharField(
        required=False,
        label='Telegram havolasi',
        help_text="Ixtiyoriy. Masalan: https://t.me/username — bo'sh bo'lsa ilovada tugma ko'rinmaydi.",
        widget=forms.URLInput(attrs={'style': 'width:100%', 'placeholder': 'https://t.me/...'}),
    )
    instagram_url = forms.CharField(
        required=False,
        label='Instagram havolasi',
        help_text="Ixtiyoriy. Masalan: https://www.instagram.com/username/",
        widget=forms.URLInput(attrs={'style': 'width:100%', 'placeholder': 'https://instagram.com/...'}),
    )

    def _parse_price(self, value):
        """400.000 / 400,000 / 400 000 / 400-000 → 400000 (int)"""
        if not value:
            return 0
        cleaned = re.sub(r'[\s.,_\-]', '', str(value))
        try:
            return int(cleaned)
        except ValueError:
            raise forms.ValidationError("Narxni to'g'ri kiriting, masalan: 400000 yoki 400.000")

    def clean_monthly_price(self):
        return self._parse_price(self.cleaned_data.get('monthly_price'))

    def clean_entry_price(self):
        return self._parse_price(self.cleaned_data.get('entry_price'))

    class Meta:
        model = Gym
        exclude = ('sports', 'facilities', 'images')
        widgets = {
            'google_maps_url': forms.URLInput(attrs={'style': 'width:100%'}),
            'yandex_maps_url': forms.URLInput(attrs={'style': 'width:100%'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'categories': CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.instance
        if isinstance(getattr(inst, 'sports', None), list) and inst.sports:
            self.fields['sports_text'].initial = ','.join(map(str, inst.sports))
        if isinstance(getattr(inst, 'facilities', None), list) and inst.facilities:
            self.fields['facilities_text'].initial = ','.join(map(str, inst.facilities))

    def _parse_comma_list(self, raw):
        if not raw:
            return []
        return [p.strip().lower() for p in re.split(r'[,\n\r]+', raw) if p.strip()]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.sports = self._parse_comma_list(self.cleaned_data.get('sports_text') or '')
        instance.facilities = self._parse_comma_list(self.cleaned_data.get('facilities_text') or '')
        if instance.monthly_price is None:
            instance.monthly_price = 0
        if instance.entry_price is None:
            instance.entry_price = 0
        if commit:
            instance.save()
            self.save_m2m()
        return instance


# ── GymAdmin ─────────────────────────────────────────────────────────────────

@admin.register(Gym)
class GymAdmin(SuperuserOnlyModelAdminMixin, admin.ModelAdmin):
    form = GymAdminForm
    inlines = [GymImageInline]

    list_display = ('id', 'cover_thumb', 'name', 'district', 'rating', 'is_open', 'images_count')
    list_display_links = ('id', 'name')
    list_filter = ('is_open', 'region')
    search_fields = ('name', 'district', 'address')
    readonly_fields = ('cover_thumb',)

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name', 'district', 'region', 'address', 'phone', 'description'),
        }),
        ("Kategoriyalar", {
            'fields': ('categories',),
            'classes': ('wide',),
        }),
        ("Narxlar va vaqt", {
            'fields': ('monthly_price', 'entry_price', 'hours', 'is_open'),
        }),
        ("Sport va imkoniyatlar", {
            'fields': ('sports_text', 'facilities_text'),
        }),
        ("Ko'rinish", {
            'fields': ('gradient', 'accent_color', 'cover_thumb'),
        }),
        ("Joylashuv va ijtimoiy tarmoqlar", {
            'fields': (
                'lat', 'lng',
                'google_maps_url', 'yandex_maps_url',
                'telegram_url', 'instagram_url',
            ),
            'description': "Telegram va Instagram ixtiyoriy — faqat to'ldirilganlari mobil ilovada pastki tugmalar sifatida chiqadi.",
        }),
    )

    def cover_thumb(self, obj):
        first = obj.gallery_images.first()
        if first and first.image:
            return format_html(
                '<img src="{}" style="height:55px;border-radius:6px;" />',
                first.image.url,
            )
        return "—"
    cover_thumb.short_description = "Rasm"

    def images_count(self, obj):
        return obj.gallery_images.count()
    images_count.short_description = "Rasmlar"


# ── GymImage standalone admin ────────────────────────────────────────────────

@admin.register(GymImage)
class GymImageAdmin(SuperuserOnlyModelAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'gym', 'preview', 'caption', 'order')
    list_select_related = ('gym',)
    list_filter = ('gym',)
    ordering = ('gym', 'order')

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;border-radius:4px;" />',
                obj.image.url,
            )
        return "—"
    preview.short_description = "Ko'rinish"


# ── GymRating admin ──────────────────────────────────────────────────────────

@admin.register(GymRating)
class GymRatingAdmin(SuperuserDeleteOnlyMixin, admin.ModelAdmin):
    list_display = ('id', 'gym', 'user', 'stars_display', 'short_comment', 'created_at')
    list_filter = ('score', 'gym')
    search_fields = ('gym__name', 'user__username', 'comment')
    readonly_fields = ('gym', 'user', 'score', 'comment', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    def stars_display(self, obj):
        filled = '★' * obj.score
        empty  = '☆' * (5 - obj.score)
        colors = {1: '#ef4444', 2: '#f97316', 3: '#eab308', 4: '#84cc16', 5: '#22c55e'}
        color  = colors.get(obj.score, '#9ca3af')
        return format_html(
            '<span style="font-size:16px;color:{};letter-spacing:1px;">{}</span>'
            '<span style="color:#d1d5db;">{}</span>',
            color, filled, empty,
        )
    stars_display.short_description = 'Baho'

    def short_comment(self, obj):
        if not obj.comment:
            return format_html('<span style="color:#d1d5db;">— izoh yo\'q —</span>')
        text = obj.comment[:80]
        if len(obj.comment) > 80:
            text += '…'
        return text
    short_comment.short_description = 'Sharh'

    def has_add_permission(self, request):
        return False


# ── GymView admin ────────────────────────────────────────────────────────────

@admin.register(GymView)
class GymViewAdmin(SuperuserDeleteOnlyMixin, admin.ModelAdmin):
    list_display = ('id', 'gym', 'ip_address', 'viewed_at')
    list_filter = ('gym',)
    readonly_fields = ('gym', 'ip_address', 'viewed_at')
    ordering = ('-viewed_at',)

    def has_add_permission(self, request):
        return False
