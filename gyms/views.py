import re

from django.db.models import Avg, Q
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Gym, GymCategory, GymRating, GymView
from .serializers import GymCategorySerializer, GymSerializer


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def parse_bool(val):
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in {'1', 'true', 'yes', 'y', 'on'}:
        return True
    if s in {'0', 'false', 'no', 'n', 'off'}:
        return False
    return None


class GymListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        region = request.query_params.get('region', '').strip()
        district = request.query_params.get('district', '').strip()
        sport = request.query_params.get('sport', '').strip()
        category = request.query_params.get('category', '').strip()
        openNow = parse_bool(request.query_params.get('openNow'))
        minRating = request.query_params.get('minRating', '').strip()
        minReviews = request.query_params.get('minReviews', '').strip()
        priceBand = request.query_params.get('priceBand', 'any')

        qs = Gym.objects.all()

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(district__icontains=q) | Q(address__icontains=q))

        if region:
            qs = qs.filter(region=region)
        if district:
            qs = qs.filter(district=district)
        if category:
            qs = qs.filter(categories__slug=category)
        if openNow is not None:
            qs = qs.filter(is_open=openNow)

        if priceBand == 'lt300':
            qs = qs.filter(monthly_price__lt=300000)
        elif priceBand == '300-450':
            qs = qs.filter(monthly_price__gte=300000, monthly_price__lte=450000)
        elif priceBand == 'gt450':
            qs = qs.filter(monthly_price__gt=450000)

        if minRating:
            try:
                qs = qs.filter(rating__gte=float(minRating))
            except ValueError:
                pass

        if minReviews:
            try:
                qs = qs.filter(reviews_count__gte=int(minReviews))
            except ValueError:
                pass

        gyms = list(qs.distinct())

        if sport:
            gyms = [g for g in gyms if sport in (g.sports or [])]

        gyms.sort(key=lambda g: (-g.rating, -g.reviews_count))

        serializer = GymSerializer(gyms, many=True, context={'request': request})
        return Response({'items': serializer.data, 'count': len(serializer.data)}, status=200)


class GymDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, gym_id):
        gym = Gym.objects.filter(id=gym_id).first()
        if not gym:
            return Response({'detail': 'Not found'}, status=404)

        # Ko'rishlar sonini hisoblash (unique IP per gym — news kabi)
        ip = get_client_ip(request)
        _, created = GymView.objects.get_or_create(gym=gym, ip_address=ip)
        if created:
            Gym.objects.filter(pk=gym.pk).update(
                views_count=GymView.objects.filter(gym=gym).count()
            )
            gym.refresh_from_db()

        serializer = GymSerializer(gym, context={'request': request})
        return Response(serializer.data, status=200)


class GymRateView(APIView):
    """Foydalanuvchi zalga 1-5 baho + izoh qoldiradi. O'rtacha avtomatik hisoblanadi."""
    permission_classes = [IsAuthenticated]

    def post(self, request, gym_id):
        gym = Gym.objects.filter(id=gym_id).first()
        if not gym:
            return Response({'detail': 'Zal topilmadi'}, status=404)

        score = request.data.get('score')
        comment = str(request.data.get('comment', '') or '').strip()
        try:
            score = int(score)
            if not (1 <= score <= 5):
                raise ValueError()
        except (TypeError, ValueError):
            return Response({'detail': "score 1-5 orasida bo'lishi kerak"}, status=400)

        rating_obj, created = GymRating.objects.update_or_create(
            gym=gym,
            user=request.user,
            defaults={'score': score, 'comment': comment},
        )

        # O'rtacha reytingni va izohlar sonini yangilash
        rating_count = GymRating.objects.filter(gym=gym).count()
        avg = GymRating.objects.filter(gym=gym).aggregate(a=Avg('score'))['a'] or 0
        rating_percent = round((avg / 5) * 100)
        
        Gym.objects.filter(pk=gym.pk).update(
            rating=round(avg, 1),
            reviews_count=rating_count
        )
        gym.refresh_from_db()

        return Response({
            'ok': True,
            'yourScore': score,
            'yourComment': comment,
            'newRating': gym.rating,
            'ratingPercent': rating_percent,
            'ratingCount': rating_count,
        })

    def get(self, request, gym_id):
        """Foydalanuvchining oldingi baho va izohini qaytaradi."""
        gym = Gym.objects.filter(id=gym_id).first()
        if not gym:
            return Response({'detail': 'Zal topilmadi'}, status=404)

        rating_obj = GymRating.objects.filter(gym=gym, user=request.user).first()
        return Response({
            'yourScore': rating_obj.score if rating_obj else None,
            'yourComment': rating_obj.comment if rating_obj else '',
            'rating': gym.rating,
            'ratingPercent': round((gym.rating / 5) * 100) if gym.rating else 0,
        })


class GymLikeView(APIView):
    """Zalni yoqtirganlar ro'yxatiga qo'shish yoki olib tashlash (toggle)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, gym_id):
        gym = Gym.objects.filter(id=gym_id).first()
        if not gym:
            return Response({'detail': 'Zal topilmadi'}, status=404)
        
        if request.user in gym.liked_by.all():
            gym.liked_by.remove(request.user)
            liked = False
        else:
            gym.liked_by.add(request.user)
            liked = True
            
        return Response({'liked': liked})

class GymCategoriesView(APIView):
    """Barcha sport kategoriyalarini qaytaradi."""
    permission_classes = [AllowAny]

    def get(self, request):
        cats = GymCategory.objects.all().order_by('order', 'name')
        serializer = GymCategorySerializer(cats, many=True)
        return Response({'categories': serializer.data})
