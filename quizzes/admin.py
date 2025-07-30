# In quizzes/admin.py

from django.contrib import admin
from .models import Question, Answer, QuizAttempt, UserAnswer

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'video', 'sequence_number')
    list_filter = ('video',)
    search_fields = ('question_text',)
    inlines = [AnswerInline]

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'attempt_number', 'status', 'score', 'percentage', 'is_passed')
    list_filter = ('status', 'is_passed', 'video')
    search_fields = ('user__username', 'video__title')

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('quiz_attempt', 'question', 'is_correct')
    list_filter = ('is_correct',)