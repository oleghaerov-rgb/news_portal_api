from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .viewsets import NewsViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('news', NewsViewSet, basename='news')

urlpatterns = [
    path('', include(router.urls)),
]
