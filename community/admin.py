from django.contrib import admin
from .models import Question, Answer


class AnswerInline(admin.TabularInline):
    """질문 상세에서 답변 인라인 표시"""
    model = Answer
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """질문 Admin"""

    list_display = [
        'title', 'user', 'video', 'is_answered',
        'views_count', 'answer_count', 'created_at'
    ]
    list_filter = ['is_answered', 'created_at']
    search_fields = ['title', 'content', 'user__username']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    raw_id_fields = ['video', 'accepted_answer']
    inlines = [AnswerInline]

    def answer_count(self, obj):
        """답변 수"""
        return obj.answers.count()
    answer_count.short_description = '답변 수'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """답변 Admin"""

    list_display = ['question', 'user', 'content_preview', 'is_accepted', 'created_at']
    list_filter = ['is_accepted', 'created_at']
    search_fields = ['question__title', 'user__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['question']

    def content_preview(self, obj):
        """내용 미리보기"""
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = '내용'
