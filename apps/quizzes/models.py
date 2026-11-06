from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.conf import settings
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


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.PROTECT,
        related_name="attempts",
    )

    total_questions = models.PositiveIntegerField()

    correct_answers = models.PositiveIntegerField()

    score_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    passed = models.BooleanField(default=False)

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-submitted_at", "-id"]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.quiz.title} - "
            f"{self.score_percent}%"
        )


class QuizAttemptAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
    )

    selected_choice = models.ForeignKey(
        AnswerChoice,
        on_delete=models.PROTECT,
    )

    is_correct = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"],
                name="unique_answer_per_attempt_question",
            ),
        ]

    def __str__(self):
        return f"Attempt {self.attempt_id} - Question {self.question_id}"
