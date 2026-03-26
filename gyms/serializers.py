from rest_framework import serializers
from .models import Gym, GymCategory, GymImage, GymRating


class GymCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GymCategory
        fields = ['id', 'name', 'slug', 'icon', 'order']


class GymImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = GymImage
        fields = ['id', 'url', 'caption', 'order']

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            url = obj.image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class GymReviewSerializer(serializers.ModelSerializer):
    """Bitta foydalanuvchi sharhi — baho + izoh + kimdan."""
    username = serializers.SerializerMethodField()
    fullName = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='updated_at', format='%d.%m.%Y')

    class Meta:
        model = GymRating
        fields = ['id', 'username', 'fullName', 'score', 'comment', 'date']

    def get_username(self, obj):
        return obj.user.username if obj.user else ''

    def get_fullName(self, obj):
        user = obj.user
        if not user:
            return ''
        full = f"{user.first_name} {user.last_name}".strip()
        return full or user.username


class GymSerializer(serializers.ModelSerializer):
    monthlyPrice = serializers.IntegerField(source='monthly_price')
    entryPrice = serializers.IntegerField(source='entry_price')
    reviewsCount = serializers.IntegerField(source='reviews_count')
    isOpen = serializers.BooleanField(source='is_open')
    accentColor = serializers.CharField(source='accent_color')
    googleMapsUrl = serializers.CharField(source='google_maps_url', allow_blank=True, required=False)
    yandexMapsUrl = serializers.CharField(source='yandex_maps_url', allow_blank=True, required=False)
    images = serializers.SerializerMethodField()
    categories = GymCategorySerializer(many=True, read_only=True)
    ratingCount = serializers.SerializerMethodField()
    ratingPercent = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Gym
        fields = [
            'id', 'name', 'district', 'region', 'address', 'phone',
            'rating', 'reviewsCount', 'ratingCount', 'ratingPercent',
            'description', 'monthlyPrice', 'entryPrice', 'hours', 'isOpen',
            'facilities', 'sports', 'categories', 'gradient', 'accentColor',
            'lat', 'lng', 'images', 'googleMapsUrl', 'yandexMapsUrl',
            'reviews',
        ]

    def get_images(self, obj):
        request = self.context.get('request')
        result = []
        for img in obj.gallery_images.order_by('order', 'id'):
            if img.image:
                url = img.image.url
                if request:
                    url = request.build_absolute_uri(url)
                result.append(url)
        return result

    def get_ratingCount(self, obj):
        return obj.user_ratings.count()

    def get_ratingPercent(self, obj):
        """0-100 oralig'ida umumiy reyting foizi (5 = 100%)."""
        if not obj.rating:
            return 0
        return round((obj.rating / 5) * 100)

    def get_reviews(self, obj):
        qs = obj.user_ratings.select_related('user').order_by('-updated_at')[:50]
        return GymReviewSerializer(qs, many=True).data
