from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


def validate_image_size(file):
    """이미지 파일 크기 검증 (5MB)"""
    from django.conf import settings
    max_size = getattr(settings, 'MAX_IMAGE_SIZE', 5 * 1024 * 1024)
    if file.size > max_size:
        raise ValidationError(f'이미지 파일은 {max_size // (1024 * 1024)}MB 이하여야 합니다.')


class User(AbstractUser):
    """커스텀 사용자 모델"""

    ROLE_CHOICES = (
        ('student', '수강생'),
        ('instructor', '강사'),
        ('admin', '관리자'),
    )

    # 기본 필드 (username, email, password는 AbstractUser에서 상속)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='역할'
    )
    is_premium = models.BooleanField(
        default=False,
        verbose_name='프리미엄 회원'
    )
    profile_image = models.ImageField(
        upload_to='profiles/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ],
        verbose_name='프로필 이미지'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='자기소개'
    )

    # 통계 필드
    followers_count = models.PositiveIntegerField(
        default=0,
        verbose_name='팔로워 수'
    )
    following_count = models.PositiveIntegerField(
        default=0,
        verbose_name='팔로잉 수'
    )
    videos_count = models.PositiveIntegerField(
        default=0,
        verbose_name='업로드한 영상 수'
    )

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def clean(self):
        """모델 레벨 검증"""
        super().clean()
        if self.bio and len(self.bio) > 500:
            raise ValidationError({'bio': '자기소개는 500자 이하로 작성해주세요.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
