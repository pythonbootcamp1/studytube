from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    UserSerializer
)
from .models import User


@extend_schema(
    tags=['인증'],
    summary='회원가입',
    description='새로운 사용자 계정을 생성합니다.',
    responses={
        201: OpenApiResponse(
            response=UserSerializer,
            description='회원가입 성공'
        ),
        400: OpenApiResponse(description='잘못된 요청 (검증 실패)')
    }
)
class RegisterView(generics.CreateAPIView):
    """회원가입 View"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                'message': '회원가입이 완료되었습니다.',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=['인증'],
    summary='로그인',
    description='JWT 토큰을 발급받습니다.',
    responses={
        200: OpenApiResponse(description='로그인 성공, access/refresh 토큰 반환'),
        401: OpenApiResponse(description='인증 실패')
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """커스텀 로그인 View (JWT 토큰 발급)"""
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    tags=['인증'],
    summary='내 프로필 조회/수정',
    description='인증된 사용자의 프로필을 조회하거나 수정합니다.',
    responses={
        200: OpenApiResponse(
            response=UserProfileSerializer,
            description='프로필 조회/수정 성공'
        ),
        401: OpenApiResponse(description='인증되지 않음')
    }
)
class ProfileView(generics.RetrieveUpdateAPIView):
    """프로필 조회/수정 View"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(
    tags=['인증'],
    summary='비밀번호 변경',
    description='현재 비밀번호를 확인하고 새로운 비밀번호로 변경합니다.',
    responses={
        200: OpenApiResponse(description='비밀번호 변경 성공'),
        400: OpenApiResponse(description='잘못된 요청 (검증 실패)'),
        401: OpenApiResponse(description='인증되지 않음')
    }
)
class ChangePasswordView(APIView):
    """비밀번호 변경 View"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'message': '비밀번호가 성공적으로 변경되었습니다.'},
            status=status.HTTP_200_OK
        )


@extend_schema(
    tags=['사용자'],
    summary='사용자 프로필 조회',
    description='특정 사용자의 공개 프로필을 조회합니다.',
    responses={
        200: OpenApiResponse(
            response=UserSerializer,
            description='사용자 프로필 조회 성공'
        ),
        404: OpenApiResponse(description='사용자를 찾을 수 없음')
    }
)
class UserDetailView(generics.RetrieveAPIView):
    """사용자 프로필 조회 View (공개)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
