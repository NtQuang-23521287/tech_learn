
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

