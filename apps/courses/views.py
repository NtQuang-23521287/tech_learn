from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from .models import Course, CourseModule, Lesson
from apps.progress.models import Enrollment, LessonProgress
from apps.quizzes.models import Quiz


def course_list(request):
    courses = Course.objects.select_related(
        "category"
    )

    if not request.user.is_staff:
        courses = courses.filter(is_published=True)

    context = {
        "courses": courses,
    }

    return render(
        request,
        "courses/course_list.html",
        context,
    )

def course_detail(request, slug):
    courses = Course.objects.select_related("category")

    # Học viên chỉ được xem khóa học đã xuất bản.
    if not request.user.is_staff:
        courses = courses.filter(is_published=True)

    course = get_object_or_404(courses, slug=slug)
    
    is_enrolled = (
        request.user.is_authenticated
        and course.enrollments.filter(
            user=request.user
        ).exists()
    )
    
    total_lessons = 0
    completed_lessons = 0
    progress_percent = 0

    if is_enrolled and course.is_published:

        # Đếm các bài học đã xuất bản trong khóa học.
        total_lessons = Lesson.objects.filter(
            module__course=course,
            is_published=True,
        ).count()

        # Đếm các bài học học viên đã hoàn thành.
        completed_lessons = LessonProgress.objects.filter(
            enrollment__user=request.user,
            enrollment__course=course,
            lesson__module__course=course,
            lesson__is_published=True,
        ).count()

        if total_lessons > 0:
            progress_percent = round(
                completed_lessons / total_lessons * 100
            )


    modules = CourseModule.objects.filter(course=course)

    # Admin xem được các bài học đang ở trạng thái nháp.
    if request.user.is_staff:
        modules = modules.prefetch_related("lessons")
    else:
        modules = modules.prefetch_related(
            Prefetch(
                "lessons",
                queryset=Lesson.objects.filter(is_published=True),
            )
        )

    context = {
        "course": course,
        "modules": modules,
        "is_enrolled": is_enrolled,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "progress_percent": progress_percent,
    }

    return render(
        request,
        "courses/course_detail.html",
        context,
    )


def lesson_detail(request, course_slug, module_id, lesson_slug):
    # Staff được xem bản nháp để kiểm thử.
    is_staff = request.user.is_staff

    lessons = Lesson.objects.select_related(
        "module__course"
    )

    if not is_staff:
        lessons = lessons.filter(
            is_published=True,
            module__course__is_published=True,
        )

    lesson = get_object_or_404(
        lessons,
        slug=lesson_slug,
        module_id=module_id,
        module__course__slug=course_slug,
    )

    course = lesson.module.course

    quiz_query = Quiz.objects.filter(lesson=lesson)

    if not request.user.is_staff:
        quiz_query = quiz_query.filter(is_published=True)

    lesson_quiz = quiz_query.first()
    
    # Lấy enrollment của học viên hiện tại.
    enrollment = None

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=course,
        ).first()

    # Học viên thường phải đăng ký mới được đọc bài.
    # Staff vẫn có quyền xem trước khi biên tập.
    if not is_staff and enrollment is None:
        messages.warning(
            request,
            "Bạn cần tham gia khóa học để xem bài học."
        )
        return redirect(
            "courses:detail",
            slug=course.slug,
        )

    is_enrolled = enrollment is not None

    # Kiểm tra bài học đã hoàn thành hay chưa.
    is_completed = False

    if enrollment:
        is_completed = LessonProgress.objects.filter(
            enrollment=enrollment,
            lesson=lesson,
        ).exists()


    visible_lessons = Lesson.objects.all()

    if not is_staff:
        visible_lessons = visible_lessons.filter(
            is_published=True
        )

    modules = CourseModule.objects.filter(
        course=course
    ).prefetch_related(
        Prefetch(
            "lessons",
            queryset=visible_lessons,
        )
    )

    # Tạo danh sách bài học theo thứ tự.
    lesson_sequence = [
        item
        for module in modules
        for item in module.lessons.all()
    ]

    current_index = next(
        index
        for index, item in enumerate(lesson_sequence)
        if item.pk == lesson.pk
    )

    previous_lesson = (
        lesson_sequence[current_index - 1]
        if current_index > 0
        else None
    )

    next_lesson = (
        lesson_sequence[current_index + 1]
        if current_index + 1 < len(lesson_sequence)
        else None
    )

    return render(
        request,
        "courses/lesson_detail.html",
        {
            "course": course,
            "lesson": lesson,
            "modules": modules,
            "previous_lesson": previous_lesson,
            "next_lesson": next_lesson,
            "is_enrolled": is_enrolled,
            "is_completed": is_completed,
            "lesson_quiz": lesson_quiz,
        },
    )
