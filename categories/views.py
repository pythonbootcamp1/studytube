from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Category, Tag
from .serializers import (
    CategorySerializer,
    CategoryCreateSerializer,
    TagSerializer,
    TagCreateSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """관리자만 생성/수정/삭제 가능, 일반 사용자는 읽기만 가능"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # is_staff, is_superuser 또는 role이 'admin'인 경우 허용
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser or request.user.role == 'admin')
        )


class CategoryViewSet(viewsets.ModelViewSet):
    """카테고리 ViewSet"""

    queryset = Category.objects.annotate(videos_count=Count('videos'))
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        """액션별 Serializer 선택"""
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateSerializer
        return CategorySerializer

    @extend_schema(
        tags=['카테고리/태그'],
        summary='카테고리 목록 조회',
        description='모든 카테고리 목록을 조회합니다.',
        responses={
            200: OpenApiResponse(response=CategorySerializer(many=True))
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['카테고리/태그'],
        summary='카테고리 상세 조회',
        description='특정 카테고리의 상세 정보를 조회합니다.',
        responses={
            200: OpenApiResponse(response=CategorySerializer),
            404: OpenApiResponse(description='카테고리를 찾을 수 없음')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=['카테고리/태그'],
        summary='카테고리 생성',
        description='새 카테고리를 생성합니다. (관리자만 가능)',
        request=CategoryCreateSerializer,
        responses={
            201: OpenApiResponse(response=CategorySerializer, description='카테고리 생성 성공'),
            400: OpenApiResponse(description='잘못된 요청'),
            403: OpenApiResponse(description='권한 없음')
        }
    )
    def create(self, request, *args, **kwargs):
        """카테고리 생성"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return Response(
            CategorySerializer(category).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        tags=['카테고리/태그'],
        summary='카테고리 수정',
        description='카테고리 정보를 수정합니다. (관리자만 가능)',
        request=CategoryCreateSerializer,
        responses={
            200: OpenApiResponse(response=CategorySerializer),
            400: OpenApiResponse(description='잘못된 요청'),
            403: OpenApiResponse(description='권한 없음'),
            404: OpenApiResponse(description='카테고리를 찾을 수 없음')
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=['카테고리/태그'],
        summary='카테고리 삭제',
        description='카테고리를 삭제합니다. (관리자만 가능)',
        responses={
            204: OpenApiResponse(description='삭제 성공'),
            403: OpenApiResponse(description='권한 없음'),
            404: OpenApiResponse(description='카테고리를 찾을 수 없음')
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class TagViewSet(viewsets.ModelViewSet):
    """태그 ViewSet"""

    queryset = Tag.objects.annotate(videos_count=Count('videos'))
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        """액션별 Serializer 선택"""
        if self.action in ['create', 'update', 'partial_update']:
            return TagCreateSerializer
        return TagSerializer

    def get_queryset(self):
        """queryset 최적화"""
        queryset = super().get_queryset()

        # 인기 태그 정렬 (영상 수 기준)
        if self.request.query_params.get('popular'):
            queryset = queryset.order_by('-videos_count')

        return queryset

    @extend_schema(
        tags=['카테고리/태그'],
        summary='태그 목록 조회',
        description='모든 태그 목록을 조회합니다. ?popular=true 옵션으로 인기 태그 순으로 정렬 가능',
        responses={
            200: OpenApiResponse(response=TagSerializer(many=True))
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['카테고리/태그'],
        summary='태그 상세 조회',
        description='특정 태그의 상세 정보를 조회합니다.',
        responses={
            200: OpenApiResponse(response=TagSerializer),
            404: OpenApiResponse(description='태그를 찾을 수 없음')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=['카테고리/태그'],
        summary='태그 생성',
        description='새 태그를 생성합니다. (관리자만 가능)',
        request=TagCreateSerializer,
        responses={
            201: OpenApiResponse(response=TagSerializer, description='태그 생성 성공'),
            400: OpenApiResponse(description='잘못된 요청'),
            403: OpenApiResponse(description='권한 없음')
        }
    )
    def create(self, request, *args, **kwargs):
        """태그 생성"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tag = serializer.save()

        return Response(
            TagSerializer(tag).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        tags=['카테고리/태그'],
        summary='태그 수정',
        description='태그 정보를 수정합니다. (관리자만 가능)',
        request=TagCreateSerializer,
        responses={
            200: OpenApiResponse(response=TagSerializer),
            400: OpenApiResponse(description='잘못된 요청'),
            403: OpenApiResponse(description='권한 없음'),
            404: OpenApiResponse(description='태그를 찾을 수 없음')
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=['카테고리/태그'],
        summary='태그 삭제',
        description='태그를 삭제합니다. (관리자만 가능)',
        responses={
            204: OpenApiResponse(description='삭제 성공'),
            403: OpenApiResponse(description='권한 없음'),
            404: OpenApiResponse(description='태그를 찾을 수 없음')
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=['카테고리/태그'],
        summary='인기 태그 조회',
        description='영상 수가 많은 인기 태그 순으로 조회합니다.',
        responses={
            200: OpenApiResponse(response=TagSerializer(many=True))
        }
    )
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """인기 태그 조회 (영상 수 기준)"""
        limit = int(request.query_params.get('limit', 10))
        tags = self.get_queryset().order_by('-videos_count')[:limit]

        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)
