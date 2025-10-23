from django.contrib import admin
from .models import VideoRating, Comment, Follow


@admin.register(VideoRating)
class VideoRatingAdmin(admin.ModelAdmin):
    """영상 평가 Admin"""

    list_display = ['user', 'video', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'video__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """댓글 Admin"""

    list_display = ['user', 'video', 'content_preview', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'video__title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['parent']

    def content_preview(self, obj):
        """내용 미리보기"""
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = '내용'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """팔로우 Admin"""

    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
    readonly_fields = ['created_at']
