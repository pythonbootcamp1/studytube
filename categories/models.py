from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class Category(models.Model):
    """영상 카테고리"""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='카테고리명'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='슬러그'
    )
    description = models.TextField(
        blank=True,
        verbose_name='설명'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text='이모지 또는 아이콘 클래스명',
        verbose_name='아이콘'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리 목록'
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        """모델 레벨 검증"""
        super().clean()
        if self.name and len(self.name) < 2:
            raise ValidationError({'name': '카테고리명은 2자 이상이어야 합니다.'})

    def save(self, *args, **kwargs):
        # 슬러그 자동 생성
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        self.full_clean()
        super().save(*args, **kwargs)


class Tag(models.Model):
    """영상 태그"""

    name = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='태그명'
    )
    slug = models.SlugField(
        max_length=30,
        unique=True,
        verbose_name='슬러그'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '태그'
        verbose_name_plural = '태그 목록'
        ordering = ['name']

    def __str__(self):
        return f"#{self.name}"

    def clean(self):
        """모델 레벨 검증"""
        super().clean()
        if self.name and len(self.name) < 2:
            raise ValidationError({'name': '태그명은 2자 이상이어야 합니다.'})

    def save(self, *args, **kwargs):
        # 슬러그 자동 생성
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        self.full_clean()
        super().save(*args, **kwargs)
