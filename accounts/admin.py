from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """커스텀 사용자 Admin"""

    list_display = [
        'username', 'email', 'role', 'is_premium',
        'followers_count', 'following_count', 'videos_count',
        'profile_image_preview', 'is_active', 'date_joined'
    ]
    list_filter = ['role', 'is_premium', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['followers_count', 'following_count', 'videos_count', 'date_joined', 'last_login']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {
            'fields': ('role', 'is_premium', 'profile_image', 'bio')
        }),
        ('통계', {
            'fields': ('followers_count', 'following_count', 'videos_count')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('추가 정보', {
            'fields': ('role', 'is_premium', 'profile_image', 'bio')
        }),
    )

    def profile_image_preview(self, obj):
        """프로필 이미지 미리보기"""
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_image.url
            )
        return '-'
    profile_image_preview.short_description = '프로필 이미지'
