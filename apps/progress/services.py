
from apps.courses.models import Lesson
from apps.quizzes.models import Quiz, QuizAttempt

from .models import LessonProgress


def get_course_progress(enrollment):
    result = {
        "total_lessons": 0,
        "completed_lessons": 0,
        "total_quizzes": 0,
        "passed_quizzes": 0,
        "total_activities": 0,
        "completed_activities": 0,
        "progress_percent": 0,
    }

    if enrollment is None:
        return result

    course = enrollment.course

    if not course.is_published:
        return result

    # 1. Các bài học đã xuất bản.
    lessons = Lesson.objects.filter(
        module__course=course,
        is_published=True,
    )

    total_lessons = lessons.count()

    completed_lessons = LessonProgress.objects.filter(
        enrollment=enrollment,
        lesson__in=lessons,
    ).count()

    # 2. Các Quiz đã xuất bản thuộc Lesson hợp lệ.
    quizzes = Quiz.objects.filter(
        lesson__in=lessons,
        is_published=True,
    )

    total_quizzes = quizzes.count()

    # Chỉ tính mỗi Quiz một lần,
    # dù học viên đã vượt qua nhiều lần.
    passed_quizzes = (
        QuizAttempt.objects.filter(
            user=enrollment.user,
            quiz__in=quizzes,
            passed=True,
        )
        .values("quiz_id")
        .distinct()
        .count()
    )

    # 3. Tính tiến độ chung.
    total_activities = total_lessons + total_quizzes

    completed_activities = (
        completed_lessons + passed_quizzes
    )

    progress_percent = (
        round(
            completed_activities / total_activities * 100
        )
        if total_activities > 0
        else 0
    )

    result.update({
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "total_quizzes": total_quizzes,
        "passed_quizzes": passed_quizzes,
        "total_activities": total_activities,
        "completed_activities": completed_activities,
        "progress_percent": progress_percent,
    })

    return result
