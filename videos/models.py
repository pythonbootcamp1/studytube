from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from categories.models import Category, Tag


def validate_video_size(file):
    """영상 파일 크기 검증 (500MB)"""
    max_size = getattr(settings, 'MAX_VIDEO_SIZE', 500 * 1024 * 1024)
    if file.size > max_size:
        raise ValidationError(f'영상 파일은 {max_size // (1024 * 1024)}MB 이하여야 합니다.')


def validate_image_size(file):
    """이미지 파일 크기 검증 (5MB)"""
    max_size = getattr(settings, 'MAX_IMAGE_SIZE', 5 * 1024 * 1024)
    if file.size > max_size:
        raise ValidationError(f'이미지 파일은 {max_size // (1024 * 1024)}MB 이하여야 합니다.')


class Video(models.Model):
    """영상 강의 모델"""

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='videos',
        verbose_name='강사'
    )
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2)],
        verbose_name='제목'
    )
    description = models.TextField(
        verbose_name='설명'
    )
    video_file = models.FileField(
        upload_to='videos/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['mp4', 'webm', 'avi']),
            validate_video_size
        ],
        verbose_name='영상 파일'
    )
    thumbnail = models.ImageField(
        upload_to='thumbnails/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ],
        verbose_name='썸네일'
    )
    duration = models.PositiveIntegerField(
        default=0,
        help_text='영상 길이 (초 단위)',
        verbose_name='영상 길이'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='videos',
        verbose_name='카테고리'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='videos',
        verbose_name='태그'
    )

    # 통계 필드
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='조회수'
    )
    likes_count = models.PositiveIntegerField(
        default=0,
        verbose_name='좋아요 수'
    )
    comments_count = models.PositiveIntegerField(
        default=0,
        verbose_name='댓글 수'
    )
    rating_avg = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name='평균 평점'
    )

    # 공개 설정
    is_public = models.BooleanField(
        default=True,
        verbose_name='공개 여부'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '영상'
        verbose_name_plural = '영상 목록'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor', '-created_at']),
            models.Index(fields=['is_public', '-created_at']),
            models.Index(fields=['-view_count']),
            models.Index(fields=['-rating_avg']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """모델 레벨 검증"""
        super().clean()

        # 제목 길이 검증
        if self.title and len(self.title) < 2:
            raise ValidationError({'title': '제목은 2자 이상이어야 합니다.'})

        # 설명 길이 검증
        if self.description and len(self.description) < 10:
            raise ValidationError({'description': '설명은 10자 이상이어야 합니다.'})

        # 강사 역할 검증
        if self.instructor and self.instructor.role not in ['instructor', 'admin']:
            raise ValidationError({'instructor': '강사 또는 관리자만 영상을 업로드할 수 있습니다.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class VideoCompletion(models.Model):
    """영상 완강 체크"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='completed_videos',
        verbose_name='사용자'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='completions',
        verbose_name='영상'
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name='완강 여부'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='완강일'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '완강 체크'
        verbose_name_plural = '완강 체크 목록'
        unique_together = [['user', 'video']]
        ordering = ['-updated_at']

    def __str__(self):
        status = "완강" if self.is_completed else "미완강"
        return f"{self.user.username} - {self.video.title} ({status})"
