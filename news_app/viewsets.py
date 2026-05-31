from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import News
from .permissions import IsAuthorOrReadOnly, IsSelfOrAdminOrReadOnly
from .serializers import NewsSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['id', 'username']

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSelfOrAdminOrReadOnly()]
        return [AllowAny()]


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.select_related('author').order_by('-date_created')
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author']
    search_fields = ['title', 'summary', 'content', 'author__username']
    ordering_fields = ['date_created', 'date_updated', 'title']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
