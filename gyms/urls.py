from django.urls import path
from .views import GymDetailView, GymListView, GymRateView, GymCategoriesView

urlpatterns = [
    path('', GymListView.as_view(), name='gym_list'),
    path('categories/', GymCategoriesView.as_view(), name='gym_categories'),
    path('<int:gym_id>/', GymDetailView.as_view(), name='gym_detail'),
    path('<int:gym_id>/rate/', GymRateView.as_view(), name='gym_rate'),
]
