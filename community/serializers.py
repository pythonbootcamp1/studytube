from rest_framework import serializers
from .models import Question, Answer
from accounts.serializers import UserSerializer
from videos.serializers import VideoListSerializer


class AnswerSerializer(serializers.ModelSerializer):
    """답변 Serializer"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'question', 'user', 'content',
            'is_accepted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_accepted', 'created_at', 'updated_at']


class AnswerCreateSerializer(serializers.ModelSerializer):
    """답변 생성 Serializer"""

    class Meta:
        model = Answer
        fields = ['question', 'content']

    def validate_content(self, value):
        """내용 검증"""
        if len(value) < 10:
            raise serializers.ValidationError('답변 내용은 10자 이상이어야 합니다.')
        return value

    def create(self, validated_data):
        """답변 생성"""
        # user는 view에서 전달
        return Answer.objects.create(**validated_data)


class QuestionListSerializer(serializers.ModelSerializer):
    """질문 목록 Serializer"""

    user = UserSerializer(read_only=True)
    video = VideoListSerializer(read_only=True)
    answers_count = serializers.IntegerField(source='answers.count', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'user', 'video', 'title', 'content',
            'is_answered', 'answers_count', 'views_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'is_answered', 'views_count',
            'created_at', 'updated_at'
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    """질문 상세 Serializer"""

    user = UserSerializer(read_only=True)
    video = VideoListSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    accepted_answer = AnswerSerializer(read_only=True)
    answers_count = serializers.IntegerField(source='answers.count', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'user', 'video', 'title', 'content',
            'is_answered', 'accepted_answer', 'answers', 'answers_count',
            'views_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'is_answered', 'accepted_answer',
            'views_count', 'created_at', 'updated_at'
        ]


class QuestionCreateSerializer(serializers.ModelSerializer):
    """질문 생성 Serializer"""

    class Meta:
        model = Question
        fields = ['video', 'title', 'content']

    def validate_title(self, value):
        """제목 검증"""
        if len(value) < 5:
            raise serializers.ValidationError('제목은 5자 이상이어야 합니다.')
        return value

    def validate_content(self, value):
        """내용 검증"""
        if len(value) < 10:
            raise serializers.ValidationError('내용은 10자 이상이어야 합니다.')
        return value

    def create(self, validated_data):
        """질문 생성"""
        # user는 view에서 전달
        return Question.objects.create(**validated_data)
