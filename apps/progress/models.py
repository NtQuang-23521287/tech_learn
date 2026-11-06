
from django.conf import settings
from django.db import models

from apps.courses.models import Course, Lesson


class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_enrollment",
            )
        ]

        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

class LessonProgress(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="completions",
    )

    completed_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-completed_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "lesson"],
                name="unique_enrollment_lesson_progress",
            )
        ]

    def __str__(self):
        return (
            f"{self.enrollment.user.username} - "
            f"{self.lesson.title}"
        )
