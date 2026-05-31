from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('news_app.api_urls')),
    path('api/token/', obtain_auth_token, name='api_token'),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('news_app.urls')),
]
