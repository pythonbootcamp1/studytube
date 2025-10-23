"""
URL configuration for StudyTube project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/videos/', include('videos.urls')),
    path('api/social/', include('social.urls')),
    path('api/qna/', include('community.urls')),
    path('api/', include('categories.urls')),
    # path('api/analytics/', include('analytics.urls')),

    # 테스트 페이지
    path('test-video/', TemplateView.as_view(template_name='video_test.html'), name='video_test'),
]

# Media files serving (개발 환경에서만)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
