from rest_framework import serializers
from .models import VideoRating, Comment, Follow
from accounts.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    """댓글 Serializer"""

    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'video', 'parent', 'content',
            'replies', 'replies_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_replies(self, obj):
        """대댓글 목록 (parent가 있는 경우 제외)"""
        if obj.parent:
            return []

        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_replies_count(self, obj):
        """대댓글 수"""
        if obj.parent:
            return 0
        return obj.replies.count()

    def validate_content(self, value):
        """내용 검증"""
        if len(value.strip()) < 1:
            raise serializers.ValidationError('댓글 내용을 입력해주세요.')
        return value


class CommentCreateSerializer(serializers.ModelSerializer):
    """댓글 생성 Serializer"""

    class Meta:
        model = Comment
        fields = ['video', 'parent', 'content']

    def validate(self, attrs):
        """검증"""
        video = attrs.get('video')
        parent = attrs.get('parent')

        # 대댓글인 경우
        if parent:
            # 대댓글의 대댓글 방지
            if parent.parent:
                raise serializers.ValidationError({
                    'parent': '대댓글의 대댓글은 작성할 수 없습니다.'
                })

            # 같은 영상의 댓글에만 답글 가능
            if parent.video != video:
                raise serializers.ValidationError({
                    'parent': '같은 영상의 댓글에만 답글을 달 수 있습니다.'
                })

        return attrs

    def create(self, validated_data):
        """댓글 생성"""
        return Comment.objects.create(
            # user=self.context['request'].user,
            **validated_data
        )


class VideoRatingSerializer(serializers.ModelSerializer):
    """영상 평가 Serializer"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = VideoRating
        fields = ['id', 'user', 'video', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        """평점 검증"""
        if value < 1 or value > 5:
            raise serializers.ValidationError('평점은 1~5점 사이여야 합니다.')
        return value


class FollowSerializer(serializers.ModelSerializer):
    """팔로우 Serializer"""

    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'follower', 'following', 'created_at']
