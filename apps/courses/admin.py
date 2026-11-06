
from django.contrib import admin

from .models import Category, Course, CourseModule, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "level",
        "is_published",
        "created_at",
    )

    list_filter = (
        "category",
        "level",
        "is_published",
    )

    search_fields = (
        "title",
        "summary",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "order",
    )

    list_filter = ("course",)

    search_fields = ("title", "description")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "module",
        "order",
        "is_published",
    )

    list_filter = (
        "module",
        "is_published",
    )

    search_fields = ("title", "content")

    prepopulated_fields = {
        "slug": ("title",),
    }

