from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django_filters.rest_framework import DjangoFilterBackend

from .models import Comment, VideoRating, Follow
from .serializers import (
    CommentSerializer,
    CommentCreateSerializer,
    VideoRatingSerializer,
    FollowSerializer
)
from accounts.models import User
from accounts.serializers import UserSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """작성자만 수정/삭제 가능"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class CommentViewSet(viewsets.ModelViewSet):
    """댓글 ViewSet"""

    queryset = Comment.objects.select_related('user', 'video').prefetch_related('replies')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['video', 'parent']

    def get_serializer_class(self):
        """액션별 Serializer 선택"""
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        """최상위 댓글만 조회 (대댓글 제외)"""
        queryset = super().get_queryset()

        # video_id 파라미터가 있으면 필터링
        video_id = self.request.query_params.get('video_id')
        if video_id:
            queryset = queryset.filter(video_id=video_id)

        # 기본적으로 최상위 댓글만 (parent가 None인 것)
        if self.action == 'list':
            queryset = queryset.filter(parent__isnull=True)

        return queryset.order_by('created_at')

    @extend_schema(
        tags=['소셜'],
        summary='댓글 작성',
        description='영상에 댓글을 작성합니다.',
        request=CommentCreateSerializer,
        responses={
            201: OpenApiResponse(response=CommentSerializer, description='댓글 작성 성공'),
            400: OpenApiResponse(description='잘못된 요청'),
            401: OpenApiResponse(description='인증되지 않음')
        }
    )
    def create(self, request, *args, **kwargs):
        """댓글 작성"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(user=request.user)

        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        tags=['소셜'],
        summary='대댓글 작성',
        description='특정 댓글에 대한 대댓글을 작성합니다.',
        request=CommentCreateSerializer,
        responses={
            201: OpenApiResponse(response=CommentSerializer, description='대댓글 작성 성공'),
            400: OpenApiResponse(description='잘못된 요청'),
            401: OpenApiResponse(description='인증되지 않음')
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reply(self, request, pk=None):
        """대댓글 작성"""
        parent_comment = self.get_object()

        # 대댓글의 대댓글 방지
        if parent_comment.parent:
            return Response(
                {'error': '대댓글의 대댓글은 작성할 수 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CommentCreateSerializer(
            data={
                'video': parent_comment.video.id,
                'parent': parent_comment.id,
                'content': request.data.get('content')
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(user=request.user)

        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )


class FollowViewSet(viewsets.GenericViewSet):
    """팔로우 ViewSet"""

    queryset = Follow.objects.select_related('follower', 'following')
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['소셜'],
        summary='사용자 팔로우',
        description='특정 사용자를 팔로우합니다.',
        request=None,
        responses={
            201: OpenApiResponse(response=FollowSerializer, description='팔로우 성공'),
            400: OpenApiResponse(description='잘못된 요청 (자기 자신 팔로우 등)'),
            404: OpenApiResponse(description='사용자를 찾을 수 없음')
        }
    )
    @action(detail=False, methods=['post'])
    def follow_user(self, request):
        """사용자 팔로우"""
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': '팔로우할 사용자 ID를 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 자기 자신 팔로우 방지
        if str(request.user.id) == str(user_id):
            return Response(
                {'error': '자기 자신을 팔로우할 수 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 팔로우할 사용자 확인
        try:
            following_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': '사용자를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 이미 팔로우 중인지 확인
        if Follow.objects.filter(follower=request.user, following=following_user).exists():
            return Response(
                {'error': '이미 팔로우한 사용자입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 팔로우 생성
        follow = Follow.objects.create(
            follower=request.user,
            following=following_user
        )

        # 통계 업데이트
        request.user.following_count = Follow.objects.filter(follower=request.user).count()
        request.user.save()

        following_user.followers_count = Follow.objects.filter(following=following_user).count()
        following_user.save()

        return Response(
            {
                'message': f'{following_user.username}님을 팔로우했습니다.',
                'follow': FollowSerializer(follow).data
            },
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        tags=['소셜'],
        summary='사용자 언팔로우',
        description='특정 사용자를 언팔로우합니다.',
        request=None,
        responses={
            200: OpenApiResponse(description='언팔로우 성공'),
            404: OpenApiResponse(description='팔로우 기록을 찾을 수 없음')
        }
    )
    @action(detail=False, methods=['delete'])
    def unfollow_user(self, request):
        """사용자 언팔로우"""
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': '언팔로우할 사용자 ID를 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            following_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': '사용자를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            follow = Follow.objects.get(
                follower=request.user,
                following=following_user
            )
            follow.delete()

            # 통계 업데이트
            request.user.following_count = Follow.objects.filter(follower=request.user).count()
            request.user.save()

            following_user.followers_count = Follow.objects.filter(following=following_user).count()
            following_user.save()

            return Response(
                {'message': f'{following_user.username}님을 언팔로우했습니다.'},
                status=status.HTTP_200_OK
            )
        except Follow.DoesNotExist:
            return Response(
                {'error': '팔로우 기록을 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        tags=['소셜'],
        summary='팔로워 목록',
        description='특정 사용자의 팔로워 목록을 조회합니다.',
        responses={
            200: OpenApiResponse(response=UserSerializer(many=True)),
            404: OpenApiResponse(description='사용자를 찾을 수 없음')
        }
    )
    @action(detail=False, methods=['get'])
    def followers(self, request):
        """팔로워 목록"""
        user_id = request.query_params.get('user_id')

        if not user_id:
            # user_id가 없으면 현재 로그인한 사용자의 팔로워
            user = request.user
        else:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': '사용자를 찾을 수 없습니다.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # 해당 사용자를 팔로우하는 사람들
        followers = User.objects.filter(
            following_relations__following=user
        ).distinct()

        serializer = UserSerializer(followers, many=True)
        return Response({
            'count': followers.count(),
            'results': serializer.data
        })

    @extend_schema(
        tags=['소셜'],
        summary='팔로잉 목록',
        description='특정 사용자가 팔로우하는 사용자 목록을 조회합니다.',
        responses={
            200: OpenApiResponse(response=UserSerializer(many=True)),
            404: OpenApiResponse(description='사용자를 찾을 수 없음')
        }
    )
    @action(detail=False, methods=['get'])
    def following(self, request):
        """팔로잉 목록"""
        user_id = request.query_params.get('user_id')

        if not user_id:
            # user_id가 없으면 현재 로그인한 사용자가 팔로우하는 사람들
            user = request.user
        else:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': '사용자를 찾을 수 없습니다.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # 해당 사용자가 팔로우하는 사람들
        following = User.objects.filter(
            follower_relations__follower=user
        ).distinct()

        serializer = UserSerializer(following, many=True)
        return Response({
            'count': following.count(),
            'results': serializer.data
        })
