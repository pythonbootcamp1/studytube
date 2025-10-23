from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import F
from django.http import FileResponse, Http404, HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import os
import re

from .models import Video, VideoCompletion
from .serializers import (
    VideoListSerializer,
    VideoDetailSerializer,
    VideoCreateSerializer,
    VideoCompletionSerializer
)
from social.models import VideoRating
from social.serializers import VideoRatingSerializer


class IsInstructorOrReadOnly(permissions.BasePermission):
    """강사 또는 읽기 전용 권한"""

    def has_permission(self, request, view):
        # 읽기 권한은 모두 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 쓰기 권한은 인증된 사용자만
        if not request.user.is_authenticated:
            return False

        # 강사 또는 관리자만 영상 업로드 가능
        return request.user.role in ['instructor', 'admin']

    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모두 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 수정/삭제는 작성자 또는 관리자만
        return obj.instructor == request.user or request.user.is_staff


class VideoViewSet(viewsets.ModelViewSet):
    """영상 ViewSet"""

    queryset = Video.objects.select_related('instructor', 'category').prefetch_related('tags')
    permission_classes = [IsInstructorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'instructor', 'is_public']
    search_fields = ['title', 'description', 'instructor__username']
    ordering_fields = ['created_at', 'view_count', 'rating_avg', 'likes_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """액션별 Serializer 선택"""
        if self.action == 'list':
            return VideoListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return VideoCreateSerializer
        return VideoDetailSerializer

    def get_queryset(self):
        """쿼리셋 필터링"""
        queryset = super().get_queryset()

        # 로그인하지 않은 사용자는 공개 영상만 조회
        if not self.request.user.is_authenticated:
            return queryset.filter(is_public=True)

        # 본인 영상은 비공개도 조회 가능
        if self.action == 'list':
            return queryset.filter(
                is_public=True
            ) | queryset.filter(
                instructor=self.request.user
            )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """영상 상세 조회 (조회수 증가)"""
        instance = self.get_object()

        # 조회수 증가 (강사 본인 제외)
        if request.user != instance.instructor:
            Video.objects.filter(pk=instance.pk).update(
                view_count=F('view_count') + 1
            )
            instance.refresh_from_db()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        tags=['영상'],
        summary='완강 체크',
        description='영상을 완강으로 표시합니다.',
        responses={
            200: OpenApiResponse(description='완강 체크 성공'),
            401: OpenApiResponse(description='인증되지 않음')
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def complete(self, request, pk=None):
        """완강 체크"""
        video = self.get_object()
        completion, created = VideoCompletion.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={
                'is_completed': True,
                'completed_at': timezone.now()
            }
        )

        if not created:
            completion.is_completed = True
            completion.completed_at = timezone.now()
            completion.save()

        return Response(
            {
                'message': '완강 처리되었습니다.',
                'completion': VideoCompletionSerializer(completion).data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=['영상'],
        summary='완강 취소',
        description='완강 체크를 취소합니다.',
        responses={
            200: OpenApiResponse(description='완강 취소 성공'),
            404: OpenApiResponse(description='완강 기록을 찾을 수 없음')
        }
    )
    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def uncomplete(self, request, pk=None):
        """완강 취소"""
        video = self.get_object()

        try:
            completion = VideoCompletion.objects.get(
                user=request.user,
                video=video
            )
            completion.is_completed = False
            completion.completed_at = None
            completion.save()

            return Response(
                {'message': '완강이 취소되었습니다.'},
                status=status.HTTP_200_OK
            )
        except VideoCompletion.DoesNotExist:
            return Response(
                {'error': '완강 기록을 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        tags=['영상'],
        summary='내가 완강한 영상 목록',
        description='로그인한 사용자가 완강한 영상 목록을 조회합니다.',
        responses={
            200: OpenApiResponse(response=VideoListSerializer(many=True)),
            401: OpenApiResponse(description='인증되지 않음')
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_completed(self, request):
        """내가 완강한 영상 목록"""
        completed_videos = Video.objects.filter(
            completions__user=request.user,
            completions__is_completed=True
        ).select_related('instructor', 'category').prefetch_related('tags')

        page = self.paginate_queryset(completed_videos)
        if page is not None:
            serializer = VideoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = VideoListSerializer(completed_videos, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['영상'],
        summary='영상 스트리밍',
        description='영상 파일을 HTTP Range 요청으로 스트리밍합니다. 브라우저에서 영상 탐색(seek)을 지원합니다.',
        responses={
            200: OpenApiResponse(description='전체 파일 반환'),
            206: OpenApiResponse(description='부분 콘텐츠 반환 (Range 요청)'),
            404: OpenApiResponse(description='파일을 찾을 수 없음')
        }
    )
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def stream(self, request, pk=None):
        """영상 스트리밍 (HTTP Range 요청 지원)"""
        video = self.get_object()

        # 파일 존재 확인
        if not video.video_file:
            raise Http404('영상 파일이 존재하지 않습니다.')

        file_path = video.video_file.path
        if not os.path.exists(file_path):
            raise Http404('영상 파일을 찾을 수 없습니다.')

        # 파일 크기
        file_size = os.path.getsize(file_path)

        # Range 요청 헤더 파싱
        range_header = request.META.get('HTTP_RANGE', '').strip()

        if range_header:
            # Range 요청 처리
            range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2)) if range_match.group(2) else file_size - 1

                # 범위 검증
                if start >= file_size:
                    return HttpResponse(status=416)  # Range Not Satisfiable

                # 끝 범위 조정
                end = min(end, file_size - 1)
                length = end - start + 1

                # 파일 열기 및 시작 위치로 이동
                file_handle = open(file_path, 'rb')
                file_handle.seek(start)

                # Partial Content 응답 (206)
                response = FileResponse(
                    file_handle,
                    status=206,
                    content_type='video/mp4'
                )
                response['Content-Length'] = str(length)
                response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
                response['Accept-Ranges'] = 'bytes'

                return response

        # 일반 요청 (Range 헤더 없음) - 전체 파일 반환
        file_handle = open(file_path, 'rb')
        response = FileResponse(
            file_handle,
            content_type='video/mp4'
        )
        response['Content-Length'] = str(file_size)
        response['Accept-Ranges'] = 'bytes'

        return response

    @extend_schema(
        tags=['영상'],
        summary='영상 평가',
        description='영상에 1-5점 평점을 부여합니다. 이미 평가한 경우 수정됩니다.',
        request=VideoRatingSerializer,
        responses={
            200: OpenApiResponse(description='평가 수정 성공'),
            201: OpenApiResponse(description='평가 등록 성공'),
            401: OpenApiResponse(description='인증되지 않음')
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        """영상 평가 (1-5점)"""
        video = self.get_object()
        rating_value = request.data.get('rating')

        if not rating_value or not (1 <= int(rating_value) <= 5):
            return Response(
                {'error': '평점은 1~5점 사이여야 합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 기존 평가가 있으면 수정, 없으면 생성
        rating, created = VideoRating.objects.update_or_create(
            user=request.user,
            video=video,
            defaults={'rating': rating_value}
        )

        # 영상의 평균 평점 업데이트
        from django.db.models import Avg
        avg_rating = VideoRating.objects.filter(video=video).aggregate(Avg('rating'))['rating__avg']
        video.rating_avg = round(avg_rating, 2) if avg_rating else 0
        video.save()

        message = '평가가 등록되었습니다.' if created else '평가가 수정되었습니다.'
        return Response(
            {
                'message': message,
                'rating': VideoRatingSerializer(rating).data
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @extend_schema(
        tags=['영상'],
        summary='영상 평가 취소',
        description='내가 남긴 영상 평가를 삭제합니다.',
        responses={
            200: OpenApiResponse(description='평가 삭제 성공'),
            404: OpenApiResponse(description='평가 기록을 찾을 수 없음')
        }
    )
    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def unrate(self, request, pk=None):
        """영상 평가 취소"""
        video = self.get_object()

        try:
            rating = VideoRating.objects.get(user=request.user, video=video)
            rating.delete()

            # 영상의 평균 평점 업데이트
            from django.db.models import Avg
            avg_rating = VideoRating.objects.filter(video=video).aggregate(Avg('rating'))['rating__avg']
            video.rating_avg = round(avg_rating, 2) if avg_rating else 0
            video.save()

            return Response(
                {'message': '평가가 삭제되었습니다.'},
                status=status.HTTP_200_OK
            )
        except VideoRating.DoesNotExist:
            return Response(
                {'error': '평가 기록을 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )
