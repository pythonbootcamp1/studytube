from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from videos.models import Video


class VideoRating(models.Model):
    """영상 평가 (1-5점)"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='video_ratings',
        verbose_name='사용자'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='영상'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='평점'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '영상 평가'
        verbose_name_plural = '영상 평가 목록'
        unique_together = [['user', 'video']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.video.title}: {self.rating}점"

    def clean(self):
        """모델 레벨 검증"""
        super().clean()
        if self.rating < 1 or self.rating > 5:
            raise ValidationError({'rating': '평점은 1~5점 사이여야 합니다.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Comment(models.Model):
    """댓글 (대댓글 지원)"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='작성자'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='영상'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='부모 댓글'
    )
    content = models.TextField(
        verbose_name='내용'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글 목록'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['video', '-created_at']),
        ]

    def __str__(self):
        if self.parent:
            return f"{self.user.username} (대댓글): {self.content[:30]}"
        return f"{self.user.username}: {self.content[:30]}"

    def clean(self):
        """모델 레벨 검증"""
        super().clean()

        # 내용 길이 검증
        if self.content and len(self.content) < 1:
            raise ValidationError({'content': '댓글 내용을 입력해주세요.'})

        # 대댓글 깊이 제한 (1단계만 허용)
        if self.parent and self.parent.parent:
            raise ValidationError({'parent': '대댓글의 대댓글은 작성할 수 없습니다.'})

        # 대댓글은 같은 영상의 댓글에만 가능
        if self.parent and self.parent.video != self.video:
            raise ValidationError({'parent': '같은 영상의 댓글에만 답글을 달 수 있습니다.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Follow(models.Model):
    """팔로우 (사용자 간 팔로우)"""

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='팔로워'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='팔로잉'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '팔로우'
        verbose_name_plural = '팔로우 목록'
        unique_together = [['follower', 'following']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['follower', '-created_at']),
            models.Index(fields=['following', '-created_at']),
        ]

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"

    def clean(self):
        """모델 레벨 검증"""
        super().clean()

        # 자기 자신을 팔로우할 수 없음
        if self.follower == self.following:
            raise ValidationError('자기 자신을 팔로우할 수 없습니다.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
