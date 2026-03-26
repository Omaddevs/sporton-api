from django.contrib import admin

from .models import PromoBanner


@admin.register(PromoBanner)
class PromoBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'target', 'sort_order', 'is_active', 'created_at')
    list_filter = ('is_active', 'target')
    list_editable = ('sort_order', 'is_active')
    ordering = ('sort_order', '-created_at')
    search_fields = ('title', 'subtitle')
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'cta_text', 'image'),
        }),
        ('Ko‘rinish', {
            'fields': ('bg_color_start', 'bg_color_end'),
        }),
        ('Havola', {
            'fields': ('target', 'link_url'),
        }),
        ('Joylashuv', {
            'fields': ('sort_order', 'is_active'),
        }),
    )
