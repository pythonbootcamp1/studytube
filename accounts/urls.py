from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    ProfileView,
    ChangePasswordView,
    UserDetailView
)

app_name = 'accounts'

urlpatterns = [
    # 회원가입
    path('register/', RegisterView.as_view(), name='register'),

    # 로그인 (JWT 토큰 발급)
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),

    # 토큰 갱신
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 프로필
    path('profile/', ProfileView.as_view(), name='profile'),

    # 비밀번호 변경
    path('password/change/', ChangePasswordView.as_view(), name='password_change'),

    # 사용자 프로필 조회 (공개)
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
]
