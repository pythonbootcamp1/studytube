from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from videos.models import Video


class Question(models.Model):
    """Q&A 질문"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='작성자'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='questions',
        verbose_name='관련 영상',
        help_text='특정 영상 관련 질문일 경우'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='제목'
    )
    content = models.TextField(
        verbose_name='내용'
    )
    is_answered = models.BooleanField(
        default=False,
        verbose_name='답변 완료 여부'
    )
    accepted_answer = models.OneToOneField(
        'Answer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_for',
        verbose_name='채택된 답변'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='조회수'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '질문'
        verbose_name_plural = '질문 목록'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['video', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """모델 레벨 검증"""
        super().clean()

        if self.title and len(self.title) < 5:
            raise ValidationError({'title': '제목은 5자 이상이어야 합니다.'})

        if self.content and len(self.content) < 10:
            raise ValidationError({'content': '내용은 10자 이상이어야 합니다.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Answer(models.Model):
    """Q&A 답변"""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='질문'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='작성자'
    )
    content = models.TextField(
        verbose_name='내용'
    )
    is_accepted = models.BooleanField(
        default=False,
        verbose_name='채택 여부'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '답변'
        verbose_name_plural = '답변 목록'
        ordering = ['-is_accepted', 'created_at']

    def __str__(self):
        status = " (채택됨)" if self.is_accepted else ""
        return f"{self.question.title}에 대한 답변{status}"

    def clean(self):
        """모델 레벨 검증"""
        super().clean()

        if self.content and len(self.content) < 10:
            raise ValidationError({'content': '답변 내용은 10자 이상이어야 합니다.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
