from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.db.models import Q

from apps.courses.models import Lesson


class Quiz(models.Model):
    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name="quiz",
    )

    title = models.CharField(max_length=200)

    passing_score = models.PositiveSmallIntegerField(
        default=70,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    is_published = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    text = models.TextField()

    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

        constraints = [
            models.UniqueConstraint(
                fields=["quiz", "order"],
                name="unique_question_order_per_quiz",
            ),
        ]

    def __str__(self):
        return self.text[:80]


class AnswerChoice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )

    text = models.CharField(max_length=500)

    is_correct = models.BooleanField(
        default=False
    )

    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

        constraints = [
            models.UniqueConstraint(
                fields=["question", "order"],
                name="unique_choice_order_per_question",
            ),

            models.UniqueConstraint(
                fields=["question"],
                condition=Q(is_correct=True),
                name="unique_correct_choice_per_question",
            ),
        ]

    def __str__(self):
        return self.text
