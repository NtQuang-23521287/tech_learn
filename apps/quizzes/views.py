
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from apps.progress.models import Enrollment

from .models import Quiz


@login_required
@require_GET
def quiz_detail(request, quiz_id):

    quiz = get_object_or_404(
        Quiz.objects.select_related(
            "lesson__module__course"
        ),
        pk=quiz_id,
    )

    lesson = quiz.lesson
    course = lesson.module.course

    # Staff được xem trước Quiz bản nháp.
    if not request.user.is_staff:

        if not (
            quiz.is_published
            and lesson.is_published
            and course.is_published
        ):
            raise Http404(
                "Bài kiểm tra chưa được xuất bản."
            )

        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=course,
        ).exists()

        if not is_enrolled:
            raise Http404(
                "Bạn chưa tham gia khóa học."
            )

    questions = []
    quiz_ready = True

    for question in quiz.questions.prefetch_related("choices"):
        choices = list(question.choices.all())

        # Kiểm tra tính hợp lệ của câu hỏi.
        if (
            len(choices) != 4
            or sum(c.is_correct for c in choices) != 1
        ):
            quiz_ready = False

        # Chỉ truyền ID và nội dung đáp án.
        # Không truyền is_correct xuống giao diện.
        questions.append({
            "id": question.id,
            "text": question.text,
            "choices": [
                {
                    "id": choice.id,
                    "text": choice.text,
                    "label": chr(65 + index),
                }
                for index, choice in enumerate(choices)
            ],
        })

    if not questions:
        quiz_ready = False

    if not quiz_ready and not request.user.is_staff:
        raise Http404("Quiz chưa sẵn sàng.")

    return render(
        request,
        "quizzes/quiz_detail.html",
        {
            "quiz": quiz,
            "lesson": lesson,
            "course": course,
            "questions": questions,
            "quiz_ready": quiz_ready,
        },
    )
