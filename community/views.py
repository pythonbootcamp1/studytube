from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django_filters.rest_framework import DjangoFilterBackend

from .models import Question, Answer
from .serializers import (
    QuestionListSerializer,
    QuestionDetailSerializer,
    QuestionCreateSerializer,
    AnswerSerializer,
    AnswerCreateSerializer
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """작성자만 수정/삭제 가능"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class QuestionViewSet(viewsets.ModelViewSet):
    """질문 ViewSet"""

    queryset = Question.objects.select_related('user', 'video', 'accepted_answer').prefetch_related('answers')
    serializer_class = QuestionDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['video', 'is_answered', 'user']

    def get_serializer_class(self):
        """액션별 Serializer 선택"""
        if self.action == 'list':
            return QuestionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return QuestionCreateSerializer
        return QuestionDetailSerializer

    def get_queryset(self):
        """queryset 최적화"""
        queryset = super().get_queryset()

        # video_id 파라미터가 있으면 필터링
        video_id = self.request.query_params.get('video_id')
        if video_id:
            queryset = queryset.filter(video_id=video_id)

        return queryset.order_by('-created_at')

    @extend_schema(
        tags=['커뮤니티'],
        summary='질문 작성',
        request=QuestionCreateSerializer,
        responses={
            201: OpenApiResponse(response=QuestionDetailSerializer, description='질문 작성 성공'),
            400: OpenApiResponse(description='잘못된 요청'),
            401: OpenApiResponse(description='인증되지 않음')
        }
    )
    def create(self, request, *args, **kwargs):
        """질문 작성"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save(user=request.user)

        return Response(
            QuestionDetailSerializer(question).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        tags=['커뮤니티'],
        summary='질문 조회',
        description='질문 상세 정보를 조회하고 조회수를 증가시킵니다.',
        responses={
            200: OpenApiResponse(response=QuestionDetailSerializer),
            404: OpenApiResponse(description='질문을 찾을 수 없음')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """질문 조회 (조회수 증가)"""
        instance = self.get_object()

        # 조회수 증가
        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        tags=['커뮤니티'],
        summary='답변 채택',
        description='질문 작성자가 답변을 채택합니다.',
        request=None,
        responses={
            200: OpenApiResponse(description='답변 채택 성공'),
            400: OpenApiResponse(description='잘못된 요청'),
            403: OpenApiResponse(description='권한 없음 (질문 작성자만 가능)'),
            404: OpenApiResponse(description='답변을 찾을 수 없음')
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept_answer(self, request, pk=None):
        """답변 채택"""
        question = self.get_object()

        # 질문 작성자만 채택 가능
        if question.user != request.user:
            return Response(
                {'error': '질문 작성자만 답변을 채택할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        answer_id = request.data.get('answer_id')
        if not answer_id:
            return Response(
                {'error': '채택할 답변 ID를 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 답변 확인
        try:
            answer = Answer.objects.get(id=answer_id, question=question)
        except Answer.DoesNotExist:
            return Response(
                {'error': '해당 질문의 답변을 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 기존 채택 답변이 있으면 해제
        if question.accepted_answer:
            old_answer = question.accepted_answer
            old_answer.is_accepted = False
            old_answer.save()

        # 새 답변 채택
        answer.is_accepted = True
        answer.save()

        question.accepted_answer = answer
        question.is_answered = True
        question.save()

        return Response(
            {
                'message': '답변이 채택되었습니다.',
                'question': QuestionDetailSerializer(question).data
            },
            status=status.HTTP_200_OK
        )


class AnswerViewSet(viewsets.ModelViewSet):
    """답변 ViewSet"""

    queryset = Answer.objects.select_related('user', 'question')
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question', 'user', 'is_accepted']

    def get_serializer_class(self):
        """액션별 Serializer 선택"""
        if self.action in ['create', 'update', 'partial_update']:
            return AnswerCreateSerializer
        return AnswerSerializer

    def get_queryset(self):
        """queryset 최적화"""
        queryset = super().get_queryset()

        # question_id 파라미터가 있으면 필터링
        question_id = self.request.query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)

        return queryset.order_by('-is_accepted', 'created_at')

    @extend_schema(
        tags=['커뮤니티'],
        summary='답변 작성',
        request=AnswerCreateSerializer,
        responses={
            201: OpenApiResponse(response=AnswerSerializer, description='답변 작성 성공'),
            400: OpenApiResponse(description='잘못된 요청'),
            401: OpenApiResponse(description='인증되지 않음')
        }
    )
    def create(self, request, *args, **kwargs):
        """답변 작성"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = serializer.save(user=request.user)

        return Response(
            AnswerSerializer(answer).data,
            status=status.HTTP_201_CREATED
        )
