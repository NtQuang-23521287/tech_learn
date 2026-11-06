
from django.core.validators import MinValueValidator
from django.db import models

from django_prose_editor.fields import ProseEditorField

from apps.courses.models import Lesson


class Lab(models.Model):

    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="labs",
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    instructions = ProseEditorField(
        extensions={
            "Bold": True,
            "Italic": True,
            "Heading": {"levels": [2, 3]},
            "BulletList": True,
            "OrderedList": True,
            "ListItem": True,
            "Code": True,
            "CodeBlock": True,
            "Link": True,
        },
        sanitize=True,
    )

    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
    )

    estimated_minutes = models.PositiveSmallIntegerField(
        default=15,
        validators=[MinValueValidator(1)],
    )

    order = models.PositiveIntegerField(default=1)

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "order"],
                name="unique_lab_order_per_lesson",
            ),
        ]

    def __str__(self):
        return self.title


class LabTask(models.Model):

    lab = models.ForeignKey(
        Lab,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(max_length=200)

    instructions = models.TextField()

    expected_result = models.TextField(
        blank=True,
        help_text="Mô tả kết quả học viên cần đạt.",
    )

    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

        constraints = [
            models.UniqueConstraint(
                fields=["lab", "order"],
                name="unique_task_order_per_lab",
            ),
        ]

    def __str__(self):
        return self.title
