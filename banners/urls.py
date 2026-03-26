from django.urls import path

from .views import PromoBannerListView

urlpatterns = [
    path('', PromoBannerListView.as_view(), name='promo_banner_list'),
]
