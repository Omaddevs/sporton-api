from rest_framework import serializers

from .models import PromoBanner


class PromoBannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    gradient = serializers.SerializerMethodField()

    class Meta:
        model = PromoBanner
        fields = (
            'id',
            'title',
            'subtitle',
            'cta_text',
            'image_url',
            'gradient',
            'bg_color_start',
            'bg_color_end',
            'target',
            'link_url',
            'sort_order',
        )

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        url = obj.image.url
        if request:
            return request.build_absolute_uri(url)
        return url

    def get_gradient(self, obj):
        a = obj.bg_color_start or '#0078FF'
        b = obj.bg_color_end or '#004aad'
        return f'linear-gradient(135deg, {a} 0%, {b} 100%)'
