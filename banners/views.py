from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from .models import PromoBanner
from .serializers import PromoBannerSerializer


class PromoBannerListView(APIView):
    """Jamoat uchun faol bannerlar ro‘yxati."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        # Show banners only after an actual image is uploaded.
        qs = (
            PromoBanner.objects
            .filter(is_active=True)
            .filter(Q(image__isnull=False) & ~Q(image=''))
            .order_by('sort_order', '-created_at')
        )
        ser = PromoBannerSerializer(qs, many=True, context={'request': request})
        return Response({'items': ser.data})
