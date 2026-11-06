from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .models import Quiz, Question, AnswerChoice


class AnswerChoiceInlineFormSet(BaseInlineFormSet):

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        choices = [
            data
            for data in self.cleaned_data
            if data
            and not data.get("DELETE", False)
            and data.get("text")
        ]

        correct_count = sum(
            1 for choice in choices
            if choice.get("is_correct")
        )

        if correct_count != 1:
            raise ValidationError(
                "Mỗi câu hỏi phải có đúng 1 đáp án đúng."
            )


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    formset = AnswerChoiceInlineFormSet

    extra = 4
    min_num = 4
    max_num = 4

    validate_min = True
    validate_max = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "lesson",
        "passing_score",
        "is_published",
    )

    list_filter = ("is_published",)
    search_fields = ("title", "lesson__title")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "order")

    list_filter = ("quiz",)
    search_fields = ("text",)

    inlines = [AnswerChoiceInline]


@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "question",
        "is_correct",
        "order",
    )

    list_filter = ("is_correct",)
    search_fields = ("text",)
