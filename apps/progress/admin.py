
from django.contrib import admin

from .models import Enrollment, LessonProgress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "course",
        "enrolled_at",
    )

    list_filter = (
        "course",
        "enrolled_at",
    )

    search_fields = (
        "user__username",
        "course__title",
    )

    readonly_fields = ("enrolled_at",)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "lesson",
        "completed_at",
    )

    list_filter = (
        "enrollment__course",
        "completed_at",
    )

    search_fields = (
        "enrollment__user__username",
        "enrollment__course__title",
        "lesson__title",
    )

    readonly_fields = ("completed_at",)
