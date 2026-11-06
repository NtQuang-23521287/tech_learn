
from django.shortcuts import render
from .models import Course
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from .models import CourseModule, Lesson



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
        },
    )
