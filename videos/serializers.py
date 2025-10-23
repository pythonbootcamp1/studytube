from rest_framework import serializers
from .models import Video, VideoCompletion
from categories.models import Category, Tag
from accounts.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """카테고리 Serializer"""

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon']


class TagSerializer(serializers.ModelSerializer):
    """태그 Serializer"""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class VideoListSerializer(serializers.ModelSerializer):
    """영상 목록용 Serializer (간단한 정보)"""

    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'thumbnail',
            'instructor', 'category', 'tags',
            'duration', 'view_count', 'likes_count',
            'comments_count', 'rating_avg', 'is_public',
            'created_at', 'updated_at'
        ]


class VideoDetailSerializer(serializers.ModelSerializer):
    """영상 상세용 Serializer"""

    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'video_file', 'thumbnail',
            'instructor', 'category', 'tags',
            'duration', 'view_count', 'likes_count',
            'comments_count', 'rating_avg', 'is_public',
            'created_at', 'updated_at'
        ]


class VideoCreateSerializer(serializers.ModelSerializer):
    """영상 생성/수정용 Serializer"""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Video
        fields = [
            'title', 'description', 'video_file', 'thumbnail',
            'category', 'tags', 'duration', 'is_public'
        ]

    def validate_title(self, value):
        """제목 검증"""
        if len(value) < 2:
            raise serializers.ValidationError('제목은 2자 이상이어야 합니다.')
        return value

    def validate_description(self, value):
        """설명 검증"""
        if len(value) < 10:
            raise serializers.ValidationError('설명은 10자 이상이어야 합니다.')
        return value

    def create(self, validated_data):
        """영상 생성"""
        tags_data = validated_data.pop('tags', [])

        # instructor는 현재 로그인한 사용자
        video = Video.objects.create(
            instructor=self.context['request'].user,
            **validated_data
        )

        # 태그 추가
        if tags_data:
            video.tags.set(tags_data)

        return video

    def update(self, instance, validated_data):
        """영상 수정"""
        tags_data = validated_data.pop('tags', None)

        # 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 태그 업데이트
        if tags_data is not None:
            instance.tags.set(tags_data)

        return instance


class VideoCompletionSerializer(serializers.ModelSerializer):
    """완강 체크 Serializer"""

    video = VideoListSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = VideoCompletion
        fields = [
            'id', 'user', 'video', 'is_completed',
            'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'video', 'created_at', 'updated_at']
