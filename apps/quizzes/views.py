from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET
from django.contrib import messages
from apps.progress.models import Enrollment
from django.db import transaction
from .models import Quiz
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from .models import QuizAttempt, QuizAttemptAnswer
from django.core.paginator import Paginator
from django.db.models import Count, Max, Q


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


@login_required
@require_POST
def submit_quiz(request, quiz_id):

    # Chỉ cho phép nộp Quiz đã xuất bản.
    quiz = get_object_or_404(
        Quiz.objects.select_related(
            "lesson__module__course"
        ).prefetch_related(
            "questions__choices"
        ),
        pk=quiz_id,
        is_published=True,
        lesson__is_published=True,
        lesson__module__course__is_published=True,
    )

    course = quiz.lesson.module.course

    # Kiểm tra học viên đã đăng ký khóa học.
    get_object_or_404(
        Enrollment,
        user=request.user,
        course=course,
    )

    questions = list(quiz.questions.all())

    if not questions:
        messages.error(
            request,
            "Quiz chưa có câu hỏi."
        )
        return redirect(
            "quizzes:take",
            quiz_id=quiz.id,
        )

    # Lưu đáp án tạm thời, chưa ghi database.
    submitted_answers = []

    for question in questions:

        choices = list(question.choices.all())

        # Kiểm tra ngân hàng câu hỏi hợp lệ.
        if (
            len(choices) != 4
            or sum(choice.is_correct for choice in choices) != 1
        ):
            messages.error(
                request,
                "Quiz có câu hỏi chưa hợp lệ."
            )
            return redirect(
                "quizzes:detail",
                quiz_id=quiz.id,
            )

        field_name = f"question_{question.id}"

        # Mỗi câu phải gửi đúng một đáp án.
        selected_values = request.POST.getlist(field_name)

        if len(selected_values) != 1:
            messages.error(
                request,
                "Bạn cần trả lời đầy đủ các câu hỏi."
            )
            return redirect(
                "quizzes:detail",
                quiz_id=quiz.id,
            )

        # Chỉ chấp nhận đáp án thuộc đúng câu hỏi.
        choice_map = {
            str(choice.id): choice
            for choice in choices
        }

        selected_choice = choice_map.get(
            selected_values[0]
        )

        if selected_choice is None:
            messages.error(
                request,
                "Đáp án gửi lên không hợp lệ."
            )
            return redirect(
                "quizzes:detail",
                quiz_id=quiz.id,
            )

        submitted_answers.append(
            (question, selected_choice)
        )

    # Chấm điểm ở server.
    total_questions = len(questions)

    correct_answers = sum(
        1
        for question, choice in submitted_answers
        if choice.is_correct
    )

    score_percent = (
        Decimal(correct_answers * 100)
        / Decimal(total_questions)
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    passed = score_percent >= quiz.passing_score

    # Lưu lần làm bài và từng đáp án trong một transaction.
    with transaction.atomic():

        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            total_questions=total_questions,
            correct_answers=correct_answers,
            score_percent=score_percent,
            passed=passed,
        )

        QuizAttemptAnswer.objects.bulk_create([
            QuizAttemptAnswer(
                attempt=attempt,
                question=question,
                selected_choice=choice,
                is_correct=choice.is_correct,
            )
            for question, choice in submitted_answers
        ])

    return redirect(
        "quizzes:result",
        attempt_id=attempt.id,
    )


@login_required
@require_GET
def quiz_result(request, attempt_id):

    attempt = get_object_or_404(
        QuizAttempt.objects.select_related(
            "quiz",
            "quiz__lesson__module__course",
        ),
        pk=attempt_id,
        user=request.user,
    )

    return render(
        request,
        "quizzes/quiz_result.html",
        {
            "attempt": attempt,
            "quiz": attempt.quiz,
            "course": attempt.quiz.lesson.module.course,
        },
    )

@login_required
@require_GET
def quiz_history(request):

    # Chỉ lấy lịch sử của người dùng hiện tại.
    attempts = QuizAttempt.objects.filter(
        user=request.user
    )

    # Thống kê tổng lượt làm và điểm cao nhất.
    overall_stats = attempts.aggregate(
        total_attempts=Count("id"),
        best_score=Max("score_percent"),
    )

    # Thống kê theo từng Quiz.
    quiz_stats = (
        attempts.order_by()
        .values("quiz_id", "quiz__title")
        .annotate(
            attempt_count=Count("id"),
            best_score=Max("score_percent"),
            passed_count=Count(
                "id",
                filter=Q(passed=True),
            ),
        )
        .order_by("quiz__title")
    )

    # Lịch sử mới nhất hiển thị trước.
    attempt_list = (
        attempts.select_related("quiz")
        .order_by("-submitted_at", "-id")
    )

    # Hiển thị tối đa 10 lần làm trên một trang.
    paginator = Paginator(attempt_list, 10)

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "overall_stats": overall_stats,
        "quiz_stats": quiz_stats,
        "page_obj": page_obj,
    }

    return render(
        request,
        "quizzes/quiz_history.html",
        context,
    )

@login_required
@require_GET
def quiz_overview(request, quiz_id):

    quiz = get_object_or_404(
        Quiz.objects.select_related(
            "lesson__module__course"
        ),
        pk=quiz_id,
    )

    lesson = quiz.lesson
    course = lesson.module.course

    # Học viên chỉ được xem Quiz đã xuất bản
    # thuộc khóa học mà mình đã đăng ký.
    if not request.user.is_staff:
        if not (
            quiz.is_published
            and lesson.is_published
            and course.is_published
        ):
            raise Http404("Quiz chưa được xuất bản.")

        if not Enrollment.objects.filter(
            user=request.user,
            course=course,
        ).exists():
            raise Http404("Bạn chưa đăng ký khóa học.")

    # Chỉ lấy lịch sử của người đang đăng nhập.
    attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        user=request.user,
    )

    stats = attempts.aggregate(
        total_attempts=Count("id"),
        best_score=Max("score_percent"),
    )

    # Mỗi trang hiển thị tối đa 5 lần làm.
    page_obj = Paginator(
        attempts.order_by("-submitted_at", "-id"),
        5,
    ).get_page(request.GET.get("page"))

    return render(
        request,
        "quizzes/quiz_overview.html",
        {
            "quiz": quiz,
            "lesson": lesson,
            "course": course,
            "stats": stats,
            "page_obj": page_obj,
        },
    )
