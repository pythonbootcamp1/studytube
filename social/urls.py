from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, FollowViewSet

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'follows', FollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
]
