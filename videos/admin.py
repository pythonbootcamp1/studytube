from django.contrib import admin
from django.utils.html import format_html
from .models import Video, VideoCompletion


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """영상 Admin"""

    list_display = [
        'title', 'instructor', 'category', 'thumbnail_preview',
        'duration_display', 'view_count', 'likes_count',
        'rating_avg', 'is_public', 'created_at'
    ]
    list_filter = ['is_public', 'category', 'created_at']
    search_fields = ['title', 'description', 'instructor__username']
    readonly_fields = [
        'view_count', 'likes_count', 'comments_count', 'rating_avg',
        'created_at', 'updated_at', 'thumbnail_preview'
    ]
    filter_horizontal = ['tags']

    fieldsets = (
        ('기본 정보', {
            'fields': ('instructor', 'title', 'description', 'category', 'tags')
        }),
        ('파일', {
            'fields': ('video_file', 'thumbnail', 'thumbnail_preview', 'duration')
        }),
        ('통계', {
            'fields': ('view_count', 'likes_count', 'comments_count', 'rating_avg')
        }),
        ('설정', {
            'fields': ('is_public',)
        }),
        ('날짜', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def thumbnail_preview(self, obj):
        """썸네일 미리보기"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="200" />',
                obj.thumbnail.url
            )
        return '-'
    thumbnail_preview.short_description = '썸네일 미리보기'

    def duration_display(self, obj):
        """영상 길이 표시 (시:분:초)"""
        hours = obj.duration // 3600
        minutes = (obj.duration % 3600) // 60
        seconds = obj.duration % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
    duration_display.short_description = '영상 길이'


@admin.register(VideoCompletion)
class VideoCompletionAdmin(admin.ModelAdmin):
    """완강 체크 Admin"""

    list_display = ['user', 'video', 'is_completed', 'completed_at', 'updated_at']
    list_filter = ['is_completed', 'completed_at']
    search_fields = ['user__username', 'video__title']
    readonly_fields = ['created_at', 'updated_at']
