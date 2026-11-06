
from django.contrib import admin

from .models import Lab, LabTask


class LabTaskInline(admin.TabularInline):
    model = LabTask

    extra = 3

    fields = (
        "order",
        "title",
        "instructions",
        "expected_result",
    )


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "lesson",
        "difficulty",
        "estimated_minutes",
        "order",
        "is_published",
    )

    list_filter = (
        "is_published",
        "difficulty",
    )

    search_fields = (
        "title",
        "lesson__title",
    )

    inlines = [LabTaskInline]
